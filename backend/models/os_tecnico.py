from sqlalchemy import Column, Integer, Float, ForeignKey

from backend.database import Base


class OSTecnico(Base):
    __tablename__ = "os_tecnicos"

    id = Column(Integer, primary_key=True, index=True)

    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id"), nullable=False)

    tecnico_id = Column(Integer, ForeignKey("tecnicos.id"), nullable=False)

    horas_trabalhadas = Column(Float, nullable=False)

    valor_total = Column(Float, nullable=False)