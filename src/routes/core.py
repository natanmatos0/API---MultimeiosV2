import logging
from flask import Blueprint, jsonify, request
from src.database import supabase
from src.utils.pagination import extrair_paginacao

logger = logging.getLogger(__name__)
core_bp = Blueprint("core", __name__)

@core_bp.route("/", methods=["GET"])
def health_check():
    """Rota raiz retornando status da aplicação em JSON."""
    return jsonify({
        "status": "online",
        "servico": "API Multimeios",
        "versao": "2.0",
        "mensagem": "Serviço operacional e conectado."
    }), 200

@core_bp.route("/sentry-debug", methods=["GET"])
def sentry_debug():
    """Endpoint de teste para verificar envio de erros e transações ao Sentry."""
    logger.info("Disparando erro de teste para validação no Sentry.")
    divisao_por_zero = 1 / 0
    return jsonify({"resultado": divisao_por_zero})

@core_bp.route("/total", methods=["GET"])
def total_livros():
    """Retorna listagem de livros da biblioteca em formato estritamente JSON."""
    try:
        page, per_page, start, end = extrair_paginacao()
        
        # Se o cliente não solicitou paginação explícita, mantém compatibilidade retornando a lista
        if "page" not in request.args:
            response = (
                supabase.schema("biblioteca")
                .table("livros")
                .select("*")
                .limit(100)
                .execute()
            )
            return jsonify(response.data), 200

        response = (
            supabase.schema("biblioteca")
            .table("livros")
            .select("*", count="exact")
            .range(start, end)
            .execute()
        )
        return jsonify({
            "pagina": page,
            "por_pagina": per_page,
            "total": response.count if response.count is not None else len(response.data),
            "livros": response.data
        }), 200

    except Exception as e:
        logger.exception("Falha ao consultar listagem geral de livros em /total")
        return jsonify({"erro": "Erro ao consultar a lista de livros"}), 500
