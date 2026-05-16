"""
Serviço de autenticação de usuários.
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Usuario
from app.utils.security import verificar_senha, hash_senha

logger = logging.getLogger(__name__)


def autenticar_usuario(db: Session, username: str, senha: str) -> Optional[Usuario]:
    """
    Autentica um usuário pelo username e senha.
    Retorna o objeto Usuario se autenticado, None caso contrário.
    """
    try:
        usuario = db.query(Usuario).filter(
            Usuario.username == username,
            Usuario.ativo == 1
        ).first()

        if not usuario:
            logger.warning(f"Tentativa de login com usuário inexistente: {username}")
            return None

        if not verificar_senha(senha, usuario.senha_hash):
            logger.warning(f"Senha incorreta para usuário: {username}")
            return None

        logger.info(f"Login bem-sucedido: {username}")
        return usuario

    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        return None


def criar_usuario(
    db: Session,
    username: str,
    nome: str,
    senha: str
) -> Optional[Usuario]:
    """Cria um novo usuário no sistema."""
    try:
        existente = db.query(Usuario).filter(Usuario.username == username).first()
        if existente:
            return None

        novo = Usuario(
            username=username,
            nome=nome,
            senha_hash=hash_senha(senha),
            ativo=1,
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar usuário: {e}")
        return None
