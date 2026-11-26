from datetime import datetime, timedelta, timezone

# Fuso horário oficial de Brasília (BRT - UTC-3)
FUSO_BRASILIA = timezone(timedelta(hours=-3))

def obter_data_atual_br() -> datetime:
    """Retorna o datetime atual considerando o fuso horário de Brasília."""
    return datetime.now(FUSO_BRASILIA)

def obter_data_atual_str() -> str:
    """Retorna a data atual de Brasília no formato YYYY-MM-DD."""
    return obter_data_atual_br().strftime("%Y-%m-%d")

def calcular_prazo_str(dias: int = 14) -> str:
    """Calcula a data futura a partir de hoje em Brasília no formato YYYY-MM-DD."""
    data_futura = obter_data_atual_br() + timedelta(days=dias)
    return data_futura.strftime("%Y-%m-%d")

def somar_dias_str(data_str: str, dias: int = 7) -> str:
    """Adiciona dias a uma data informada no formato YYYY-MM-DD."""
    data_obj = datetime.strptime(data_str, "%Y-%m-%d")
    nova_data = data_obj + timedelta(days=dias)
    return nova_data.strftime("%Y-%m-%d")
