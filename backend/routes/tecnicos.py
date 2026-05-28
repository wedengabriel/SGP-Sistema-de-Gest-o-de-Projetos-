from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import SessionLocal
from backend.models.tecnico import Tecnico


router = APIRouter()


class TecnicoCreate(BaseModel):
    nome: str
    valor_hora: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/tecnicos")
def criar_tecnico(tecnico: TecnicoCreate, db: Session = Depends(get_db)):
    novo_tecnico = Tecnico(
        nome=tecnico.nome,
        valor_hora=tecnico.valor_hora
    )

    db.add(novo_tecnico)
    db.commit()
    db.refresh(novo_tecnico)

    return novo_tecnico


@router.get("/tecnicos")
def listar_tecnicos(db: Session = Depends(get_db)):
    tecnicos = db.query(Tecnico).all()
    return tecnicos