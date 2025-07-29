from datetime import datetime, timedelta
from typing import Optional
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config import settings
from models import TokenData, User, UserCreate, PasswordRecoveryRequest, PasswordResetRequest
from database_postgresql import SessionLocal, engine, Base
from db_models import UserORM

# Garantir que as tabelas existam sem falhar em ambientes sem banco
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Aviso: não foi possível criar tabelas no banco de dados: {e}")

# Configuração de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Utilidades de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_username(db: Session, username: str) -> Optional[UserORM]:
    return db.query(UserORM).filter(UserORM.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[UserORM]:
    return db.query(UserORM).filter(UserORM.email == email).first()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Autentica um usuário no banco de dados"""
    with SessionLocal() as db:
        user_db = get_user_by_username(db, username)
        if not user_db:
            return None

        if not verify_password(password, user_db.hashed_password):
            return None

        return User(
            username=user_db.username,
            name=user_db.name,
            email=user_db.email,
            access_level=user_db.access_level,
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
    
    with SessionLocal() as db:
        user_db = get_user_by_username(db, token_data.username)
        if not user_db:
            raise credentials_exception

        return User(
            username=user_db.username,
            name=user_db.name,
            email=user_db.email,
            access_level=user_db.access_level,
        )


def create_user(user: UserCreate) -> User:
    """Cria um novo usuário no banco"""
    with SessionLocal() as db:
        if get_user_by_username(db, user.username) or get_user_by_email(db, user.email):
            raise HTTPException(status_code=400, detail="Usuário já existe")

        new_user = UserORM(
            name=user.name,
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password),
            access_level=user.access_level,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return User(
            username=new_user.username,
            name=new_user.name,
            email=new_user.email,
            access_level=new_user.access_level,
        )


def generate_password_recovery(email: str) -> str:
    """Gera token de recuperação de senha"""
    with SessionLocal() as db:
        user_db = get_user_by_email(db, email)
        if not user_db:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        token = secrets.token_urlsafe(32)
        user_db.reset_token = token
        user_db.reset_expiration = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        return token


def reset_password(token: str, new_password: str) -> None:
    """Altera a senha utilizando o token de recuperação"""
    with SessionLocal() as db:
        user_db = (
            db.query(UserORM)
            .filter(UserORM.reset_token == token, UserORM.reset_expiration > datetime.utcnow())
            .first()
        )

        if not user_db:
            raise HTTPException(status_code=400, detail="Token inválido ou expirado")

        user_db.hashed_password = get_password_hash(new_password)
        user_db.reset_token = None
        user_db.reset_expiration = None
        db.commit()

