from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from logica_negocio_predictiva import (
    plan_compras_mensual,
    presupuesto_anual_escenarios,
    distribucion_stock_decision,
    vehiculos_costo_y_reemplazo,
    simulador_ahorro_escenarios,
    calendario_compras_con_precios,
    estimacion_costos_futuros,
    tabla_resumen_ejecutivo,
    tabla_consumo_proyectado_detallado,
)
from kpi_anomalias import (
    kpi_consumo_promedio_vehiculo,
    kpi_consumo_por_area,
    kpi_eficiencia_km_litro,
    kpi_desviacion_consumo,
    kpi_vehiculos_consumo_anomalo,
    analisis_consumo_por_mes,
    analisis_consumo_fines_semana,
    analisis_areas_eficiencia,
    prediccion_consumo_proximo_mes,
    dashboard_kpi_completo,
)
import pandas as pd

router_predictivo = APIRouter(
    prefix="/predictiva",
    tags=["Predictiva"],
    responses={404: {"description": "Not found"}},
)

def df_to_json(data):
    # Convierte DataFrame a lista de dicts para JSON
    if isinstance(data, pd.DataFrame):
        return data.fillna("").to_dict(orient="records")
    return data

@router_predictivo.get("/plan-compras-mensual")
def api_plan_compras_mensual(tipo_combustible: str = Query("DIESEL", regex="^(DIESEL|GASOLINA)$")):
    """Recomendación práctica de compra mensual para el tipo de combustible elegido."""
    resultado = plan_compras_mensual(tipo_combustible.upper())
    if "error" in resultado:
        raise HTTPException(status_code=404, detail=resultado["error"])
    return resultado

@router_predictivo.get("/presupuesto-anual")
def api_presupuesto_anual(anio: Optional[int] = None):
    """Presupuesto anual con escenarios para gas/diesel."""
    resultado = presupuesto_anual_escenarios(anio)
    return resultado

@router_predictivo.get("/distribucion-stock")
def api_distribucion_stock(litros_disponibles: float = Query(..., gt=0), tipo_combustible: str = Query("DIESEL", regex="^(DIESEL|GASOLINA)$")):
    """Distribución de stock disponible por áreas para el combustible seleccionado."""
    resultado = distribucion_stock_decision(litros_disponibles, tipo_combustible.upper())
    if "error" in resultado:
        raise HTTPException(status_code=404, detail=resultado["error"])
    return resultado

@router_predictivo.get("/vehiculos-costo-reemplazo")
def api_vehiculos_costo_reemplazo(costo_vehiculo_nuevo_bs: float = 120000.0, meses_futuro: int = 6):
    """Análisis de vehículos costosos y alertas de reemplazo."""
    resultado = vehiculos_costo_y_reemplazo(costo_vehiculo_nuevo_bs, meses_futuro)
    if "error" in resultado:
        raise HTTPException(status_code=404, detail=resultado["error"])
    return resultado

@router_predictivo.get("/simulador-ahorro")
def api_simulador_ahorro(reducciones: str = "5,10,15,20", meses: int = 12):
    """
    Escenarios de ahorro. 
    Parámetro 'reducciones' es lista CSV de porcentajes, ej: 5,10,15,20
    """
    try:
        porcentajes = [float(p) for p in reducciones.split(",")]
    except:
        raise HTTPException(status_code=400, detail="Formato inválido para 'reducciones'. Debe ser CSV de números.")
    
    resultado = simulador_ahorro_escenarios(porcentajes, meses)
    return resultado

@router_predictivo.get("/calendario-compras")
def api_calendario_compras(meses: int = 6, inflacion_mensual: float = None):
    """
    Calendario de compras con proyección de precios.
    inflacion_mensual: decimal, ejemplo 0.0025 para 0.25% mensual, si no se suministra usa 3% anual/12
    """
    resultado = calendario_compras_con_precios(meses, inflacion_mensual)
    return resultado

@router_predictivo.get("/estimacion-costos-futuros")
def api_estimacion_costos_futuros(horizonte_meses: int = 12, escenario_precio: str = Query("moderado", regex="^(conservador|moderado|pesimista)$")):
    """Proyección de inversión combinando volumen y precios según escenario."""
    resultado = estimacion_costos_futuros(horizonte_meses, escenario_precio)
    return resultado

@router_predictivo.get("/resumen-ejecutivo")
def api_resumen_ejecutivo():
    """Resumen ejecutivo de indicadores clave y alertas prioritarias."""
    resultado = tabla_resumen_ejecutivo()
    return resultado

@router_predictivo.get("/tabla-consumo-proyectado")
def api_tabla_consumo_proyectado(meses_proyeccion: int = 12):
    """Tabla detallada mensual de consumo proyectado con escenarios optimista, base y pesimista."""
    resultado = tabla_consumo_proyectado_detallado(meses_proyeccion)
    return resultado


# ══════════════════════════════════════════════════════════════════════
#  NUEVOS ENDPOINTS: KPIs REALES Y DETECCIÓN DE ANOMALÍAS
# ══════════════════════════════════════════════════════════════════════

@router_predictivo.get("/kpi/consumo-por-vehiculo")
def api_kpi_consumo_vehiculo():
    """
    KPI 1: Consumo promedio por vehículo.
    RESPONDE: ¿Qué vehículos consumen más? ¿Cuáles son más eficientes?
    """
    try:
        resultado = kpi_consumo_promedio_vehiculo()
        if "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_predictivo.get("/kpi/consumo-por-area")
def api_kpi_consumo_area():
    """
    KPI 2: Consumo total y promedio por área de trabajo.
    RESPONDE: ¿Qué áreas gastan más? ¿Cuál es la más eficiente?
    """
    try:
        resultado = kpi_consumo_por_area()
        if "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_predictivo.get("/kpi/eficiencia-kmpl")
def api_kpi_eficiencia():
    """
    KPI 3: Rendimiento de combustible (km/litro).
    RESPONDE: ¿Qué vehículos son más eficientes? ¿Cuál es el promedio de la flota?
    NOTA: Requiere campos km_inicio y km_final en boletas
    """
    try:
        resultado = kpi_eficiencia_km_litro()
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_predictivo.get("/kpi/desviacion-consumo")
def api_kpi_desviacion(umbral_pct: float = Query(30, ge=5, le=100)):
    """
    KPI 4: Desviación entre consumo esperado histórico vs real actual.
    RESPONDE: ¿Dónde hay desviaciones significativas?
    PARAMETRO: umbral_pct (por defecto 30%) - porcentaje para diferenciar desviación normal de anómala
    """
    try:
        resultado = kpi_desviacion_consumo(umbral_pct)
        if "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_predictivo.get("/kpi/anomalias-consumo")
def api_kpi_anomalias():
    """
    KPI 5: Detección de vehículos con consumo anómalo.
    ALERTA: Detecta posibles fugas, mal uso, robo de combustible.
    MÉTODO: Compara consumo reciente vs histórico (desv. estándar + transacciones)
    """
    try:
        resultado = kpi_vehiculos_consumo_anomalo()
        if "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════
#  ANÁLISIS RESPONDEN PREGUNTAS DE NEGOCIO ESPECÍFICAS
# ══════════════════════════════════════════════════════════════════════

@router_predictivo.get("/analisis/consumo-por-mes")
def api_analisis_meses():
    """
    PREGUNTA: ¿El consumo sube en ciertos meses?
    RESPONDE: Identifica meses pico, bajos, tendencias estacionales
    """
    try:
        resultado = analisis_consumo_por_mes()
        if "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_predictivo.get("/analisis/consumo-fines-semana")
def api_analisis_fines_semana():
    """
    PREGUNTA: ¿Qué unidades gastan más en fines de semana?
    RESPONDE: Comparativa consumo día de semana vs fin de semana por vehículo
    """
    try:
        resultado = analisis_consumo_fines_semana()
        if "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_predictivo.get("/analisis/areas-eficiencia")
def api_analisis_areas_eficiencia():
    """
    PREGUNTA: ¿Qué áreas son menos eficientes?
    RESPONDE: Ranking de áreas por consumo per-cápita, por vehículo, por transacción
    """
    try:
        resultado = analisis_areas_eficiencia()
        if "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_predictivo.get("/prediccion/proximo-mes")
def api_prediccion_proximo_mes(tipo_combustible: str = Query("TODOS", regex="^(TODOS|DIESEL|GASOLINA)$")):
    """
    PREGUNTA: ¿Cuánto combustible necesitará el município el próximo mes?
    RESPONDE: Predicción basada en estadísticas, tendencia, estacionalidad
    """
    try:
        resultado = prediccion_consumo_proximo_mes(tipo_combustible.upper())
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_predictivo.get("/dashboard/kpi-completo")
def api_dashboard_kpi_completo():
    """
    🎯 DASHBOARD INTEGRAL - Todos los KPIs y respuestas a preguntas de negocio en un solo endpoint.
    
    CONTIENE:
    - KPI 1: Consumo por vehículo
    - KPI 2: Consumo por área
    - KPI 3: Eficiencia (km/L)
    - KPI 4: Desviación consumo vs esperado
    - KPI 5: Detección de anomalías
    - 4 Análisis: meses, fines de semana, área eficiencia, predicción próximo mes
    
    ⚠️ ADVERTENCIA: Puede ser lento en primera ejecución (multiquery).
    """
    try:
        resultado = dashboard_kpi_completo()
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))