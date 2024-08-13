from sqlalchemy import Table, Column, Integer, String, MetaData,ForeignKey,DateTime
from database import metadata
from sqlalchemy.sql import func

items = Table(
    "item",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("qty", Integer)
)

users = Table(
    "pemakai",  # changed table name to "users" for consistency
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50), unique=True),
    Column("phone_number", String(20), nullable=True),  # Added phone number column
    Column("email", String(100), unique=True),          # Added email column
    Column("first_name", String(50), nullable=False),   # Added first name column
    Column("last_name", String(50), nullable=False),    # Added last name column
    Column("hashed_password", String(200))              # Moved hashed_password column to the bottom
)

refresh_tokens = Table(
    "refresh_tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("pemakai.id", ondelete="CASCADE")),
    Column("refresh_token", String(255), unique=True),
    Column("expires_at", DateTime, default=lambda: datetime.utcnow() + timedelta(days=7)),  # 7 days expiry
    Column("created_at", DateTime, default=func.now())
)
