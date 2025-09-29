"""
File-based persistence implementation for offline testing mode.

PR003946-95: Offline test mode for backend
- Implements DynamoStore protocol using JSON file storage
- Environment variable switchable persistence layer
- Supports all CRUD operations without external dependencies
"""
import json
import os
import copy
from typing import Any, Dict, List, Optional
from pathlib import Path
from ..core import now_iso
from ..id_generator import add_audit_timestamps

class FileStore:
    """
    File-based implementation of DynamoStore protocol.
    
    Uses a single JSON file per table to store data.
    Supports all DynamoDB-like operations for testing isolation.
    """
    
    def __init__(self, table_name: str, pk_name: str, id_generator_func=None):
        # Validate table name to prevent path traversal
        if not table_name or not isinstance(table_name, str):
            raise ValueError("table_name must be a non-empty string")
        
        # Sanitize table name to prevent directory traversal
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', table_name) or '..' in table_name or '/' in table_name:
            raise ValueError(f"Invalid table name: {table_name}. Only alphanumeric characters, hyphens, and underscores are allowed.")
        
        self.table_name = table_name
        self.pk_name = pk_name
        self.id_generator = id_generator_func
        
        # Set up file storage path with validation
        storage_dir_path = os.getenv("FILE_PERSISTENCE_DIR", "/tmp/cmz_test_data")
        self.storage_dir = Path(storage_dir_path).resolve()
        self.storage_dir.mkdir(exist_ok=True, parents=True)
        self.storage_file = self.storage_dir / f"{table_name}.json"
        
        # Initialize with test data if file doesn't exist
        if not self.storage_file.exists():
            self._initialize_test_data()
    
    def _initialize_test_data(self):
        """Initialize storage file with pre-populated test data."""
        test_data_path = Path(__file__).parent / "test_data.json"
        
        # Validate that the test data path is within expected directory structure
        if not test_data_path.is_file() or not test_data_path.resolve().is_relative_to(Path(__file__).parent.resolve()):
            # Create empty dataset if no valid test data file exists
            table_data = []
        else:
            try:
                with open(test_data_path, 'r', encoding='utf-8') as f:
                    all_test_data = json.load(f)
                
                # Extract data for this specific table
                table_data = all_test_data.get(self.table_name, [])
            except (json.JSONDecodeError, IOError, OSError) as e:
                # Log error and continue with empty dataset
                import logging
                logging.getLogger(__name__).warning(f"Failed to load test data from {test_data_path}: {e}")
                table_data = []
            
        self._save_data(table_data)
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """Load data from JSON file."""
        if not self.storage_file.exists():
            return []
        
        # Validate that storage file is within expected directory
        if not self.storage_file.resolve().is_relative_to(self.storage_dir.resolve()):
            import logging
            logging.getLogger(__name__).error(f"Storage file path {self.storage_file} is outside expected directory")
            return []
            
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, IOError, OSError) as e:
            logging.getLogger(__name__).warning(f"Failed to load data from {self.storage_file}: {e}")
            return []
    
    def _save_data(self, data: List[Dict[str, Any]]):
        """Save data to JSON file."""
        # Validate that storage file is within expected directory
        if not self.storage_file.resolve().is_relative_to(self.storage_dir.resolve()):
            logging.getLogger(__name__).error(f"Storage file path {self.storage_file} is outside expected directory")
            raise ValueError(f"Invalid storage path: {self.storage_file}")
            
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except (IOError, OSError) as e:
            logging.getLogger(__name__).error(f"Failed to save data to {self.storage_file}: {e}")
            raise
    
    def _find_item_index(self, data: List[Dict[str, Any]], pk_value: Any) -> Optional[int]:
        """Find index of item with given primary key value."""
        for i, item in enumerate(data):
            if item.get(self.pk_name) == pk_value:
                return i
        return None
    
    def list(self, hide_soft_deleted: bool = True) -> List[Dict[str, Any]]:
        """
        List all entities, optionally filtering soft-deleted ones.
        
        PR003946-66: Soft-delete flag consistency across all entities
        """
        data = self._load_data()
        
        if hide_soft_deleted:
            # Filter out soft-deleted items
            return [item for item in data if not item.get("softDelete", False)]
        
        return data
    
    def get(self, pk: Any) -> Optional[Dict[str, Any]]:
        """Get a single item by primary key."""
        data = self._load_data()
        index = self._find_item_index(data, pk)
        
        if index is not None:
            return copy.deepcopy(data[index])
        
        return None
    
    def create(self, item: Dict[str, Any]) -> None:
        """Create a new item."""
        item = copy.deepcopy(item)
        pk_value = item.get(self.pk_name)
        
        # PR003946-69: Auto-generate ID if not provided
        if pk_value in (None, ""):
            if self.id_generator:
                item = self.id_generator(item)
                pk_value = item.get(self.pk_name)
            else:
                from botocore.exceptions import ClientError
                raise ClientError(
                    {"Error": {"Code": "ValidationException",
                               "Message": f"Missing required primary key '{self.pk_name}' and no ID generator configured"}},
                    "PutItem",
                )
        
        # Add audit timestamps
        item = add_audit_timestamps(item)
        
        # Check if item already exists
        data = self._load_data()
        if self._find_item_index(data, pk_value) is not None:
            from botocore.exceptions import ClientError
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException",
                           "Message": f"Item already exists: {self.pk_name}={pk_value}"}},
                "PutItem",
            )
        
        # Add the new item
        data.append(item)
        self._save_data(data)
    
    def update_fields(self, pk: Any, fields: Dict[str, Any]) -> None:
        """Update specific fields of an existing item."""
        data = self._load_data()
        index = self._find_item_index(data, pk)
        
        if index is None:
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException",
                           "Message": f"Item does not exist: {self.pk_name}={pk}"}},
                "UpdateItem",
            )
        
        # Update fields (skip primary key and None values)
        for key, value in fields.items():
            if key == self.pk_name or value is None:
                continue
            data[index][key] = value
        
        # Update modification timestamp
        data[index]["modified"] = {"at": now_iso()}
        
        self._save_data(data)
    
    def soft_delete(self, pk: Any, soft_field: str = "softDelete") -> None:
        """
        Soft delete an entity by setting the soft delete flag.
        
        PR003946-66: Consistent soft-delete implementation
        """
        data = self._load_data()
        index = self._find_item_index(data, pk)
        
        if index is None:
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException",
                           "Message": f"Item does not exist: {self.pk_name}={pk}"}},
                "UpdateItem",
            )
        
        # Set soft delete flag and update modification timestamp
        data[index][soft_field] = True
        data[index]["modified"] = {"at": now_iso()}
        
        self._save_data(data)
    
    def recover_soft_deleted(self, pk: Any, soft_field: str = "softDelete") -> None:
        """
        Recover a soft-deleted entity by unsetting the soft delete flag.
        
        PR003946-68: Soft-delete recovery functionality
        """
        data = self._load_data()
        index = self._find_item_index(data, pk)
        
        if index is None:
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException",
                           "Message": f"Item does not exist: {self.pk_name}={pk}"}},
                "UpdateItem",
            )
        
        # Unset soft delete flag and update modification timestamp
        data[index][soft_field] = False
        data[index]["modified"] = {"at": now_iso()}
        
        self._save_data(data)
    
    def exists_on_gsi(self, index_attr_name: str, value: str, *, hide_soft_deleted: bool = True) -> bool:
        """
        Returns True if there's at least one item with the given attribute value.
        Simulates GSI query for file-based storage.
        """
        data = self._load_data()
        
        for item in data:
            # Check if attribute matches
            if item.get(index_attr_name) != value:
                continue
                
            # Check soft delete status if needed
            if hide_soft_deleted and item.get("softDelete", False):
                continue
                
            return True
            
        return False
    
    def query_gsi(self, index_attr_name: str, value: str, *, limit: int = 100):
        """
        Simulate GSI query for file-based storage.
        Returns list of items matching the attribute value.
        """
        data = self._load_data()
        results = []
        
        for item in data:
            if item.get(index_attr_name) == value:
                results.append(item)
                if len(results) >= limit:
                    break
                    
        return results