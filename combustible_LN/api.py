"""
API REST — Sistema de Control de Combustible
Municipio de Caranavi

Iniciar:  uvicorn api:app --reload --port 8000
Docs:     http://localhost:8000/docs

CORS:     Configurar según ambiente (ver ALLOWED_ORIGINS)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

# ══════════════════════════════════════════════════════
#  CONFIGURACIÓN POR AMBIENTE
# ══════════════════════════════════════════════════════
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# CORS: Dominio(s) permitido(s)
if ENVIRONMENT == "production":
    # 🔴 PRODUCCIÓN: Especificar dominios explícitamente
    ALLOWED_ORIGINS = [
        "https://caranavi.gob.bo",           # Sitio principal
        "https://admin.caranavi.gob.bo",     # Panel de administración
        "https://reportes.caranavi.gob.bo",  # Reportes
    ]
else:
    # 🟢 DESARROLLO: Permitir cualquier origen
    ALLOWED_ORIGINS = ["*"]

print(f"[API] Ambiente: {ENVIRONMENT.upper()} | CORS: {ALLOWED_ORIGINS}")

from logica_negocio import (
    consumo_por_area,
    consumo_por_vehiculo,
    consumo_mensual,
    consumo_por_conductor,
    stock_actual,
    top10_vehiculos,
    detectar_excesos,
    tendencia_predictiva,
    resumen_ejecutivo,
    costos_por_mes_area,
    ingresos_combustible,
    eficiencia_vehiculos,
    detectar_anomalias_por_vehiculo,
    benchmarks_por_tipo_vehiculo,
    validar_stock_disponible,
)
import graficos as g

# Whitelist de valores válidos (defensa contra inyección)
TIPOS_COMBUSTIBLES = {"TODOS", "GASOLINA", "DIESEL"}

app = FastAPI(
    title="API de Control de Combustible",
    description="Sistema de reportes y análisis — Municipio de Caranavi",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True if ENVIRONMENT == "production" else False,
    allow_methods=["GET", "POST"],  # Solo GET y POST (no DELETE, PUT, etc)
    allow_headers=["Content-Type", "Authorization"],
)

def df_json(df):
    if df.empty:
        return []
    return df.fillna("").to_dict(orient="records")



#  endpoints de datos 
@app.get("/", tags=["Info"])
def root():
    return {
        "sistema": "Control de Combustible — Caranavi",
        "version": "1.0",
        "endpoints_disponibles": {
            "KPIs": ["/resumen"],
            "Consumo": [
                "/consumo/area?tipo_combustible=TODOS|GASOLINA|DIESEL",
                "/consumo/vehiculo",
                "/consumo/mensual",
                "/consumo/conductor",
            ],
            "Stock": ["/stock"],
            "Alertas": [
                "/excesos",
                "/anomalias-por-vehiculo",
                "/benchmarks-vehiculos",
            ],
            "Eficiencia": ["/eficiencia/vehiculos"],
            "Predicción": ["/tendencia?tipo=DIESEL|GASOLINA"],
            "Validación": [
                "/validar-stock?apertura_id=1&tipo_combustible_id=1&cantidad_solicitada=50"
            ],
            "Ingresos": ["/ingresos"],
            "Costos": ["/costos/mes-area"],
            "Gráficos": [
                "/graficos/{nombre}",
                "/graficos/generar-todos",
            ]
        }
    }


@app.get("/resumen", tags=["KPIs"])
def get_resumen():
    """Indicadores clave generales del sistema."""
    return resumen_ejecutivo()


@app.get("/consumo/area", tags=["Consumo"])
def get_consumo_area(
    tipo_combustible: str = Query(
        "TODOS",
        description="GASOLINA, DIESEL o TODOS",
        regex="^(TODOS|GASOLINA|DIESEL)$"
    )
):
    """Consumo de litros por área/programa municipal."""
    tipo = tipo_combustible.upper().strip()
    
    # Validación adicional (defensa en profundidad)
    if tipo not in TIPOS_COMBUSTIBLES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de combustible inválido. Use: {sorted(TIPOS_COMBUSTIBLES)}"
        )
    
    df = consumo_por_area(tipo)
    return df_json(df)


@app.get("/consumo/vehiculo", tags=["Consumo"])
def get_consumo_vehiculo():
    """Consumo total por vehículo."""
    return df_json(consumo_por_vehiculo())


@app.get("/consumo/mensual", tags=["Consumo"])
def get_consumo_mensual():
    """Histórico mensual de consumo."""
    return df_json(consumo_mensual())


@app.get("/consumo/conductor", tags=["Consumo"])
def get_consumo_conductor():
    """Consumo total por conductor."""
    return df_json(consumo_por_conductor())


@app.get("/stock", tags=["Stock"])
def get_stock():
    """Stock actual de combustible por área."""
    return df_json(stock_actual())





@app.get("/tendencia", tags=["Predicción"])
def get_tendencia(
    tipo: str = Query(
        "DIESEL",
        description="GASOLINA o DIESEL",
        regex="^(GASOLINA|DIESEL)$"
    )
):
    """Serie temporal mensual para análisis predictivo con proyección."""
    tipo = tipo.upper().strip()
    
    # Validación
    if tipo not in {"GASOLINA", "DIESEL"}:
        raise HTTPException(
            status_code=400,
            detail="Tipo debe ser GASOLINA o DIESEL"
        )
    
    return df_json(tendencia_predictiva(tipo))


@app.get("/ingresos", tags=["Ingresos"])
def get_ingresos():
    """Historial de ingresos de combustible al sistema."""
    return df_json(ingresos_combustible())


@app.get("/costos/mes-area", tags=["Costos"])
def get_costos_mes_area():
    """Costo mensual desglosado por área."""
    return df_json(costos_por_mes_area())



#  ENDPOINTS DE GRÁFICOS (11 total)
GRAFICOS_DISPONIBLES = {
    "consumo-area":      ("graficos/01_consumo_por_area.png",        g.grafico_consumo_por_area),
    "top-vehiculos":     ("graficos/02_top10_vehiculos.png",          g.grafico_top_vehiculos),
    "consumo-mensual":   ("graficos/03_consumo_mensual.png",          g.grafico_consumo_mensual),
    "conductores":       ("graficos/04_consumo_conductores.png",      g.grafico_conductores),
    "stock":             ("graficos/05_stock_actual.png",             g.grafico_stock_actual),
    "costos-mensuales":  ("graficos/06_costos_mensuales.png",         g.grafico_costos_mensuales),
    "prediccion":        ("graficos/07_prediccion_tendencia.png",     g.grafico_tendencia_predictiva),
    "excesos":           ("graficos/08_alertas_exceso.png",           g.grafico_excesos),
    "comparativo":       ("graficos/09_comparativo_combustibles.png",  g.grafico_comparativo_combustibles),
    "eficiencia":        ("graficos/10_eficiencia_vehiculos.png",     g.grafico_eficiencia_vehiculos),
    "resumen":           ("graficos/11_resumen_ejecutivo.png",        g.grafico_resumen_ejecutivo),
}


@app.get("/graficos/{nombre}", tags=["Gráficos"])
def get_grafico(nombre: str):
    """
    Retorna un gráfico PNG. Opciones disponibles:
    - consumo-area
    - top-vehiculos
    - consumo-mensual
    - conductores
    - stock
    - costos-mensuales
    - prediccion (con bandas de confianza 95%)
    - excesos (alertas por severidad)
    - comparativo
    - eficiencia (km/litro por vehículo)
    - resumen (KPI table)
    """
    if nombre not in GRAFICOS_DISPONIBLES:
        raise HTTPException(
            status_code=404,
            detail=f"Gráfico '{nombre}' no encontrado. "
                   f"Disponibles: {sorted(GRAFICOS_DISPONIBLES.keys())}"
        )

    path, generador = GRAFICOS_DISPONIBLES[nombre]

    # Si el archivo no existe, generarlo en el momento
    if not os.path.exists(path):
        generador()

    return FileResponse(path, media_type="image/png")


@app.get("/excesos", tags=["Alertas"])
def get_excesos():
    """Boletas con consumo excesivamente alto (>2x promedio)."""
    return df_json(detectar_excesos())


@app.get("/anomalias-por-vehiculo", tags=["Alertas"])
def get_anomalias_vehiculo():
    """Vehículos con consumo anómalo vs su propio historial (desviación estándar)."""
    return df_json(detectar_anomalias_por_vehiculo())


@app.get("/benchmarks-vehiculos", tags=["Alertas"])
def get_benchmarks():
    """Estándares de consumo por tipo de vehículo (camión, auto, etc.)."""
    return df_json(benchmarks_por_tipo_vehiculo())


@app.get("/eficiencia/vehiculos", tags=["Eficiencia"])
def get_eficiencia():
    """Rendimiento km/litro por vehículo."""
    return df_json(eficiencia_vehiculos())


@app.post("/validar-stock", tags=["Validación"])
def validar_stock(
    apertura_id: int = Query(..., description="ID del área/apertura"),
    tipo_combustible_id: int = Query(..., description="ID del tipo de combustible (1=GASOLINA, 2=DIESEL)"),
    cantidad_solicitada: float = Query(..., gt=0, description="Litros solicitados")
):
    """
    Valida si hay stock disponible ANTES de aprobar una solicitud.
    
    Ejemplo:
    POST /validar-stock?apertura_id=5&tipo_combustible_id=2&cantidad_solicitada=50
    
    Respuesta:
    {
        "valido": true,
        "area": "Transportes",
        "tipo_combustible": "DIESEL",
        "stock_disponible": 150.5,
        "solicitado": 50.0,
        "diferencia": 100.5,
        "mensaje": "Stock OK: 150.50 lts disponibles"
    }
    """
    if apertura_id < 1 or tipo_combustible_id < 1 or cantidad_solicitada <= 0:
        raise HTTPException(
            status_code=400,
            detail="Parámetros inválidos"
        )
    
    resultado = validar_stock_disponible(apertura_id, tipo_combustible_id, cantidad_solicitada)
    return resultado


@app.post("/graficos/generar-todos", tags=["Gráficos"])
def generar_todos_los_graficos():
    """Genera (o regenera) los 11 gráficos de reportes TD."""
    generados = []
    errores = []
    for nombre, (path, fn) in GRAFICOS_DISPONIBLES.items():
        try:
            fn()
            generados.append(nombre)
        except Exception as e:
            errores.append({"grafico": nombre, "error": str(e)})

    return {
        "generados": generados,
        "errores": errores,
        "total": len(generados),
        "mensaje": "✅ Todos los gráficos generados correctamente" if not errores else f"⚠️ {len(errores)} error(es)"
    }
