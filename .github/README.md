# Configurações do GitHub — API Multimeios V2

Este diretório contém os templates e automações que operam no repositório GitHub da API:

| Arquivo / Pasta | Finalidade |
| :--- | :--- |
| [`pull_request_template.md`](pull_request_template.md) | Modelo obrigatório de preenchimento de Pull Requests, alinhado com [`CONVENCOES_GIT.md`](../CONVENCOES_GIT.md). |
| [`workflows/ci.yml`](workflows/ci.yml) | Pipeline de Integração Contínua (GitHub Actions) que executa os testes automatizados (`tests/test_smoke.py`) a cada push ou PR nas branches `main` e `develop`. |
| [`ISSUE_TEMPLATE/`](ISSUE_TEMPLATE/) | Formulários padronizados para relatar bugs e propor novas funcionalidades para a API. |
