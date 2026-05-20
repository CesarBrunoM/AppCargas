"""
Modelos SQLAlchemy para o sistema de gerenciamento de cargas.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum, Text
from sqlalchemy.orm import DeclarativeBase
import enum


class Base(DeclarativeBase):
    pass


class StatusCarga(str, enum.Enum):
    AGENDADO = "Agendado"
    EM_CARREGAMENTO = "Em carregamento"
    EM_TRANSITO = "Em trânsito"
    ENTREGUE = "Entregue"
    CANCELADO = "Cancelado"


class PerfilUsuario(str, enum.Enum):
    ADMIN = "Administrador"
    OPERADOR = "Operador"


class Usuario(Base):
    """Modelo de usuário do sistema."""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), nullable=True)
    senha_hash = Column(String(256), nullable=False)
    perfil = Column(String(30), default=PerfilUsuario.OPERADOR.value, nullable=False)
    ativo = Column(Integer, default=1)  # 1=ativo, 0=inativo
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Carga(Base):
    """Modelo de carga/agendamento."""
    __tablename__ = "cargas"

    id = Column(Integer, primary_key=True, index=True)

    # Dados de agendamento
    data_carregamento = Column(Date, nullable=False)
    cliente = Column(String(150), nullable=False)
    carregador = Column(String(150), nullable=False)
    tamanho = Column(String(50), nullable=False)
    motorista = Column(String(150), nullable=False)
    placa = Column(String(20), nullable=False)
    destino = Column(String(200), nullable=False)
    preco = Column(Float, nullable=False, default=0.0)

    # Dados operacionais (preenchidos na edição)
    quantidade_frutas = Column(Float, nullable=True)
    peso_caminhao = Column(Float, nullable=True)
    observacoes = Column(Text, nullable=True)

    # Status e controle
    status = Column(String(30), default=StatusCarga.AGENDADO.value, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
