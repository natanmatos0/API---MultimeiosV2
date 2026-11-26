import logging
from flask import Blueprint, jsonify
from src.database import supabase
from src.utils.validators import validar_uuid
from src.utils.dates import obter_data_atual_str, calcular_prazo_str, somar_dias_str

logger = logging.getLogger(__name__)
emprestimos_bp = Blueprint("emprestimos", __name__)

@emprestimos_bp.route("/alunos/<aluno_id>/alugar/<numero_registro>", methods=["POST"])
def aluno_alugar_livro(aluno_id: str, numero_registro: str):
    """
    Aluga um livro para um aluno.
    Aplica verificação atômica de concorrência e compensação (rollback) em caso de falha.
    """
    if not validar_uuid(aluno_id):
        return jsonify({"erro": "O ID do aluno fornecido não é um UUID válido"}), 400

    num_reg = str(numero_registro).strip()

    try:
        # 1. Verifica se o aluno existe
        res_aluno = (
            supabase.schema("biblioteca")
            .table("alunos")
            .select("id, nome")
            .eq("id", aluno_id)
            .execute()
        )
        if not res_aluno.data:
            return jsonify({"erro": f"Aluno com ID '{aluno_id}' não encontrado"}), 404

        nome_aluno = res_aluno.data[0]["nome"]

        # 2. Verifica se o livro existe e checa disponibilidade preliminar
        res_livro = (
            supabase.schema("biblioteca")
            .table("livros")
            .select("numero_de_registro, titulo, alugado")
            .eq("numero_de_registro", num_reg)
            .execute()
        )
        if not res_livro.data:
            return jsonify({"erro": f"Livro com registro '{num_reg}' não encontrado"}), 404

        livro = res_livro.data[0]
        if livro.get("alugado") == "sim":
            return jsonify({"erro": "Este livro já está alugado no momento"}), 409

        # 3. Calcula as datas com fuso de Brasília (prazo padrão de 14 dias)
        data_aluguel = obter_data_atual_str()
        data_entrega_prevista = calcular_prazo_str(dias=14)

        # 4. Bloqueio atômico de concorrência: só atualiza se 'alugado' ainda for 'não'
        res_bloqueio = (
            supabase.schema("biblioteca")
            .table("livros")
            .update({
                "alugado": "sim",
                "aluno": nome_aluno,
                "data_aluguel": data_aluguel,
                "data_entrega": data_entrega_prevista
            })
            .eq("numero_de_registro", num_reg)
            .eq("alugado", "não")
            .execute()
        )

        # Se nenhum registro foi alterado, outra requisição concorrente alugou primeiro
        if not res_bloqueio.data:
            logger.warning("Concorrência detectada: livro %s já foi reservado por outro processo.", num_reg)
            return jsonify({"erro": "O livro acabou de ser alugado por outro usuário ou não está disponível"}), 409

        # 5. Registra o empréstimo na tabela emprestimos
        novo_emprestimo = {
            "aluno_id": aluno_id,
            "numero_de_registro": num_reg,
            "data_aluguel": data_aluguel,
            "data_entrega_prevista": data_entrega_prevista,
            "status": "ativo"
        }

        try:
            res_emprestimo = (
                supabase.schema("biblioteca")
                .table("emprestimos")
                .insert(novo_emprestimo)
                .execute()
            )
            if not res_emprestimo.data:
                raise RuntimeError("Falha ao inserir empréstimo na tabela.")

        except Exception as insert_err:
            # Compensação / Rollback manual: desfaz o bloqueio do livro
            logger.error("Falha ao registrar empréstimo para %s. Revertendo status do livro: %s", num_reg, str(insert_err))
            supabase.schema("biblioteca").table("livros").update({
                "alugado": "não",
                "aluno": None,
                "data_aluguel": None,
                "data_entrega": None
            }).eq("numero_de_registro", num_reg).execute()
            raise insert_err

        return jsonify({
            "status": "sucesso",
            "mensagem": f"Livro '{livro['titulo']}' alugado para {nome_aluno}. Devolução até {data_entrega_prevista}.",
            "emprestimo": res_emprestimo.data[0]
        }), 201

    except Exception as e:
        logger.exception("Erro inesperado ao alugar livro %s para aluno %s", num_reg, aluno_id)
        return jsonify({"erro": "Erro interno ao processar o empréstimo"}), 500

@emprestimos_bp.route("/alunos/<aluno_id>/renovar/<numero_registro>", methods=["POST"])
def renovar_livro_aluno(aluno_id: str, numero_registro: str):
    """
    Renova o empréstimo ativo do livro para o aluno informado.
    Adiciona 7 dias ao prazo de entrega e sincroniza simultaneamente as tabelas 'livros' e 'emprestimos'.
    """
    if not validar_uuid(aluno_id):
        return jsonify({"erro": "O ID do aluno fornecido não é um UUID válido"}), 400

    num_reg = str(numero_registro).strip()

    try:
        # 1. Busca o empréstimo ativo correspondente deste aluno com este livro
        res_emprestimo = (
            supabase.schema("biblioteca")
            .table("emprestimos")
            .select("*")
            .eq("aluno_id", aluno_id)
            .eq("numero_de_registro", num_reg)
            .eq("status", "ativo")
            .execute()
        )

        if not res_emprestimo.data:
            return jsonify({"erro": "Nenhum empréstimo ativo encontrado para este aluno e livro"}), 404

        emprestimo = res_emprestimo.data[0]
        data_base_str = emprestimo.get("data_entrega_prevista") or obter_data_atual_str()

        # 2. Calcula a nova data de entrega (+7 dias adicionais)
        nova_data_entrega_str = somar_dias_str(data_base_str, dias=7)

        # 3. Atualiza a tabela 'emprestimos'
        res_update_emp = (
            supabase.schema("biblioteca")
            .table("emprestimos")
            .update({"data_entrega_prevista": nova_data_entrega_str})
            .eq("id", emprestimo["id"])
            .execute()
        )

        # 4. Atualiza simultaneamente a tabela 'livros'
        res_update_livro = (
            supabase.schema("biblioteca")
            .table("livros")
            .update({"data_entrega": nova_data_entrega_str})
            .eq("numero_de_registro", num_reg)
            .execute()
        )

        return jsonify({
            "status": "sucesso",
            "mensagem": f"Livro renovado com sucesso! Nova data de entrega: {nova_data_entrega_str}.",
            "nova_data_entrega": nova_data_entrega_str,
            "emprestimo": res_update_emp.data[0] if res_update_emp.data else None
        }), 200

    except Exception as e:
        logger.exception("Erro ao renovar livro %s para aluno %s", num_reg, aluno_id)
        return jsonify({"erro": "Erro interno ao renovar empréstimo"}), 500

@emprestimos_bp.route("/livros/renovar/<numero_registro>", methods=["POST"])
def renovar_livro_compatibilidade(numero_registro: str):
    """
    Rota de compatibilidade com frontends que ainda chamam /livros/renovar/<id>.
    Localiza o empréstimo ativo pelo número de registro e delega para a renovação relacional.
    """
    num_reg = str(numero_registro).strip()
    try:
        res_emprestimo = (
            supabase.schema("biblioteca")
            .table("emprestimos")
            .select("aluno_id")
            .eq("numero_de_registro", num_reg)
            .eq("status", "ativo")
            .execute()
        )
        if not res_emprestimo.data:
            return jsonify({"erro": "Nenhum empréstimo ativo encontrado para este livro"}), 404

        aluno_id = res_emprestimo.data[0]["aluno_id"]
        return renovar_livro_aluno(aluno_id, num_reg)

    except Exception as e:
        logger.exception("Erro ao renovar livro via rota de compatibilidade: %s", num_reg)
        return jsonify({"erro": "Erro interno ao renovar empréstimo"}), 500

@emprestimos_bp.route("/livros/devolver/<numero_registro>", methods=["POST"])
def devolver_livro_compatibilidade(numero_registro: str):
    """
    Rota de compatibilidade com frontends que ainda chamam /livros/devolver/<id>.
    Localiza o empréstimo ativo pelo número de registro e executa a devolução coordenada.
    """
    num_reg = str(numero_registro).strip()
    try:
        res_emprestimo = (
            supabase.schema("biblioteca")
            .table("emprestimos")
            .select("aluno_id")
            .eq("numero_de_registro", num_reg)
            .eq("status", "ativo")
            .execute()
        )
        if not res_emprestimo.data:
            return jsonify({"erro": "Nenhum empréstimo ativo encontrado para este livro"}), 404

        aluno_id = res_emprestimo.data[0]["aluno_id"]
        return aluno_devolver_livro(aluno_id, num_reg)

    except Exception as e:
        logger.exception("Erro ao devolver livro via rota de compatibilidade: %s", num_reg)
        return jsonify({"erro": "Erro interno ao registrar devolução"}), 500

@emprestimos_bp.route("/alunos/<aluno_id>/devolver/<numero_registro>", methods=["POST"])
def aluno_devolver_livro(aluno_id: str, numero_registro: str):
    """
    Registra a devolução de um exemplar alugado por um aluno.
    Atualiza o status na tabela 'emprestimos' e libera o livro na tabela 'livros'.
    """
    if not validar_uuid(aluno_id):
        return jsonify({"erro": "O ID do aluno fornecido não é um UUID válido"}), 400

    num_reg = str(numero_registro).strip()

    try:
        # 1. Busca o empréstimo ativo desse aluno com esse livro
        res_emprestimo = (
            supabase.schema("biblioteca")
            .table("emprestimos")
            .select("*")
            .eq("aluno_id", aluno_id)
            .eq("numero_de_registro", num_reg)
            .eq("status", "ativo")
            .execute()
        )

        if not res_emprestimo.data:
            return jsonify({"erro": "Nenhum empréstimo ativo encontrado para este aluno e livro"}), 404

        emprestimo = res_emprestimo.data[0]
        data_devolucao_real = obter_data_atual_str()

        # 2. Atualiza o registro de empréstimo para 'devolvido'
        supabase.schema("biblioteca").table("emprestimos").update({
            "status": "devolvido",
            "data_devolucao_real": data_devolucao_real
        }).eq("id", emprestimo["id"]).execute()

        # 3. Libera o livro na tabela livros
        supabase.schema("biblioteca").table("livros").update({
            "alugado": "não",
            "aluno": None,
            "data_aluguel": None,
            "data_entrega": None
        }).eq("numero_de_registro", num_reg).execute()

        return jsonify({
            "status": "sucesso",
            "mensagem": f"Livro '{num_reg}' devolvido com sucesso em {data_devolucao_real}."
        }), 200

    except Exception as e:
        logger.exception("Erro ao devolver livro %s para aluno %s", num_reg, aluno_id)
        return jsonify({"erro": "Erro interno ao registrar devolução"}), 500

@emprestimos_bp.route("/alunos/<aluno_id>/historico", methods=["GET"])
def historico_aluno(aluno_id: str):
    """
    Consulta o histórico de empréstimos do aluno com join relacional (evitando N+1 queries).
    Retorna os dados do empréstimo associados aos detalhes completos do exemplar.
    """
    if not validar_uuid(aluno_id):
        return jsonify({"erro": "O ID do aluno fornecido não é um UUID válido"}), 400

    try:
        # 1. Verifica se o aluno existe
        res_aluno = (
            supabase.schema("biblioteca")
            .table("alunos")
            .select("id, nome")
            .eq("id", aluno_id)
            .execute()
        )
        if not res_aluno.data:
            return jsonify({"erro": f"Aluno com ID '{aluno_id}' não encontrado"}), 404

        nome_aluno = res_aluno.data[0]["nome"]

        # 2. Busca enriquecida com join relacional direto no PostgREST
        res_historico = (
            supabase.schema("biblioteca")
            .table("emprestimos")
            .select("*, livros(titulo, autor, genero, categoria, localizacao)")
            .eq("aluno_id", aluno_id)
            .order("data_aluguel", desc=True)
            .execute()
        )

        return jsonify({
            "aluno_id": aluno_id,
            "aluno": nome_aluno,
            "total_emprestimos": len(res_historico.data),
            "historico": res_historico.data
        }), 200

    except Exception as e:
        logger.exception("Erro ao consultar histórico do aluno: %s", aluno_id)
        return jsonify({"erro": "Erro ao consultar histórico de empréstimos"}), 500
