from fastapi import FastAPI

from backend.routes.tecnicos import router as tecnicos_router
from backend.routes.projetos import router as projetos_router
from backend.routes.ordens_servico import router as ordens_servico_router
from backend.routes.os_tecnicos import router as os_tecnicos_router
from backend.routes.materiais import router as materiais_router

app = FastAPI(
    title="SGPO API",
    description="Sistema de Gestão de Projetos",
    version="1.0.0"
)


app.include_router(tecnicos_router)
app.include_router(projetos_router)
app.include_router(ordens_servico_router)
app.include_router(os_tecnicos_router)
app.include_router(materiais_router)

@app.get("/")
def home():
    return {"mensagem": "SGPO API funcionando!"}