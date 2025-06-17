from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from server.database import db

router = APIRouter()

# Ініціалізація OAuth2 схеми
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Секретний ключ для JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Термін дії токену (1 година)

# Тимчасовий чорний список токенів (можна зберігати в Redis або базі даних)
blacklisted_tokens = set()
active_tokens = {}  # {username: token} для відстеження активних токенів

# Колекція користувачів
users_collection = db["users"]

# Pydantic-схеми
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register")
def register(user: UserCreate):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Цей логін вже зайнято")

    hashed_pw = bcrypt.hash(user.password)
    users_collection.insert_one({"username": user.username, "hashed_password": hashed_pw})
    return {"message": "Користувач зареєстрований успішно"}


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
def login(user: UserLogin):
    db_user = users_collection.find_one({"username": user.username})
    if not db_user or not bcrypt.verify(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Невірний логін або пароль")

    # Генеруємо JWT токен
    token_data = {"sub": user.username}
    access_token = create_access_token(token_data)
    return {"message": "Успішний вхід", "access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    if token in blacklisted_tokens:
        return {"message": "Токен вже деактивовано"}
    
    blacklisted_tokens.add(token)
    return {"message": "Вихід успішний"}

