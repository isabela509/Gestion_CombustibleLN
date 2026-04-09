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