"""Página 'Histórico' — métricas e lista de relatórios anteriores."""
import os
import json
from datetime import datetime, timezone
from pathlib import Path

import customtkinter as ctk

from gui.styles import COLORS, FONTS, SIZES
from gui.components.metric_card import MetricCard


def _carregar_historico() -> list[dict]:
    """Carrega o histórico de relatórios gerados."""
    historico_path = Path.home() / "Documents" / "Relatorios LF" / "historico.json"
    if not historico_path.exists():
        return []
    try:
        dados = json.loads(historico_path.read_text(encoding="utf-8"))
        return dados.get("relatorios", [])
    except Exception:
        return []


def _tempo_relativo(iso_str: str) -> str:
    """Converte string ISO para tempo relativo (ex: '2 horas atrás')."""
    try:
        dt = datetime.fromisoformat(iso_str)
        agora = datetime.now()
        diff = agora - dt
        segundos = diff.total_seconds()
        if segundos < 60:
            return "Agora mesmo"
        if segundos < 3600:
            m = int(segundos // 60)
            return f"{m} min atrás"
        if segundos < 86400:
            h = int(segundos // 3600)
            return f"{h}h atrás"
        d = int(segundos // 86400)
        return f"{d}d atrás"
    except Exception:
        return "—"


class PaginaHistorico(ctk.CTkFrame):
    """Página de histórico de relatórios gerados."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True,
                    padx=SIZES["page_padding_x"], pady=SIZES["page_padding_y"])

        ctk.CTkLabel(scroll, text="Histórico",
                     font=FONTS["page_title"],
                     text_color=COLORS["text_primary"],
                     anchor="w").pack(fill="x")
        ctk.CTkLabel(scroll, text="Relatórios gerados anteriormente",
                     font=FONTS["page_subtitle"],
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(fill="x", pady=(2, 20))

        relatorios = _carregar_historico()

        # ── Métricas ──────────────────────────────────────────────────────
        from datetime import timedelta
        agora = datetime.now()
        ultimo_mes = [r for r in relatorios
                      if (agora - datetime.fromisoformat(r["data"])).days <= 30
                      if r.get("data")]
        try:
            ultimo = _tempo_relativo(relatorios[0]["data"]) if relatorios else "—"
        except Exception:
            ultimo = "—"

        total_emissoes = sum(r.get("emissoes", 0) for r in relatorios)

        frame_metricas = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_metricas.pack(fill="x", pady=(0, 20))
        frame_metricas.columnconfigure(0, weight=1)
        frame_metricas.columnconfigure(1, weight=1)
        frame_metricas.columnconfigure(2, weight=1)

        MetricCard(frame_metricas, label="Total gerados",
                   valor=str(len(ultimo_mes)),
                   subtexto="últimos 30 dias").grid(row=0, column=0, sticky="ew", padx=(0, 8))
        MetricCard(frame_metricas, label="Emissões rastreadas",
                   valor=str(total_emissoes),
                   subtexto="acumulado").grid(row=0, column=1, sticky="ew", padx=(0, 8))
        MetricCard(frame_metricas, label="Última execução",
                   valor=ultimo,
                   subtexto="").grid(row=0, column=2, sticky="ew")

        # ── Lista de relatórios ───────────────────────────────────────────
        if not relatorios:
            ctk.CTkLabel(
                scroll,
                text="Nenhum relatório gerado ainda.\nUse a página 'Gerar relatório' para criar o primeiro.",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
                justify="center",
            ).pack(pady=40)
            return

        ctk.CTkLabel(scroll, text="Relatórios gerados",
                     font=FONTS["section_title"],
                     text_color=COLORS["text_primary"],
                     anchor="w").pack(fill="x", pady=(0, 8))

        for rel in relatorios:
            self._item_relatorio(scroll, rel)

    def _item_relatorio(self, parent, rel: dict):
        """Renderiza um item da lista de relatórios."""
        item = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                            corner_radius=10, border_width=1,
                            border_color=COLORS["border_light"])
        item.pack(fill="x", pady=(0, 6))

        row = ctk.CTkFrame(item, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=10)

        # Ícone LF
        icone = ctk.CTkFrame(row, fg_color=COLORS["primary_100"],
                              corner_radius=8, width=40, height=40)
        icone.pack(side="left", padx=(0, 12))
        icone.pack_propagate(False)
        ctk.CTkLabel(icone, text="LF", font=("Arial", 11, "bold"),
                     text_color=COLORS["primary_700"]).place(relx=0.5, rely=0.5, anchor="center")

        # Detalhes
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        nome = rel.get("arquivo") or rel.get("caminho", "—")
        ctk.CTkLabel(info, text=Path(nome).name if nome else "—",
                     font=FONTS["body"],
                     text_color=COLORS["text_primary"],
                     anchor="w").pack(fill="x")

        filtros = rel.get("filtros", {})
        rating = filtros.get("rating_minimo", "?")
        periodo = filtros.get("periodo_meses", "?")
        emissoes = rel.get("emissoes", 0)
        tempo = _tempo_relativo(rel.get("data", ""))

        meta = f"{tempo}  ·  Rating: {rating}  ·  {emissoes} emissão(ões)  ·  {periodo}m"
        ctk.CTkLabel(info, text=meta, font=FONTS["small"],
                     text_color=COLORS["text_muted"],
                     anchor="w").pack(fill="x")

        # Botão Abrir
        caminho = rel.get("caminho", "")
        if caminho and Path(caminho).exists():
            ctk.CTkButton(
                row, text="Abrir", width=70, height=30,
                corner_radius=8,
                fg_color=COLORS["primary_600"], hover_color=COLORS["primary_700"],
                text_color="white", font=("Arial", 12),
                command=lambda c=caminho: os.startfile(c),
            ).pack(side="right")

    def atualizar(self):
        """Recarrega o histórico."""
        for w in self.winfo_children():
            w.destroy()
        self._construir()
