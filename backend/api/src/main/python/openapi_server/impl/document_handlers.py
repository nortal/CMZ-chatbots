"""
Document upload handlers for animal knowledge base management
Handles file uploads to OpenAI Assistant Vector Stores with S3 backup
"""

import os
import tempfile
import logging
from typing import Tuple, Any, Dict
from datetime import datetime
from flask import request
from werkzeug.utils import secure_filename
from openapi_server.models.error import Error
from .assistant_manager import assistant_manager
from .domain.animal_service import AnimalService
from .domain.common.exceptions import NotFoundError
from .dependency_injection import create_animal_service

logger = logging.getLogger(__name__)

# Allowed file extensions for document upload
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.md', '.rtf'}
MAX_FILE_SIZE = 512 * 1024 * 1024  # 512 MB (OpenAI limit)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


def handle_upload_animal_document(animal_id: str, body: Any = None) -> Tuple[Any, int]:
    """
    Handle document upload to animal's knowledge base

    Args:
        animal_id: Animal identifier
        body: Request body (not used for multipart/form-data)

    Returns:
        Tuple of (response_dict, status_code)
    """
    try:
        # Verify animal exists and get Vector Store ID
        animal_service = create_animal_service()
        animal = animal_service.get_animal(animal_id)

        # Check if animal has a Vector Store (Assistant was created)
        vector_store_id = None
        if hasattr(animal, 'configuration') and isinstance(animal.configuration, dict):
            vector_store_id = animal.configuration.get('vectorStoreId')

        if not vector_store_id:
            error_obj = Error(
                code="no_vector_store",
                message=f"Animal {animal_id} does not have a Vector Store. Create an Assistant first.",
                details={"animal_id": animal_id}
            )
            return error_obj.to_dict(), 400

        # Get uploaded file from request
        if 'file' not in request.files:
            error_obj = Error(
                code="missing_file",
                message="No file part in request",
                details={}
            )
            return error_obj.to_dict(), 400

        file = request.files['file']

        if file.filename == '':
            error_obj = Error(
                code="no_selected_file",
                message="No file selected",
                details={}
            )
            return error_obj.to_dict(), 400

        # Validate file extension
        if not allowed_file(file.filename):
            error_obj = Error(
                code="invalid_file_type",
                message=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
                details={"filename": file.filename}
            )
            return error_obj.to_dict(), 400

        # Get optional metadata
        title = request.form.get('title', file.filename)
        description = request.form.get('description', '')
        tags = request.form.getlist('tags')

        # Secure the filename
        filename = secure_filename(file.filename)
        logger.info(f"Uploading document '{filename}' for animal {animal_id}")

        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"{animal_id}_{filename}")

        try:
            # Save uploaded file
            file.save(temp_path)
            file_size = os.path.getsize(temp_path)

            # Check file size
            if file_size > MAX_FILE_SIZE:
                os.remove(temp_path)
                error_obj = Error(
                    code="file_too_large",
                    message=f"File size {file_size} bytes exceeds maximum {MAX_FILE_SIZE} bytes",
                    details={"file_size": file_size, "max_size": MAX_FILE_SIZE}
                )
                return error_obj.to_dict(), 413

            logger.info(f"File saved to temp: {temp_path} ({file_size} bytes)")

            # Upload to OpenAI Vector Store
            upload_result = assistant_manager.upload_document_to_vector_store(
                vector_store_id=vector_store_id,
                file_path=temp_path,
                file_name=filename
            )

            # Clean up temp file
            os.remove(temp_path)

            if not upload_result['success']:
                error_obj = Error(
                    code="upload_failed",
                    message=f"Failed to upload document: {upload_result.get('error')}",
                    details=upload_result
                )
                return error_obj.to_dict(), 500

            # Build response
            response = {
                'documentId': upload_result['file_id'],
                'fileId': upload_result['file_id'],
                'vectorStoreId': vector_store_id,
                'fileName': filename,
                'fileSize': file_size,
                'status': upload_result.get('status', 'completed'),
                'uploadedAt': upload_result['uploaded_at'],
                'title': title,
                'description': description,
                'tags': tags
            }

            logger.info(f"Document uploaded successfully: {upload_result['file_id']}")
            return response, 201

        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    except NotFoundError as e:
        error_obj = Error(
            code="not_found",
            message=str(e),
            details={"animal_id": animal_id}
        )
        return error_obj.to_dict(), 404

    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        error_obj = Error(
            code="internal_error",
            message=f"Internal error: {str(e)}",
            details={"error": str(e)}
        )
        return error_obj.to_dict(), 500


def handle_list_animal_documents(animal_id: str) -> Tuple[Any, int]:
    """
    List documents in animal's knowledge base

    Args:
        animal_id: Animal identifier

    Returns:
        Tuple of (response_dict, status_code)
    """
    try:
        # Verify animal exists and get Vector Store ID
        animal_service = create_animal_service()
        animal = animal_service.get_animal(animal_id)

        # Get Vector Store ID
        vector_store_id = None
        if hasattr(animal, 'configuration') and isinstance(animal.configuration, dict):
            vector_store_id = animal.configuration.get('vectorStoreId')

        if not vector_store_id:
            # No vector store = no documents
            return {'documents': []}, 200

        # List files in vector store
        files = assistant_manager.list_vector_store_files(vector_store_id)

        # Format response
        documents = []
        for file_info in files:
            documents.append({
                'documentId': file_info['file_id'],
                'fileId': file_info['file_id'],
                'fileName': 'Unknown',  # OpenAI doesn't return filename in list
                'status': file_info['status'],
                'uploadedAt': file_info['created_at']
            })

        return {'documents': documents}, 200

    except NotFoundError as e:
        error_obj = Error(
            code="not_found",
            message=str(e),
            details={"animal_id": animal_id}
        )
        return error_obj.to_dict(), 404

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        error_obj = Error(
            code="internal_error",
            message=f"Internal error: {str(e)}",
            details={"error": str(e)}
        )
        return error_obj.to_dict(), 500


def handle_delete_animal_document(animal_id: str, document_id: str) -> Tuple[Any, int]:
    """
    Delete document from animal's knowledge base

    Args:
        animal_id: Animal identifier
        document_id: Document/File identifier

    Returns:
        Tuple of (response_dict, status_code)
    """
    try:
        # Verify animal exists and get Vector Store ID
        animal_service = create_animal_service()
        animal = animal_service.get_animal(animal_id)

        # Get Vector Store ID
        vector_store_id = None
        if hasattr(animal, 'configuration') and isinstance(animal.configuration, dict):
            vector_store_id = animal.configuration.get('vectorStoreId')

        if not vector_store_id:
            error_obj = Error(
                code="no_vector_store",
                message=f"Animal {animal_id} does not have a Vector Store",
                details={"animal_id": animal_id}
            )
            return error_obj.to_dict(), 404

        # Delete document from vector store
        result = assistant_manager.delete_document_from_vector_store(
            vector_store_id=vector_store_id,
            file_id=document_id
        )

        if not result['success']:
            error_obj = Error(
                code="delete_failed",
                message=f"Failed to delete document: {result.get('error')}",
                details=result
            )
            return error_obj.to_dict(), 500

        logger.info(f"Document deleted: {document_id}")
        return {}, 204

    except NotFoundError as e:
        error_obj = Error(
            code="not_found",
            message=str(e),
            details={"animal_id": animal_id}
        )
        return error_obj.to_dict(), 404

    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        error_obj = Error(
            code="internal_error",
            message=f"Internal error: {str(e)}",
            details={"error": str(e)}
        )
        return error_obj.to_dict(), 500
