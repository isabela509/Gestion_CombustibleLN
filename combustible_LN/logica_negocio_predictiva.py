"""
LÓGICA DE NEGOCIO PREDICTIVA V2 — SISTEMA DE COMBUSTIBLE
Municipio de Caranavi

"""

from database import query_to_df
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE PRECIOS
# ══════════════════════════════════════════════════════════════════════

PRECIOS_COMBUSTIBLE = {
    "DIESEL": 3.72,
    "GASOLINA": 3.74,
}

# Proyección de precios (ejemplo: inflación anual 3%)
#nos permite responder: ¿si hay inflación, cuánto cuesta/costara?
#Decision BI: ¿Y si sube 5%? 
#CAMBIAS A 0.05, ves como impacta el presupuesto 
INFLACION_ANUAL = 0.03 #herramienta de decision

DIAS_LABORALES_MES = 22
MESES_PROYECCION = 12
#asunciones definidad para construir modelo a futuro 

# ══════════════════════════════════════════════════════════════════════
#  FUNCIONES BASE (corregidas y simplificadas)
# ══════════════════════════════════════════════════════════════════════

def _serie_mensual(tipo_combustible: str = "TODOS") -> pd.DataFrame:
    """Obtiene serie mensual de litros consumidos."""
    if tipo_combustible == "TODOS":
        sql = """
            SELECT
                DATE_FORMAT(b.fecha, '%Y-%m') AS mes,
                SUM(b.cantidad) AS litros,
                SUM(b.total) AS costo_bs
            FROM boletas b
            WHERE b.estado = 'APROBADO'
            GROUP BY mes
            ORDER BY mes ASC
        """
        return query_to_df(sql)
    else:
        sql = """
            SELECT
                DATE_FORMAT(b.fecha, '%Y-%m') AS mes,
                SUM(b.cantidad) AS litros,
                SUM(b.total) AS costo_bs
            FROM boletas b
            JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
            WHERE b.estado = 'APROBADO'
              AND tc.nombre = %s
            GROUP BY mes
            ORDER BY mes ASC
        """
        return query_to_df(sql, params=(tipo_combustible,))


def _estadisticas_consumo(tipo_combustible: str) -> dict:
    """
    Calcula estadísticas reales del consumo histórico.
    Reemplaza la regresión lineal inútil (R² bajo) por estadísticas descriptivas.
    """
    df = _serie_mensual(tipo_combustible)
    if df.empty or len(df) < 3:
        return {
            "promedio": 0, "maximo": 0, "minimo": 0, 
            "desv_std": 0, "meses_datos": 0
        }
    
    litros = pd.to_numeric(df["litros"], errors="coerce").dropna()
    
    return {
        "promedio": float(litros.mean()),
        "maximo": float(litros.max()),
        "minimo": float(litros.min()),
        "desv_std": float(litros.std()),
        "mediana": float(litros.median()),
        "meses_datos": len(litros),
        "ultimo_mes": df["mes"].iloc[-1] if len(df) > 0 else None
    }


def _siguiente_meses(desde_mes_str: str, n: int) -> list:
    """Genera lista de strings 'YYYY-MM' para los próximos n meses."""
    base = datetime.strptime(desde_mes_str + "-01", "%Y-%m-%d")
    return [(base + timedelta(days=32 * (i + 1))).strftime("%Y-%m")
            for i in range(n)]


# ══════════════════════════════════════════════════════════════════════
#  P1. PLAN DE COMPRAS MENSUAL (reemplaza proyección lineal inútil)
# ══════════════════════════════════════════════════════════════════════

#BI predictiva: "¿Cuánto comprar el próximo mes para no quedarnos sin stock ni comprar de más?"
#decision de negocio: Jefe: "¿Cuánto debo solicitar a YPFB para el próximo mes?"
#sistema: "5,850 litros DIESEL, Bs 21,762"
#jefe: "¿Y si hay consumo pico?"
#sistema: "Planifica para 6,550L (rango de riesgo)"
#jefe: "¿Qué pasa si corto un 10%?"
#sistema: "Te faltará en 16% de los meses" ← DECISIÓN INFORMADA

def plan_compras_mensual(tipo_combustible: str = "DIESEL") -> dict:
    """
    Plan práctico de compras basado en estadísticas reales, no en modelos falsos.
    
    Returns:
        dict con: recomendacion_compra, rango_seguro, rango_riesgo, 
                  promedio, maximo, minimo, justificacion
    """
    stats_hist = _estadisticas_consumo(tipo_combustible)
    
    if stats_hist["meses_datos"] == 0:
        return {"error": "Sin datos históricos"}
    
    promedio = stats_hist["promedio"]
    maximo = stats_hist["maximo"]
    desv = stats_hist["desv_std"]
    
    # Recomendación conservadora: promedio + 1 desviación estándar
    # Esto cubre ~84% de los meses históricos (asumiendo distribución normal)
    recomendacion = promedio + desv
    
    # Si la desviación es muy alta (>50% del promedio), usar percentil 75
    if desv / promedio > 0.5:
        df = _serie_mensual(tipo_combustible)
        litros = pd.to_numeric(df["litros"], errors="coerce").dropna()
        recomendacion = litros.quantile(0.75)
    
    return {
        "tipo_combustible": tipo_combustible,
        "recomendacion_compra": round(recomendacion, 0),
        "rango_seguro": {
            "min": round(max(0, promedio - desv), 0),
            "max": round(promedio + desv, 0)
        },
        "rango_riesgo": {
            "min": round(max(0, promedio - 2*desv), 0),
            "max": round(promedio + 2*desv, 0)
        },
        "promedio_historico": round(promedio, 0),
        "maximo_historico": round(maximo, 0),
        "minimo_historico": round(stats_hist["minimo"], 0),
        "variacion_tipica": round(desv / promedio * 100, 1),
        "meses_analizados": stats_hist["meses_datos"],
        "justificacion": (
            f"Recomendación = promedio ({promedio:,.0f}L) + "
            f"variación típica ({desv:,.0f}L). "
            f"Cubre el 84% de los meses históricos."
        ),
        "precio_actual": PRECIOS_COMBUSTIBLE.get(tipo_combustible, 3.72),
        "costo_estimado_bs": round(recomendacion * PRECIOS_COMBUSTIBLE.get(tipo_combustible, 3.72), 0)
    }


# ══════════════════════════════════════════════════════════════════════
#  P2. PRESUPUESTO ANUAL CON ESCENARIOS (mejorado)
# ══════════════════════════════════════════════════════════════════════

#Responde: ¿Si todo va mal, cuanto sera/es?)
#Decision BI:  - Jefe solicita a gobernación: "Necesitamos Bs 291,000"
      #Si le dan menos (250,000) → Scenario Optimista 
      #Si le dan exacto (291,000) → Scenario Base + 5% seguridad
      #Si le dan más (330,000) → Pueden cubrir peor caso (improbable)
      
def presupuesto_anual_escenarios(anio_proyeccion: int = None) -> dict:
    """
    Presupuesto anual con 3 escenarios realistas.
    Elimina la proyección lineal plana e innecesaria.
    """
    if anio_proyeccion is None:
        anio_proyeccion = datetime.now().year + 1
    
    resultados = {}
    total_escenarios = {"optimista": 0, "base": 0, "pesimista": 0}
    
    for tipo in ["GASOLINA", "DIESEL"]:
        plan = plan_compras_mensual(tipo)
        if "error" in plan:
            continue
            
        precio = PRECIOS_COMBUSTIBLE.get(tipo, 3.72)
        
        # Escenarios mensuales
        mensual_optimista = plan["promedio_historico"] * 0.85  # -15% eficiencia (decision de negocio realista basado en lo historico)
        mensual_base = plan["recomendacion_compra"]  # Recomendación normal
        mensual_pesimista = plan["maximo_historico"]  # Peor mes histórico
        
        # Anual
        anual_optimista = mensual_optimista * 12
        anual_base = mensual_base * 12
        anual_pesimista = mensual_pesimista * 12
        
        resultados[tipo] = {
            "litros_mensual_optimista": round(mensual_optimista, 0),
            "litros_mensual_base": round(mensual_base, 0),
            "litros_mensual_pesimista": round(mensual_pesimista, 0),
            "litros_anual_optimista": round(anual_optimista, 0),
            "litros_anual_base": round(anual_base, 0),
            "litros_anual_pesimista": round(anual_pesimista, 0),
            "costo_optimista_bs": round(anual_optimista * precio, 0),
            "costo_base_bs": round(anual_base * precio, 0),
            "costo_pesimista_bs": round(anual_pesimista * precio, 0),
            "precio_litro": precio,
        }
        
        total_escenarios["optimista"] += anual_optimista * precio
        total_escenarios["base"] += anual_base * precio
        total_escenarios["pesimista"] += anual_pesimista * precio
    
    return {
        "anio": anio_proyeccion,
        "por_tipo": resultados,
        "total_optimista_bs": round(total_escenarios["optimista"], 0),
        "total_base_bs": round(total_escenarios["base"], 0),
        "total_pesimista_bs": round(total_escenarios["pesimista"], 0),
        "recomendacion_solicitud": round(total_escenarios["base"] * 1.05, 0),
        "justificacion": (
            "Solicitar el escenario base + 5% de contingencia. "
            "El escenario pesimista representa el peor mes histórico "
            "repetido 12 veces (improbable)."
        )
    }


# ══════════════════════════════════════════════════════════════════════
#  P3. DISTRIBUCIÓN DE STOCK (simplificada y accionable)
# ══════════════════════════════════════════════════════════════════════

def distribucion_stock_decision(litros_disponibles: float, tipo_combustible: str = "DIESEL") -> dict:
    """
    Distribución práctica de stock con mensaje claro de decisión.
    Responde: ¿Cuantos DIAS de cobertura dan estos litros a cada area?
    """
    sql = """
        SELECT
            a.nombre AS area,
            SUM(b.cantidad) / COUNT(DISTINCT DATE_FORMAT(b.fecha,'%Y-%m')) AS consumo_mensual_promedio
        FROM boletas b
        JOIN aperturas a ON b.apertura_id = a.apertura_id
        JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
        WHERE b.estado = 'APROBADO'
          AND tc.nombre = %s
        GROUP BY a.apertura_id
        HAVING consumo_mensual_promedio > 0
        ORDER BY consumo_mensual_promedio DESC
    """
    df = query_to_df(sql, params=(tipo_combustible,))
    
    if df.empty:
        return {"error": "Sin datos de consumo"}
    
    df["consumo_mensual_promedio"] = pd.to_numeric(df["consumo_mensual_promedio"], errors="coerce")
    total_necesidad = df["consumo_mensual_promedio"].sum()
    
    # Calcular asignación proporcional
    df["porcentaje_necesidad"] = (df["consumo_mensual_promedio"] / total_necesidad * 100).round(1)
    df["litros_asignados"] = (df["porcentaje_necesidad"] / 100 * litros_disponibles).round(0)
    df["dias_cobertura"] = (df["litros_asignados"] / (df["consumo_mensual_promedio"] / DIAS_LABORALES_MES)).round(0)
    
    #¿Porque BI? 
    #Responde pregunta de jefe: "¿Cuánto tarda en acabarse?"
       #Permite decisión: "¿4,000L son suficientes? ¿O necesita reabastecimiento?"
    
    
    
    # Determinar prioridad
    #Automatizacion inteligente
    def prioridad(row):
        if row["dias_cobertura"] < 7:
            return " CRÍTICO - Requiere reabastecimiento inmediato"
        elif row["dias_cobertura"] < 15:
            return " ALERTA - Programar compra"
        else:
            return " OK - Stock suficiente"
    
    df["prioridad"] = df.apply(prioridad, axis=1)
    
    # Resumen ejecutivo
    areas_criticas = df[df["dias_cobertura"] < 7]
    cobertura_promedio = df["dias_cobertura"].mean()
    
    return {
        "tipo_combustible": tipo_combustible,
        "litros_disponibles": litros_disponibles,
        "necesidad_total_mensual": round(total_necesidad, 0),
        "cobertura_promedio_dias": round(cobertura_promedio, 0),
        "porcentaje_cubierto": round(litros_disponibles / total_necesidad * 100, 1),
        "areas_criticas_count": len(areas_criticas),
        "tabla_asignacion": df[["area", "consumo_mensual_promedio", "porcentaje_necesidad", 
                                "litros_asignados", "dias_cobertura", "prioridad"]].to_dict('records'),
        "recomendacion": (
            f"Con {litros_disponibles:,.0f}L cubres {litros_disponibles/total_necesidad*100:.1f}% "
            f"de la necesidad mensual total ({total_necesidad:,.0f}L). "
            f"Promedio de cobertura: {cobertura_promedio:.0f} días. "
            f"{len(areas_criticas)} áreas requieren atención inmediata."
        )
    }


# ══════════════════════════════════════════════════════════════════════
#  P4. TOP VEHÍCULOS COSTOSOS (con alertas de reemplazo)
# ══════════════════════════════════════════════════════════════════════

def vehiculos_costo_y_reemplazo(costo_vehiculo_nuevo_bs: float = 120_000, meses_futuro: int = 6) -> dict:
    """
    Análisis unificado: costo proyectado + evaluación de reemplazo.
    Combina P07 y P08 en una sola tabla accionable.
    """
    # Costo histórico acumulado
    sql_hist = """
        SELECT
            v.nombre AS vehiculo,
            COALESCE(v.placa, 'SIN-PLACA') AS placa,
            v.marca,
            SUM(b.total) AS costo_total_historico,
            COUNT(DISTINCT DATE_FORMAT(b.fecha,'%Y-%m')) AS meses_activos,
            SUM(b.cantidad) AS litros_totales,
            tc.nombre AS tipo_combustible
        FROM boletas b
        JOIN vehiculos v ON b.vehiculo_id = v.vehiculo_id
        JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
        WHERE b.estado = 'APROBADO'
        GROUP BY v.vehiculo_id, tc.tipo_combustible_id
        HAVING meses_activos >= 2
    """
    df_hist = query_to_df(sql_hist)
    
    if df_hist.empty:
        return {"error": "Sin datos de vehículos"}
    
    # Calcular métricas
    df_hist["costo_mensual_promedio"] = (df_hist["costo_total_historico"] / df_hist["meses_activos"]).round(2)
    df_hist["costo_proyectado_6m"] = (df_hist["costo_mensual_promedio"] * meses_futuro).round(0)
    df_hist["porcentaje_vs_nuevo"] = (df_hist["costo_total_historico"] / costo_vehiculo_nuevo_bs * 100).round(1)
    
    # Clasificación de alerta
    def alerta_reemplazo(row):
        pct = row["porcentaje_vs_nuevo"]
        if pct >= 100:
            return "🔴 REEMPLAZAR - Costo combustible > vehículo nuevo"
        elif pct >= 75:
            return "🟡 EVALUAR - Cerca del punto de reemplazo"
        elif row["costo_proyectado_6m"] > 30000:
            return "🟠 MONITOREAR - Alto consumo"
        else:
            return "🟢 NORMAL"
    
    df_hist["alerta_reemplazo"] = df_hist.apply(alerta_reemplazo, axis=1)
    df_hist["prioridad"] = df_hist["porcentaje_vs_nuevo"] + (df_hist["costo_proyectado_6m"] / 1000)
    
    # Top 15 más costosos
    top = df_hist.nlargest(15, "prioridad")
    
    # Resumen
    reemplazar = len(df_hist[df_hist["porcentaje_vs_nuevo"] >= 100])
    evaluar = len(df_hist[(df_hist["porcentaje_vs_nuevo"] >= 75) & (df_hist["porcentaje_vs_nuevo"] < 100)])
    alto_consumo = len(df_hist[df_hist["costo_proyectado_6m"] > 30000])
    
    return {
        "costo_vehiculo_referencia": costo_vehiculo_nuevo_bs,
        "top_15_vehiculos": top[["vehiculo", "placa", "marca", "tipo_combustible",
                                  "costo_total_historico", "costo_mensual_promedio",
                                  "costo_proyectado_6m", "porcentaje_vs_nuevo",
                                  "alerta_reemplazo"]].to_dict('records'),
        "resumen_alertas": {
            "reemplazar_urgente": reemplazar,
            "evaluar": evaluar,
            "alto_consumo": alto_consumo,
            "total_vehiculos": len(df_hist)
        },
        "inversion_proyectada_6m_top15": round(top["costo_proyectado_6m"].sum(), 0),
        "recomendacion": (
            f"{reemplazar} vehículos han costado más que uno nuevo en combustible. "
            f"Evaluar reemplazo inmediato. "
            f"Los top 15 vehículos concentran Bs {top['costo_proyectado_6m'].sum():,.0f} "
            f"en los próximos 6 meses."
        )
    }


# ══════════════════════════════════════════════════════════════════════
#  P5. SIMULADOR DE AHORRO (mantener - ya está bien)
# ══════════════════════════════════════════════════════════════════════

def simulador_ahorro_escenarios(porcentajes_reduccion: list = [5, 10, 15, 20], meses: int = 12) -> dict:
    """
    Simulador de ahorro mejorado con múltiples escenarios.
    """
    resultados = []
    
    # Obtener proyección base realista
    presup = presupuesto_anual_escenarios()
    costo_base_total = presup["total_base_bs"]
    
    for pct in porcentajes_reduccion:
        ahorro_bs = costo_base_total * (pct / 100)
        ahorro_litros = ahorro_bs / ((PRECIOS_COMBUSTIBLE["DIESEL"] + PRECIOS_COMBUSTIBLE["GASOLINA"]) / 2)
        
        resultados.append({
            "reduccion_porcentaje": pct,
            "ahorro_anual_bs": round(ahorro_bs, 0),
            "ahorro_litros": round(ahorro_litros, 0),
            "nuevo_costo_anual": round(costo_base_total - ahorro_bs, 0),
            "equivalente_salarios_minimos": round(ahorro_bs / 2250, 1),  # SMN Bolivia ~2250
            "equivalente_porcentaje_presupuesto": pct
        })
    
    return {
        "costo_base_anual_bs": round(costo_base_total, 0),
        "escenarios": resultados,
        "recomendacion": (
            "Una reducción del 10% ahorra Bs {:,.0f} anuales, "
            "equivalente a {:.0f} salarios mínimos.".format(
                resultados[1]["ahorro_anual_bs"] if len(resultados) > 1 else 0,
                resultados[1]["equivalente_salarios_minimos"] if len(resultados) > 1 else 0
            )
        )
    }


# ══════════════════════════════════════════════════════════════════════
#  P6. CALENDARIO DE COMPRAS CON PROYECCIÓN DE PRECIOS (nuevo)
# ══════════════════════════════════════════════════════════════════════

#Responde: "¿Cuándo y a qué precio debo comprar en los próximos 6 meses?"
def calendario_compras_con_precios(meses: int = 6, inflacion_mensual: float = None) -> dict:
    """
    Calendario de compras que incluye proyección de precios.
    Si inflacion_mensual es None, usa 3% anual / 12.
    """
    if inflacion_mensual is None:
        inflacion_mensual = INFLACION_ANUAL / 12
    
    # Obtener stock actual
    sql_stock = """
        SELECT
            tc.nombre AS tipo_combustible,
            COALESCE(SUM(id2.t_litros), 0) - 
            COALESCE(SUM(CASE WHEN b.estado='APROBADO' THEN b.cantidad ELSE 0 END), 0) AS stock_actual
        FROM tipo_combustibles tc
        LEFT JOIN ingreso_detalles id2 ON 1=1
        LEFT JOIN vales v ON id2.vale_id = v.vale_id AND tc.tipo_combustible_id = v.tipo_combustible_id
        LEFT JOIN boletas b ON tc.tipo_combustible_id = b.tipo_combustible_id
        GROUP BY tc.tipo_combustible_id
    """
    df_stock = query_to_df(sql_stock)
    
    filas = []
    meses_nombres = []
    
    base_fecha = datetime.now()
    
    for i in range(meses):
        mes_futuro = base_fecha + timedelta(days=30*i)
        mes_nombre = mes_futuro.strftime("%Y-%m")
        meses_nombres.append(mes_nombre)
        
        # Factor de precio proyectado
        factor_precio = (1 + inflacion_mensual) ** i
        
        for tipo in ["GASOLINA", "DIESEL"]:
            precio_base = PRECIOS_COMBUSTIBLE.get(tipo, 3.72)
            precio_proyectado = precio_base * factor_precio
            
            # Consumo del plan
            plan = plan_compras_mensual(tipo)
            consumo = plan["recomendacion_compra"]
            reserva = consumo * 0.15
            
            # Stock simulado (simplificado)
            stock_inicial = 0 if i == 0 else filas[-1]["stock_final_estimado"] if filas else 0
            if i == 0 and not df_stock.empty:
                row_s = df_stock[df_stock["tipo_combustible"].str.contains(tipo, case=False, na=False)]
                stock_inicial = float(row_s["stock_actual"].sum()) if not row_s.empty else consumo * 1.5
            
            necesidad = consumo + reserva
            compra = max(0, necesidad - stock_inicial)
            stock_final = stock_inicial + compra - consumo
            
            filas.append({
                "mes": mes_nombre,
                "tipo_combustible": tipo,
                "precio_proyectado_bs": round(precio_proyectado, 2),
                "consumo_litros": round(consumo, 0),
                "reserva_seguridad_litros": round(reserva, 0),
                "cantidad_comprar_litros": round(compra, 0),
                "costo_compra_bs": round(compra * precio_proyectado, 0),
                "stock_final_estimado": round(stock_final, 0),
                "inflacion_acumulada_pct": round((factor_precio - 1) * 100, 2)
            })
    
    df_result = pd.DataFrame(filas)
    
    # Resumen por tipo
    resumen = {}
    for tipo in ["GASOLINA", "DIESEL"]:
        sub = df_result[df_result["tipo_combustible"] == tipo]
        resumen[tipo] = {
            "litros_totales": round(sub["cantidad_comprar_litros"].sum(), 0),
            "costo_total_bs": round(sub["costo_compra_bs"].sum(), 0),
            "precio_inicial": PRECIOS_COMBUSTIBLE.get(tipo, 3.72),
            "precio_final": round(sub["precio_proyectado_bs"].iloc[-1], 2) if len(sub) > 0 else PRECIOS_COMBUSTIBLE.get(tipo, 3.72),
            "impacto_inflacion_bs": round(sub["costo_compra_bs"].sum() - 
                                          (sub["cantidad_comprar_litros"].sum() * PRECIOS_COMBUSTIBLE.get(tipo, 3.72)), 0)
        }
    
    total_inversion = sum(r["costo_total_bs"] for r in resumen.values())
    
    return {
        "meses_proyectados": meses,
        "inflacion_mensual_asumida": round(inflacion_mensual * 100, 2),
        "calendario_detalle": filas,
        "resumen_por_tipo": resumen,
        "inversion_total_bs": round(total_inversion, 0),
        "recomendacion": (
            f"Inversión total proyectada: Bs {total_inversion:,.0f} en {meses} meses. "
            f"El impacto de la inflación asumida ({inflacion_mensual*100:.2f}% mensual) "
            f"incrementa el costo en Bs {sum(r['impacto_inflacion_bs'] for r in resumen.values()):,.0f}. "
            f"Recomendación: compras anticipadas para mitigar alza de precios."
        )
    }


# ══════════════════════════════════════════════════════════════════════
#  P7. ESTIMACIÓN DE COSTOS FUTUROS CON PRECIOS (nuevo - solicitado)
# ══════════════════════════════════════════════════════════════════════

#Para DECISION BI:
#- Si presupuesto es fijo: Bs 270,000
     #→ No alcanza en escenario moderado (necesita 277,000)
    #Si presupuesto es flexible: Bs 280,000
    #→ Alcanza moderado pero falta en pesimista (300,000)
    #DECISIÓN: Negociar funds para pesimista o reducir consumo
def estimacion_costos_futuros(horizonte_meses: int = 12, escenario_precio: str = "moderado") -> dict:
    """
    Proyección de inversión en combustible combinando volumen y precios.
    Responde : "¿Cual es el rango de costos posibles?"
    Escenarios de precio:
    - conservador: precios actuales sin cambio
    - moderado: inflación 3% anual
    - pesimista: inflación 8% anual + shock 10% en mes 6
    """
    
    # Definir escenarios de precio
    escenarios = {
        "conservador": {"inflacion_anual": 0.0, "shock": 0.0, "mes_shock": None},
        "moderado": {"inflacion_anual": 0.03, "shock": 0.0, "mes_shock": None},
        "pesimista": {"inflacion_anual": 0.08, "shock": 0.10, "mes_shock": 6}
    }
    
    config = escenarios.get(escenario_precio, escenarios["moderado"])
    inflacion_mensual = config["inflacion_anual"] / 12
    
    resultados = []
    
    for mes in range(1, horizonte_meses + 1):
        factor_inflacion = (1 + inflacion_mensual) ** mes
        
        # Aplicar shock si corresponde
        factor_shock = 1.0
        if config["mes_shock"] and mes >= config["mes_shock"]:
            factor_shock = 1 + config["shock"]
        
        factor_total = factor_inflacion * factor_shock
        
        mes_data = {"mes": mes, "detalle_por_tipo": {}}
        total_mes = 0
        
        for tipo in ["GASOLINA", "DIESEL"]:
            # Volumen del plan de compras
            plan = plan_compras_mensual(tipo)
            volumen = plan["recomendacion_compra"]
            
            # Precio proyectado
            precio_base = PRECIOS_COMBUSTIBLE.get(tipo, 3.72)
            precio_proy = precio_base * factor_total
            
            costo = volumen * precio_proy
            
            mes_data["detalle_por_tipo"][tipo] = {
                "volumen_litros": round(volumen, 0),
                "precio_bs": round(precio_proy, 2),
                "costo_total_bs": round(costo, 0),
                "precio_vs_actual_pct": round((factor_total - 1) * 100, 1)
            }
            total_mes += costo
        
        mes_data["costo_total_mes_bs"] = round(total_mes, 0)
        mes_data["factor_precio_acumulado"] = round(factor_total, 3)
        resultados.append(mes_data)
    
    # Resúmenes
    total_anual = sum(m["costo_total_mes_bs"] for m in resultados)
    
    # Comparar con escenario base (sin inflación)
    total_base = 0
    for tipo in ["GASOLINA", "DIESEL"]:
        plan = plan_compras_mensual(tipo)
        total_base += plan["recomendacion_compra"] * PRECIOS_COMBUSTIBLE.get(tipo, 3.72) * horizonte_meses
    
    impacto_precios = total_anual - total_base
    
    # Acumulado trimestral
    trimestres = []
    for q in range(1, 5):
        meses_q = resultados[(q-1)*3:q*3]
        trimestres.append({
            "trimestre": q,
            "costo_bs": round(sum(m["costo_total_mes_bs"] for m in meses_q), 0),
            "precio_promedio_gasolina": round(sum(m["detalle_por_tipo"]["GASOLINA"]["precio_bs"] for m in meses_q) / 3, 2),
            "precio_promedio_diesel": round(sum(m["detalle_por_tipo"]["DIESEL"]["precio_bs"] for m in meses_q) / 3, 2)
        })
    
    return {
        "escenario": escenario_precio,
        "horizonte_meses": horizonte_meses,
        "proyeccion_mensual": resultados,
        "resumen_trimestral": trimestres,
        "total_anual_proyectado_bs": round(total_anual, 0),
        "total_escenario_base_bs": round(total_base, 0),
        "impacto_precios_bs": round(impacto_precios, 0),
        "variacion_pct_vs_base": round((total_anual / total_base - 1) * 100, 1),
        "precio_final_gasolina": resultados[-1]["detalle_por_tipo"]["GASOLINA"]["precio_bs"] if resultados else PRECIOS_COMBUSTIBLE["GASOLINA"],
        "precio_final_diesel": resultados[-1]["detalle_por_tipo"]["DIESEL"]["precio_bs"] if resultados else PRECIOS_COMBUSTIBLE["DIESEL"],
        "recomendacion": (
            f"Escenario {escenario_precio}: Inversión anual proyectada Bs {total_anual:,.0f}. "
            f"Impacto de precios: Bs {impacto_precios:,.0f} ({(total_anual/total_base-1)*100:.1f}%). "
            f"Peor trimestre: Q{max(trimestres, key=lambda x: x['costo_bs'])['trimestre']}. "
            f"Recomendación: compras programadas anticipadas."
        )
    }


# ══════════════════════════════════════════════════════════════════════
#  P8. TABLA RESUMEN EJECUTIVA (nuevo - para dashboard)
# ══════════════════════════════════════════════════════════════════════

def tabla_resumen_ejecutivo() -> dict:
    """
    Resumen ejecutivo de una página para el alcalde/jefe de logística.
    """
    # Datos clave
    diesel = plan_compras_mensual("DIESEL")
    gasolina = plan_compras_mensual("GASOLINA")
    presup = presupuesto_anual_escenarios()
    vehiculos = vehiculos_costo_y_reemplazo()
    
    # Estimación de costos futuros
    costos_moderado = estimacion_costos_futuros(12, "moderado")
    costos_pesimista = estimacion_costos_futuros(12, "pesimista")
    
    return {
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "indicadores_clave": {
            "compra_mensual_recomendada_diesel_litros": diesel.get("recomendacion_compra", 0),
            "compra_mensual_recomendada_gasolina_litros": gasolina.get("recomendacion_compra", 0),
            "costo_mensual_estimado_bs": diesel.get("costo_estimado_bs", 0) + gasolina.get("costo_estimado_bs", 0),
            "presupuesto_anual_solicitar_bs": presup.get("recomendacion_solicitud", 0),
            "vehiculos_reemplazar_urgente": vehiculos.get("resumen_alertas", {}).get("reemplazar_urgente", 0),
            "inversion_anual_moderada_bs": costos_moderado.get("total_anual_proyectado_bs", 0),
            "riesgo_precio_pesimista_bs": costos_pesimista.get("total_anual_proyectado_bs", 0) - costos_moderado.get("total_anual_proyectado_bs", 0)
        },
        "alertas_prioritarias": [
            f"🔴 {vehiculos.get('resumen_alertas', {}).get('reemplazar_urgente', 0)} vehículos requieren reemplazo inmediato",
            f"🟡 {vehiculos.get('resumen_alertas', {}).get('evaluar', 0)} vehículos en evaluación",
            f"📈 Riesgo de alza de precios: Bs {costos_pesimista.get('total_anual_proyectado_bs', 0) - costos_moderado.get('total_anual_proyectado_bs', 0):,.0f} adicionales en escenario pesimista"
        ],
        "recomendaciones_accion": [
            f"Solicitar presupuesto anual: Bs {presup.get('recomendacion_solicitud', 0):,.0f}",
            f"Compra mensual diesel: {diesel.get('recomendacion_compra', 0):,.0f}L (cubre 84% de meses históricos)",
            f"Compra mensual gasolina: {gasolina.get('recomendacion_compra', 0):,.0f}L",
            "Programar evaluación técnica de vehículos marcados para reemplazo",
            "Considerar compras anticipadas ante riesgo de inflación"
        ]
    }
    
    # ══════════════════════════════════════════════════════════════════════
#  P9. TABLA DETALLADA DE CONSUMO PROYECTADO (nuevo - solicitado)
# ══════════════════════════════════════════════════════════════════════

def tabla_consumo_proyectado_detallado(meses_proyeccion: int = 12) -> dict:
    """
    Genera tabla detallada mensual de consumo proyectado por tipo de combustible.
    Incluye escenarios optimista, base y pesimista para cada mes.
    
    Returns:
        dict con tablas mensuales, totales anuales, y resumen ejecutivo
    """
    # Obtener estadísticas base
    stats_diesel = _estadisticas_consumo("DIESEL")
    stats_gasolina = _estadisticas_consumo("GASOLINA")
    
    # Generar meses futuros
    mes_actual = datetime.now()
    meses_nombres = []
    for i in range(meses_proyeccion):
        mes_futuro = mes_actual + timedelta(days=30*i)
        meses_nombres.append(mes_futuro.strftime("%Y-%m"))
    
    # Factores estacionales (ejemplo: consumo más alto en ciertos meses)
    # Esto puede ajustarse según patrones históricos reales
    factores_estacionales = {
        # Mes: factor multiplicador (1.0 = promedio)
        "01": 1.05, "02": 0.95, "03": 1.0, "04": 1.0,
        "05": 1.1, "06": 1.15, "07": 1.2, "08": 1.1,
        "09": 1.05, "10": 1.0, "11": 0.95, "12": 0.9
    }
    
    filas_tabla = []
    
    for mes in meses_nombres:
        mes_num = mes.split("-")[1]
        factor_est = factores_estacionales.get(mes_num, 1.0)
        
        for tipo, stats, precio in [("DIESEL", stats_diesel, PRECIOS_COMBUSTIBLE["DIESEL"]),
                                    ("GASOLINA", stats_gasolina, PRECIOS_COMBUSTIBLE["GASOLINA"])]:
            
            if stats["meses_datos"] == 0:
                continue
            
            promedio = stats["promedio"]
            maximo = stats["maximo"]
            minimo = stats["minimo"]
            desv = stats["desv_std"]
            
            # Escenarios con factor estacional
            optimista = max(0, (promedio - desv) * factor_est * 0.85)  # -15% eficiencia
            base = (promedio + desv * 0.5) * factor_est  # Levemente conservador
            pesimista = min(maximo * 1.1, (promedio + 2*desv) * factor_est)  # Peor caso +10%
            
            filas_tabla.append({
                "mes": mes,
                "tipo_combustible": tipo,
                "factor_estacional": factor_est,
                "litros_optimista": round(optimista, 0),
                "litros_base": round(base, 0),
                "litros_pesimista": round(pesimista, 0),
                "costo_optimista_bs": round(optimista * precio, 0),
                "costo_base_bs": round(base * precio, 0),
                "costo_pesimista_bs": round(pesimista * precio, 0),
                "precio_litro": precio
            })
    
    df = pd.DataFrame(filas_tabla)
    
    # Totales anuales por tipo y escenario
    totales = {}
    for tipo in ["DIESEL", "GASOLINA"]:
        sub = df[df["tipo_combustible"] == tipo]
        if not sub.empty:
            totales[tipo] = {
                "litros_optimista": round(sub["litros_optimista"].sum(), 0),
                "litros_base": round(sub["litros_base"].sum(), 0),
                "litros_pesimista": round(sub["litros_pesimista"].sum(), 0),
                "costo_optimista_bs": round(sub["costo_optimista_bs"].sum(), 0),
                "costo_base_bs": round(sub["costo_base_bs"].sum(), 0),
                "costo_pesimista_bs": round(sub["costo_pesimista_bs"].sum(), 0),
            }
    
    # Totales generales
    total_litros_opt = sum(t["litros_optimista"] for t in totales.values())
    total_litros_base = sum(t["litros_base"] for t in totales.values())
    total_litros_pes = sum(t["litros_pesimista"] for t in totales.values())
    
    return {
        "periodo_proyeccion": f"{meses_nombres[0]} a {meses_nombres[-1]}",
        "meses_proyectados": meses_proyeccion,
        "tabla_mensual_detallada": df.to_dict('records'),
        "totales_por_tipo": totales,
        "totales_generales": {
            "litros_optimista": total_litros_opt,
            "litros_base": total_litros_base,
            "litros_pesimista": total_litros_pes,
            "costo_optimista_bs": sum(t["costo_optimista_bs"] for t in totales.values()),
            "costo_base_bs": sum(t["costo_base_bs"] for t in totales.values()),
            "costo_pesimista_bs": sum(t["costo_pesimista_bs"] for t in totales.values()),
        },
        "promedio_mensual": {
            "litros_base": round(total_litros_base / meses_proyeccion, 0),
            "costo_base_bs": round(sum(t["costo_base_bs"] for t in totales.values()) / meses_proyeccion, 0)
        },
        "recomendacion": (
            f"Para {meses_proyeccion} meses: Consumo base estimado de {total_litros_base:,.0f} litros "
            f"(Bs {sum(t['costo_base_bs'] for t in totales.values()):,.0f}). "
            f"Rango: {total_litros_opt:,.0f} - {total_litros_pes:,.0f} litros. "
            f"Promedio mensual: {round(total_litros_base/meses_proyeccion, 0):,.0f} litros."
        )
    }


def exportar_tabla_excel_format(datos: dict, nombre_archivo: str = "tabla_consumo_proyectado"):
    """
    Genera string con formato de tabla para copiar a Excel o mostrar en consola.
    """
    df = pd.DataFrame(datos["tabla_mensual_detallada"])
    
    # Pivotear para mejor visualización
    try:
        tabla_pivot = df.pivot_table(
            index='mes', 
            columns='tipo_combustible',
            values=['litros_base', 'costo_base_bs', 'litros_optimista', 'litros_pesimista']
        ).round(0)
    except:
        pass  # No es crítico, solo para debug
    
    # Formato para consola/Excel
    output = []
    output.append("=" * 100)
    output.append(f"TABLA DE CONSUMO PROYECTADO - {datos['periodo_proyeccion']}")
    output.append("=" * 100)
    output.append("")
    
    # Encabezados
    header = f"{'MES':<12} | {'DIESEL (L)':>12} | {'DIESEL (Bs)':>14} | {'GASOLINA (L)':>14} | {'GASOLINA (Bs)':>14} | {'TOTAL (L)':>12} | {'TOTAL (Bs)':>14}"
    output.append(header)
    output.append("-" * 100)
    
    # Datos mensuales
    for mes in df['mes'].unique():
        row_diesel = df[(df['mes'] == mes) & (df['tipo_combustible'] == 'DIESEL')]
        row_gas = df[(df['mes'] == mes) & (df['tipo_combustible'] == 'GASOLINA')]
        
        # CORRECCIÓN: Verificar usando len() en lugar de .empty()
        if len(row_diesel) > 0 and len(row_gas) > 0:
            l_diesel = float(row_diesel['litros_base'].values[0])
            c_diesel = float(row_diesel['costo_base_bs'].values[0])
            l_gas = float(row_gas['litros_base'].values[0])
            c_gas = float(row_gas['costo_base_bs'].values[0])
            
            line = f"{mes:<12} | {l_diesel:>12,.0f} | {c_diesel:>14,.0f} | {l_gas:>14,.0f} | {c_gas:>14,.0f} | {l_diesel+l_gas:>12,.0f} | {c_diesel+c_gas:>14,.0f}"
            output.append(line)
    
    output.append("-" * 100)
    
    # Totales
    tot = datos["totales_generales"]
    tot_diesel = datos["totales_por_tipo"]["DIESEL"]
    tot_gas = datos["totales_por_tipo"]["GASOLINA"]
    
    line_total = f"{'TOTAL ANUAL':<12} | {tot_diesel['litros_base']:>12,.0f} | {tot_diesel['costo_base_bs']:>14,.0f} | {tot_gas['litros_base']:>14,.0f} | {tot_gas['costo_base_bs']:>14,.0f} | {tot['litros_base']:>12,.0f} | {tot['costo_base_bs']:>14,.0f}"
    output.append(line_total)
    output.append("")
    
    # Escenarios
    output.append("ESCENARIOS ANUALES:")
    output.append(f"  Optimista:  {tot['litros_optimista']:>10,.0f} L  |  Bs {tot['costo_optimista_bs']:>12,.0f}")
    output.append(f"  Base:       {tot['litros_base']:>10,.0f} L  |  Bs {tot['costo_base_bs']:>12,.0f}")
    output.append(f"  Pesimista:  {tot['litros_pesimista']:>10,.0f} L  |  Bs {tot['costo_pesimista_bs']:>12,.0f}")
    output.append("")
    output.append(f"Promedio mensual: {datos['promedio_mensual']['litros_base']:,.0f} litros  |  Bs {datos['promedio_mensual']['costo_base_bs']:,.0f}")
    output.append("=" * 100)
    
    return "\n".join(output)

