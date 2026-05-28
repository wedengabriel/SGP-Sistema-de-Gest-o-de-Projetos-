from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from backend.database import SessionLocal
from backend.models.projeto import Projeto
from backend.models.ordem_servico import OrdemServico
from backend.models.os_tecnico import OSTecnico
from backend.models.material import Material
from backend.models.ordem_servico import OrdemServico

router = APIRouter()


class ProjetoCreate(BaseModel):
    numero_projeto: str
    cliente: str
    cidade: str
    uf: str
    unidade: str | None = None
    valor_cobrado: float
    aliquota_municipal: float
    status: str
    data_inicio: date | None = None
    data_fim: date | None = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/projetos")
def criar_projeto(projeto: ProjetoCreate, db: Session = Depends(get_db)):
    
    novo_projeto = Projeto(
        numero_projeto=projeto.numero_projeto,
        cliente=projeto.cliente,
        cidade=projeto.cidade,
        uf=projeto.uf,
        unidade=projeto.unidade,
        valor_cobrado=projeto.valor_cobrado,
        aliquota_municipal=projeto.aliquota_municipal,
        status=projeto.status,
        data_inicio=projeto.data_inicio,
        data_fim=projeto.data_fim
    )

    db.add(novo_projeto)
    db.commit()
    db.refresh(novo_projeto)

    return novo_projeto


@router.get("/projetos")
def listar_projetos(db: Session = Depends(get_db)):
    projetos = db.query(Projeto).all()
    return projetos

@router.get("/projetos/{projeto_id}/custos")
def custos_do_projeto(projeto_id: int, db: Session = Depends(get_db)):
    projeto = db.query(Projeto).filter(Projeto.id == projeto_id).first()

    if projeto is None:
        return {"erro": "Projeto não encontrado"}

    ordens = db.query(OrdemServico).filter(
        OrdemServico.projeto_id == projeto_id
    ).all()

    ids_ordens = [os.id for os in ordens]

    custo_deslocamento = sum(os.valor_deslocamento for os in ordens)
    custo_refeicao = sum(os.valor_refeicao for os in ordens)

    custo_mao_obra = 0

    if ids_ordens:
        registros_tecnicos = db.query(OSTecnico).filter(
            OSTecnico.ordem_servico_id.in_(ids_ordens)
        ).all()

        custo_mao_obra = sum(registro.valor_total for registro in registros_tecnicos)

    materiais = db.query(Material).filter(
        Material.projeto_id == projeto_id
    ).all()

    custo_materiais = sum(material.valor_total for material in materiais)

    custo_total = custo_mao_obra + custo_deslocamento + custo_refeicao + custo_materiais

    imposto_municipal = projeto.valor_cobrado * (projeto.aliquota_municipal / 100)
    imposto_federal = projeto.valor_cobrado * 0.11
    imposto_total = imposto_municipal + imposto_federal

    recebimento_liquido = projeto.valor_cobrado - imposto_total

    lucro_reais = recebimento_liquido - custo_total

    if recebimento_liquido > 0:
        lucro_percentual = (lucro_reais / recebimento_liquido) * 100
    else:
        lucro_percentual = 0

    return {
        "projeto_id": projeto.id,
        "numero_projeto": projeto.numero_projeto,
        "cliente": projeto.cliente,
        "valor_cobrado": projeto.valor_cobrado,
        "imposto_municipal": imposto_municipal,
        "imposto_federal": imposto_federal,
        "imposto_total": imposto_total,
        "recebimento_liquido": recebimento_liquido,
        "custo_mao_obra": custo_mao_obra,
        "custo_deslocamento": custo_deslocamento,
        "custo_refeicao": custo_refeicao,
        "custo_materiais": custo_materiais,
        "custo_total": custo_total,
        "lucro_reais": lucro_reais,
        "lucro_percentual": lucro_percentual
    }

@router.get("/projetos/{projeto_id}/ordens-servico")
def listar_os_projeto(
    projeto_id: int,
    db: Session = Depends(get_db)
):

    ordens = db.query(OrdemServico).filter(
        OrdemServico.projeto_id == projeto_id
    ).all()

    return ordens