import time
from typing import Dict
from passlib.context import CryptContext
import jwt
from decouple import config
from datetime import datetime, timedelta

# Use default values if environment variables are not set
JWT_SECRET = config("secret", default="5a46acd86f0dcc06f9ea2689603e23b49f1eaf000d45d1e5")
JWT_ALGORITHM = config("algorithm", default="HS256")

# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = 10  # Access token expires in 10 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Refresh token expires in 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def token_response(access_token: str, refresh_token: str) -> Dict[str, str]:
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def sign_jwt(user_id: str, username: str, first_name: str, last_name: str, email: str) -> Dict[str, str]:
    # Create access token
    access_token_expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_payload = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "exp": access_token_expires
    }
    access_token = jwt.encode(access_token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Create refresh token
    refresh_token_expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_payload = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "exp": access_token_expires
    }
    refresh_token = jwt.encode(refresh_token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(access_token, refresh_token)

def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # Ensure the token is not expired
        if datetime.fromtimestamp(decoded_token["exp"]) >= datetime.utcnow():
            return decoded_token
        else:
            return {}
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return {}
    except jwt.InvalidTokenError as e:
        print(f"Invalid token error: {e}")
        return {}

def decode_refresh_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # Ensure the refresh token is not expired
        if datetime.fromtimestamp(decoded_token["exp"]) >= datetime.utcnow():
            return decoded_token
        else:
            return {}
    except jwt.ExpiredSignatureError:
        print("Refresh token has expired.")
        return {}
    except jwt.InvalidTokenError as e:
        print(f"Invalid refresh token error: {e}")
        return {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    # Set expiration time to 10 minutes from now
    expires = datetime.utcnow() + timedelta(minutes=10)
    to_encode = data.copy()
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt
