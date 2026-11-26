import uuid
from typing import Any, Tuple, Optional
from flask import request, jsonify, Response

def validar_uuid(valor: Any) -> bool:
    """Verifica se uma string ou valor representa um UUID válido."""
    if not valor:
        return False
    try:
        uuid_obj = uuid.UUID(str(valor).strip())
        return str(uuid_obj) == str(valor).strip().lower()
    except (ValueError, AttributeError):
        return False

def obter_json_seguro() -> Tuple[Optional[dict], Optional[Tuple[Response, int]]]:
    """
    Obtém o JSON da requisição com tratamento seguro contra payloads nulos ou malformados.
    Evita quebras de execução com AttributeError.
    """
    dados = request.get_json(silent=True)
    if dados is None or not isinstance(dados, dict):
        return None, (jsonify({"erro": "O corpo da requisição deve ser um JSON válido e não-vazio"}), 400)
    return dados, None
