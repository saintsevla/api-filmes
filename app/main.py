"""API de Filmes: CRUD com FastAPI + SQLite."""
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.database import get_connection, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="API de Filmes",
    description="Lista de filmes e avaliações com SQLite, hospedada no Azure App Service.",
    version="1.0.0",
    lifespan=lifespan,
)


class FilmeEntrada(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=150)
    genero: str = Field(..., min_length=1, max_length=50)
    nota: Optional[float] = Field(None, ge=0, le=10)
    assistido: bool = False


class Filme(FilmeEntrada):
    id: int
    criado_em: str


def _para_dict(linha) -> dict:
    item = dict(linha)
    item["assistido"] = bool(item["assistido"])
    return item


def _buscar(conn, item_id: int):
    linha = conn.execute("SELECT * FROM filmes WHERE id = ?", (item_id,)).fetchone()
    if linha is None:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    return _para_dict(linha)


@app.get("/health", tags=["Status"])
def health():
    """Usado para verificar se a API está no ar."""
    return {"status": "ok"}


@app.get("/filmes", response_model=list[Filme], tags=["Filmes"])
def listar_filmes():
    with get_connection() as conn:
        linhas = conn.execute("SELECT * FROM filmes ORDER BY id").fetchall()
    return [_para_dict(l) for l in linhas]


@app.get("/filmes/{item_id}", response_model=Filme, tags=["Filmes"])
def buscar_filme(item_id: int):
    with get_connection() as conn:
        return _buscar(conn, item_id)


@app.post("/filmes", response_model=Filme, status_code=201, tags=["Filmes"])
def criar_filme(dados: FilmeEntrada):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO filmes (titulo, genero, nota, assistido) VALUES (?, ?, ?, ?)",
            (dados.titulo, dados.genero, dados.nota, int(dados.assistido),),
        )
        return _buscar(conn, cursor.lastrowid)


@app.put("/filmes/{item_id}", response_model=Filme, tags=["Filmes"])
def atualizar_filme(item_id: int, dados: FilmeEntrada):
    with get_connection() as conn:
        _buscar(conn, item_id)
        conn.execute(
            "UPDATE filmes SET titulo = ?, genero = ?, nota = ?, assistido = ? WHERE id = ?",
            (dados.titulo, dados.genero, dados.nota, int(dados.assistido), item_id),
        )
        return _buscar(conn, item_id)


@app.delete("/filmes/{item_id}", status_code=204, tags=["Filmes"])
def remover_filme(item_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM filmes WHERE id = ?", (item_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
