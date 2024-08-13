from pydantic import BaseModel, EmailStr, constr

class Item(BaseModel):
    name: str
    qty: int

class User(BaseModel):
    username: str
    phone_number: constr(max_length=20) = None  # Optional phone number with max length constraint
    email: EmailStr  # Validates email format
    first_name: constr(max_length=50)
    last_name: constr(max_length=50)
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
    
class UserInDB(BaseModel):
    username: str
    hashed_password: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str