import logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask, jsonify
from flask_cors import CORS
from src.config import Config

def init_sentry() -> None:
    """Inicializa o Sentry com Performance Tracing para análise de uso das rotas."""
    if Config.SENTRY_DSN and not sentry_sdk.is_initialized():
        sentry_sdk.init(
            dsn=Config.SENTRY_DSN,
            integrations=[FlaskIntegration()],
            # Tracing: taxa de amostragem de 1.0 (100%) para capturar todas as requisições
            # e viabilizar a visualização das rotas mais acessadas no painel Performance do Sentry
            traces_sample_rate=Config.SENTRY_TRACES_SAMPLE_RATE,
            profile_session_sample_rate=Config.SENTRY_PROFILE_SESSION_SAMPLE_RATE,
            profile_lifecycle=Config.SENTRY_PROFILE_LIFECYCLE,
            environment=Config.SENTRY_ENVIRONMENT,
        )

def create_app() -> Flask:
    """Fábrica da aplicação Flask com configuração e registro de Blueprints."""
    # Configuração de logging estruturado
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Inicialização do Sentry para monitoramento e tracing de rotas
    init_sentry()

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
        if Config.SENTRY_DSN:
            sentry_sdk.capture_exception(e)
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
