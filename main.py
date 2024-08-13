from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from database import database, metadata, engine
from models import items, users
from schemas import Item, User, UserInDB,UserLogin,TokenRefreshRequest
from auth.auth_bearer import JWTBearer
from auth.auth_handler import sign_jwt, get_password_hash, verify_password, create_access_token,decode_refresh_token

app = FastAPI()

metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# @app.post("/signup", status_code=status.HTTP_201_CREATED)
# async def signup(user: User):
#     hashed_password = get_password_hash(user.password)
#     query = users.insert().values(username=user.username, hashed_password=hashed_password)
#     try:
#         await database.execute(query)
#         return {"message": "User created successfully"}
#     except IntegrityError:
#         raise HTTPException(status_code=400, detail="Username already registered")

@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: User):
    hashed_password = get_password_hash(user.password)
    query = users.insert().values(
        username=user.username,
        phone_number=user.phone_number,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password
    )
    try:
        await database.connect()  # Ensure the database is connected
        await database.execute(query)
        await database.disconnect()  # Disconnect from the database
        return {"message": "User created successfully"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already registered")

@app.post("/login")
async def login(user: UserLogin):
    query = select(users).where(users.c.username == user.username)
    result = await database.fetch_one(query)
    
    if not result:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    user_in_db = UserInDB(username=result['username'], hashed_password=result['hashed_password'])
    
    if not verify_password(user.password, user_in_db.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = sign_jwt(
        user_id=str(result['id']),
        username=result['username'],
        first_name=result['first_name'],
        last_name=result['last_name'],
        email=result['email']
    )['access_token']
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/refresh-token/")
async def refresh_token(request: TokenRefreshRequest):
    # Check if the token has three segments
    if len(request.refresh_token.split(".")) != 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token format")

    try:
        # Decode and validate the refresh token
        payload = decode_refresh_token(request.refresh_token)
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid refresh token: {e}")
    
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    
    user_id = payload.get("user_id")
    username = payload.get("username")
    first_name = payload.get("first_name")
    last_name = payload.get("last_name")
    email = payload.get("email")

    if not user_id or not username or not first_name or not last_name or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    # Generate a new access token with full user details
    access_token = sign_jwt(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email
    )['access_token']
    
    return {"access_token": access_token, "token_type": "bearer"}
    
@app.post("/items/", response_model=Item, dependencies=[Depends(JWTBearer())])
async def create_item(item: Item):
    query = items.insert().values(name=item.name, qty=item.qty)
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}

@app.put("/items/{item_id}", response_model=Item, dependencies=[Depends(JWTBearer())])
async def update_item(item_id: int, item: Item):
    query = items.update().where(items.c.id == item_id).values(name=item.name, qty=item.qty)
    await database.execute(query)
    return {**item.dict(), "id": item_id}

@app.delete("/items/{item_id}", dependencies=[Depends(JWTBearer())])
async def delete_item(item_id: int):
    query = items.delete().where(items.c.id == item_id)
    await database.execute(query)
    return {"message": "Item deleted successfully"}
