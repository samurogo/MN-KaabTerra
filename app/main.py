from fastapi import FastAPI
from app.routes import analytics, pasaporte

app = FastAPI(
    title="Kaab Terra Analytics API",
    description="API de minería de datos, clustering y trazabilidad para la cadena de valor del café.",
    version="2.0.0"
)

app.include_router(analytics.router)
app.include_router(pasaporte.router)


@app.get("/")
def root():
    return {
        "mensaje": "Bienvenido a la API de Kaab Terra",
        "documentacion": "/docs"
    }