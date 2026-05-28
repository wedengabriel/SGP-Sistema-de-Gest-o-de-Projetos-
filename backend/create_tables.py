from backend.database import engine, Base

from backend.models.tecnico import Tecnico
from backend.models.projeto import Projeto
from backend.models.ordem_servico import OrdemServico
from backend.models.os_tecnico import OSTecnico
from backend.models.material import Material

print("Criando tabelas...")

Base.metadata.create_all(bind=engine)

print("Tabelas criadas com sucesso!")