"""
LÓGICA DE NEGOCIO DESCRIPTIVA - SISTEMA DE COMBUSTIBLE 
Municipio de Caranavi

Contiene todas las consultas y cálculos de negocio:
  - Consumo por área (apertura)
  - Consumo por vehículo
  - Consumo por conductor
  - Consumo mensual
  - Stock actual de combustible
  - Análisis de costos
  - Detección de excesos
  - Datos para predicción de tendencias
"""

from database import query_to_df
import pandas as pd


#  1. CONSUMO POR ÁREA (apertura)
def consumo_por_area(tipo_combustible: str = "TODOS") -> pd.DataFrame:
    """
    Litros y costo total consumido por cada área/programa municipal.
    tipo_combustible: 'GASOLINA', 'DIESEL' o 'TODOS'
    """
    if tipo_combustible == "TODOS":
        sql = """
            SELECT
                a.nombre                         AS area,
                tc.nombre                        AS tipo_combustible,
                SUM(b.cantidad)                  AS litros_consumidos,
                SUM(b.total)                     AS costo_total_bs,
                COUNT(b.boleta_id)               AS nro_boletas
            FROM boletas b
            JOIN aperturas       a   ON b.apertura_id        = a.apertura_id
            JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
            WHERE b.estado = 'APROBADO'
            GROUP BY a.apertura_id, tc.tipo_combustible_id
            ORDER BY litros_consumidos DESC
        """
        return query_to_df(sql)
    else:
        sql = """
            SELECT
                a.nombre                         AS area,
                tc.nombre                        AS tipo_combustible,
                SUM(b.cantidad)                  AS litros_consumidos,
                SUM(b.total)                     AS costo_total_bs,
                COUNT(b.boleta_id)               AS nro_boletas
            FROM boletas b
            JOIN aperturas       a   ON b.apertura_id        = a.apertura_id
            JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
            WHERE b.estado = 'APROBADO'
              AND tc.nombre = %s
            GROUP BY a.apertura_id, tc.tipo_combustible_id
            ORDER BY litros_consumidos DESC
        """
        return query_to_df(sql, params=(tipo_combustible,))



#  2. CONSUMO POR VEHÍCULO
def consumo_por_vehiculo() -> pd.DataFrame:
    """Top de vehículos por litros consumidos."""
    sql = """
        SELECT
            v.nombre                          AS vehiculo,
            v.vehiculo_id                     AS vehiculo_id,
            COALESCE(v.placa, 'SIN-PLACA')    AS placa,
            v.marca,
            tc.nombre                         AS tipo_combustible,
            SUM(b.cantidad)                   AS litros_consumidos,
            SUM(b.total)                      AS costo_total_bs,
            COUNT(b.boleta_id)                AS nro_solicitudes,
            MAX(b.km_inicial)                 AS km_maximo
        FROM boletas b
        JOIN vehiculos        v  ON b.vehiculo_id         = v.vehiculo_id
        JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
        WHERE b.estado = 'APROBADO'
        GROUP BY v.vehiculo_id, tc.tipo_combustible_id
        ORDER BY litros_consumidos DESC
    """
    df = query_to_df(sql)
    
    # Limpieza adicional y creación de identificador alternativo
    if not df.empty:
        # Reemplazar valores nulos o vacíos
        df["placa"] = df["placa"].replace(["nan", "NaN", "", None], "SIN-PLACA")
        
        # Crear columna de identificación para gráficos
        # Si tiene placa, usa placa. Si no, usa nombre del vehículo
        df["identificador"] = df.apply(
            lambda r: r["placa"] if r["placa"] != "SIN-PLACA" 
            else f"{str(r['vehiculo'])[:12]}... (ID:{r['vehiculo_id']})",
            axis=1
        )
        
        # Crear etiqueta completa para gráficos
        df["etiqueta_grafico"] = df.apply(
            lambda r: f"{r['identificador']}\n{r['tipo_combustible'][:3]}",
            axis=1
        )
    
    return df

#  2B. EFICIENCIA POR VEHÍCULO (km/litro)

def eficiencia_vehiculos() -> pd.DataFrame:
    """
    Como pocos registros tienen km_inicial/km_final, calcula en cambio
    el COSTO PROMEDIO POR SOLICITUD por vehículo (igualmente útil para TD).
    """
    sql = """
        SELECT
            v.nombre                                AS vehiculo,
            COALESCE(v.placa, 'SIN-PLACA')          AS placa,
            tc.nombre                               AS tipo_combustible,
            COUNT(b.boleta_id)                      AS nro_solicitudes,
            ROUND(AVG(b.cantidad), 1)               AS litros_promedio,
            ROUND(MAX(b.cantidad), 1)               AS litros_maximo,
            ROUND(MIN(b.cantidad), 1)               AS litros_minimo,
            ROUND(AVG(b.total), 1)                  AS costo_promedio_bs,
            ROUND(SUM(b.cantidad), 1)               AS litros_totales
        FROM boletas b
        JOIN vehiculos        v  ON b.vehiculo_id        = v.vehiculo_id
        JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
        WHERE b.estado = 'APROBADO'
          AND v.cplaca = 1
        GROUP BY v.vehiculo_id, tc.tipo_combustible_id
        HAVING COUNT(b.boleta_id) >= 3
        ORDER BY litros_promedio DESC
    """
    return query_to_df(sql)
    
    
def consumo_mensual() -> pd.DataFrame:
    """Litros y costo total mes a mes."""
    sql = """
        SELECT
            DATE_FORMAT(b.fecha, '%Y-%m')    AS mes,
            tc.nombre                        AS tipo_combustible,
            SUM(b.cantidad)                  AS litros_consumidos,
            SUM(b.total)                     AS costo_total_bs,
            COUNT(b.boleta_id)               AS nro_boletas
        FROM boletas b
        JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
        WHERE b.estado = 'APROBADO'
        GROUP BY mes, tc.tipo_combustible_id
        ORDER BY mes ASC
    """
    return query_to_df(sql)


# ══════════════════════════════════════════════════════
#  4. CONSUMO POR CONDUCTOR
# ══════════════════════════════════════════════════════

def consumo_por_conductor() -> pd.DataFrame:
    """Consumo total por conductor ordenado de mayor a menor."""
    sql = """
        SELECT
            CONCAT(c.nombres, ' ', COALESCE(c.apellidos,'')) AS conductor,
            c.licencia,
            tc.nombre                                         AS tipo_combustible,
            SUM(b.cantidad)                                   AS litros_consumidos,
            SUM(b.total)                                      AS costo_total_bs,
            COUNT(b.boleta_id)                                AS nro_solicitudes
        FROM boletas b
        JOIN conductors        c  ON b.conductor_id        = c.conductor_id
        JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
        WHERE b.estado = 'APROBADO'
        GROUP BY c.conductor_id, tc.tipo_combustible_id
        ORDER BY litros_consumidos DESC
    """
    return query_to_df(sql)


# ══════════════════════════════════════════════════════
#  5. STOCK ACTUAL DE COMBUSTIBLE POR ÁREA
# ══════════════════════════════════════════════════════

def stock_actual() -> pd.DataFrame:
    """
    Stock actual de combustible por área.
    Calcula dinámicamente: Ingresos - Consumos aprobados (por tipo de combustible)
    """
    sql = """
        SELECT
            a.nombre                                            AS area,
            tc.nombre                                           AS tipo_combustible,
            COALESCE(SUM(id2.t_litros), 0)                      AS litros_ingresados,
            COALESCE(SUM(CASE 
                WHEN b.estado = 'APROBADO' THEN b.cantidad 
                ELSE 0 
            END), 0)                                            AS litros_consumidos,
            COALESCE(SUM(id2.t_litros), 0) - 
            COALESCE(SUM(CASE 
                WHEN b.estado = 'APROBADO' THEN b.cantidad 
                ELSE 0 
            END), 0)                                            AS stock_disponible_lts
        FROM aperturas a
        CROSS JOIN tipo_combustibles tc
        LEFT JOIN ingreso_detalles id2 ON a.apertura_id = id2.apertura_id
        LEFT JOIN ingresos i ON id2.ingreso_id = i.ingreso_id
        LEFT JOIN boletas b ON a.apertura_id = b.apertura_id 
                            AND tc.tipo_combustible_id = b.tipo_combustible_id
        GROUP BY a.apertura_id, tc.tipo_combustible_id
        HAVING stock_disponible_lts > 0
        ORDER BY area ASC, stock_disponible_lts DESC
    """
    return query_to_df(sql)


# ══════════════════════════════════════════════════════
#  6. ANÁLISIS DE COSTOS POR MES Y ÁREA
# ══════════════════════════════════════════════════════

def costos_por_mes_area() -> pd.DataFrame:
    """Tabla cruzada: gasto mensual desglosado por área."""
    sql = """
        SELECT
            DATE_FORMAT(b.fecha, '%Y-%m')  AS mes,
            a.nombre                       AS area,
            SUM(b.total)                   AS costo_total_bs
        FROM boletas b
        JOIN aperturas a ON b.apertura_id = a.apertura_id
        WHERE b.estado = 'APROBADO'
        GROUP BY mes, a.apertura_id
        ORDER BY mes ASC, costo_total_bs DESC
    """
    return query_to_df(sql)


# ══════════════════════════════════════════════════════
#  7. VEHÍCULOS CON MAYOR CONSUMO (TOP 10)
# ══════════════════════════════════════════════════════

def top10_vehiculos() -> pd.DataFrame:
    """Top 10 vehículos con mayor gasto en combustible."""
    df = consumo_por_vehiculo()
    return df.head(10)


# ══════════════════════════════════════════════════════
#  8. DETECCIÓN DE EXCESOS (boletas > promedio * 2)
# ══════════════════════════════════════════════════════

def detectar_excesos() -> pd.DataFrame:
    """
    Identifica boletas con cantidad inusualmente alta
    (más del doble del promedio general por tipo de combustible).
    """
    sql = """
        SELECT
            b.nro_solicitud,
            b.fecha,
            b.cantidad                                          AS litros,
            b.total                                             AS costo_bs,
            a.nombre                                            AS area,
            v.nombre                                            AS vehiculo,
            CONCAT(c.nombres,' ',COALESCE(c.apellidos,''))      AS conductor,
            tc.nombre                                           AS tipo_combustible,
            b.motivo
        FROM boletas b
        JOIN aperturas        a  ON b.apertura_id         = a.apertura_id
        JOIN vehiculos        v  ON b.vehiculo_id         = v.vehiculo_id
        JOIN conductors       c  ON b.conductor_id        = c.conductor_id
        JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
        WHERE b.estado = 'APROBADO'
          AND b.cantidad > (
                SELECT AVG(b2.cantidad) * 2
                FROM boletas b2
                WHERE b2.estado = 'APROBADO'
                  AND b2.tipo_combustible_id = b.tipo_combustible_id
              )
        ORDER BY b.cantidad DESC
    """
    return query_to_df(sql)


# ══════════════════════════════════════════════════════
#  8B. DETECCIÓN DE ANOMALÍAS POR VEHÍCULO (estadística)
# ══════════════════════════════════════════════════════

def detectar_anomalias_por_vehiculo() -> pd.DataFrame:
    """
    Detecta vehículos con consumo anómalo comparando contra su PROPIO
    historial (desviación estándar), no el promedio general.
    
    Alerta si: último_consumo > promedio_vehículo + 2*desviación_estándar
    
    Requiere mínimo 5 registros por vehículo para estadística confiable.
    """
    sql = """
        SELECT 
            v.placa,
            v.nombre                                           AS vehiculo,
            ROUND(AVG(b.cantidad), 2)                          AS promedio_litros,
            ROUND(STDDEV(b.cantidad), 2)                       AS desviacion_std,
            COUNT(b.boleta_id)                                 AS nro_boletas,
            (SELECT ROUND(cantidad, 2) FROM boletas b2 
             WHERE b2.vehiculo_id = v.vehiculo_id 
               AND b2.estado = 'APROBADO'
             ORDER BY fecha DESC LIMIT 1)                      AS ultimo_consumo,
            (SELECT DATE(fecha) FROM boletas b2 
             WHERE b2.vehiculo_id = v.vehiculo_id 
               AND b2.estado = 'APROBADO'
             ORDER BY fecha DESC LIMIT 1)                      AS fecha_ultimo,
            CASE 
                WHEN (SELECT cantidad FROM boletas b2 
                      WHERE b2.vehiculo_id = v.vehiculo_id 
                        AND b2.estado = 'APROBADO'
                      ORDER BY fecha DESC LIMIT 1) > 
                     (AVG(b.cantidad) + 2 * STDDEV(b.cantidad))
                THEN 'ALERTA'
                ELSE 'Normal'
            END                                                 AS estado
        FROM vehiculos v
        JOIN boletas b ON v.vehiculo_id = b.vehiculo_id
        WHERE b.estado = 'APROBADO'
        GROUP BY v.vehiculo_id
        HAVING COUNT(b.boleta_id) >= 5
        ORDER BY estado DESC, desviacion_std DESC
    """
    return query_to_df(sql)


# ══════════════════════════════════════════════════════
#  9B. VALIDACIÓN DE STOCK DISPONIBLE
# ══════════════════════════════════════════════════════

def validar_stock_disponible(apertura_id: int, tipo_combustible_id: int, 
                            cantidad_solicitada: float) -> dict:
    """
    Valida si hay suficiente stock antes de aprobar una solicitud.
    
    Args:
        apertura_id: ID del área/apertura
        tipo_combustible_id: ID del tipo de combustible
        cantidad_solicitada: Litros solicitados
    
    Returns:
        dict con:
        - valido: bool
        - area: str
        - tipo_combustible: str
        - stock_disponible: float (litros)
        - solicitado: float
        - diferencia: float (positivo = sobra, negativo = falta)
        - mensaje: str (descripción clara del estado)
    """
    sql = """
        SELECT 
            a.nombre                                            AS area,
            tc.nombre                                           AS tipo_combustible,
            COALESCE(SUM(id2.t_litros), 0)                      AS litros_ingresados,
            COALESCE((SELECT SUM(b.cantidad) 
                     FROM boletas b 
                     WHERE b.apertura_id = a.apertura_id 
                       AND b.tipo_combustible_id = tc.tipo_combustible_id
                       AND b.estado = 'APROBADO'), 0)           AS litros_consumidos,
            COALESCE(SUM(id2.t_litros), 0) -
            COALESCE((SELECT SUM(b.cantidad) 
                     FROM boletas b 
                     WHERE b.apertura_id = a.apertura_id 
                       AND b.tipo_combustible_id = tc.tipo_combustible_id
                       AND b.estado = 'APROBADO'), 0)           AS stock_disponible
        FROM aperturas a
        CROSS JOIN tipo_combustibles tc
        LEFT JOIN ingreso_detalles id2 ON a.apertura_id = id2.apertura_id 
                                       AND tc.tipo_combustible_id = id2.tipo_combustible_id
        WHERE a.apertura_id = %s
          AND tc.tipo_combustible_id = %s
        GROUP BY a.apertura_id, tc.tipo_combustible_id
    """
    df = query_to_df(sql, params=(apertura_id, tipo_combustible_id))
    
    if df.empty:
        return {
            "valido": False,
            "mensaje": "Área o tipo de combustible no encontrado",
            "stock_disponible": 0,
            "solicitado": cantidad_solicitada
        }
    
    row = df.iloc[0]
    stock = float(row['stock_disponible'])
    diferencia = stock - cantidad_solicitada
    
    return {
        "valido": stock >= cantidad_solicitada,
        "area": row['area'],
        "tipo_combustible": row['tipo_combustible'],
        "stock_disponible": round(stock, 2),
        "solicitado": cantidad_solicitada,
        "diferencia": round(diferencia, 2),
        "mensaje": f"Stock OK: {stock:.2f} lts disponibles" if stock >= cantidad_solicitada 
                   else f"INSUFICIENTE: Falta {abs(diferencia):.2f} lts"
    }


# ══════════════════════════════════════════════════════
#  9. INGRESOS DE COMBUSTIBLE (compras al proveedor)
# ══════════════════════════════════════════════════════

def ingresos_combustible() -> pd.DataFrame:
    """Historial de ingresos de combustible al sistema."""
    sql = """
        SELECT
            i.fecha_ingreso                   AS fecha,
            p.nombre                          AS proveedor,
            a.nombre                          AS area,
            v.nombre                          AS tipo_vale,
            id2.t_litros                      AS litros_ingresados,
            id2.t_bs                          AS monto_bs,
            id2.precio                        AS precio_litro
        FROM ingresos i
        JOIN proveedors      p   ON i.proveedor_id         = p.proveedor_id
        JOIN ingreso_detalles id2 ON i.ingreso_id          = id2.ingreso_id
        JOIN aperturas        a   ON id2.apertura_id       = a.apertura_id
        JOIN vales            v   ON id2.vale_id           = v.vale_id
        ORDER BY i.fecha_ingreso DESC
    """
    return query_to_df(sql)


# ══════════════════════════════════════════════════════
#  9B. BENCHMARKS POR TIPO DE VEHÍCULO
# ══════════════════════════════════════════════════════

def benchmarks_por_tipo_vehiculo() -> pd.DataFrame:
    """
    Establece "normales" de consumo por TIPO de vehículo.
    Útil para saber si un camión consume "más de lo esperado para un camión".
    
    Proporciona: promedio, desviación, mín, máx por tipo.
    """
    sql = """
        SELECT
            v.modelo                                           AS tipo_vehiculo,
            COUNT(DISTINCT v.vehiculo_id)                      AS cantidad_vehiculos,
            COUNT(b.boleta_id)                                 AS nro_boletas,
            ROUND(AVG(b.cantidad), 2)                          AS promedio_litros,
            ROUND(STDDEV(b.cantidad), 2)                       AS desviacion_std,
            ROUND(MIN(b.cantidad), 2)                          AS consumo_minimo,
            ROUND(MAX(b.cantidad), 2)                          AS consumo_maximo,
            ROUND(AVG(b.total), 2)                             AS promedio_costo_bs
        FROM vehiculos v
        JOIN boletas b ON v.vehiculo_id = b.vehiculo_id
        WHERE b.estado = 'APROBADO'
          AND v.modelo IS NOT NULL
        GROUP BY v.modelo
        ORDER BY promedio_litros DESC
    """
    return query_to_df(sql)


# ══════════════════════════════════════════════════════
#  10. TENDENCIA PREDICTIVA (serie de tiempo mensual)
# ══════════════════════════════════════════════════════

def tendencia_predictiva(tipo_combustible: str = "DIESEL") -> pd.DataFrame:
    """
    Retorna la serie mensual de litros consumidos lista para
    calcular una proyección lineal de los próximos 3 meses.
    tipo_combustible: 'GASOLINA' o 'DIESEL'
    """
    sql = """
        SELECT
            DATE_FORMAT(b.fecha, '%Y-%m')  AS mes,
            SUM(b.cantidad)                AS litros
        FROM boletas b
        JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
        WHERE b.estado = 'APROBADO'
          AND tc.nombre = %s
        GROUP BY mes
        ORDER BY mes ASC
    """
    df = query_to_df(sql, params=(tipo_combustible,))
    return df


# ══════════════════════════════════════════════════════
#  11. RESUMEN EJECUTIVO (KPIs generales)
# ══════════════════════════════════════════════════════

def resumen_ejecutivo() -> dict:
    """Retorna los indicadores clave del sistema."""
    sql_totales = """
        SELECT
            tc.nombre                 AS tipo,
            SUM(b.cantidad)           AS total_litros,
            SUM(b.total)              AS total_bs,
            COUNT(DISTINCT b.vehiculo_id)   AS vehiculos_activos,
            COUNT(DISTINCT b.apertura_id)   AS areas_activas,
            COUNT(b.boleta_id)        AS total_solicitudes
        FROM boletas b
        JOIN tipo_combustibles tc ON b.tipo_combustible_id = tc.tipo_combustible_id
        WHERE b.estado = 'APROBADO'
        GROUP BY tc.tipo_combustible_id
    """
    df = query_to_df(sql_totales)
    return df.to_dict(orient="records")
