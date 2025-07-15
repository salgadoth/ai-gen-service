import os
from fastapi import HTTPException, Request, status
import jwt  # PyJWT
from utils.logger import get_logger
from dotenv import load_dotenv  # Add this import

# Load environment variables from .env file in the root directory
load_dotenv()

# JWT secret (set JWT_SECRET in your .env file at the project root)
jwt_secret = os.getenv("JWT_SECRET", "your_jwt_secret")
# Set to True to enable role checking
enable_role_check = False
required_role = "admin"  # Example role

logger = get_logger("jwt")

# NOTE: Configure jwt_secret and enable_role_check as needed for your environment.

def verify_jwt(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header", path=str(request.url))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])  # Adjust algorithm as needed
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired", path=str(request.url))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token", path=str(request.url))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    # Optional: Role check (disabled by default)
    if enable_role_check:
        user_role = payload.get("role")
        if user_role != required_role:
            logger.warning("Role check failed", user_role=user_role, required_role=required_role, path=str(request.url))
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    logger.info("JWT validated successfully", subject=payload.get("sub"), role=payload.get("role"), path=str(request.url))
    return payload 