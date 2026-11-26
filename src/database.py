from supabase import create_client, Client
from src.config import Config

# Instância lazy do cliente Supabase — criada apenas no primeiro acesso real.
# Isso evita que o import do módulo tente conectar ao Supabase durante testes
# ou no carregamento do CI, onde as variáveis de ambiente são mocks.

_supabase_client: Client | None = None


def _get_supabase() -> Client:
    """Retorna a instância singleton do cliente Supabase, criando-a se necessário."""
    global _supabase_client
    if _supabase_client is None:
        Config.validar()
        _supabase_client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    return _supabase_client


class _SupabaseProxy:
    """Proxy transparente que delega todas as chamadas ao cliente real via lazy init.
    
    Permite que os módulos continuem usando `from src.database import supabase`
    como se fosse o cliente real, sem precisar alterar nenhuma rota.
    """
    def __getattr__(self, name):
        return getattr(_get_supabase(), name)


supabase: Client = _SupabaseProxy()  # type: ignore[assignment]
