import os
from fpdf import FPDF
from fpdf.fonts import FontFace

class DocumentacaoPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 13)
        self.set_text_color(30, 58, 138)  # Azul Marinho
        self.cell(0, 6.5, 'API Multimeios V2 — Manual de Métodos e Endpoints Operacionais', new_x='LMARGIN', new_y='NEXT')
        
        self.set_font('Arial', '', 7.5)
        self.set_text_color(100, 116, 139) # Cinza Ardósia
        self.cell(0, 4.5, 'Base URL: https://api-multimeios.onrender.com | Local: http://localhost:5000 | Header: Content-Type: application/json; charset=utf-8', new_x='LMARGIN', new_y='NEXT')
        self.ln(1.5)

    def footer(self):
        self.set_y(-9)
        self.set_font('Arial', 'I', 7)
        self.set_text_color(148, 163, 184)
        self.cell(0, 6, f'Página {self.page_no()}/{{nb}} — Documentação Técnica Oficial API Multimeios V2 (Flask + Supabase)', align='C')

def gerar_pdf(caminho_saida='tabela_metodos_operacionais.pdf'):
    pdf = DocumentacaoPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_margins(left=10, top=10, right=10)

    # Carrega fontes Arial padrão do Windows com suporte a Unicode
    pdf.add_font('Arial', '', r'C:\Windows\Fonts\arial.ttf')
    pdf.add_font('Arial', 'B', r'C:\Windows\Fonts\arialbd.ttf')
    pdf.add_font('Arial', 'I', r'C:\Windows\Fonts\ariali.ttf')
    pdf.add_page()

    dados = [
        ('GET', '/', 'core.py', 'Nenhum', '200 OK', 'Health Check: Retorna o status online e versão da API em formato JSON.'),
        ('GET', '/total', 'core.py', '?page=1&per_page=20 (opcional)', '200 OK', 'Listagem Geral: Retorna todos os livros do acervo em JSON (com suporte a paginação).'),
        ('GET', '/livros', 'livros.py', '?page=1&per_page=20 (opcional)', '200 OK', 'Listar Livros: Retorna a lista paginada do acervo de livros da biblioteca.'),
        ('GET', '/livros/<livro_titulo>', 'livros.py', 'Na URL: prefixo do título', '200 OK / 404', 'Buscar por Título: Busca livros que se iniciem pelo título informado (ilike).'),
        ('POST', '/livros/post', 'livros.py', 'JSON: numero_de_registro, titulo, ...', '201 Created', 'Cadastrar Livro: Insere novo livro no acervo. Registro e título são obrigatórios.'),
        ('GET', '/livros/alugados', 'livros.py', '?page=1&per_page=20 (opcional)', '200 OK', 'Listar Alugados: Retorna apenas os livros com status alugado == sim.'),
        ('POST', '/criar_aluno', 'alunos.py', 'JSON: nome, curso, ano', '201 Created', 'Criar Aluno: Cadastra novo aluno no sistema e gera automaticamente seu UUID.'),
        ('POST', '/alunos', 'alunos.py', 'JSON: nome, curso, ano', '201 Created', 'Criar Aluno (Alias): Rota mantida para retrocompatibilidade no cadastro de alunos.'),
        ('GET', '/alunos', 'alunos.py', '?page=1&per_page=20 (opcional)', '200 OK', 'Listar Alunos: Retorna a lista completa de alunos cadastrados com paginação.'),
        ('GET', '/alunos/<aluno_id>', 'alunos.py', 'Na URL: aluno_id (UUID)', '200 OK / 400', 'Buscar Aluno: Retorna os dados cadastrais do aluno. Valida formato UUID.'),
        ('POST', '/alunos/<aluno_id>/alugar/<numero_registro>', 'emprestimos.py', 'Na URL: aluno_id, registro', '201 Created', 'Alugar Livro: Prazo de 14 dias (fuso de Brasília). Bloqueio atômico e rollback.'),
        ('POST', '/alunos/<aluno_id>/renovar/<numero_registro>', 'emprestimos.py', 'Na URL: aluno_id, registro', '200 OK / 404', 'Renovar Empréstimo: Prorroga o prazo em +7 dias, sincronizando livros e emprestimos.'),
        ('POST', '/alunos/<aluno_id>/devolver/<numero_registro>', 'emprestimos.py', 'Na URL: aluno_id, registro', '200 OK / 404', 'Devolver Livro: Registra data de devolução real e libera o exemplar no acervo.'),
        ('GET', '/alunos/<aluno_id>/historico', 'emprestimos.py', 'Na URL: aluno_id (UUID)', '200 OK / 400', 'Histórico do Aluno: Consulta relacional única sem N+1 com dados do livro.'),
        ('POST', '/login', 'auth.py', 'JSON: user, pass', '200 OK / 401', 'Login Administrativo: Validação de credenciais contra LISTA_USUARIOS.')
    ]

    col_widths = (16, 68, 25, 48, 25, 95)
    headers = ('Método', 'Endpoint / Rota', 'Módulo', 'Parâmetros / Body', 'Status', 'Descrição da Operação')

    pdf.set_font('Arial', '', 7.8)

    with pdf.table(col_widths=col_widths, line_height=4.2, padding=1.6) as table:
        header_row = table.row()
        for col in headers:
            header_row.cell(col, style=FontFace(emphasis='BOLD', fill_color=(30, 58, 138), color=(255, 255, 255)))

        for i, row in enumerate(dados):
            table_row = table.row()
            bg_color = (255, 255, 255) if i % 2 == 0 else (248, 250, 252)
            metodo_color = (22, 101, 52) if row[0] == 'GET' else (30, 64, 175)

            table_row.cell(row[0], style=FontFace(emphasis='BOLD', fill_color=bg_color, color=metodo_color))
            table_row.cell(row[1], style=FontFace(emphasis='BOLD', fill_color=bg_color, color=(15, 23, 42)))
            table_row.cell(row[2], style=FontFace(fill_color=bg_color, color=(71, 85, 105)))
            table_row.cell(row[3], style=FontFace(fill_color=bg_color, color=(51, 65, 85)))
            table_row.cell(row[4], style=FontFace(emphasis='BOLD', fill_color=bg_color, color=(30, 41, 59)))
            table_row.cell(row[5], style=FontFace(fill_color=bg_color, color=(51, 65, 85)))

    pdf.output(caminho_saida)
    print(f'PDF gerado com sucesso em: {caminho_saida} (Tamanho: {os.path.getsize(caminho_saida)} bytes)')

if __name__ == '__main__':
    gerar_pdf()
