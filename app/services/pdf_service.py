# -*- coding: utf-8 -*-
"""
Servico de geracao de PDFs profissionais para o CargoFlow.
Utiliza ReportLab para criacao de documentos com identidade visual.
"""
import io
import logging
from datetime import datetime, date
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfgen import canvas as pdfgen_canvas

from app.models import Carga
from app.utils.helpers import formatar_preco, formatar_data, status_emoji

logger = logging.getLogger(__name__)

# ── Paleta de cores (espelha o CSS da aplicacao) ─────────────────────────────
AZUL_ESCURO   = colors.HexColor("#1E3A8A")
AZUL_MEDIO    = colors.HexColor("#1E40AF")
AZUL_CLARO    = colors.HexColor("#3B82F6")
CINZA_ESCURO  = colors.HexColor("#0F172A")
CINZA_MEDIO   = colors.HexColor("#64748B")
CINZA_CLARO   = colors.HexColor("#F1F5F9")
CINZA_BORDA   = colors.HexColor("#E2E8F0")
VERDE         = colors.HexColor("#10B981")
AMARELO       = colors.HexColor("#F59E0B")
VERMELHO      = colors.HexColor("#EF4444")
ROXO          = colors.HexColor("#8B5CF6")
BRANCO        = colors.white

W, H = A4
MARGEM = 18 * mm


def _cor_status(status: str) -> colors.Color:
    mapa = {
        "Agendado": AZUL_CLARO,
        "Em carregamento": AMARELO,
        "Em transito": ROXO,
        "Em trânsito": ROXO,
        "Entregue": VERDE,
        "Cancelado": VERMELHO,
    }
    return mapa.get(status, CINZA_MEDIO)


# ── Numeracao de paginas ──────────────────────────────────────────────────────

class _RodapeNumPagina:
    """Canvas personalizado que desenha cabecalho e rodape em cada pagina."""

    def __init__(self, titulo_doc: str, subtitulo: str = ""):
        self.titulo_doc = titulo_doc
        self.subtitulo = subtitulo

    def __call__(self, c: pdfgen_canvas.Canvas, doc) -> None:
        c.saveState()
        w, h = A4

        # ── Cabecalho ──────────────────────────────────────────
        # Barra superior azul escura
        c.setFillColor(AZUL_ESCURO)
        c.rect(0, h - 22 * mm, w, 22 * mm, fill=1, stroke=0)

        # Icone / marca
        c.setFillColor(AZUL_CLARO)
        c.roundRect(MARGEM - 2 * mm, h - 18 * mm, 14 * mm, 14 * mm, 3 * mm, fill=1, stroke=0)
        c.setFillColor(BRANCO)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(MARGEM + 5 * mm, h - 12.5 * mm, "CF")

        # Nome sistema
        c.setFillColor(BRANCO)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(MARGEM + 17 * mm, h - 10 * mm, "CargoFlow")
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.HexColor("#93C5FD"))
        c.drawString(MARGEM + 17 * mm, h - 15 * mm, "Sistema de Gerenciamento de Cargas")

        # Titulo do documento (direita)
        c.setFillColor(BRANCO)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(w - MARGEM, h - 10 * mm, self.titulo_doc)
        if self.subtitulo:
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor("#93C5FD"))
            c.drawRightString(w - MARGEM, h - 15 * mm, self.subtitulo)

        # ── Rodape ────────────────────────────────────────────
        c.setFillColor(CINZA_CLARO)
        c.rect(0, 0, w, 12 * mm, fill=1, stroke=0)
        c.setStrokeColor(CINZA_BORDA)
        c.setLineWidth(0.5)
        c.line(0, 12 * mm, w, 12 * mm)

        # Pagina
        c.setFillColor(CINZA_MEDIO)
        c.setFont("Helvetica", 7.5)
        num = f"Pagina {doc.page}"
        c.drawCentredString(w / 2, 4.5 * mm, num)

        # Data de emissao (esquerda)
        agora = datetime.now().strftime("%d/%m/%Y as %H:%M")
        c.drawString(MARGEM, 4.5 * mm, f"Emitido em {agora}")

        # Aviso (direita)
        c.drawRightString(w - MARGEM, 4.5 * mm, "Documento gerado pelo CargoFlow")

        c.restoreState()


# ── Estilos de texto ─────────────────────────────────────────────────────────

def _estilos():
    base = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "Titulo",
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=CINZA_ESCURO,
        spaceAfter=2,
        leading=20,
    )
    subtitulo = ParagraphStyle(
        "Subtitulo",
        fontName="Helvetica",
        fontSize=9,
        textColor=CINZA_MEDIO,
        spaceAfter=10,
    )
    secao = ParagraphStyle(
        "Secao",
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=AZUL_MEDIO,
        spaceBefore=8,
        spaceAfter=4,
        textTransform="uppercase",
        letterSpacing=0.8,
    )
    label = ParagraphStyle(
        "Label",
        fontName="Helvetica",
        fontSize=8,
        textColor=CINZA_MEDIO,
        leading=12,
    )
    valor = ParagraphStyle(
        "Valor",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=CINZA_ESCURO,
        leading=12,
    )
    normal = ParagraphStyle(
        "NormalCF",
        fontName="Helvetica",
        fontSize=8.5,
        textColor=CINZA_ESCURO,
        leading=13,
    )
    cabecalho_tab = ParagraphStyle(
        "CabTab",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        textColor=BRANCO,
        alignment=TA_LEFT,
    )
    celula_tab = ParagraphStyle(
        "CelTab",
        fontName="Helvetica",
        fontSize=8,
        textColor=CINZA_ESCURO,
        leading=11,
    )
    rodape_obs = ParagraphStyle(
        "Obs",
        fontName="Helvetica-Oblique",
        fontSize=8,
        textColor=CINZA_MEDIO,
        leading=11,
    )

    return {
        "titulo": titulo, "subtitulo": subtitulo, "secao": secao,
        "label": label, "valor": valor, "normal": normal,
        "cabecalho_tab": cabecalho_tab, "celula_tab": celula_tab,
        "obs": rodape_obs,
    }


# ── Helper: par label / valor em linha ───────────────────────────────────────

def _par(label_txt: str, valor_txt: str, s) -> Table:
    """Retorna uma mini-tabela de 2 colunas: label e valor."""
    t = Table(
        [[Paragraph(label_txt, s["label"]), Paragraph(str(valor_txt), s["valor"])]],
        colWidths=[45 * mm, None],
    )
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, CINZA_BORDA),
    ]))
    return t


def _badge_status(status: str, s) -> Table:
    """Retorna uma 'pill' colorida com o status."""
    cor = _cor_status(status)
    emoji = status_emoji(status)
    txt = Paragraph(
        f"{emoji}  {status}",
        ParagraphStyle("badge", fontName="Helvetica-Bold", fontSize=9,
                       textColor=BRANCO, alignment=TA_CENTER),
    )
    t = Table([[txt]], colWidths=[55 * mm], rowHeights=[8 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), cor),
        ("ROUNDEDCORNERS", [4]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


# ─────────────────────────────────────────────────────────────────────────────
#  PDF INDIVIDUAL DE CARGA
# ─────────────────────────────────────────────────────────────────────────────

def gerar_pdf_carga(carga: Carga) -> bytes:
    """
    Gera um PDF profissional de uma unica carga para envio ao cliente.
    Retorna os bytes do PDF pronto para download.
    """
    buf = io.BytesIO()
    s = _estilos()
    rodape = _RodapeNumPagina(
        titulo_doc=f"Ordem de Carga  #{carga.id}",
        subtitulo=f"Cliente: {carga.cliente}",
    )

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGEM,
        rightMargin=MARGEM,
        topMargin=28 * mm,
        bottomMargin=18 * mm,
        title=f"Ordem de Carga #{carga.id} - {carga.cliente}",
        author="CargoFlow",
        subject="Documento de Carga",
    )

    story = []

    # ── Titulo principal ───────────────────────────────────────────────────
    story.append(Spacer(1, 4 * mm))

    topo = Table(
        [[
            Paragraph(f"Ordem de Carga  <font color='#3B82F6'>#{carga.id}</font>", s["titulo"]),
            _badge_status(carga.status, s),
        ]],
        colWidths=[W - 2 * MARGEM - 60 * mm, 60 * mm],
    )
    topo.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(topo)

    data_fmt = formatar_data(carga.data_carregamento) if carga.data_carregamento else "-"
    story.append(Paragraph(
        f"Data de carregamento: <b>{data_fmt}</b>  &nbsp;·&nbsp;  "
        f"Emitido em: <b>{datetime.now().strftime('%d/%m/%Y as %H:%M')}</b>",
        s["subtitulo"],
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CINZA_BORDA, spaceAfter=6))

    # ── Secao: Dados do Cliente ────────────────────────────────────────────
    story.append(Paragraph("Dados do Cliente e Agendamento", s["secao"]))

    dados_cliente = [
        ["Cliente", carga.cliente, "Data de Carregamento", data_fmt],
        ["Carregador", carga.carregador, "Tamanho do Veiculo", carga.tamanho],
        ["Destino", carga.destino, "Preco do Frete", formatar_preco(carga.preco)],
    ]

    cw = (W - 2 * MARGEM) / 4
    tab_cliente = Table(
        [[Paragraph(c if i % 2 == 0 else "", s["label"]) if i % 2 == 0
          else Paragraph(str(c), s["valor"])
          for i, c in enumerate(row)]
         for row in dados_cliente],
        colWidths=[cw * 0.7, cw * 1.3, cw * 0.9, cw * 1.1],
    )
    tab_cliente.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, CINZA_BORDA),
        ("BACKGROUND", (0, 0), (-1, -1), BRANCO),
    ]))
    story.append(tab_cliente)
    story.append(Spacer(1, 6 * mm))

    # ── Secao: Dados do Transporte ─────────────────────────────────────────
    story.append(Paragraph("Dados do Transporte", s["secao"]))

    dados_transp = [
        ["Motorista", carga.motorista, "Placa do Veiculo", carga.placa],
        ["Status", f"{status_emoji(carga.status)} {carga.status}", "", ""],
    ]

    tab_transp = Table(
        [[Paragraph(c if i % 2 == 0 else "", s["label"]) if i % 2 == 0
          else Paragraph(str(c), s["valor"])
          for i, c in enumerate(row)]
         for row in dados_transp],
        colWidths=[cw * 0.7, cw * 1.3, cw * 0.9, cw * 1.1],
    )
    tab_transp.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, CINZA_BORDA),
    ]))
    story.append(tab_transp)
    story.append(Spacer(1, 6 * mm))

    # ── Secao: Dados Operacionais (se preenchidos) ─────────────────────────
    if carga.quantidade_frutas or carga.peso_caminhao or carga.observacoes:
        story.append(Paragraph("Dados Operacionais", s["secao"]))

        op_rows = []
        if carga.quantidade_frutas:
            op_rows.append(["Quantidade de Frutas", f"{carga.quantidade_frutas:,.0f} unidades", "", ""])
        if carga.peso_caminhao:
            op_rows.append(["Peso do Caminhao", f"{carga.peso_caminhao:,.0f} kg", "", ""])

        if op_rows:
            tab_op = Table(
                [[Paragraph(c if i % 2 == 0 else "", s["label"]) if i % 2 == 0
                  else Paragraph(str(c), s["valor"])
                  for i, c in enumerate(row)]
                 for row in op_rows],
                colWidths=[cw * 0.7, cw * 1.3, cw * 0.9, cw * 1.1],
            )
            tab_op.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -1), 0.3, CINZA_BORDA),
            ]))
            story.append(tab_op)

        if carga.observacoes:
            story.append(Spacer(1, 3 * mm))
            story.append(Paragraph("Observacoes:", s["label"]))
            story.append(Paragraph(carga.observacoes, s["obs"]))

        story.append(Spacer(1, 6 * mm))

    # ── Box de assinaturas ─────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=CINZA_BORDA, spaceBefore=4))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Confirmacao e Assinaturas", s["secao"]))
    story.append(Spacer(1, 4 * mm))

    larg_ass = (W - 2 * MARGEM - 10 * mm) / 3
    linha_ass = "_" * 38

    ass = Table(
        [[
            Paragraph(f"{linha_ass}<br/><br/>Motorista<br/><font size='8' color='#64748B'>{carga.motorista}</font>", s["normal"]),
            Paragraph(f"{linha_ass}<br/><br/>Responsavel pelo Carregamento<br/><font size='8' color='#64748B'>{carga.carregador}</font>", s["normal"]),
            Paragraph(f"{linha_ass}<br/><br/>Cliente / Destinatario<br/><font size='8' color='#64748B'>{carga.cliente}</font>", s["normal"]),
        ]],
        colWidths=[larg_ass, larg_ass, larg_ass],
        rowHeights=[28 * mm],
    )
    ass.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), CINZA_ESCURO),
    ]))
    story.append(ass)

    # ── Nota de rodape do documento ────────────────────────────────────────
    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width="100%", thickness=0.3, color=CINZA_BORDA))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "Este documento foi gerado automaticamente pelo sistema CargoFlow e nao substitui "
        "documentos fiscais obrigatorios. Em caso de duvidas, entre em contato com o emitente.",
        s["obs"],
    ))

    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
#  PDF DE RELATORIO / LISTAGEM
# ─────────────────────────────────────────────────────────────────────────────

def gerar_pdf_relatorio(
    cargas: List[Carga],
    filtros_desc: str = "Todas as cargas",
) -> bytes:
    """
    Gera um PDF de relatorio com a listagem de multiplas cargas.
    Ideal para impressao de pauta do dia ou relatorio gerencial.
    """
    buf = io.BytesIO()
    s = _estilos()
    rodape = _RodapeNumPagina(
        titulo_doc="Relatorio de Cargas",
        subtitulo=filtros_desc,
    )

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGEM,
        rightMargin=MARGEM,
        topMargin=28 * mm,
        bottomMargin=18 * mm,
        title="Relatorio de Cargas - CargoFlow",
        author="CargoFlow",
    )

    story = []
    story.append(Spacer(1, 4 * mm))

    # Titulo
    story.append(Paragraph("Relatorio de Cargas", s["titulo"]))
    story.append(Paragraph(
        f"Filtro: <b>{filtros_desc}</b>  &nbsp;·&nbsp;  "
        f"Total: <b>{len(cargas)} registro(s)</b>  &nbsp;·&nbsp;  "
        f"Emitido: <b>{datetime.now().strftime('%d/%m/%Y as %H:%M')}</b>",
        s["subtitulo"],
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CINZA_BORDA, spaceAfter=6))

    if not cargas:
        story.append(Spacer(1, 10 * mm))
        story.append(Paragraph("Nenhuma carga encontrada com os filtros aplicados.", s["normal"]))
        doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
        return buf.getvalue()

    # Cabecalhos da tabela
    headers = ["ID", "Data", "Cliente", "Motorista", "Placa", "Destino", "Preco", "Status"]
    cw_total = W - 2 * MARGEM
    # Larguras fixas; a ultima coluna preenche o restante explicitamente
    col_widths = [
        10 * mm,   # ID
        18 * mm,   # Data
        38 * mm,   # Cliente
        34 * mm,   # Motorista
        18 * mm,   # Placa
        38 * mm,   # Destino
        22 * mm,   # Preco
        0,         # Status — calculado abaixo
    ]
    col_widths[-1] = max(
        20 * mm,
        cw_total - sum(col_widths[:-1])
    )

    cab_style = ParagraphStyle(
        "CabH", fontName="Helvetica-Bold", fontSize=7,
        textColor=BRANCO, alignment=TA_LEFT,
    )
    cel_style = ParagraphStyle(
        "CelH", fontName="Helvetica", fontSize=7.5,
        textColor=CINZA_ESCURO, leading=10,
    )
    cel_status = ParagraphStyle(
        "CelS", fontName="Helvetica-Bold", fontSize=7,
        textColor=CINZA_ESCURO, leading=10,
    )

    rows = [[Paragraph(h, cab_style) for h in headers]]

    for c in cargas:
        data_fmt = formatar_data(c.data_carregamento) if c.data_carregamento else "-"
        preco_fmt = formatar_preco(c.preco) if c.preco else "-"
        status_txt = f"{status_emoji(c.status)} {c.status}"
        rows.append([
            Paragraph(str(c.id), cel_style),
            Paragraph(data_fmt, cel_style),
            Paragraph(c.cliente or "-", cel_style),
            Paragraph(c.motorista or "-", cel_style),
            Paragraph(c.placa or "-", cel_style),
            Paragraph(c.destino or "-", cel_style),
            Paragraph(preco_fmt, cel_style),
            Paragraph(status_txt, cel_status),
        ])

    tab = Table(rows, colWidths=col_widths, repeatRows=1)

    # Estilo zebrado
    ts = TableStyle([
        # Cabecalho
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_ESCURO),
        ("TEXTCOLOR", (0, 0), (-1, 0), BRANCO),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        # Linhas de dados
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, CINZA_BORDA),
        ("GRID", (0, 0), (-1, 0), 0.3, AZUL_MEDIO),
    ])

    # Zebrado nas linhas de dados
    for i in range(1, len(rows)):
        if i % 2 == 0:
            ts.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F8FAFC"))
        else:
            ts.add("BACKGROUND", (0, i), (-1, i), BRANCO)

    tab.setStyle(ts)
    story.append(tab)

    # Sumario ao final
    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CINZA_BORDA))
    story.append(Spacer(1, 3 * mm))

    from app.models import StatusCarga
    contagem = {}
    receita = 0.0
    for c in cargas:
        contagem[c.status] = contagem.get(c.status, 0) + 1
        if c.status == StatusCarga.ENTREGUE.value:
            receita += c.preco or 0

    resumo_itens = [f"{st}: {qt}" for st, qt in contagem.items()]
    story.append(Paragraph(
        "Resumo: " + "  |  ".join(resumo_itens) +
        f"  |  Receita total (entregues): {formatar_preco(receita)}",
        s["obs"],
    ))

    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    return buf.getvalue()
