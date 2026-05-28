from sqlalchemy import Column, Integer, String, Float, Date

from backend.database import Base


class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(Integer, primary_key=True, index=True)
    numero_projeto = Column(String, unique=True, nullable=False, index=True)
    cliente = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    uf = Column(String, nullable=False)
    unidade = Column(String, nullable=True)
    valor_cobrado = Column(Float, nullable=False)
    aliquota_municipal = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="Em andamento")
    data_inicio = Column(Date, nullable=True)
    data_fim = Column(Date, nullable=True)