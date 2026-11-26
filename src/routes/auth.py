import logging
from flask import Blueprint, jsonify, request
from src.config import Config
from src.utils.validators import obter_json_seguro

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """Endpoint de autenticação administrativa utilizando credenciais configuradas."""
    dados, erro_resp = obter_json_seguro()
    if erro_resp:
        return erro_resp

    try:
        user_input = dados.get("user")
        pass_input = dados.get("pass")

        # Verifica se o par user/pass existe na lista de usuários configurada
        usuario_valido = any(
            isinstance(u, dict) and u.get("user") == user_input and u.get("pass") == pass_input
            for u in Config.LISTA_USUARIOS
        )

        if usuario_valido:
            logger.info("Login bem-sucedido para o usuário: %s", user_input)
            return jsonify({
                "success": True,
                "mensagem": f"Bem-vindo, {user_input}!"
            }), 200

        logger.warning("Tentativa de login inválida para o usuário: %s", user_input)
        return jsonify({
            "success": False,
            "mensagem": "Usuário ou senha incorretos"
        }), 401

    except Exception as e:
        logger.exception("Erro ao processar login administrativo")
        return jsonify({
            "success": False,
            "erro": "Erro ao processar login"
        }), 500
