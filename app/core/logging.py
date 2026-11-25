import logging
import sys
from datetime import datetime

APP_LOGGER_NAME = "app"


def configure_logging() -> None:
    """Prepara a saída de log da aplicação.

    O handler é anexado diretamente no logger "app" em vez de depender do
    logging.basicConfig: o uvicorn configura o logging antes de importar a
    aplicação, e o basicConfig não faz nada se o root já tiver um handler.
    """
    logger = logging.getLogger(APP_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)


def now_label() -> str:
    """Data e hora atuais no formato do dia a dia: 11/08/2026 às 21:15:03."""
    return datetime.now().strftime("%d/%m/%Y às %H:%M:%S")


def duration_label(elapsed_ms: float) -> str:
    """Descreve uma duração em palavras, para quem não lê milissegundos."""
    if elapsed_ms < 1000:
        return f"{elapsed_ms:.0f} milissegundos"

    seconds = elapsed_ms / 1000
    unit = "segundo" if seconds < 2 else "segundos"
    return f"{seconds:.1f} {unit}".replace(".", ",")
