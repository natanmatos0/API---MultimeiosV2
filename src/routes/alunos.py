import logging
from flask import Blueprint, jsonify, request
from src.database import supabase
from src.utils.validators import obter_json_seguro, validar_uuid
from src.utils.pagination import extrair_paginacao

logger = logging.getLogger(__name__)
alunos_bp = Blueprint("alunos", __name__)

@alunos_bp.route("/criar_aluno", methods=["POST"])
@alunos_bp.route("/alunos", methods=["POST"])
def cadastrar_aluno():
    """
    Cadastra um novo aluno no sistema.
    Endpoint oficial: POST /criar_aluno (mantendo alias POST /alunos para compatibilidade).
    """
    dados, erro_resp = obter_json_seguro()
    if erro_resp:
        return erro_resp

    try:
        nome = str(dados.get("nome") or "").strip()
        curso = str(dados.get("curso") or "").strip()
        ano_raw = dados.get("ano")

        if not nome or not curso or ano_raw is None:
            return jsonify({"erro": "Os campos 'nome', 'curso' e 'ano' são obrigatórios"}), 400

        try:
            ano = int(ano_raw)
        except (ValueError, TypeError):
            return jsonify({"erro": "O campo 'ano' deve ser um número inteiro válido"}), 400

        novo_aluno = {
            "nome": nome,
            "curso": curso,
            "ano": ano
        }

        response = (
            supabase.schema("biblioteca")
            .table("alunos")
            .insert(novo_aluno)
            .execute()
        )

        if not response.data:
            return jsonify({"erro": "Não foi possível cadastrar o aluno"}), 500

        return jsonify({
            "status": "sucesso",
            "aluno_cadastrado": response.data[0]
        }), 201

    except Exception as e:
        logger.exception("Erro ao cadastrar aluno: %s", dados.get("nome"))
        return jsonify({"erro": "Erro interno ao cadastrar aluno"}), 500

@alunos_bp.route("/alunos", methods=["GET"])
def listar_alunos():
    """Lista todos os alunos cadastrados com suporte a paginação."""
    try:
        page, per_page, start, end = extrair_paginacao()

        if "page" not in request.args:
            response = (
                supabase.schema("biblioteca")
                .table("alunos")
                .select("*")
                .limit(100)
                .execute()
            )
            return jsonify(response.data), 200

        response = (
            supabase.schema("biblioteca")
            .table("alunos")
            .select("*", count="exact")
            .range(start, end)
            .execute()
        )
        return jsonify({
            "pagina": page,
            "por_pagina": per_page,
            "total": response.count if response.count is not None else len(response.data),
            "alunos": response.data
        }), 200

    except Exception as e:
        logger.exception("Erro ao listar alunos")
        return jsonify({"erro": "Erro ao consultar a lista de alunos"}), 500

@alunos_bp.route("/alunos/<aluno_id>", methods=["GET"])
def buscar_aluno(aluno_id: str):
    """Busca os dados de um aluno específico pelo seu UUID."""
    if not validar_uuid(aluno_id):
        return jsonify({"erro": "O ID do aluno fornecido não é um UUID válido"}), 400

    try:
        response = (
            supabase.schema("biblioteca")
            .table("alunos")
            .select("*")
            .eq("id", aluno_id)
            .execute()
        )

        if not response.data:
            return jsonify({"erro": f"Aluno com ID '{aluno_id}' não encontrado"}), 404

        return jsonify(response.data[0]), 200

    except Exception as e:
        logger.exception("Erro ao buscar aluno por ID: %s", aluno_id)
        return jsonify({"erro": "Erro ao consultar dados do aluno"}), 500
