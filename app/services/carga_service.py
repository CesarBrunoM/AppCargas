"""
Serviço de gerenciamento de cargas - regras de negócio.
"""
import logging
from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import pandas as pd
from app.models import Carga, StatusCarga

logger = logging.getLogger(__name__)


def criar_carga(db: Session, dados: Dict[str, Any]) -> Optional[Carga]:
    """Cria um novo registro de carga no banco de dados."""
    try:
        carga = Carga(
            data_carregamento=dados["data_carregamento"],
            cliente=dados["cliente"].strip(),
            carregador=dados["carregador"].strip(),
            tamanho=dados["tamanho"],
            motorista=dados["motorista"].strip(),
            placa=dados["placa"].upper().strip(),
            destino=dados["destino"].strip(),
            preco=float(dados["preco"]),
            status=StatusCarga.AGENDADO.value,
        )
        db.add(carga)
        db.commit()
        db.refresh(carga)
        logger.info(f"Carga criada com ID: {carga.id}")
        return carga
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar carga: {e}")
        return None


def buscar_carga_por_id(db: Session, carga_id: int) -> Optional[Carga]:
    """Busca uma carga pelo ID."""
    return db.query(Carga).filter(Carga.id == carga_id).first()


def listar_cargas(
    db: Session,
    cliente: str = "",
    motorista: str = "",
    status: str = "",
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    termo_busca: str = "",
) -> List[Carga]:
    """
    Lista cargas com filtros opcionais.
    Suporta filtro por cliente, motorista, status, intervalo de datas e busca geral.
    """
    query = db.query(Carga)

    if cliente:
        query = query.filter(Carga.cliente.ilike(f"%{cliente}%"))
    if motorista:
        query = query.filter(Carga.motorista.ilike(f"%{motorista}%"))
    if status:
        query = query.filter(Carga.status == status)
    if data_inicio:
        query = query.filter(Carga.data_carregamento >= data_inicio)
    if data_fim:
        query = query.filter(Carga.data_carregamento <= data_fim)
    if termo_busca:
        query = query.filter(
            or_(
                Carga.cliente.ilike(f"%{termo_busca}%"),
                Carga.motorista.ilike(f"%{termo_busca}%"),
                Carga.destino.ilike(f"%{termo_busca}%"),
                Carga.placa.ilike(f"%{termo_busca}%"),
            )
        )

    return query.order_by(Carga.data_carregamento.desc()).all()


def atualizar_carga(db: Session, carga_id: int, dados: Dict[str, Any]) -> Optional[Carga]:
    """Atualiza os dados operacionais e status de uma carga."""
    try:
        carga = buscar_carga_por_id(db, carga_id)
        if not carga:
            return None

        # Campos editáveis
        if "quantidade_frutas" in dados:
            carga.quantidade_frutas = dados["quantidade_frutas"]
        if "peso_caminhao" in dados:
            carga.peso_caminhao = dados["peso_caminhao"]
        if "status" in dados:
            carga.status = dados["status"]
        if "observacoes" in dados:
            carga.observacoes = dados["observacoes"]

        # Permite editar dados base também
        campos_base = ["data_carregamento", "cliente", "carregador", "tamanho",
                       "motorista", "placa", "destino", "preco"]
        for campo in campos_base:
            if campo in dados and dados[campo] is not None:
                setattr(carga, campo, dados[campo])

        db.commit()
        db.refresh(carga)
        logger.info(f"Carga {carga_id} atualizada.")
        return carga
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar carga {carga_id}: {e}")
        return None


def obter_metricas(db: Session) -> Dict[str, Any]:
    """Calcula métricas do dashboard."""
    try:
        total = db.query(Carga).count()
        agendadas = db.query(Carga).filter(Carga.status == StatusCarga.AGENDADO.value).count()
        em_transito = db.query(Carga).filter(Carga.status == StatusCarga.EM_TRANSITO.value).count()
        entregues = db.query(Carga).filter(Carga.status == StatusCarga.ENTREGUE.value).count()
        canceladas = db.query(Carga).filter(Carga.status == StatusCarga.CANCELADO.value).count()
        em_carregamento = db.query(Carga).filter(Carga.status == StatusCarga.EM_CARREGAMENTO.value).count()

        # Receita total de cargas entregues
        cargas_entregues = db.query(Carga).filter(
            Carga.status == StatusCarga.ENTREGUE.value
        ).all()
        receita_total = sum(c.preco for c in cargas_entregues)

        return {
            "total": total,
            "agendadas": agendadas,
            "em_carregamento": em_carregamento,
            "em_transito": em_transito,
            "entregues": entregues,
            "canceladas": canceladas,
            "receita_total": receita_total,
        }
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        return {}


def cargas_para_dataframe(cargas: List[Carga]) -> pd.DataFrame:
    """Converte lista de cargas para DataFrame pandas."""
    if not cargas:
        return pd.DataFrame()

    dados = []
    for c in cargas:
        dados.append({
            "ID": c.id,
            "Data": c.data_carregamento.strftime("%d/%m/%Y") if c.data_carregamento else "-",
            "Cliente": c.cliente,
            "Carregador": c.carregador,
            "Tamanho": c.tamanho,
            "Motorista": c.motorista,
            "Placa": c.placa,
            "Destino": c.destino,
            "Preço": c.preco,
            "Qtd. Frutas": c.quantidade_frutas or "-",
            "Peso (kg)": c.peso_caminhao or "-",
            "Status": c.status,
            "Cadastrado em": c.criado_em.strftime("%d/%m/%Y %H:%M") if c.criado_em else "-",
        })

    return pd.DataFrame(dados)
