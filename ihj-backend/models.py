from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Modelos de autenticação
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    name: str
    email: Optional[str] = None
    access_level: str

# Models for user creation and password recovery
class UserCreate(BaseModel):
    name: str
    email: str
    username: str
    password: str
    access_level: str = "user"

class PasswordRecoveryRequest(BaseModel):
    email: str

class PasswordResetRequest(BaseModel):
    token: str
    new_password: str

# Modelos para busca de equipamentos
class ClasseResponse(BaseModel):
    classes: List[str]

class CaracteristicaResponse(BaseModel):
    caracteristicas: List[str]

class FiltroRequest(BaseModel):
    classes: List[str]
    filtros: Dict[str, List[str]]

class EquipamentoFiltrado(BaseModel):
    equipamento: str
    centro: Optional[str] = None
    classe: Optional[str] = None

class FiltroResponse(BaseModel):
    equipamentos: List[EquipamentoFiltrado]
    dados_pivot: Optional[Dict[str, Any]] = None

# Modelos para análise de similaridade
class SimilaridadeRequest(BaseModel):
    equipamento: str
    quantidade: int = 10

class EquipamentoSimilar(BaseModel):
    equipamento: str
    similarity_score: float
    centro: Optional[str] = None
    classe: Optional[str] = None

class SimilaridadeResponse(BaseModel):
    equipamento_alvo: str
    equipamentos_similares: List[EquipamentoSimilar]
    detalhes_completos: Optional[Dict[str, Any]] = None

# Modelos de resposta padrão
class MessageResponse(BaseModel):
    message: str
    status: str = "success"

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status: str = "error"

