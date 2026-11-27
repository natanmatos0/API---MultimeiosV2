import os
import json
import logging
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "").strip()
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "").strip()
    PORT: int = int(os.getenv("PORT", "5000"))
    
    # Origens permitidas para CORS
    _raw_origins = os.getenv("ALLOWED_ORIGINS", "*").strip()
    if _raw_origins == "*" or not _raw_origins:
        ALLOWED_ORIGINS = "*"
    else:
        ALLOWED_ORIGINS = [orig.strip() for orig in _raw_origins.split(",") if orig.strip()]

    # Usuários para autenticação administrativa (/login)
    try:
        LISTA_USUARIOS = json.loads(os.getenv("LISTA_USUARIOS", "[]"))
    except Exception as e:
        logger.warning("Falha ao analisar LISTA_USUARIOS do .env: %s. Utilizando lista vazia.", str(e))
        LISTA_USUARIOS = []

    # Monitoramento de desempenho, rastreamento de rotas e captura de erros (Sentry)
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "").strip()
    SENTRY_ENVIRONMENT: str = os.getenv("SENTRY_ENVIRONMENT", os.getenv("FLASK_ENV", "production")).strip()
    try:
        SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))
    except (ValueError, TypeError):
        SENTRY_TRACES_SAMPLE_RATE = 1.0

    try:
        SENTRY_PROFILE_SESSION_SAMPLE_RATE: float = float(
            os.getenv("SENTRY_PROFILE_SESSION_SAMPLE_RATE", os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "1.0"))
        )
    except (ValueError, TypeError):
        SENTRY_PROFILE_SESSION_SAMPLE_RATE = 1.0

    SENTRY_PROFILE_LIFECYCLE: str = os.getenv("SENTRY_PROFILE_LIFECYCLE", "trace").strip()

    @classmethod
    def validar(cls) -> None:
        """Validação fail-fast das variáveis de ambiente essenciais."""
        faltantes = []
        if not cls.SUPABASE_URL:
            faltantes.append("SUPABASE_URL")
        if not cls.SUPABASE_KEY:
            faltantes.append("SUPABASE_KEY")

        if faltantes:
            mensagem = f"Variáveis de ambiente obrigatórias não encontradas: {', '.join(faltantes)}"
            logger.critical(mensagem)
            raise RuntimeError(mensagem)
