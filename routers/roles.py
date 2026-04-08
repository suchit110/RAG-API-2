from fastapi import APIRouter
import database

router = APIRouter()

@router.post("/roles/create")
def create_role(name: str):
    if name == "Admin":
        permissions = ["upload", "view", "delete", "search"]
    elif name == "Analyst":
        permissions = ["upload", "view", "search"]
    elif name == "Client":
        permissions = ["view"]
    elif name == "Auditor":
        permissions = ["view", "search"]
    else:
        permissions = []
    role = {
        "name": name,
        "permissions": permissions
    }
    database.roles.append(role)
    return {"message": "role created"}

@router.post("/users/assign-role")
def assign_role(user_id: int, role_name: str):
    for user in database.users:
        if user["id"] == user_id:
            for role in database.roles:
                if role["name"] == role_name:
                    user["role"] = role_name
                    return {"message": "role assigned"}
            return {"message": "role not found"}
    return {"message": "user not found"}

@router.get("/users")
def get_users():
    return database.users

@router.get("/user/{user_id}/roles")
def get_user_role(user_id: int):
    for user in database.users:
        if user["id"] == user_id:
            return {"role": user["role"]}
    return {"message": "user not found"}

@router.get("/user/{user_id}/permissions")
def permissions(user_id: int):
    for user in database.users:
        if user["id"] == user_id:
            role_name = user["role"]
            for role in database.roles:
                if role["name"] == role_name:
                    return {"permissions": role["permissions"]}
            return {"message": "role not found"}
    return {"message": "user not found"}
