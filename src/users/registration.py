from fastapi import FastAPI, HTTPException
from database.DBconnection import DatabaseConnection
from pydantic import BaseModel
import hashlib

app = FastAPI()
db = DatabaseConnection()

class User(BaseModel):
    username: str
    password: str

@app.post("/register")
async def register_user(user: User):
    # Verify super user credentials
    if user.username != "root":
        raise HTTPException(status_code=403, detail="Unauthorized access")

    # Validate username and password
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    # Hash the password
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

    # Check if the username already exists
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (user.username,))
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Insert the new user into the database
        insert_query = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
        try:
            cursor.execute(insert_query, (user.username, hashed_password))
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to register user") from e
    
    return {"message": "User registered successfully"}

