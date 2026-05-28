from sqlalchemy import Column, Integer, String, Float

from backend.database import Base


class Tecnico(Base):
    __tablename__ = "tecnicos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    valor_hora = Column(Float, nullable=False)