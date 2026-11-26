<!--
Título do PR: tipo(escopo): descrição curta em pt-BR (conforme CONVENCOES_GIT.md)
Exemplos:
  feat(emprestimos): adiciona rota de renovacao sincronizada
  fix(livros): corrige codigo http 404 em busca inexistente
-->

## O que muda e por quê
<!-- Descreva objetivamente o que foi implementado ou corrigido e qual a motivação -->

## Tipo de Alteração
- [ ] `feat`: nova funcionalidade ou novo endpoint
- [ ] `fix`: correção de bug, erro de validação ou status HTTP
- [ ] `refactor`: reorganização interna sem alterar contratos externos
- [ ] `perf`: melhoria de desempenho (paginação, otimização de queries)
- [ ] `test`: adição ou atualização de testes automatizados
- [ ] `docs`: documentação ou atualização de PDFs
- [ ] `chore`: dependências ou configuração

## Escopo Afetado
- [ ] `livros` (acervo, busca, cadastro)
- [ ] `alunos` (cadastro, listagem, consulta)
- [ ] `emprestimos` (aluguel, renovação, devolução, histórico)
- [ ] `auth` (login e credenciais)
- [ ] `core` (infraestrutura, database, config, factory)
- [ ] `tests` / `docs`

## Impacto no Frontend e Contratos da API
- **Rotas afetadas:** <!-- Nenhuma rota alterada | lista das rotas -->
- **Payloads ou Status HTTP:** <!-- Sem impacto / retrocompatível | quais mudaram -->
- **Variáveis de Ambiente:** <!-- Não | Sim: quais precisam ser adicionadas no .env -->

## Como Testar
```bash
# Executar a suíte de testes de fumaça localmente
python -m unittest tests/test_smoke.py
```

## Evidência dos Testes
<!-- Cole o resumo da execução dos testes locais (ex.: Ran 15 tests in 0.020s - OK) -->

## Checklist Obrigatório
- [ ] Testes locais passando (`tests/test_smoke.py`)
- [ ] **NENHUMA** chamada `POST` ou mutação real foi feita contra o banco de dados durante os testes
- [ ] Nenhum arquivo `.env`, credencial ou segredo incluído no diff (`git status`)
- [ ] Mensagens de commit seguem o padrão de [CONVENCOES_GIT.md](CONVENCOES_GIT.md)
- [ ] O agente de IA não realizou merge nem force push
