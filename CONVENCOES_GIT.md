# Convenções de Git, Commits e Pull Requests — API Multimeios V2

> **Quando consultar:** antes de criar uma branch, commitar alterações, fazer push, abrir/revisar um Pull Request (PR) ou preparar uma release.

---

## 1. Estratégia de Branches

* **Branches Permanentes:**
  * `main`: Código estável e em produção (ex.: deploy no Render). Recebe alterações apenas via PR de release vindo da `develop`.
  * `develop`: Branch de integração contínua onde as novas funcionalidades e correções são testadas antes de irem para produção.
  * *Regra:* Nenhuma das duas recebe commits diretos — toda mudança entra via Pull Request.

* **Branches de Trabalho:**
  * Devem sempre partir da `develop` atualizada:
    ```bash
    git fetch origin
    git switch -c <tipo>/<slug> origin/develop
    ```
  * **Nomenclatura:** `<tipo>/<slug>`
    * `<tipo>`: Os mesmos tipos usados nos commits (§2).
    * `<slug>`: Curto, descritivo, em `kebab-case` e pt-BR sem acentos. Se houver uma issue vinculada, inicie pelo número: `fix/42-corrige-concorrencia-aluguel`.
  * Após o merge do PR, a branch de trabalho remota deve ser apagada.

---

## 2. Padrão de Commits

Utilizamos o padrão **Conventional Commits** adaptado para português (pt-BR):

```text
tipo(escopo): descrição curta em pt-BR

Corpo opcional: explique o porquê da mudança, decisões tomadas ou impacto no frontend.
```

### Tipos Permitidos
| Tipo | Quando utilizar |
| :--- | :--- |
| **`feat`** | Novo endpoint, nova funcionalidade ou novo comportamento visível |
| **`fix`** | Correção de bug, erro de validação, falha de concorrência ou status HTTP incorreto |
| **`refactor`** | Reorganização de código/arquitetura sem alterar o comportamento externo |
| **`test`** | Adição ou ajuste de testes automatizados (`tests/test_smoke.py`) |
| **`perf`** | Melhoria de desempenho (ex.: paginação, eliminação de N+1 queries) |
| **`docs`** | Alterações em documentação (`README.md`, PDFs, convenções) |
| **`chore`** | Manutenção: dependências (`requirements.txt`), configurações, scripts, formatação |

### Escopos do Projeto (API Multimeios V2)
* `livros` — Endpoints e regras do acervo (`/livros`, `/livros/post`, `/livros/alugados`)
* `alunos` — Cadastro, listagem e busca de leitores (`/criar_aluno`, `/alunos`)
* `emprestimos` — Aluguel, renovação, devolução e histórico
* `auth` — Autenticação administrativa (`/login`)
* `core` — Health check, fábrica Flask (`src/__init__.py`), `config.py`, `database.py`, utilitários
* `tests` — Suíte de testes de fumaça
* `docs` — Documentação e scripts geradores de PDF
* `deps` — Dependências e ambiente

### Boas Práticas de Mensagem
* Comece a descrição com **letra minúscula** e **sem ponto final**.
* Use verbos no imperativo/presente indicando o efeito (ex.: `feat(emprestimos): adiciona rota de renovacao sincronizada`).
* Evite mensagens vagas como `ajuste`, `wip`, `atualizacao` ou `correcoes`.
* Mantenha commits pequenos e focados em um único assunto.

---

## 3. Push e Segurança

* Faça push apenas da sua branch de trabalho:
  ```bash
  git push -u origin <tipo>/<slug>
  ```
* **Nunca** execute `git push --force` (`--force` ou `--force-with-lease`) em branches compartilhadas ou já publicadas.
* Para atualizar sua branch com o que entrou na `develop`, utilize merge:
  ```bash
  git fetch origin
  git merge origin/develop
  ```
* **Conferência obrigatória antes do commit:**
  * Sempre rode `git status` antes de adicionar arquivos.
  * **Nunca** adicione o arquivo `.env`, a pasta `venv/` ou arquivos de cache (`__pycache__/`).

---

## 4. Pull Requests (PR)

* **Destino:**
  * Branches de trabalho (`feat/*`, `fix/*`, `refactor/*`, etc.) → **`develop`**
  * Releases (código validado para produção) → **`main`** (`develop → main`)
* **Título do PR:** Deve seguir exatamente o formato do commit: `tipo(escopo): descrição clara`.
* **Pronto vs. Rascunho (`Draft`):**
  * Abra **Pronto para Revisão** apenas quando os testes locais (`python -m unittest tests/test_smoke.py`) estiverem passando.
  * Utilize **Draft PR** caso queira opinião antecipada sobre uma mudança em andamento.
* **Template Padrão para o Corpo do PR:**

```markdown
## Resumo da Mudança
<!-- Descreva objetivamente o que foi alterado e o motivo -->

## Tipo de Alteração
- [ ] feat (nova funcionalidade)
- [ ] fix (correção de bug)
- [ ] refactor (refatoração sem quebra de contrato)
- [ ] perf / test / docs / chore

## Impacto no Frontend / Banco de Dados
<!-- Alguma rota mudou? Algum payload ou status HTTP mudou? Se não, escreva "Sem impacto" -->

## Como foi Testado
- [ ] `python -m unittest tests/test_smoke.py` passando
- [ ] Verificado que não há chamadas de escrita/POST contra o banco em testes
```

---

## 5. Merge e Release

* **Estratégia de Merge:** Utilize **Merge Commit** (*Create a merge commit*) para preservar o histórico dos commits pequenos e rastreáveis. Evite *squash* ou *rebase* em branches compartilhadas.
* **Conflitos:** Devem ser resolvidos localmente na branch de trabalho (`git merge origin/develop`), nunca editando diretamente na `develop` ou `main`.
* **Regras para Agentes de IA:**
  * Agentes de IA nunca devem fazer *force push* nem *merge* direto na `main` ou `develop` sem revisão e aprovação explícita.
  * Nunca executar comandos `POST` contra o banco de produção durante validações de PR/testes.
