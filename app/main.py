from fastapi import FastAPI
from app.routes import analytics, pasaporte, nlp

app = FastAPI(
    title="Kaab Terra API",
    description="Plataforma digital para la gestión, analítica predictiva y trazabilidad del café.",
    version="2.0.0"
)

# Incluir Routers
app.include_router(analytics.router)
app.include_router(pasaporte.router)
app.include_router(nlp.router)

@app.get("/")
def read_root():
    return {
        "sistema": "Kaab Terra API",
        "version": "2.0.0",
        "estado": "Operativo",
        "modulos": [
            "Analítica y ML (Clustering, Clasificación, Regresión, Isolation Forest)",
            "Trazabilidad (Pasaporte Digital QR)",
            "Procesamiento de Lenguaje Natural (spaCy / RAG Asistente)"
        ]
    }