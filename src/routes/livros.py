import logging
from flask import Blueprint, jsonify, request
from src.database import supabase
from src.utils.validators import obter_json_seguro
from src.utils.pagination import extrair_paginacao

logger = logging.getLogger(__name__)
livros_bp = Blueprint("livros", __name__)

@livros_bp.route("/livros", methods=["GET"])
def listar_livros():
    """Lista os livros do acervo com suporte a paginação."""
    try:
        page, per_page, start, end = extrair_paginacao()
        
        if "page" not in request.args:
            res = (
                supabase.schema("biblioteca")
                .table("livros")
                .select("*")
                .limit(100)
                .execute()
            )
            return jsonify(res.data), 200

        res = (
            supabase.schema("biblioteca")
            .table("livros")
            .select("*", count="exact")
            .range(start, end)
            .execute()
        )
        return jsonify({
            "pagina": page,
            "por_pagina": per_page,
            "total": res.count if res.count is not None else len(res.data),
            "livros": res.data
        }), 200

    except Exception as e:
        logger.exception("Erro ao listar livros do acervo")
        return jsonify({"erro": "Erro ao listar livros"}), 500

@livros_bp.route("/livros/<livro_titulo>", methods=["GET"])
def buscar_livros_por_titulo(livro_titulo: str):
    """Busca livros cujo título se inicia pelo texto informado (ilike)."""
    try:
        titulo_busca = livro_titulo.strip()
        response = (
            supabase.schema("biblioteca")
            .table("livros")
            .select("*")
            .ilike("titulo", f"{titulo_busca}%")
            .execute()
        )

        if not response.data:
            return jsonify({"erro": f"Livro '{livro_titulo}' não encontrado"}), 404

        return jsonify(response.data), 200

    except Exception as e:
        logger.exception("Erro ao buscar livro por título: %s", livro_titulo)
        return jsonify({"erro": "Erro ao realizar busca de livro"}), 500

@livros_bp.route("/livros/post", methods=["POST"])
def cadastrar_livro():
    """Cadastra um novo livro no acervo."""
    dados, erro_resp = obter_json_seguro()
    if erro_resp:
        return erro_resp

    try:
        numero_registro = str(dados.get("numero_de_registro") or "").strip()
        titulo = str(dados.get("titulo") or "").strip()

        if not numero_registro or not titulo:
            return jsonify({"erro": "Registro e Titulo são campos obrigatorios"}), 400

        novo_registro = {
            "numero_de_registro": numero_registro,
            "titulo": titulo,
            "autor": dados.get("autor"),
            "genero": dados.get("genero"),
            "categoria": dados.get("categoria"),
            "localizacao": dados.get("localizacao"),
            "observacoes": dados.get("observacoes"),
            "alugado": "não",
            "aluno": None,
            "data_aluguel": None,
            "data_entrega": None
        }

        response = (
            supabase.schema("biblioteca")
            .table("livros")
            .insert(novo_registro)
            .execute()
        )

        if not response.data:
            return jsonify({"erro": "Não foi possível cadastrar o livro"}), 500

        return jsonify({
            "status": "sucesso",
            "dados_inseridos": response.data[0]
        }), 201

    except Exception as e:
        logger.exception("Erro ao inserir novo livro: %s", dados.get("numero_de_registro"))
        # Verifica se foi violação de chave primária duplicada
        msg_erro = str(e).lower()
        if "duplicate key" in msg_erro or "unique" in msg_erro:
            return jsonify({"erro": f"Já existe um livro cadastrado com o registro '{numero_registro}'"}), 409
        return jsonify({"erro": "Erro interno ao cadastrar livro"}), 500

@livros_bp.route("/livros/alugados", methods=["GET"])
def listar_alugados():
    """Lista todos os livros atualmente marcados como alugados."""
    try:
        page, per_page, start, end = extrair_paginacao()

        if "page" not in request.args:
            res = (
                supabase.schema("biblioteca")
                .table("livros")
                .select("*")
                .ilike("alugado", "sim%")
                .execute()
            )
            return jsonify(res.data), 200

        res = (
            supabase.schema("biblioteca")
            .table("livros")
            .select("*", count="exact")
            .ilike("alugado", "sim%")
            .range(start, end)
            .execute()
        )
        return jsonify({
            "pagina": page,
            "por_pagina": per_page,
            "total": res.count if res.count is not None else len(res.data),
            "livros_alugados": res.data
        }), 200

    except Exception as e:
        logger.exception("Erro ao listar livros alugados")
        return jsonify({"erro": "Erro ao listar livros alugados"}), 500
