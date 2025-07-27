from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from datetime import timedelta
import uvicorn

from config import settings
from models import *
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    create_user,
    generate_password_recovery,
    reset_password,
)
from services import equipamento_service, similaridade_service

# Criação da aplicação FastAPI
app = FastAPI(
    title="IHJ Sistema de Busca de Equipamentos API",
    description="API para busca e análise de similaridade de equipamentos",
    version="1.0.0",
    debug=True
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de segurança
security = HTTPBearer()

@app.get("/", response_model=MessageResponse)
async def root():
    """Endpoint raiz da API"""
    return MessageResponse(message="IHJ Sistema de Busca de Equipamentos API está funcionando!")

# Endpoints de Autenticação
@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Endpoint para autenticação de usuário"""
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.post("/auth/register", response_model=MessageResponse)
async def register(
    user: UserCreate,
    current_user: User = Depends(get_current_user)
):
    """Endpoint para registrar um novo usuário"""
    if current_user.access_level != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem criar novos usuários",
        )

    created = create_user(user)
    return MessageResponse(message=f"Usuário {created.name} criado com sucesso")


@app.post("/auth/recover", response_model=MessageResponse)
async def recover_password(request: PasswordRecoveryRequest):
    """Endpoint para solicitar recuperação de senha"""
    token = generate_password_recovery(request.email)
    # Em uma aplicação real, este token seria enviado por e-mail
    return MessageResponse(message=f"Token de recuperação: {token}")


@app.post("/auth/reset", response_model=MessageResponse)
async def reset_password_endpoint(request: PasswordResetRequest):
    """Endpoint para redefinir senha usando token"""
    reset_password(request.token, request.new_password)
    return MessageResponse(message="Senha atualizada com sucesso")

@app.post("/auth/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Endpoint para logout (invalidação do token seria implementada com Redis/cache)"""
    return MessageResponse(message=f"Usuário {current_user.name} deslogado com sucesso")

@app.get("/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Endpoint para obter informações do usuário atual"""
    return current_user

# Endpoints de Equipamentos
@app.get("/equipamentos/classes", response_model=ClasseResponse)
async def get_classes(current_user: User = Depends(get_current_user)):
    """Obtém lista de classes disponíveis"""
    try:
        classes = equipamento_service.get_classes()
        return ClasseResponse(classes=classes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/equipamentos/caracteristicas", response_model=CaracteristicaResponse)
async def get_caracteristicas(
    classes: str,  # Classes separadas por vírgula
    current_user: User = Depends(get_current_user)
):
    """Obtém características disponíveis para as classes selecionadas"""
    try:
        classes_list = [c.strip() for c in classes.split(',')]
        caracteristicas = equipamento_service.get_caracteristicas(classes_list)
        return CaracteristicaResponse(caracteristicas=caracteristicas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/equipamentos/valores/{caracteristica}")
async def get_valores_caracteristica(
    caracteristica: str,
    classes: str,  # Classes separadas por vírgula
    current_user: User = Depends(get_current_user)
):
    """Obtém valores disponíveis para uma característica específica"""
    try:
        classes_list = [c.strip() for c in classes.split(',')]
        valores = equipamento_service.get_valores_caracteristica(caracteristica, classes_list)
        return {"valores": valores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/equipamentos/filtrar", response_model=FiltroResponse)
async def filtrar_equipamentos(
    filtro_request: FiltroRequest,
    current_user: User = Depends(get_current_user)
):
    """Filtra equipamentos com base nos critérios especificados"""
    try:
        resultado = equipamento_service.filtrar_equipamentos(filtro_request)
        
        equipamentos = [
            EquipamentoFiltrado(equipamento=eq["equipamento"])
            for eq in resultado["equipamentos"]
        ]
        
        return FiltroResponse(
            equipamentos=equipamentos,
            dados_pivot=resultado["dados_pivot"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints de Similaridade
@app.get("/equipamentos/similaridade/{equipment_id}", response_model=SimilaridadeResponse)
async def get_equipamentos_similares(
    equipment_id: str,
    quantidade: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Busca equipamentos similares ao equipamento especificado"""
    try:
        request = SimilaridadeRequest(equipamento=equipment_id, quantidade=quantidade)
        resultado = similaridade_service.analisar_similaridade(request)
        
        equipamentos_similares = [
            EquipamentoSimilar(
                equipamento=eq["equipamento"],
                similarity_score=eq["similarity_score"],
                centro=eq.get("centro"),
                classe=eq.get("classe")
            )
            for eq in resultado["equipamentos_similares"]
        ]
        
        return SimilaridadeResponse(
            equipamento_alvo=resultado["equipamento_alvo"],
            equipamentos_similares=equipamentos_similares,
            detalhes_completos=resultado["detalhes_completos"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint de saúde
@app.get("/health", response_model=MessageResponse)
async def health_check():
    """Endpoint para verificação de saúde da API"""
    return MessageResponse(message="API está saudável")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

