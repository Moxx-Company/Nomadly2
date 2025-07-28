"""
Authentication Routes for Nomadly3 API
FastAPI router for user authentication and registration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import logging

from ...schemas.user_schemas import UserRegistrationRequest, UserLoginRequest, UserResponse
from ...services.user_service import UserService
from ...repositories.user_repo import UserRepository
from ...repositories.transaction_repo import TransactionRepository
from ...core.database import get_db_session
from ...core.security import verify_jwt_token, create_jwt_token

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Create router
auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}}
)

def get_user_service() -> UserService:
    """Dependency injection for UserService"""
    db_session = get_db_session()
    user_repo = UserRepository(db_session)
    transaction_repo = TransactionRepository(db_session)
    return UserService(db_session, user_repo, transaction_repo)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """Get current authenticated user"""
    try:
        payload = verify_jwt_token(credentials.credentials)
        telegram_id = payload.get("telegram_id")
        
        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user_profile = user_service.get_user_profile(telegram_id)
        if not user_profile.get("success"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user_profile["user"]
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    registration_data: UserRegistrationRequest,
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """
    Register new user account
    
    Creates new user with Telegram ID and initial settings
    """
    try:
        logger.info(f"Registering user: {registration_data.telegram_id}")
        
        # Check if user already exists
        existing_user = user_service.get_user_profile(registration_data.telegram_id)
        if existing_user.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered"
            )
        
        # Create new user
        result = user_service.create_user(
            telegram_id=registration_data.telegram_id,
            username=registration_data.username,
            first_name=registration_data.first_name,
            last_name=registration_data.last_name,
            language_code=registration_data.language,
            initial_balance=registration_data.initial_balance
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Registration failed")
            )
        
        # Generate JWT token
        token = create_jwt_token({"telegram_id": registration_data.telegram_id})
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": result["user"],
            "access_token": token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@auth_router.post("/login", response_model=UserResponse)
async def login_user(
    login_data: UserLoginRequest,
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """
    User login authentication
    
    Authenticates user and returns JWT token
    """
    try:
        logger.info(f"Login attempt for user: {login_data.telegram_id}")
        
        # Verify user exists
        user_profile = user_service.get_user_profile(login_data.telegram_id)
        if not user_profile.get("success"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Additional validation can be added here (password, 2FA, etc.)
        
        # Generate JWT token
        token = create_jwt_token({"telegram_id": login_data.telegram_id})
        
        return {
            "success": True,
            "message": "Login successful",
            "user": user_profile["user"],
            "access_token": token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user profile
    
    Returns authenticated user's profile information
    """
    return {
        "success": True,
        "user": current_user,
        "message": "Profile retrieved successfully"
    }

@auth_router.post("/refresh")
async def refresh_token(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Refresh JWT token
    
    Issues new token for authenticated user
    """
    try:
        # Generate new JWT token
        token = create_jwt_token({"telegram_id": current_user["telegram_id"]})
        
        return {
            "success": True,
            "access_token": token,
            "token_type": "bearer",
            "message": "Token refreshed successfully"
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@auth_router.post("/logout")
async def logout_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    User logout
    
    Invalidates current session (client-side token removal)
    """
    logger.info(f"User logout: {current_user['telegram_id']}")
    
    return {
        "success": True,
        "message": "Logout successful"
    }
# Export router for import compatibility  
router = auth_router
