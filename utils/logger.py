"""Logging configurável para o Agente B3 (console + arquivo)."""
import logging
import sys
from datetime import datetime
from pathlib import Path

_configurado = False


def configurar_logger(
    verbose: bool = False,
    logs_dir: Path | None = None,
    nome_arquivo: str | None = None,
) -> None:
    """
    Configura o logger raiz do agente.

    Parâmetros:
        verbose: Se True, exibe nível DEBUG no console; caso contrário, INFO.
        logs_dir: Diretório para salvar o arquivo de log. None = sem arquivo.
        nome_arquivo: Nome do arquivo de log. None = gera automaticamente com timestamp.
    """
    global _configurado
    if _configurado:
        return

    nivel_console = logging.DEBUG if verbose else logging.INFO
    formato = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    formato_data = "%H:%M:%S"

    logger_raiz = logging.getLogger()
    logger_raiz.setLevel(logging.DEBUG)

    # Handler de console com colorama (se disponível)
    handler_console = logging.StreamHandler(sys.stdout)
    handler_console.setLevel(nivel_console)
    try:
        from colorama import Fore, Style, init
        init(autoreset=True)

        class FormatterColorido(logging.Formatter):
            CORES = {
                logging.DEBUG: Fore.CYAN,
                logging.INFO: Fore.GREEN,
                logging.WARNING: Fore.YELLOW,
                logging.ERROR: Fore.RED,
                logging.CRITICAL: Fore.MAGENTA,
            }

            def format(self, record):
                cor = self.CORES.get(record.levelno, "")
                texto = super().format(record)
                return f"{cor}{texto}{Style.RESET_ALL}"

        handler_console.setFormatter(FormatterColorido(formato, formato_data))
    except ImportError:
        handler_console.setFormatter(logging.Formatter(formato, formato_data))

    logger_raiz.addHandler(handler_console)

    # Handler de arquivo (opcional)
    if logs_dir is not None:
        logs_dir.mkdir(parents=True, exist_ok=True)
        if nome_arquivo is None:
            nome_arquivo = f"agente_b3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        caminho_log = logs_dir / nome_arquivo
        handler_arquivo = logging.FileHandler(caminho_log, encoding="utf-8")
        handler_arquivo.setLevel(logging.DEBUG)
        handler_arquivo.setFormatter(logging.Formatter(formato, "%Y-%m-%d %H:%M:%S"))
        logger_raiz.addHandler(handler_arquivo)

    _configurado = True


def obter_logger(nome: str) -> logging.Logger:
    """Retorna logger nomeado para um módulo."""
    return logging.getLogger(nome)
