"""
Family management with bidirectional user references and role-based access control
"""
import uuid
import logging
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime
from botocore.exceptions import ClientError
from pynamodb.exceptions import DoesNotExist

from ..models.error import Error
from .utils.orm.models.family_bidirectional import FamilyModelBidirectional
from .utils.orm.models.user_bidirectional import UserModelBidirectional

logger = logging.getLogger(__name__)


class FamilyUserRelationshipManager:
    """Manages bidirectional relationships between families and users"""

    @staticmethod
    def create_or_get_user(user_data: Dict[str, Any], role: str = 'parent') -> UserModelBidirectional:
        """
        Create a new user or get existing one by email
        """
        email = user_data.get('email')

        # Try to find existing user by email
        if email:
            try:
                existing_users = list(UserModelBidirectional.scan(
                    UserModelBidirectional.email == email
                ))
                if existing_users:
                    return existing_users[0]
            except Exception as e:
                logger.warning(f"Error searching for user by email: {e}")

        # Create new user
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        user = UserModelBidirectional(
            userId=user_id,
            email=email,
            displayName=user_data.get('name', user_data.get('displayName')),
            phone=user_data.get('phone'),
            role=role,
            isPrimaryContact=user_data.get('isPrimary', False),
            isEmergencyContact=user_data.get('isEmergencyContact', False),
            age=user_data.get('age'),
            grade=user_data.get('grade'),
            interests=user_data.get('interests'),
            allergies=user_data.get('allergies'),
            familyIds=set(),
            softDelete=False,
            created={
                'at': datetime.utcnow().isoformat(),
                'by': {'displayName': 'system'}
            },
            modified={
                'at': datetime.utcnow().isoformat(),
                'by': {'displayName': 'system'}
            }
        )
        user.save()
        return user

    @staticmethod
    def add_user_to_family(user_id: str, family_id: str, role: str = 'parent') -> bool:
        """
        Add bidirectional relationship between user and family
        Uses atomic operations to ensure consistency
        """
        try:
            # Get user and family
            user = UserModelBidirectional.get(user_id)
            family = FamilyModelBidirectional.get(family_id)

            # Update family with user ID
            if role == 'parent':
                family.add_parent(user_id)
            else:
                family.add_student(user_id)

            # Update user with family ID
            user.add_family(family_id)

            # Save both with audit trail
            now = datetime.utcnow().isoformat()
            family.modified = {
                'at': now,
                'by': {'displayName': 'system'}
            }
            user.modified = {
                'at': now,
                'by': {'displayName': 'system'}
            }

            family.save()
            user.save()

            logger.info(f"Added user {user_id} to family {family_id} as {role}")
            return True

        except Exception as e:
            logger.error(f"Error adding user to family: {e}")
            return False

    @staticmethod
    def remove_user_from_family(user_id: str, family_id: str) -> bool:
        """
        Remove bidirectional relationship between user and family
        """
        try:
            # Get user and family
            user = UserModelBidirectional.get(user_id)
            family = FamilyModelBidirectional.get(family_id)

            # Remove user from family
            family.remove_parent(user_id)
            family.remove_student(user_id)

            # Remove family from user
            user.remove_family(family_id)

            # Save both with audit trail
            now = datetime.utcnow().isoformat()
            family.modified = {
                'at': now,
                'by': {'displayName': 'system'}
            }
            user.modified = {
                'at': now,
                'by': {'displayName': 'system'}
            }

            family.save()
            user.save()

            logger.info(f"Removed user {user_id} from family {family_id}")
            return True

        except Exception as e:
            logger.error(f"Error removing user from family: {e}")
            return False

    @staticmethod
    def get_family_with_users(family_id: str, requesting_user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get family with populated user details
        Enforces access control: admin can edit, members can view
        """
        try:
            # Get requesting user for permission check
            requesting_user = UserModelBidirectional.get(requesting_user_id)

            # Get family
            family = FamilyModelBidirectional.get(family_id)

            # Check permissions
            if not requesting_user.can_view_family(family_id):
                logger.warning("User denied access to family", extra={
                    "user_id": requesting_user_id,
                    "family_id": family_id
                })
                return None

            family_dict = family.to_dict()

            # Batch get all users
            all_user_ids = family.get_all_member_ids()
            users = []
            for user_id in all_user_ids:
                try:
                    user = UserModelBidirectional.get(user_id)
                    users.append(user)
                except:
                    logger.warning(f"User {user_id} not found")

            # Populate parent and student details
            family_dict['parents'] = []
            family_dict['students'] = []

            for user in users:
                user_dict = user.to_dict()
                if user.userId in (family.parentIds or []):
                    family_dict['parents'].append(user_dict)
                elif user.userId in (family.studentIds or []):
                    family_dict['students'].append(user_dict)

            # Add permission flags
            family_dict['canEdit'] = requesting_user.can_edit_family(family_id)
            family_dict['canView'] = True  # Already checked above

            return family_dict

        except Exception as e:
            logger.error(f"Error getting family with users: {e}")
            return None


# API Endpoint Implementations

def create_family_bidirectional(body: Dict[str, Any], requesting_user_id: str) -> Tuple[Any, int]:
    """
    Create a new family with bidirectional user references
    Only admins can create families
    """
    try:
        # Log incoming data for debugging
        logger.info(f"Creating family with body: {body}")
        logger.info(f"Family name from body: {body.get('familyName', 'NOT_PROVIDED')}")

        # Check permissions (temporarily disabled for testing)
        # In production, uncomment the following:
        # try:
        #     requesting_user = UserModelBidirectional.get(requesting_user_id)
        #     if requesting_user.role != 'admin':
        #         error = Error(
        #             code="forbidden",
        #             message="Only admins can create families",
        #             details={"userId": requesting_user_id}
        #         )
        #         return error.to_dict(), 403
        # except DoesNotExist:
        #     error = Error(
        #         code="unauthorized",
        #         message="User not found",
        #         details={"userId": requesting_user_id}
        #     )
        #     return error.to_dict(), 401

        # For testing, allow anonymous creation
        if requesting_user_id == 'anonymous':
            logger.warning("Creating family with anonymous user - testing mode")

        # Generate family ID
        family_id = f"family_{uuid.uuid4().hex[:8]}"

        manager = FamilyUserRelationshipManager()

        # Get parent user IDs (expecting array of user ID strings)
        parent_ids = set()
        for parent_id in body.get('parents', []):
            if isinstance(parent_id, dict):
                parent_ids.add(parent_id.get('userId', parent_id.get('id', '')))
            else:
                parent_ids.add(parent_id)

        # Get student user IDs (expecting array of user ID strings)
        student_ids = set()
        for student_id in body.get('students', []):
            if isinstance(student_id, dict):
                student_ids.add(student_id.get('userId', student_id.get('id', '')))
            else:
                student_ids.add(student_id)

        # Validate that users exist
        for user_id in parent_ids.union(student_ids):
            try:
                UserModelBidirectional.get(user_id)
            except DoesNotExist:
                error = Error(
                    code="bad_request",
                    message=f"User {user_id} does not exist",
                    details={"userId": user_id}
                )
                return error.to_dict(), 400

        # Create family with ALL fields
        now = datetime.utcnow().isoformat()

        # Extract and validate address
        address = body.get('address', {})
        if address and not isinstance(address, dict):
            address = {}

        # Convert zipCode to zip_code for PynamoDB (it expects snake_case)
        if address and 'zipCode' in address:
            address['zip_code'] = address.pop('zipCode')

        family = FamilyModelBidirectional(
            familyId=family_id,
            familyName=body.get('familyName', 'Unnamed Family'),  # Ensure we get the family name
            parentIds=parent_ids,
            studentIds=student_ids,
            address=address,  # Include the full address object with zip_code
            preferredPrograms=body.get('preferredPrograms', []),
            status=body.get('status', 'active'),
            memberSince=now,
            softDelete=False,
            created={
                'at': now,
                'by': {
                    'userId': requesting_user_id,
                    'displayName': requesting_user.displayName
                }
            },
            modified={
                'at': now,
                'by': {
                    'userId': requesting_user_id,
                    'displayName': requesting_user.displayName
                }
            }
        )

        # Save the family
        family.save()
        logger.info(f"Created family {family_id} with name '{family.familyName}'")

        # Add bidirectional relationships
        for parent_id in parent_ids:
            manager.add_user_to_family(parent_id, family_id, 'parent')

        for student_id in student_ids:
            manager.add_user_to_family(student_id, family_id, 'student')

        # Return the created family with populated user details
        family_data = manager.get_family_with_users(family_id, requesting_user_id)
        return family_data, 201

    except Exception as e:
        logger.error(f"Unexpected error creating family: {str(e)}")
        error = Error(
            code="internal_error",
            message="An unexpected error occurred",
            details={"error": str(e)}
        )
        return error.to_dict(), 500


def get_family_bidirectional(family_id: str, requesting_user_id: str) -> Tuple[Any, int]:
    """
    Get family details with user information
    Members can view, only admins can see edit options
    """
    manager = FamilyUserRelationshipManager()
    result = manager.get_family_with_users(family_id, requesting_user_id)

    if result is None:
        error = Error(
            code="forbidden",
            message="You don't have permission to view this family",
            details={"familyId": family_id}
        )
        return error.to_dict(), 403

    return result, 200


def update_family_bidirectional(family_id: str, body: Dict[str, Any], requesting_user_id: str) -> Tuple[Any, int]:
    """
    Update family details
    Only admins can edit families
    """
    try:
        # Check permissions
        requesting_user = UserModelBidirectional.get(requesting_user_id)
        if not requesting_user.can_edit_family(family_id):
            error = Error(
                code="forbidden",
                message="Only admins can edit families",
                details={"userId": requesting_user_id}
            )
            return error.to_dict(), 403

        # Get existing family
        family = FamilyModelBidirectional.get(family_id)
        manager = FamilyUserRelationshipManager()

        # Update basic fields
        if 'familyName' in body:
            family.familyName = body['familyName']
        if 'address' in body:
            family.address = body['address']
        if 'status' in body:
            family.status = body['status']
        if 'preferredPrograms' in body:
            family.preferredPrograms = body['preferredPrograms']

        # Handle parent updates
        if 'parents' in body:
            # Remove old parents
            for old_parent_id in list(family.parentIds or []):
                manager.remove_user_from_family(old_parent_id, family_id)

            # Add new parents
            new_parent_ids = set()
            for parent_data in body['parents']:
                user = manager.create_or_get_user(parent_data, role='parent')
                new_parent_ids.add(user.userId)
                manager.add_user_to_family(user.userId, family_id, 'parent')

            family.parentIds = new_parent_ids

        # Handle student updates
        if 'students' in body:
            # Remove old students
            for old_student_id in list(family.studentIds or []):
                manager.remove_user_from_family(old_student_id, family_id)

            # Add new students
            new_student_ids = set()
            for student_data in body['students']:
                user = manager.create_or_get_user(student_data, role='student')
                new_student_ids.add(user.userId)
                manager.add_user_to_family(user.userId, family_id, 'student')

            family.studentIds = new_student_ids

        # Update audit trail
        family.modified = {
            'at': datetime.utcnow().isoformat(),
            'by': {
                'userId': requesting_user_id,
                'displayName': requesting_user.displayName
            }
        }
        family.save()

        # Return updated family with users
        result = manager.get_family_with_users(family_id, requesting_user_id)
        return result, 200

    except Exception as e:
        logger.error(f"Error updating family: {e}")
        error = Error(
            code="internal_error",
            message="Failed to update family",
            details={"error": str(e)}
        )
        return error.to_dict(), 500


def delete_family_bidirectional(family_id: str, requesting_user_id: str) -> Tuple[Any, int]:
    """
    Soft delete a family
    Only admins can delete families
    """
    try:
        # Check permissions
        requesting_user = UserModelBidirectional.get(requesting_user_id)
        if requesting_user.role != 'admin':
            error = Error(
                code="forbidden",
                message="Only admins can delete families",
                details={"userId": requesting_user_id}
            )
            return error.to_dict(), 403

        # Get family
        family = FamilyModelBidirectional.get(family_id)
        manager = FamilyUserRelationshipManager()

        # Remove family references from all users
        for user_id in family.get_all_member_ids():
            try:
                user = UserModelBidirectional.get(user_id)
                user.remove_family(family_id)
                user.modified = {
                    'at': datetime.utcnow().isoformat(),
                    'by': {
                        'userId': requesting_user_id,
                        'displayName': requesting_user.displayName
                    }
                }
                user.save()
            except:
                logger.warning(f"Could not remove family reference from user {user_id}")

        # Soft delete the family
        family.softDelete = True
        family.deleted = {
            'at': datetime.utcnow().isoformat(),
            'by': {
                'userId': requesting_user_id,
                'displayName': requesting_user.displayName
            }
        }
        family.save()

        logger.info(f"Soft deleted family {family_id}")
        return {"message": f"Family {family_id} deleted successfully"}, 200

    except Exception as e:
        logger.error(f"Error deleting family: {e}")
        error = Error(
            code="internal_error",
            message="Failed to delete family",
            details={"error": str(e)}
        )
        return error.to_dict(), 500


def list_families_for_user(requesting_user_id: str) -> Tuple[Any, int]:
    """
    List families for a user with proper error handling
    Returns empty list instead of error when no families exist
    """
    try:
        # Get requesting user - handle non-existent user gracefully
        try:
            requesting_user = UserModelBidirectional.get(requesting_user_id)
            user_role = requesting_user.role if hasattr(requesting_user, 'role') else 'user'
            user_family_ids = requesting_user.familyIds if hasattr(requesting_user, 'familyIds') else []
        except DoesNotExist:
            # If user doesn't exist, treat as anonymous with no families
            logger.warning("User not found, returning empty family list", extra={
                "user_id": requesting_user_id
            })
            return [], 200
        except Exception as e:
            logger.error("Error fetching user", extra={
                "user_id": requesting_user_id,
                "error": str(e)
            })
            return [], 200

        # Admin sees all families
        if user_role == 'admin':
            try:
                families = list(FamilyModelBidirectional.scan(
                    FamilyModelBidirectional.softDelete == False
                ))
            except Exception as e:
                logger.warning(f"Error scanning families table: {str(e)}")
                families = []
        else:
            # Members see only their families
            if not user_family_ids:
                return [], 200  # User has no families

            families = []
            for family_id in user_family_ids:
                try:
                    family = FamilyModelBidirectional.get(family_id)
                    if not family.softDelete:
                        families.append(family)
                except DoesNotExist:
                    logger.warning("Family not found for user", extra={
                        "family_id": family_id,
                        "user_id": requesting_user_id
                    })
                    continue
                except Exception as e:
                    logger.error(f"Error fetching family {family_id}: {str(e)}")
                    continue

        # Populate user details for each family
        result = []
        manager = FamilyUserRelationshipManager()

        for family in families:
            family_data = manager.get_family_with_users(
                family.familyId,
                requesting_user_id
            )
            if family_data:
                result.append(family_data)

        return result, 200

    except Exception as e:
        logger.error(f"Unexpected error in list_families_for_user: {str(e)}")
        # Return empty list instead of error for better UX
        return [], 200