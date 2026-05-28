from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey

from backend.database import Base


class Material(Base):
    __tablename__ = "materiais"

    id = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id"), nullable=False)

    data_compra = Column(Date, nullable=False)
    item = Column(String, nullable=False)
    quantidade = Column(Float, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    valor_total = Column(Float, nullable=False)