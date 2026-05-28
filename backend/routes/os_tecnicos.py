from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import SessionLocal
from backend.models.os_tecnico import OSTecnico
from backend.models.tecnico import Tecnico


router = APIRouter()


class OSTecnicoCreate(BaseModel):
    ordem_servico_id: int
    tecnico_id: int
    horas_trabalhadas: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/os-tecnicos")
def criar_os_tecnico(os_tecnico: OSTecnicoCreate, db: Session = Depends(get_db)):
    tecnico = db.query(Tecnico).filter(Tecnico.id == os_tecnico.tecnico_id).first()

    if tecnico is None:
        raise HTTPException(status_code=404, detail="Técnico não encontrado")

    valor_total = os_tecnico.horas_trabalhadas * tecnico.valor_hora

    novo_registro = OSTecnico(
        ordem_servico_id=os_tecnico.ordem_servico_id,
        tecnico_id=os_tecnico.tecnico_id,
        horas_trabalhadas=os_tecnico.horas_trabalhadas,
        valor_total=valor_total
    )

    db.add(novo_registro)
    db.commit()
    db.refresh(novo_registro)

    return novo_registro


@router.get("/os-tecnicos")
def listar_os_tecnicos(db: Session = Depends(get_db)):
    return db.query(OSTecnico).all()