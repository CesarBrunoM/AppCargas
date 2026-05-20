"""
Serviço de autenticação e gerenciamento de usuários.
"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import Usuario, PerfilUsuario
from app.utils.security import verificar_senha, hash_senha

logger = logging.getLogger(__name__)

PERFIS = [p.value for p in PerfilUsuario]


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
    senha: str,
    perfil: str = PerfilUsuario.OPERADOR.value,
    email: str = "",
) -> Optional[Usuario]:
    """Cria um novo usuário no sistema."""
    try:
        existente = db.query(Usuario).filter(Usuario.username == username).first()
        if existente:
            return None

        novo = Usuario(
            username=username.strip().lower(),
            nome=nome.strip(),
            senha_hash=hash_senha(senha),
            perfil=perfil,
            email=email.strip() if email else None,
            ativo=1,
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
        logger.info(f"Usuário criado: {username} (perfil={perfil})")
        return novo
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar usuário: {e}")
        return None


def listar_usuarios(db: Session) -> List[Usuario]:
    """Retorna todos os usuários ordenados por nome."""
    return db.query(Usuario).order_by(Usuario.nome).all()


def buscar_usuario_por_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    """Busca um usuário pelo ID."""
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def atualizar_usuario(
    db: Session,
    usuario_id: int,
    nome: str = None,
    email: str = None,
    perfil: str = None,
    ativo: int = None,
) -> Optional[Usuario]:
    """Atualiza dados de um usuário existente."""
    try:
        usuario = buscar_usuario_por_id(db, usuario_id)
        if not usuario:
            return None

        if nome is not None:
            usuario.nome = nome.strip()
        if email is not None:
            usuario.email = email.strip() if email.strip() else None
        if perfil is not None:
            usuario.perfil = perfil
        if ativo is not None:
            usuario.ativo = ativo

        db.commit()
        db.refresh(usuario)
        logger.info(f"Usuário {usuario_id} atualizado.")
        return usuario
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar usuário {usuario_id}: {e}")
        return None


def redefinir_senha(
    db: Session,
    usuario_id: int,
    nova_senha: str,
) -> bool:
    """Redefine a senha de um usuário."""
    try:
        usuario = buscar_usuario_por_id(db, usuario_id)
        if not usuario:
            return False
        usuario.senha_hash = hash_senha(nova_senha)
        db.commit()
        logger.info(f"Senha redefinida para usuário {usuario_id}.")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao redefinir senha do usuário {usuario_id}: {e}")
        return False


def alterar_senha_propria(
    db: Session,
    usuario_id: int,
    senha_atual: str,
    nova_senha: str,
) -> tuple[bool, str]:
    """
    Permite que o próprio usuário altere sua senha,
    exigindo a confirmação da senha atual.
    Retorna (sucesso, mensagem).
    """
    usuario = buscar_usuario_por_id(db, usuario_id)
    if not usuario:
        return False, "Usuário não encontrado."

    if not verificar_senha(senha_atual, usuario.senha_hash):
        return False, "Senha atual incorreta."

    if len(nova_senha) < 6:
        return False, "A nova senha deve ter ao menos 6 caracteres."

    ok = redefinir_senha(db, usuario_id, nova_senha)
    if ok:
        return True, "Senha alterada com sucesso!"
    return False, "Erro ao salvar nova senha."


def toggle_ativo(db: Session, usuario_id: int, admin_id: int) -> tuple[bool, str]:
    """
    Ativa ou desativa um usuário.
    Impede que o admin desative a si mesmo.
    """
    if usuario_id == admin_id:
        return False, "Você não pode desativar sua própria conta."

    usuario = buscar_usuario_por_id(db, usuario_id)
    if not usuario:
        return False, "Usuário não encontrado."

    novo_estado = 0 if usuario.ativo == 1 else 1
    resultado = atualizar_usuario(db, usuario_id, ativo=novo_estado)
    if resultado:
        acao = "ativado" if novo_estado == 1 else "desativado"
        return True, f"Usuário {acao} com sucesso."
    return False, "Erro ao alterar estado do usuário."


def is_admin(perfil: str) -> bool:
    """Verifica se o perfil tem permissão de administrador."""
    return perfil == PerfilUsuario.ADMIN.value

