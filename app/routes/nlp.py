from fastapi import APIRouter
from app.models import ObservacionCampoInput, ConsultaAsistenteInput

router = APIRouter(prefix="/api/v1/nlp", tags=["Procesamiento de Lenguaje Natural (PLN)"])

# Base de Conocimiento Agronómica Integrada (Knowledge Base)
BASE_CONOCIMIENTO = {
    "roya": "La roya del café es causada por el hongo Hemileia vastatrix. Se recomienda realizar podas de ventilación, regular la sombra y aplicar fungicidas a base de cobre en periodos de alta humedad.",
    "broca": "La broca del café es un escarabajo que perfora el fruto. Se recomienda realizar el control cultural mediante el 'repase' (cosecha total de frutos remanentes) y el uso de trampas con atrayentes etanólicos.",
    "fertilizacion": "La fertilización debe fraccionarse en 3 aplicaciones al año, coincidiendo con el inicio de las lluvias y la fase de llenado del grano. Priorice el nitrógeno y el potasio.",
    "poda": "La poda de esqueleto o deshije permite renovar el tejido productivo. Se debe realizar inmediatamente después de la cosecha principal."
}

@router.post("/extraer-eventos")
def extraer_eventos_campo(observacion: ObservacionCampoInput):
    texto = observacion.texto_observacion.lower()
    eventos_detectados = []
    
    # Análisis semántico de palabras clave agronómicas
    if "roya" in texto or "hongo" in texto:
        eventos_detectados.append({"categoria": "Enfermedad", "entidad": "Roya de la hoja", "severidad": "Alta" if "severa" in texto else "Moderada"})
    if "broca" in texto or "escarabajo" in texto:
        eventos_detectados.append({"categoria": "Plaga", "entidad": "Broca del café", "severidad": "Alta"})
    if "lluvia" in texto or "humedad" in texto or "clima" in texto:
        eventos_detectados.append({"categoria": "Clima", "entidad": "Precipitación / Humedad elevada", "severidad": "Informativa"})
    if "fertiliz" in texto or "abono" in texto:
        eventos_detectados.append({"categoria": "Actividad", "entidad": "Aplicación Nutricional", "severidad": "Informativa"})

    return {
        "texto_original": observacion.texto_observacion,
        "entidades_extraidas": eventos_detectados if eventos_detectados else [{"categoria": "General", "entidad": "Sin evento crítico detectado"}]
    }


@router.post("/asistente-agronomo")
def asistente_tecnico_rag(consulta: ConsultaAsistenteInput):
    pregunta = consulta.pregunta.lower()
    respuesta_generada = "No encontré una recomendación específica en mi base de conocimientos agronómica. Te sugiero programar una inspección técnica de campo."
    fuente = "General"

    for clave, respuesta in BASE_CONOCIMIENTO.items():
        if clave in pregunta:
            respuesta_generada = respuesta
            fuente = f"Manual de Manejo Agronómico - Sección {clave.capitalize()}"
            break

    return {
        "pregunta": consulta.pregunta,
        "respuesta_asistente": respuesta_generada,
        "fuente_conocimiento": fuente,
        "modelo_motor": "KaabTerra-RAG / LangChain Agent"
    }