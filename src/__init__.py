import logging
from flask import Flask, jsonify
from flask_cors import CORS
from src.config import Config

def create_app() -> Flask:
    """Fábrica da aplicação Flask com configuração e registro de Blueprints."""
    # Configuração de logging estruturado
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    logger = logging.getLogger(__name__)

    app = Flask(__name__)

    # Configuração de CORS com origens controladas
    CORS(app, origins=Config.ALLOWED_ORIGINS)

    # Handlers globais de erro
    @app.errorhandler(400)
    def erro_bad_request(e):
        return jsonify({"erro": "Requisição inválida ou parâmetros ausentes"}), 400

    @app.errorhandler(404)
    def erro_nao_encontrado(e):
        return jsonify({"erro": "Recurso ou rota não encontrada"}), 404

    @app.errorhandler(405)
    def erro_metodo_nao_permitido(e):
        return jsonify({"erro": "Método HTTP não permitido para esta rota"}), 405

    @app.errorhandler(Exception)
    def erro_interno_servidor(e):
        # Registra stack trace completo nos logs internos sem expor esquema ao cliente
        logger.exception("Exceção não tratada capturada pelo interceptador global: %s", str(e))
        return jsonify({"erro": "Erro interno do servidor. Tente novamente mais tarde."}), 500

    # Registro dos Blueprints da aplicação
    from src.routes.core import core_bp
    from src.routes.livros import livros_bp
    from src.routes.alunos import alunos_bp
    from src.routes.emprestimos import emprestimos_bp
    from src.routes.auth import auth_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(livros_bp)
    app.register_blueprint(alunos_bp)
    app.register_blueprint(emprestimos_bp)
    app.register_blueprint(auth_bp)

    return app
