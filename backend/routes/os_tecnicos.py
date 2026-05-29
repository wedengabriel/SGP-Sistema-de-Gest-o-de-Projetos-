from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import SessionLocal
from backend.models.os_tecnico import OSTecnico
from backend.models.tecnico import Tecnico
from backend.models.ordem_servico import OrdemServico


router = APIRouter()


class OSTecnicoCreate(BaseModel):
    ordem_servico_id: int
    tecnico_id: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/os-tecnicos")
def criar_os_tecnico(os_tecnico: OSTecnicoCreate, db: Session = Depends(get_db)):
    ordem_servico = db.query(OrdemServico).filter(
        OrdemServico.id == os_tecnico.ordem_servico_id
    ).first()

    if ordem_servico is None:
        raise HTTPException(status_code=404, detail="OS não encontrada")

    tecnico = db.query(Tecnico).filter(
        Tecnico.id == os_tecnico.tecnico_id
    ).first()

    if tecnico is None:
        raise HTTPException(status_code=404, detail="Técnico não encontrado")

    data_hora_saida = ordem_servico.hora_saida
    data_hora_retorno = ordem_servico.hora_retorno

    diferenca = (
        data_hora_retorno.hour + data_hora_retorno.minute / 60
    ) - (
        data_hora_saida.hour + data_hora_saida.minute / 60
    )

    horas_trabalhadas = diferenca

    valor_total = horas_trabalhadas * tecnico.valor_hora

    novo_registro = OSTecnico(
        ordem_servico_id=os_tecnico.ordem_servico_id,
        tecnico_id=os_tecnico.tecnico_id,
        horas_trabalhadas=horas_trabalhadas,
        valor_total=valor_total
    )

    db.add(novo_registro)
    db.commit()
    db.refresh(novo_registro)

    return novo_registro


@router.get("/os-tecnicos")
def listar_os_tecnicos(db: Session = Depends(get_db)):
    return db.query(OSTecnico).all()