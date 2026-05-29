from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, time

from backend.database import SessionLocal
from backend.models.ordem_servico import OrdemServico
from backend.models.os_tecnico import OSTecnico
from backend.models.tecnico import Tecnico

router = APIRouter()


class OrdemServicoCreate(BaseModel):
    projeto_id: int
    data_servico: date
    km_saida: float
    km_retorno: float
    hora_saida: time
    hora_inicio: time | None = None
    hora_termino: time | None = None
    hora_retorno: time
    acompanhado_por: str | None = None
    tipo_servico: str | None = None
    equipamento_tag_local: str | None = None
    diagnostico: str | None = None
    descricao_servico: str | None = None
    status: str = "Em andamento"
    quantidade_tecnicos: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/ordens-servico")
def criar_ordem_servico(os: OrdemServicoCreate, db: Session = Depends(get_db)):
    dados_os = os.model_dump()

    km_rodado = dados_os["km_retorno"] - dados_os["km_saida"]
    valor_deslocamento = km_rodado * 0.70

    hora_retorno = dados_os["hora_retorno"]

    valor_refeicao = 0

    if hora_retorno.hour >= 13:
        valor_refeicao = dados_os["quantidade_tecnicos"] * 75

    nova_os = OrdemServico(
        **dados_os,
        valor_deslocamento=valor_deslocamento,
        valor_refeicao=valor_refeicao
    )

    db.add(nova_os)
    db.commit()
    db.refresh(nova_os)

    return nova_os


@router.get("/ordens-servico")
def listar_ordens_servico(db: Session = Depends(get_db)):
    return db.query(OrdemServico).all()

@router.get("/ordens-servico/{os_id}/tecnicos")
def listar_tecnicos_os(
    os_id: int,
    db: Session = Depends(get_db)
):

    registros = db.query(OSTecnico).filter(
        OSTecnico.ordem_servico_id == os_id
    ).all()

    resultado = []

    for registro in registros:

        tecnico = db.query(Tecnico).filter(
            Tecnico.id == registro.tecnico_id
        ).first()

        resultado.append({
            "id": registro.id,
            "tecnico": tecnico.nome,
            "horas_trabalhadas": registro.horas_trabalhadas,
            "valor_total": registro.valor_total
        })

    return resultado