"""Testes automatizados da API (rodar com: pytest)."""
import os
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "teste.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

EXEMPLO = {'titulo': 'Cidade de Deus', 'genero': 'Drama', 'nota': 9.5, 'assistido': True}
ATUALIZADO = {'titulo': 'Cidade de Deus', 'genero': 'Drama', 'nota': 9.5, 'assistido': False}
INVALIDO = {'titulo': 'X', 'genero': 'Y', 'nota': 15}


def test_fluxo_completo():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}

        criado = client.post("/filmes", json=EXEMPLO)
        assert criado.status_code == 201
        item_id = criado.json()["id"]

        assert len(client.get("/filmes").json()) == 1

        atualizado = client.put(f"/filmes/{item_id}", json=ATUALIZADO)
        assert atualizado.status_code == 200
        assert atualizado.json()["assistido"] is False

        assert client.delete(f"/filmes/{item_id}").status_code == 204
        assert client.get(f"/filmes/{item_id}").status_code == 404


def test_validacao():
    with TestClient(app) as client:
        assert client.post("/filmes", json=INVALIDO).status_code == 422
