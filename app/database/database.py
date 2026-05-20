"""
Configuração e inicialização do banco de dados SQLite com SQLAlchemy.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base, Usuario, StatusCarga
from app.utils.security import hash_senha

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./cargas.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Retorna uma sessão do banco de dados."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e


def init_db() -> None:
    """
    Cria todas as tabelas e insere dados iniciais se necessário.
    Executa migrações automáticas para colunas novas.
    Deve ser chamado na inicialização da aplicação.
    """
    logger.info("Inicializando banco de dados...")
    Base.metadata.create_all(bind=engine)
    _migrar_colunas()
    _criar_usuario_admin()
    logger.info("Banco de dados inicializado com sucesso.")


def _migrar_colunas() -> None:
    """Adiciona colunas novas em tabelas existentes (migrações simples via ALTER TABLE)."""
    from sqlalchemy import text, inspect
    insp = inspect(engine)
    with engine.connect() as conn:
        # Tabela usuarios — colunas adicionadas na versão com perfil/email
        colunas_usuarios = [col["name"] for col in insp.get_columns("usuarios")]
        if "email" not in colunas_usuarios:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN email VARCHAR(150)"))
            logger.info("Coluna 'email' adicionada à tabela usuarios.")
        if "perfil" not in colunas_usuarios:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN perfil VARCHAR(30) DEFAULT 'Administrador'"))
            logger.info("Coluna 'perfil' adicionada à tabela usuarios.")
        if "atualizado_em" not in colunas_usuarios:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN atualizado_em DATETIME"))
            logger.info("Coluna 'atualizado_em' adicionada à tabela usuarios.")
        conn.commit()


def _criar_usuario_admin() -> None:
    """Cria o usuário administrador padrão se não existir."""
    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.username == "admin").first()
        if not admin:
            admin_user = Usuario(
                username="admin",
                nome="Administrador",
                senha_hash=hash_senha("admin123"),
                ativo=1,
            )
            db.add(admin_user)
            db.commit()
            logger.info("Usuário admin criado: username=admin, senha=admin123")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar usuário admin: {e}")
    finally:
        db.close()
