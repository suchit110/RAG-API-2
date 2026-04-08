from jose import jwt

SECRET_KEY = "mysrcretkey"
ALGORITHM = "HS256"


def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["username"]
    except:
        return None
