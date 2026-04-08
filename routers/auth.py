from fastapi import APIRouter
from jose import jwt
import database
from auth import get_current_user, SECRET_KEY, ALGORITHM

router = APIRouter()

@router.post("/auth/register")
def register(username: str, password: str):
    user = {
        "id": len(database.users) + 1,
        "username": username,
        "password": password,
        "role": None
    }
    database.users.append(user)
    return {"message": "user registered"}

@router.post("/auth/login")
def login(username: str, password: str):
    for user in database.users:
        if user["username"] == username and user["password"] == password:
            token = jwt.encode({"username": username}, SECRET_KEY, algorithm=ALGORITHM)
            return {
                "access_token": token,
                "message": "login successful"
            }
    return {"message": "invalid credentials"}
