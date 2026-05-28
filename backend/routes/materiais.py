from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from backend.database import SessionLocal
from backend.models.material import Material
from backend.models.projeto import Projeto


router = APIRouter()


class MaterialCreate(BaseModel):
    projeto_id: int
    data_compra: date
    item: str
    quantidade: float
    valor_unitario: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/materiais")
def criar_material(material: MaterialCreate, db: Session = Depends(get_db)):
    projeto = db.query(Projeto).filter(Projeto.id == material.projeto_id).first()

    if projeto is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    valor_total = material.quantidade * material.valor_unitario

    novo_material = Material(
        projeto_id=material.projeto_id,
        data_compra=material.data_compra,
        item=material.item,
        quantidade=material.quantidade,
        valor_unitario=material.valor_unitario,
        valor_total=valor_total
    )

    db.add(novo_material)
    db.commit()
    db.refresh(novo_material)

    return novo_material


@router.get("/materiais")
def listar_materiais(db: Session = Depends(get_db)):
    return db.query(Material).all()