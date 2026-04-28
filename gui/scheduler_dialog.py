"""Diálogo de agendamento automático via Windows Task Scheduler."""
import json
import subprocess
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from gui.styles import COLORS, FONTS


class SchedulerDialog(tk.Toplevel):
    """Janela modal para agendar execuções automáticas."""

    def __init__(self, parent, presets_dir: Path = None):
        super().__init__(parent)
        self.parent = parent
        self.presets_dir = presets_dir
        self._configurar_janela()
        self._construir_ui()
        self._verificar_agendamento_existente()
        self._centralizar()

        self.grab_set()
        self.focus_set()
        self.wait_window()

    def _configurar_janela(self):
        self.title("Agendamento Automático")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

    def _construir_ui(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Agendamento Automático",
                 font=FONTS["subtitle"], bg=COLORS["bg"],
                 fg=COLORS["primary"]).pack(anchor="w", pady=(0, 12))

        # ── Frequência ────────────────────────────────────────────────────────
        tk.Label(frame, text="Frequência", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")

        self.var_freq = tk.StringVar(value="diario")
        frame_freq = tk.Frame(frame, bg=COLORS["bg"])
        frame_freq.pack(fill="x", pady=(4, 0))

        for valor, label in [("diario", "Diário"), ("semanal", "Semanal"), ("mensal", "Mensal")]:
            tk.Radiobutton(
                frame_freq, text=label, variable=self.var_freq, value=valor,
                font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text"],
                activebackground=COLORS["bg"],
                selectcolor=COLORS["primary_light"],
                cursor="hand2"
            ).pack(side="left", padx=(0, 16))

        # ── Horário ───────────────────────────────────────────────────────────
        tk.Label(frame, text="Horário de execução", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_secondary"]).pack(anchor="w", pady=(12, 0))

        frame_hora = tk.Frame(frame, bg=COLORS["bg"])
        frame_hora.pack(fill="x", pady=(4, 0))

        self.spin_hora = tk.Spinbox(frame_hora, from_=0, to=23, width=3,
                                    font=FONTS["body"], justify="center",
                                    relief="solid", bd=1,
                                    highlightthickness=1,
                                    highlightbackground=COLORS["border"])
        self.spin_hora.delete(0, "end")
        self.spin_hora.insert(0, "08")
        self.spin_hora.pack(side="left")

        tk.Label(frame_hora, text=":", font=FONTS["body"],
                 bg=COLORS["bg"]).pack(side="left", padx=4)

        self.spin_minuto = tk.Spinbox(frame_hora, from_=0, to=59, width=3,
                                      font=FONTS["body"], justify="center",
                                      relief="solid", bd=1,
                                      highlightthickness=1,
                                      highlightbackground=COLORS["border"])
        self.spin_minuto.delete(0, "end")
        self.spin_minuto.insert(0, "00")
        self.spin_minuto.pack(side="left")

        # ── Preset para execução automática ──────────────────────────────────
        tk.Label(frame, text="Filtros para execução automática",
                 font=FONTS["field_label"], bg=COLORS["bg"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(12, 0))

        presets = self._listar_presets()
        opcoes = ["(Usar filtros padrão)"] + [p["nome"] for p in presets]
        self._presets_lista = presets

        self.var_preset = tk.StringVar(value=opcoes[0])
        self.combo_preset = tk.OptionMenu(frame, self.var_preset, *opcoes)
        self.combo_preset.config(font=FONTS["body"], bg=COLORS["bg"],
                                  relief="solid", bd=1, cursor="hand2")
        self.combo_preset.pack(fill="x", pady=(4, 0))

        # ── Status atual ──────────────────────────────────────────────────────
        tk.Frame(frame, bg=COLORS["border"], height=1).pack(fill="x", pady=16)

        self.label_status = tk.Label(frame, text="",
                                     font=FONTS["small"], bg=COLORS["bg"],
                                     fg=COLORS["text_secondary"], wraplength=400,
                                     justify="left")
        self.label_status.pack(anchor="w")

        # ── Botões ────────────────────────────────────────────────────────────
        frame_btns = tk.Frame(frame, bg=COLORS["bg"])
        frame_btns.pack(fill="x", pady=(16, 0))

        tk.Button(frame_btns, text="Cancelar", font=FONTS["body"],
                  bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                  relief="solid", bd=1, padx=12, pady=6,
                  cursor="hand2", command=self.destroy).pack(side="right", padx=(8, 0))

        tk.Button(frame_btns, text="Remover agendamento", font=FONTS["body"],
                  bg=COLORS["error_bg"], fg=COLORS["error"],
                  relief="solid", bd=1, padx=12, pady=6,
                  cursor="hand2", command=self._remover).pack(side="right", padx=(8, 0))

        tk.Button(frame_btns, text="Agendar", font=FONTS["body"],
                  bg=COLORS["primary"], fg="white",
                  relief="flat", padx=12, pady=6,
                  cursor="hand2", command=self._agendar).pack(side="right")

    def _listar_presets(self) -> list[dict]:
        if not self.presets_dir or not self.presets_dir.exists():
            return []
        from config.filters import FiltrosConsulta
        return FiltrosConsulta.listar_presets(self.presets_dir)

    def _verificar_agendamento_existente(self):
        try:
            resultado = subprocess.run(
                ["schtasks", "/query", "/tn", "AgenteB3", "/fo", "LIST"],
                capture_output=True, text=True, encoding="cp1252"
            )
            if resultado.returncode == 0 and "AgenteB3" in resultado.stdout:
                self.label_status.config(
                    text="Agendamento ativo: tarefa 'AgenteB3' encontrada no Agendador de Tarefas.",
                    fg=COLORS["success"]
                )
            else:
                self.label_status.config(
                    text="Nenhum agendamento ativo para o Agente B3.",
                    fg=COLORS["text_secondary"]
                )
        except Exception:
            self.label_status.config(
                text="Não foi possível verificar o Agendador de Tarefas.",
                fg=COLORS["text_secondary"]
            )

    def _agendar(self):
        frequencia = self.var_freq.get()
        hora = self.spin_hora.get().zfill(2)
        minuto = self.spin_minuto.get().zfill(2)
        horario = f"{hora}:{minuto}"

        # Salvar preset escolhido em scheduler_config.json
        preset_nome = self.var_preset.get()
        self._salvar_scheduler_config(preset_nome)

        # Determinar caminho do executável
        import sys
        from pathlib import Path as P
        if getattr(sys, "frozen", False):
            exe = sys.executable
        else:
            launcher = P(__file__).resolve().parent.parent / "launcher.py"
            exe = f'"{sys.executable}" "{launcher}" --auto'

        agendamento_map = {
            "diario": "DAILY",
            "semanal": "WEEKLY",
            "mensal": "MONTHLY",
        }
        schtask_freq = agendamento_map.get(frequencia, "DAILY")

        cmd = [
            "schtasks", "/create",
            "/tn", "AgenteB3",
            "/tr", exe if getattr(sys, "frozen", False) else f'"{sys.executable}" "{P(__file__).resolve().parent.parent / "launcher.py"}" --auto',
            "/sc", schtask_freq,
            "/st", horario,
            "/f",
        ]

        try:
            resultado = subprocess.run(cmd, capture_output=True, text=True, encoding="cp1252")
            if resultado.returncode == 0:
                messagebox.showinfo(
                    "Agendamento criado",
                    f"Execução automática agendada com sucesso!\n"
                    f"Frequência: {frequencia.capitalize()} às {horario}.",
                    parent=self
                )
                self._verificar_agendamento_existente()
            else:
                raise RuntimeError(resultado.stderr or resultado.stdout)
        except Exception as e:
            messagebox.showerror(
                "Erro ao agendar",
                f"Não foi possível criar o agendamento.\n"
                f"Verifique se você tem permissões de administrador.",
                parent=self
            )

    def _remover(self):
        if not messagebox.askyesno(
            "Remover agendamento",
            "Deseja remover o agendamento automático do Agente B3?",
            parent=self
        ):
            return
        try:
            resultado = subprocess.run(
                ["schtasks", "/delete", "/tn", "AgenteB3", "/f"],
                capture_output=True, text=True, encoding="cp1252"
            )
            if resultado.returncode == 0:
                messagebox.showinfo("Removido", "Agendamento removido com sucesso.", parent=self)
                self._verificar_agendamento_existente()
            else:
                raise RuntimeError(resultado.stderr)
        except Exception as e:
            messagebox.showerror("Erro", "Não foi possível remover o agendamento.", parent=self)

    def _salvar_scheduler_config(self, preset_nome: str):
        from pathlib import Path as P
        projeto_dir = P(__file__).resolve().parent.parent
        config = {"preset_nome": preset_nome, "preset_path": ""}

        if preset_nome != "(Usar filtros padrão)":
            for p in self._presets_lista:
                if p["nome"] == preset_nome:
                    config["preset_path"] = p["arquivo"]
                    break

        config_path = projeto_dir / "scheduler_config.json"
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    def _centralizar(self):
        self.update_idletasks()
        w = self.winfo_width() or 460
        h = self.winfo_height() or 400
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")
