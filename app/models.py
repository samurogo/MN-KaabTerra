from pydantic import BaseModel, Field


# ==========================================
# 1. MODELO K-MEANS (Perfil Productivo)
# ==========================================
class LoteInput(BaseModel):
    altitud: float = Field(..., example=1450.0, description="Altitud en msnm")
    humedad: float = Field(..., example=64.0, description="Humedad relativa %")
    temperatura: float = Field(..., example=18.5, description="Temperatura promedio °C")
    rendimiento: float = Field(..., example=12.0, description="Rendimiento estimado kg/ha")
    costo_kilo: float = Field(..., example=3.2, description="Costo de producción por kg en USD")
    puntaje_sca: float = Field(..., example=84.5, description="Puntaje de catación SCA")


# ==========================================
# 2. MODELO CLASIFICADOR (Estado de Salud)
# ==========================================
class EstadoLoteInput(BaseModel):
    humedad_suelo: float = Field(..., example=45.0, description="Humedad del suelo %")
    temperatura_suelo: float = Field(..., example=22.5, description="Temperatura del suelo °C")
    severidad_plaga: int = Field(..., ge=0, le=3, example=1, description="0: Ninguna, 1: Leve, 2: Moderada, 3: Severa")
    severidad_enfermedad: int = Field(..., ge=0, le=3, example=0, description="0: Ninguna, 1: Leve, 2: Moderada, 3: Severa")
    dias_ultima_fertilizacion: int = Field(..., example=45, description="Días transcurridos desde la última fertilización")
    dias_ultima_poda: int = Field(..., example=120, description="Días transcurridos desde la última poda")
    rendimiento_actual: float = Field(..., example=11.5, description="Rendimiento actual medido kg/ha")


# ==========================================
# 3. MODELO REGRESOR (Estimación de Cosecha)
# ==========================================
class EstimacionProduccionInput(BaseModel):
    rendimiento_historico_q_ha: float = Field(..., example=11.5, description="Rendimiento de cosechas anteriores (quintales/ha)")
    area_hectareas: float = Field(..., example=2.0, description="Área total productiva del lote en hectáreas")
    edad_cultivo_anios: int = Field(..., example=6, description="Edad promedio de las plantas en años")
    densidad_plantas_ha: int = Field(..., example=4000, description="Número de plantas por hectárea")
    humedad_promedio: float = Field(..., example=64.0, description="Humedad relativa promedio %")
    temperatura_promedio: float = Field(..., example=19.0, description="Temperatura promedio °C")
    fertilizaciones_realizadas_anio: int = Field(..., example=3, description="Número de aplicaciones de fertilizante en el último ciclo")


# ==========================================
# 4. PASAPORTE DIGITAL
# ==========================================
class ProductorInfo(BaseModel):
    nombre: str
    finca: str
    ubicacion: str
    altitud_msnm: float


class ManejoAgronomico(BaseModel):
    variedad: str
    proceso_beneficio: str
    puntaje_sca: float
    certificaciones: list[str]


class PasaporteDigital(BaseModel):
    lote_id: str
    productor: ProductorInfo
    agronomia: ManejoAgronomico
    cluster_categoria: str
    huella_carbono_estimada_kg: float
    fecha_cosecha: str