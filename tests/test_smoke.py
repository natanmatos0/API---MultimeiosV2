import unittest
from unittest.mock import patch, MagicMock
from app import app

class SmokeTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_check_json(self):
        """Valida que a rota raiz / responde com JSON 200 OK sem HTML."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertEqual(data.get("status"), "online")
        self.assertIn("versao", data)

    @patch("src.routes.core.supabase")
    def test_total_livros_json(self, mock_sb):
        """Valida que /total responde com JSON sem HTML."""
        mock_exec = MagicMock()
        mock_exec.data = [{"numero_de_registro": "LIV-01", "titulo": "Livro 1"}]
        mock_sb.schema.return_value.table.return_value.select.return_value.limit.return_value.execute.return_value = mock_exec

        response = self.client.get("/total")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    @patch("src.routes.livros.supabase")
    def test_livro_inexistente_retorna_404(self, mock_sb):
        """Valida que consultar livro inexistente retorna 404 (e não 200)."""
        mock_exec = MagicMock()
        mock_exec.data = []
        mock_sb.schema.return_value.table.return_value.select.return_value.ilike.return_value.execute.return_value = mock_exec

        response = self.client.get("/livros/TITULO_INEXISTENTE")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIn("erro", data)

    @patch("src.routes.livros.supabase")
    def test_livro_existente_retorna_200(self, mock_sb):
        """Valida que consultar livro existente retorna 200 com lista de livros."""
        mock_exec = MagicMock()
        mock_exec.data = [{"numero_de_registro": "LIV-01", "titulo": "Dom Casmurro"}]
        mock_sb.schema.return_value.table.return_value.select.return_value.ilike.return_value.execute.return_value = mock_exec

        response = self.client.get("/livros/Dom")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_cadastro_livro_payload_nulo_retorna_400(self):
        """Valida que POST /livros/post sem body retorna 400 sem estourar AttributeError."""
        response = self.client.post("/livros/post", data="", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.is_json)

    def test_cadastro_livro_campos_faltantes_retorna_400(self):
        """Valida que POST /livros/post sem titulo/registro retorna 400."""
        response = self.client.post("/livros/post", json={"autor": "Autor Teste"})
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIn("erro", data)

    def test_criar_aluno_campos_obrigatorios(self):
        """Valida que POST /criar_aluno sem campos essenciais retorna 400."""
        response = self.client.post("/criar_aluno", json={"nome": "Apenas Nome"})
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIn("erro", data)

    @patch("src.routes.alunos.supabase")
    def test_criar_aluno_sucesso_retorna_201(self, mock_sb):
        """Valida criação de aluno com sucesso retornando 201 Created."""
        mock_exec = MagicMock()
        mock_exec.data = [{"id": "c1a9f1a2-2b3c-4d5e-8f90-123456789abc", "nome": "Maria", "curso": "Geral", "ano": 1}]
        mock_sb.schema.return_value.table.return_value.insert.return_value.execute.return_value = mock_exec

        response = self.client.post("/criar_aluno", json={"nome": "Maria", "curso": "Geral", "ano": 1})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertEqual(data.get("status"), "sucesso")

    def test_buscar_aluno_uuid_invalido_retorna_400(self):
        """Valida que passar ID não-UUID em /alunos/<id> retorna 400 (e não 500 do Postgres)."""
        response = self.client.get("/alunos/codigo-invalido-123")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIn("UUID", data.get("erro", ""))

    def test_alugar_uuid_invalido_retorna_400(self):
        """Valida que UUID inválido na rota de aluguel retorna 400 imediatamente."""
        response = self.client.post("/alunos/invalido/alugar/LIV-001")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.is_json)

    def test_renovar_uuid_invalido_retorna_400(self):
        """Valida que UUID inválido na rota de renovação retorna 400 imediatamente."""
        response = self.client.post("/alunos/invalido/renovar/LIV-001")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.is_json)

    @patch("src.routes.emprestimos.supabase")
    def test_renovar_sucesso_retorna_200(self, mock_sb):
        """Valida fluxo de renovação somando 7 dias e retornando 200."""
        # Mock busca emprestimo
        mock_emp = MagicMock()
        mock_emp.data = [{
            "id": "11111111-1111-1111-1111-111111111111",
            "aluno_id": "c1a9f1a2-2b3c-4d5e-8f90-123456789abc",
            "numero_de_registro": "LIV-01",
            "data_entrega_prevista": "2026-11-01",
            "status": "ativo"
        }]
        
        mock_update = MagicMock()
        mock_update.data = [{"id": "11111111-1111-1111-1111-111111111111", "data_entrega_prevista": "2026-11-08"}]

        # Configura as chamadas do mock do supabase
        table_mock = MagicMock()
        mock_sb.schema.return_value.table.return_value = table_mock
        table_mock.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_emp
        table_mock.update.return_value.eq.return_value.execute.return_value = mock_update

        response = self.client.post("/alunos/c1a9f1a2-2b3c-4d5e-8f90-123456789abc/renovar/LIV-01")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertEqual(data.get("status"), "sucesso")
        self.assertEqual(data.get("nova_data_entrega"), "2026-11-08")

    def test_devolver_uuid_invalido_retorna_400(self):
        """Valida que UUID inválido na rota de devolução retorna 400 imediatamente."""
        response = self.client.post("/alunos/invalido/devolver/LIV-001")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.is_json)

    def test_historico_uuid_invalido_retorna_400(self):
        """Valida que UUID inválido no histórico retorna 400 imediatamente."""
        response = self.client.get("/alunos/invalido/historico")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.is_json)

    def test_login_incorreto_retorna_401(self):
        """Valida que login incorreto retorna 401 Unauthorized."""
        response = self.client.post("/login", json={"user": "errado", "pass": "errado"})
        self.assertEqual(response.status_code, 401)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertFalse(data.get("success"))

if __name__ == "__main__":
    unittest.main()
