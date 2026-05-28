from sqlalchemy import Column, Integer, String, Float, Date, Time, ForeignKey, Text

from backend.database import Base


class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    id = Column(Integer, primary_key=True, index=True)

    projeto_id = Column(Integer, ForeignKey("projetos.id"), nullable=False)

    data_servico = Column(Date, nullable=False)

    km_saida = Column(Float, nullable=False)
    km_retorno = Column(Float, nullable=False)
    valor_deslocamento = Column(Float, nullable=False, default=0)

    quantidade_tecnicos = Column(Integer, nullable=False, default=1)
    
    valor_refeicao = Column(Float, nullable=False, default=0)

    hora_saida = Column(Time, nullable=False)
    hora_inicio = Column(Time, nullable=True)
    hora_termino = Column(Time, nullable=True)
    hora_retorno = Column(Time, nullable=False)

    acompanhado_por = Column(String, nullable=True)
    tipo_servico = Column(String, nullable=True)
    equipamento_tag_local = Column(String, nullable=True)

    diagnostico = Column(Text, nullable=True)
    descricao_servico = Column(Text, nullable=True)

    status = Column(String, nullable=False, default="Em andamento")