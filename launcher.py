"""
Ponto de entrada do Agente B3.
- Sem argumentos: abre interface gráfica.
- Com argumentos CLI: roda no terminal.
- Com --auto: roda silenciosamente (agendamento).
"""
import sys
import os


def main():
    args = sys.argv[1:]

    if "--auto" in args:
        _executar_modo_automatico()
    elif args:
        _attach_console_if_needed()
        from main import main as cli_main
        cli_main()
    else:
        from gui.app import iniciar_gui
        iniciar_gui()


def _executar_modo_automatico():
    """Execução silenciosa com preset agendado ou filtros padrão."""
    import logging
    from pathlib import Path
    from datetime import datetime

    log_dir = Path.home() / "Documents" / "Relatorios LF" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(filename=str(log_file), level=logging.INFO,
                        format="[%(asctime)s] [%(levelname)s] %(message)s")

    try:
        from config.filters import FiltrosConsulta
        from config.settings import PROJECT_ROOT
        from main import executar_agente
        import json

        # Tentar carregar preset agendado
        scheduler_config = PROJECT_ROOT / "scheduler_config.json"
        if scheduler_config.exists():
            config = json.loads(scheduler_config.read_text(encoding="utf-8"))
            preset_path = config.get("preset_path")
            if preset_path and Path(preset_path).exists():
                filtros, nome = FiltrosConsulta.carregar_preset(Path(preset_path))
                logging.info(f"Usando preset agendado: {nome}")
            else:
                filtros = FiltrosConsulta()
        else:
            filtros = FiltrosConsulta()

        filtros.output_dir = str(Path.home() / "Documents" / "Relatorios LF")
        resultado = executar_agente(filtros=filtros, verbose=False)

        if resultado["sucesso"]:
            logging.info(f"Relatório gerado: {resultado['arquivo']} ({resultado['emissoes']} emissões)")
        else:
            logging.error(f"Erro: {resultado.get('erro', 'desconhecido')}")
    except Exception as e:
        logging.error(f"Erro na execução automática: {e}")


def _attach_console_if_needed():
    if sys.platform == "win32" and not sys.stdout:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.AllocConsole()
            sys.stdout = open("CONOUT$", "w")
            sys.stderr = open("CONOUT$", "w")
        except Exception:
            pass


if __name__ == "__main__":
    main()
