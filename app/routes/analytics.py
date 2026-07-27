import os
import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from app.models import (
    LoteInput, 
    EstadoLoteInput, 
    EstimacionProduccionInput, 
    AnomaliaCostosInput
)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analítica y ML"])

# -------------------------------------------------------------
# RUTAS A LOS MODELOS BINARIOS GUARDADOS
# -------------------------------------------------------------
KMEANS_PATH = os.path.join("models_saved", "pipeline_kaab_terra_clustering.joblib")
CLASIFICADOR_PATH = os.path.join("models_saved", "pipeline_clasificador_estado.joblib")
REGRESION_PATH = os.path.join("models_saved", "pipeline_regresion_produccion.joblib")
ANOMALIAS_PATH = os.path.join("models_saved", "model_isolation_forest.joblib")

# Carga dinámica de K-Means
try:
    kmeans_pipeline = joblib.load(KMEANS_PATH)
except Exception:
    kmeans_pipeline = None

# Carga dinámica del Clasificador
try:
    clasificador_pipeline = joblib.load(CLASIFICADOR_PATH)
except Exception:
    clasificador_pipeline = None

# Carga dinámica del Regresor
try:
    regresion_pipeline = joblib.load(REGRESION_PATH)
except Exception:
    regresion_pipeline = None

# Carga dinámica de Isolation Forest (Anomalías)
try:
    anomalias_model = joblib.load(ANOMALIAS_PATH)
except Exception:
    anomalias_model = None


# -------------------------------------------------------------
# DICCIONARIOS DE INTERPRETABILIDAD Y DIAGNÓSTICO
# -------------------------------------------------------------
PERFILES_KMEANS = {
    0: {
        "categoria": "Café Especial / Premium",
        "estrategia": "Venta directa en Marketplace con Pasaporte QR.",
        "riesgo": "Bajo"
    },
    1: {
        "categoria": "Producción Masiva / Alta Eficiencia",
        "estrategia": "Consolidación en cooperativas por volumen.",
        "riesgo": "Bajo"
    },
    2: {
        "categoria": "Lote Crítico / Estrés Agronómico",
        "estrategia": "Requiere asistencia técnica preventiva.",
        "riesgo": "Alto"
    }
}

DIAGNOSTICOS_ESTADO = {
    "SALUDABLE": {
        "icono": "🟢",
        "estado": "SALUDABLE",
        "descripcion": "Condiciones adecuadas y sin problemas importantes detectados.",
        "accion": "Mantener el plan nutricional y esquema de monitoreo actual."
    },
    "ATENCION": {
        "icono": "🟡",
        "estado": "ATENCIÓN",
        "descripcion": "Existen factores de riesgo o rezagos agronómicos que requieren seguimiento.",
        "accion": "Programar inspección focalizada en fertilización o control preventivo de plagas."
    },
    "RIESGO": {
        "icono": "🔴",
        "estado": "RIESGO",
        "descripcion": "Existen problemas importantes detectados que requieren intervención inmediata.",
        "accion": "Emitir alerta prioritaria a la cooperativa y al técnico asignado para visita de campo."
    }
}


# -------------------------------------------------------------
# ENDPOINT 1: PERFIL PRODUCTIVO (Clustering K-Means)
# -------------------------------------------------------------
@router.post("/clasificar-lote")
def clasificar_lote(lote: LoteInput):
    if not kmeans_pipeline:
        raise HTTPException(
            status_code=500,
            detail="El modelo K-Means no está cargado. Asegúrate de haber ejecutado su notebook."
        )

    input_df = pd.DataFrame([lote.model_dump()])
    cluster_id = int(kmeans_pipeline.predict(input_df)[0])

    return {
        "lote": lote.model_dump(),
        "cluster_id": cluster_id,
        "diagnostico": PERFILES_KMEANS.get(cluster_id, {})
    }


# -------------------------------------------------------------
# ENDPOINT 2: ESTADO DEL LOTE (Clasificador Supervisado)
# -------------------------------------------------------------
@router.post("/evaluar-estado")
def evaluar_estado_lote(datos_evaluacion: EstadoLoteInput):
    if not clasificador_pipeline:
        raise HTTPException(
            status_code=500,
            detail="El modelo Clasificador de Estado no está cargado."
        )

    input_df = pd.DataFrame([datos_evaluacion.model_dump()])
    prediccion = clasificador_pipeline.predict(input_df)[0]
    probabilidades = clasificador_pipeline.predict_proba(input_df)[0]
    clases = list(clasificador_pipeline.classes_)
    
    confianza = round(float(max(probabilidades)) * 100, 2)

    return {
        "mediciones": datos_evaluacion.model_dump(),
        "evaluacion_modelo": DIAGNOSTICOS_ESTADO.get(prediccion, {}),
        "confianza_prediccion": f"{confianza}%",
        "distribucion_probabilidades": {clases[i]: round(float(probabilidades[i]), 4) for i in range(len(clases))}
    }


# -------------------------------------------------------------
# ENDPOINT 3: ESTIMACIÓN DE COSECHA (Regresión Supervisada)
# -------------------------------------------------------------
@router.post("/estimar-produccion")
def estimar_produccion_cosecha(datos_lote: EstimacionProduccionInput):
    if not regresion_pipeline:
        raise HTTPException(
            status_code=500,
            detail="El modelo de Regresión de Producción no está cargado. Ejecuta 'entrenamiento_regresion_produccion.ipynb'."
        )

    input_df = pd.DataFrame([datos_lote.model_dump()])
    
    # Inferencia del rendimiento por hectárea
    rendimiento_est = float(regresion_pipeline.predict(input_df)[0])
    rendimiento_est = round(rendimiento_est, 2)
    
    # Cálculo derivado: Producción total en quintales = Rendimiento * Área
    produccion_total_quintales = round(rendimiento_est * datos_lote.area_hectareas, 2)

    return {
        "parametros_entrada": datos_lote.model_dump(),
        "estimacion_cosecha": {
            "rendimiento_estimado_q_ha": rendimiento_est,
            "produccion_total_estimada_quintales": produccion_total_quintales,
            "unidad": "Quintales (q = 100 lb / 46 kg aprox)",
            "nota": "Estimación basada en el historial del lote, curva de edad del cultivo e insumos aplicados."
        }
    }


# -------------------------------------------------------------
# ENDPOINT 4: DETECCIÓN DE ANOMALÍAS (Isolation Forest)
# -------------------------------------------------------------
@router.post("/detectar-anomalias-costos")
def detectar_anomalias_costos(datos_costos: AnomaliaCostosInput):
    if not anomalias_model:
        raise HTTPException(
            status_code=500,
            detail="El modelo Isolation Forest no está cargado. Ejecuta 'entrenamiento_anomalias_isolation_forest.ipynb'."
        )

    input_df = pd.DataFrame([datos_costos.model_dump()])
    
    # IsolationForest devuelve -1 para datos anómalos y 1 para normales
    prediccion = int(anomalias_model.predict(input_df)[0])
    es_anomalo = (prediccion == -1)

    diagnostico = (
        "⚠️ ALERTA: Se detectó una variación atípica e inusual en los costos/rendimiento de este lote." 
        if es_anomalo 
        else "🟢 Comportamiento dentro de los parámetros esperados de costo y rendimiento."
    )

    accion = (
        "Revisar posibles sobrecostos en mano de obra o fuga de insumos frente al rendimiento reportado."
        if es_anomalo
        else "Mantener la gestión de costos sin ajustes urgentes."
    )

    return {
        "datos_evaluados": datos_costos.model_dump(),
        "resultado_analisis": {
            "es_anomalo": es_anomalo,
            "diagnostico": diagnostico,
            "accion_sugerida": accion,
            "algoritmo": "Isolation Forest (Detección No Supervisada de Anomalías)"
        }
    }