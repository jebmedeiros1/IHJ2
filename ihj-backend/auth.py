from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import yaml
from yaml.loader import SafeLoader
from config import settings
from models import TokenData, User

# Configuração de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Carregamento das credenciais do arquivo config.yaml
def load_user_credentials():
    """Carrega as credenciais dos usuários do arquivo config.yaml"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.load(file, Loader=SafeLoader)
            return config.get('credentials', {}).get('usernames', {})
    except FileNotFoundError:
        # Retorna usuários padrão se o arquivo não existir
        return {
            "admin": {
                "name": "Administrador",
                "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
                "email": "admin@ihj.com"
            }
        }

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Autentica um usuário"""
    users = load_user_credentials()
    
    if username not in users:
        return None
    
    user_data = users[username]
    if not verify_password(password, user_data["password"]):
        return None
    
    return User(
        username=username,
        name=user_data["name"],
        email=user_data.get("email")
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um token de acesso JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Obtém o usuário atual a partir do token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    users = load_user_credentials()
    if token_data.username not in users:
        raise credentials_exception
    
    user_data = users[token_data.username]
    return User(
        username=token_data.username,
        name=user_data["name"],
        email=user_data.get("email")
    )

