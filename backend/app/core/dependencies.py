"""
Dependencias de FastAPI.

Define las dependencias reutilizables para la aplicaci?n,
especialmente para la autenticaci?n y autorizaci?n.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.config import settings
from schemas.auth_schema import UserInToken
from services import auth_service

# Configuraci?n del esquema de seguridad Bearer
security = HTTPBearer()


def _mock_admin_user() -> UserInToken:
    return UserInToken(
        id_usuario=1,
        email_usuario="mock-admin@revital.local",
        nom_usuario="Mock",
        ape_usuario="Admin",
        id_rol=1,
    )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserInToken:
    """
    Dependencia para obtener el usuario actual autenticado.
    
    Args:
        credentials: Credenciales del token Bearer
        db: Sesi?n de la base de datos
        
    Returns:
        UserInToken: Informaci?n del usuario autenticado
        
    Raises:
        HTTPException: Si el token es inv?lido o el usuario no existe
    """
    if settings.MOCK_MODE:
        return _mock_admin_user()
    return auth_service.get_current_user(db, credentials.credentials)

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[UserInToken]:
    """
    Dependencia para obtener el usuario actual de forma opcional.
    No lanza error si no hay token.
    
    Args:
        credentials: Credenciales del token Bearer (opcional)
        db: Sesi?n de la base de datos
        
    Returns:
        Optional[UserInToken]: Informaci?n del usuario autenticado o None
    """
    if settings.MOCK_MODE:
        return _mock_admin_user()
    if not credentials:
        return None
    
    try:
        return auth_service.get_current_user(db, credentials.credentials)
    except HTTPException:
        return None

def require_role(required_role: int):
    """
    Dependencia para verificar que el usuario tenga un rol espec?fico.
    
    Args:
        required_role (int): ID del rol requerido
        
    Returns:
        function: Funci?n de dependencia que verifica el rol
    """
    def role_checker(current_user: UserInToken = Depends(get_current_user)) -> UserInToken:
        if current_user.id_rol != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para realizar esta acci?n"
            )
        return current_user
    
    return role_checker

def require_admin():
    """
    Dependencia para verificar que el usuario sea administrador.
    Asume que el rol de administrador tiene ID = 1.
    
    Returns:
        UserInToken: Usuario autenticado con rol de administrador
    """
    return require_role(1)


def _admin_ai_chat_allows_anonymous() -> bool:
    """
    Chat/health IA sin JWT cuando:
    - ADMIN_AI_PUBLIC_CHAT expl?cito, o MOCK_MODE, o
    - entorno distinto de production (hackathon / dev local sin .env extra).
    En production solo con ADMIN_AI_PUBLIC_CHAT=true.
    """
    if settings.ADMIN_AI_PUBLIC_CHAT or settings.MOCK_MODE:
        return True
    return str(getattr(settings, "ENVIRONMENT", "")).lower() != "production"


def require_admin_or_ai_public_chat():
    """
    Admin con JWT o acceso an?nimo solo para rutas acotadas (health/chat)
    cuando `_admin_ai_chat_allows_anonymous()` es True (usuario sint?tico).
    """
    def dependency(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(
            HTTPBearer(auto_error=False)
        ),
        db: Session = Depends(get_db),
    ) -> UserInToken:
        if _admin_ai_chat_allows_anonymous():
            return _mock_admin_user()
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autenticado",
            )
        user = auth_service.get_current_user(db, credentials.credentials)
        if user.id_rol != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para realizar esta acci?n",
            )
        return user

    return dependency

def require_user_or_admin(user_id: int):
    """
    Dependencia para verificar que el usuario sea el propietario del recurso o administrador.
    
    Args:
        user_id (int): ID del usuario propietario del recurso
        
    Returns:
        function: Funci?n de dependencia que verifica el acceso
    """
    def access_checker(current_user: UserInToken = Depends(get_current_user)) -> UserInToken:
        if current_user.id_usuario != user_id and current_user.id_rol != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso"
            )
        return current_user
    
    return access_checker 