"""
Utilitários de segurança: hashing de senhas e verificação.
"""
import bcrypt
import logging

logger = logging.getLogger(__name__)


def hash_senha(senha: str) -> str:
    """Gera um hash seguro para a senha usando bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(senha.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Verifica se a senha corresponde ao hash armazenado."""
    try:
        return bcrypt.checkpw(
            senha.encode("utf-8"),
            hash_armazenado.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {e}")
        return False
