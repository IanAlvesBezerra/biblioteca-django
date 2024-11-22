from django.test import TestCase
from django.utils.http import urlencode
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Colecao
from core import views
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class ColecaoTests(APITestCase):
    def create_user_and_set_token_credentials(self):
        user = User.objects.create_user(
            "user01", "user01@example.com", "user01P4ssw0rD"
        )
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token.key))

    def post_livro(self, titulo, autor, categoria, publicado_em):
        url = reverse(views.LivroList.name)
        print(url)
        data = {
            "titulo": titulo,
            "autor": autor,
            "categoria": categoria,
            "publicado_em": publicado_em,
        }
        response = self.client.post(url, data, format="json")
        return response
    
    def post_autor(self, nome):
        url = reverse(views.AutorList.name)
        print(url)
        data = {
            "nome": nome
        }
        response = self.client.post(url, data, format="json")
        return response
    
    def post_categoria(self, nome):
        url = reverse(views.CategoriaList.name)
        print(url)
        data = {
            "nome": nome
        }
        response = self.client.post(url, data, format="json")
        return response
    
    def post_colecao(self, nome, descricao, livros, colecionador):
        url = reverse(views.ColecaoList.name)
        print(url)
        data = {
            "nome": nome,
            "descricao": descricao,
            "livros": livros,
            "colecionador": colecionador,
        }
        response = self.client.post(url, data, format="json")
        return response
    
    def setUp(self):
        self.create_user_and_set_token_credentials()
    
    # Testa o método POST
    def test_post_colecao(self):
        autor = self.post_autor("autor teste")
        categoria = self.post_categoria("categoria teste")
        livros = self.post_livro("livro teste", autor.data['id'], categoria.data['id'], "2024-11-22")
        colecionador = User.objects.get(username="user01")
        
        response = self.post_colecao("Colecao 1", "Descricao teste", [livros.data['id']], colecionador.id)
        print("PK {0}".format(Colecao.objects.get().pk))
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_owner_can_update(self):
        autor = self.post_autor("autor teste")
        categoria = self.post_categoria("categoria teste")
        livro = self.post_livro("livro teste", autor.data['id'], categoria.data['id'], "2024-11-22")
        
        colecionador = User.objects.get(username="user01")
        response = self.post_colecao("Colecao 1", "Descricao teste", [livro.data['id']], colecionador.id)

        url_edit = reverse(views.ColecaoDetail.name, args=[response.data['id']])
        data_edit = {
            "nome": "Colecao Editada",
            "descricao": "Descricao Editada",
            "livros": [livro.data['id']],
            "colecionador": colecionador.id,
        }
        edit_response = self.client.patch(url_edit, data_edit, format="json")
        self.assertEqual(status.HTTP_200_OK, edit_response.status_code)
        self.assertEqual(edit_response.data['nome'], "Colecao Editada")

    def test_other_user_cant_update(self):
        autor = self.post_autor("autor teste")
        categoria = self.post_categoria("categoria teste")
        livro = self.post_livro("livro teste", autor.data['id'], categoria.data['id'], "2024-11-22")
        
        colecionador = User.objects.get(username="user01")
        response = self.post_colecao("Colecao 1", "Descricao teste", [livro.data['id']], colecionador.id)
        
        segundo_usuario = User.objects.create_user("user02", "user02@example.com", "user02P4ssw0rD")
        segundo_usuario_token = Token.objects.create(user=segundo_usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {segundo_usuario_token.key}")
        
        # Tentando editar a coleção como outro usuário
        url_edit = reverse(views.ColecaoDetail.name, args=[response.data['id']])
        data_edit = {
            "nome": "Colecao Editada por Outro",
            "descricao": "Descricao Editada por Outro",
            "livros": [livro.data['id']],
            "colecionador": colecionador.id,
        }
        edit_response = self.client.patch(url_edit, data_edit, format="json")
        self.assertEqual(status.HTTP_403_FORBIDDEN, edit_response.status_code)

    def test_owner_can_delete(self):
        autor = self.post_autor("autor teste")
        categoria = self.post_categoria("categoria teste")
        livro = self.post_livro("livro teste", autor.data['id'], categoria.data['id'], "2024-11-22")
        
        colecionador = User.objects.get(username="user01")
        response = self.post_colecao("Colecao 1", "Descricao teste", [livro.data['id']], colecionador.id)
        
        # Deletando a coleção como o colecionador
        url_delete = reverse(views.ColecaoDetail.name, args=[response.data['id']])
        delete_response = self.client.delete(url_delete)
        self.assertEqual(status.HTTP_204_NO_CONTENT, delete_response.status_code)
        self.assertEqual(Colecao.objects.filter(id=response.data['id']).count(), 0)

    def test_other_user_cant_delete(self):
        autor = self.post_autor("autor teste")
        categoria = self.post_categoria("categoria teste")
        livro = self.post_livro("livro teste", autor.data['id'], categoria.data['id'], "2024-11-22")
        
        colecionador = User.objects.get(username="user01")
        response = self.post_colecao("Colecao 1", "Descricao teste", [livro.data['id']], colecionador.id)
        
        segundo_usuario = User.objects.create_user("user02", "user02@example.com", "user02P4ssw0rD")
        segundo_usuario_token = Token.objects.create(user=segundo_usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {segundo_usuario_token.key}")
        
        # Tentando deletar a coleção como outro usuário
        url_delete = reverse(views.ColecaoDetail.name, args=[response.data['id']])
        delete_response = self.client.delete(url_delete)
        self.assertEqual(status.HTTP_403_FORBIDDEN, delete_response.status_code)
    
    def test_post_colecao_without_token(self):
        autor = self.post_autor("autor teste")
        categoria = self.post_categoria("categoria teste")
        livro = self.post_livro("livro teste", autor.data['id'], categoria.data['id'], "2024-11-22")
        
        colecionador = User.objects.get(username="user01")

        nome_colecao = "Colecao 1"
        descricao_colecao = "Descricao teste"
        
        self.client.credentials()
        
        # Tentando criar a coleção sem autenticação
        url = reverse(views.ColecaoList.name)
        data = {
            "nome": nome_colecao,
            "descricao": descricao_colecao,
            "livros": [livro.data['id']],
            "colecionador": colecionador.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_update_colecao_without_token(self):
        autor = self.post_autor("autor teste")
        categoria = self.post_categoria("categoria teste")
        livro = self.post_livro("livro teste", autor.data['id'], categoria.data['id'], "2024-11-22")       
        
        colecionador = User.objects.get(username="user01")
        response = self.post_colecao("Colecao 1", "Descricao teste", [livro.data['id']], colecionador.id)

        self.client.credentials()

        # Tentando atualizar a coleção sem autenticação
        url_edit = reverse(views.ColecaoDetail.name, args=[response.data['id']])
        data_edit = {
            "nome": "Colecao Editada",
            "descricao": "Descricao Editada",
            "livros": [livro.data['id']],
            "colecionador": colecionador.id,
        }
        response = self.client.put(url_edit, data_edit, format="json")
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_colecao_without_token(self):
        autor = self.post_autor("autor teste")
        categoria = self.post_categoria("categoria teste")
        livro = self.post_livro("livro teste", autor.data['id'], categoria.data['id'], "2024-11-22")       
        
        colecionador = User.objects.get(username="user01")
        response = self.post_colecao("Colecao 1", "Descricao teste", [livro.data['id']], colecionador.id)

        self.client.credentials()

        # Tentando deletar a coleção sem autenticação
        url_delete = reverse(views.ColecaoDetail.name, args=[response.data['id']])
        response = self.client.delete(url_delete)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_other_user_can_list(self):
        autor = self.post_autor("autor teste")
        categoria = self.post_categoria("categoria teste")
        livro = self.post_livro("livro teste", autor.data['id'], categoria.data['id'], "2024-11-22")       
        
        colecionador = User.objects.get(username="user01")
        
        self.post_colecao("Colecao 1", "Descricao teste", [livro.data['id']], colecionador.id)
        self.post_colecao("Colecao 2", "Outra descricao teste", [livro.data['id']], colecionador.id)

        segundo_usuario = User.objects.create_user("user02", "user02@example.com", "user02P4ssw0rD")
        segundo_usuario_token = Token.objects.create(user=segundo_usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {segundo_usuario_token.key}")
        
        # Tentando listar a coleção como outro usuário
        url = reverse(views.ColecaoList.name)
        response = self.client.get(url, format="json")
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(len(response.data) > 0, "Nenhuma coleção foi retornada.")
        self.assertIn("Colecao 1", [colecao['nome'] for colecao in response.data['results']])
        self.assertIn("Colecao 2", [colecao['nome'] for colecao in response.data['results']])

