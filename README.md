# Documentação da API — Multimeios V2

API RESTful modular para gestão de acervo bibliográfico, alunos e ciclo de vida de empréstimos, construída em Python (Flask) integrado ao Supabase (PostgreSQL).

Base URL: `https://api-multimeios.onrender.com`  
*(Em ambiente de desenvolvimento local: `http://localhost:5000`)*

---

## 1. Arquitetura do Projeto

O código-fonte segue a arquitetura orientada a **Flask Blueprints** sob o diretório `src/`:

```
C:\API - MultimeiosV2\
├── src/
│   ├── __init__.py          # Fábrica da aplicação (create_app), CORS e tratamento global de erros
│   ├── config.py            # Validação fail-fast das variáveis de ambiente (.env)
│   ├── database.py          # Cliente Supabase singleton com pool HTTP
│   ├── utils/
│   │   ├── validators.py    # Sanitização de UUID e extração defensiva de JSON
│   │   ├── dates.py         # Tratamento de datas com fuso de Brasília (America/Sao_Paulo)
│   │   ├── responses.py     # Respostas padronizadas de sucesso e erro semântico
│   │   └── pagination.py    # Paginação reutilizável (.range(start, end))
│   └── routes/
│       ├── core.py          # Health check (/) e listagem geral (/total) em JSON
│       ├── livros.py        # Acervo (/livros, /livros/post, /livros/alugados)
│       ├── alunos.py        # Cadastro (/criar_aluno) e listagem (/alunos)
│       ├── emprestimos.py   # Empréstimos (/alugar, /renovar, /devolver, /historico)
│       └── auth.py          # Autenticação (/login)
├── tests/
│   └── test_smoke.py        # Suíte automatizada de testes de fumaça e contratos HTTP
├── app.py                   # Ponto de entrada limpo (compatível com Gunicorn e Flask CLI)
├── requirements.txt         # Dependências do projeto (UTF-8 sem BOM)
└── README.md
```

---

## 2. Endpoints da API

Todas as requisições que enviam corpo devem utilizar o cabeçalho:  
`Content-Type: application/json; charset=utf-8`

### 2.1. Status e Health Check

#### Status do Serviço
- **Método:** `GET`
- **Endpoint:** `/`
- **Resposta:** `200 OK`
```json
{
  "status": "online",
  "servico": "API Multimeios",
  "versao": "2.0",
  "mensagem": "Serviço operacional e conectado."
}
```

#### Listagem Geral / Total
- **Método:** `GET`
- **Endpoint:** `/total` (suporta `?page=1&per_page=20`)
- **Resposta:** `200 OK` com a lista de livros do acervo.

---

### 2.2. Livros (Acervo)

#### Listar Livros
- **Método:** `GET`
- **Endpoint:** `/livros` (suporta `?page=1&per_page=20`)
- **Resposta:** `200 OK`

#### Buscar Livro por Título
- **Método:** `GET`
- **Endpoint:** `/livros/<livro_titulo>`
- **Resposta:** `200 OK` com os livros que coincidem com a busca, ou `404 Not Found` se não encontrar.

#### Cadastrar Livro
- **Método:** `POST`
- **Endpoint:** `/livros/post`
- **Body:**
```json
{
  "numero_de_registro": "LIV-100",
  "titulo": "O Cortiço",
  "autor": "Aluísio Azevedo",
  "genero": "Naturalismo",
  "categoria": "Literatura Brasileira",
  "localizacao": "Estante B, Prateleira 2",
  "observacoes": "Exemplar em bom estado"
}
```
- **Respostas:**
  - `201 Created`: Livro cadastrado com sucesso.
  - `400 Bad Request`: Falta de `numero_de_registro` ou `titulo`.
  - `409 Conflict`: Número de registro já existente no acervo.

#### Listar Livros Alugados
- **Método:** `GET`
- **Endpoint:** `/livros/alugados` (suporta `?page=1&per_page=20`)
- **Resposta:** `200 OK` com os exemplares atualmente alugados.

---

### 2.3. Alunos

#### Cadastrar Aluno
- **Método:** `POST`
- **Endpoint:** `/criar_aluno` *(alias: `/alunos`)*
- **Body:**
```json
{
  "nome": "Carlos Silva",
  "curso": "Informática",
  "ano": 2
}
```
- **Respostas:**
  - `201 Created`: Retorna os dados do aluno cadastrado com seu UUID.
  - `400 Bad Request`: Campos obrigatórios (`nome`, `curso`, `ano`) ausentes ou inválidos.

#### Listar Alunos
- **Método:** `GET`
- **Endpoint:** `/alunos` (suporta `?page=1&per_page=20`)
- **Resposta:** `200 OK`

#### Buscar Aluno por ID
- **Método:** `GET`
- **Endpoint:** `/alunos/<aluno_id>`
- **Respostas:**
  - `200 OK`: Dados do aluno.
  - `400 Bad Request`: `aluno_id` não é um UUID válido.
  - `404 Not Found`: Aluno inexistente.

---

### 2.4. Empréstimos, Renovações e Devoluções

#### Alugar Livro
- **Método:** `POST`
- **Endpoint:** `/alunos/<aluno_id>/alugar/<numero_registro>`
- **Descrição:** Registra o empréstimo com data de entrega calculada para 14 dias a partir de hoje (fuso de Brasília). Possui bloqueio atômico contra concorrência e rollback automático.
- **Respostas:**
  - `201 Created`: Empréstimo confirmado.
  - `400 Bad Request`: UUID do aluno inválido.
  - `404 Not Found`: Aluno ou livro não encontrado.
  - `409 Conflict`: Livro já se encontra alugado.

#### Renovar Livro
- **Método:** `POST`
- **Endpoint:** `/alunos/<aluno_id>/renovar/<numero_registro>`
- **Descrição:** Adiciona **7 dias** ao prazo de entrega do empréstimo ativo correspondente, sincronizando simultaneamente as tabelas `livros` e `emprestimos`.
- **Respostas:**
  - `200 OK`: Prazo prorrogado com sucesso.
  - `400 Bad Request`: UUID inválido.
  - `404 Not Found`: Nenhum empréstimo ativo para este aluno e livro.

#### Devolver Livro
- **Método:** `POST`
- **Endpoint:** `/alunos/<aluno_id>/devolver/<numero_registro>`
- **Descrição:** Finaliza o empréstimo ativo gravando a data de devolução real e desocupa o livro.
- **Respostas:**
  - `200 OK`: Livro devolvido.
  - `400 Bad Request`: UUID inválido.
  - `404 Not Found`: Nenhum empréstimo ativo encontrado.

#### Histórico de Empréstimos do Aluno
- **Método:** `GET`
- **Endpoint:** `/alunos/<aluno_id>/historico`
- **Descrição:** Consulta otimizada sem N+1 queries. Retorna todos os empréstimos (ativos e devolvidos) com os dados enriquecidos do livro (`titulo`, `autor`, `genero`, etc.).
- **Respostas:**
  - `200 OK`: Histórico completo.
  - `400 Bad Request`: UUID inválido.
  - `404 Not Found`: Aluno não encontrado.


## 3. Configuração de Ambiente (.env)

| Variável | Obrigatória | Descrição | Exemplo |
| :--- | :---: | :--- | :--- |
| `SUPABASE_URL` | Sim | URL da instância Supabase | `https://xxxx.supabase.co` |
| `SUPABASE_KEY` | Sim | Chave de serviço/anônima da Supabase | `eyJhbGciOi...` |
| `PORT` | Não | Porta do servidor web (padrão: 5000) | `5000` |
| `ALLOWED_ORIGINS` | Não | Origens autorizadas para CORS (separadas por vírgula) | `*` ou `https://meuapp.com` |
| `LISTA_USUARIOS` | Não | JSON com lista de credenciais de login | `[{"user":"admin","pass":"secret"}]` |
