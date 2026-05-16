"""
Utilitários gerais do sistema.
"""
import re
import logging
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)


def formatar_preco(valor: float) -> str:
    """Formata um valor float como moeda brasileira."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(d: Optional[date]) -> str:
    """Formata uma data para o padrão brasileiro DD/MM/AAAA."""
    if d is None:
        return "-"
    return d.strftime("%d/%m/%Y")


def validar_placa(placa: str) -> bool:
    """Valida formato de placa brasileira (antigo ou Mercosul)."""
    placa = placa.upper().replace("-", "").replace(" ", "")
    padrao_antigo = re.compile(r'^[A-Z]{3}\d{4}$')
    padrao_mercosul = re.compile(r'^[A-Z]{3}\d[A-Z]\d{2}$')
    return bool(padrao_antigo.match(placa) or padrao_mercosul.match(placa))


def formatar_placa(placa: str) -> str:
    """Formata placa removendo caracteres especiais e convertendo para maiúsculo."""
    return placa.upper().replace("-", "").replace(" ", "")


def status_cor(status: str) -> str:
    """Retorna a cor associada ao status da carga."""
    mapa = {
        "Agendado": "#3B82F6",        # azul
        "Em carregamento": "#F59E0B",  # âmbar
        "Em trânsito": "#8B5CF6",      # roxo
        "Entregue": "#10B981",         # verde
        "Cancelado": "#EF4444",        # vermelho
    }
    return mapa.get(status, "#6B7280")


def status_emoji(status: str) -> str:
    """Retorna o emoji associado ao status da carga."""
    mapa = {
        "Agendado": "📅",
        "Em carregamento": "🔄",
        "Em trânsito": "🚛",
        "Entregue": "✅",
        "Cancelado": "❌",
    }
    return mapa.get(status, "❓")
