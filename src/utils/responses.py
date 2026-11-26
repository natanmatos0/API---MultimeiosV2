from typing import Any, Optional, Tuple
from flask import jsonify, Response

def resposta_sucesso(dados: Any = None, mensagem: Optional[str] = None, status_code: int = 200, **kwargs) -> Tuple[Response, int]:
    """Gera uma resposta padronizada de sucesso em formato JSON."""
    corpo = {}
    if mensagem is not None:
        corpo["status"] = "sucesso"
        corpo["mensagem"] = mensagem
    if dados is not None:
        if isinstance(dados, dict) and "status" in dados and not mensagem:
            corpo = dados
        else:
            corpo["dados"] = dados
    for k, v in kwargs.items():
        corpo[k] = v

    return jsonify(corpo), status_code

def resposta_erro(mensagem: str, status_code: int = 400) -> Tuple[Response, int]:
    """Gera uma resposta padronizada de erro em formato JSON com código de status semântico."""
    return jsonify({"erro": mensagem}), status_code
