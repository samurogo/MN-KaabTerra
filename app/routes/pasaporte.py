import io
import qrcode
from fastapi import APIRouter, HTTPException, Response
from app.models import PasaporteDigital, ProductorInfo, ManejoAgronomico

router = APIRouter(prefix="/api/v1/pasaporte", tags=["Trazabilidad y Pasaporte Digital"])

BASE_WEB_URL = "https://kaabterra.org/pasaporte"

# Registro simulado en memoria
BASE_DATOS_LOTES = {
    "LOT-2026-CHIS-001": PasaporteDigital(
        lote_id="LOT-2026-CHIS-001",
        productor=ProductorInfo(
            nombre="Don Mateo Gómez",
            finca="Finca El Paraíso",
            ubicacion="Jaltenango, Chiapas, México",
            altitud_msnm=1450.0
        ),
        agronomia=ManejoAgronomico(
            variedad="Typica & Bourbon",
            proceso_beneficio="Honey Amarillo",
            puntaje_sca=85.5,
            certificaciones=["Comercio Justo", "Orgánico"]
        ),
        cluster_categoria="Café Especial / Premium",
        huella_carbono_estimada_kg=1.2,
        fecha_cosecha="2026-02-15"
    )
}


@router.get("/{lote_id}", response_model=PasaporteDigital)
def obtener_pasaporte(lote_id: str):
    if lote_id not in BASE_DATOS_LOTES:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return BASE_DATOS_LOTES[lote_id]


@router.get("/{lote_id}/qr")
def generar_qr_pasaporte(lote_id: str):
    if lote_id not in BASE_DATOS_LOTES:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    url_destino = f"{BASE_WEB_URL}/{lote_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url_destino)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#2E5A44", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return Response(content=buffer.getvalue(), media_type="image/png")