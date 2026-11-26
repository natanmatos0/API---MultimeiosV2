from supabase import create_client, Client
from src.config import Config

# Valida as configurações no carregamento do módulo
Config.validar()

# Instância única do cliente Supabase para reaproveitamento de pool de conexões
supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
