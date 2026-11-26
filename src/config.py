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
