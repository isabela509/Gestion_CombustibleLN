"""
╔════════════════════════════════════════════════════════════════════════════╗
║ SISTEMA DE KPI - GESTIÓN DE COMBUSTIBLE MUNICIPIO CARANAVI              ║
╚════════════════════════════════════════════════════════════════════════════╝

Indicadores Clave de Desempeño:
  ✓ Consumo promedio por vehículo
  ✓ Consumo por área de trabajo
  ✓ Rendimiento (km/litro)
  ✓ Desviación consumo esperado vs real
  ✓ Detección de anomalías (fuga, robo, mal uso)
  ✓ Análisis estacional
  ✓ Predicción de consumo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database import query_to_df
import warnings
warnings.filterwarnings('ignore')


# ═══════════════════════════════════════════════════════════════════════════
#  1. CONSUMO PROMEDIO POR VEHÍCULO
# ═══════════════════════════════════════════════════════════════════════════

def kpi_consumo_vehiculo():
    """
    ¿Cuáles son los vehículos que más combustible consumen?
    Retorna ranking de vehículos por consumo promedio mensual
    """
    sql = """
    SELECT 
        v.vehiculo_id,
        v.nombre AS vehiculo,
        v.placa,
        v.marca,
        COUNT(DISTINCT DATE_FORMAT(b.fecha, '%Y-%m')) AS meses_activos,
        SUM(b.cantidad) AS consumo_total,
        ROUND(SUM(b.cantidad) / COUNT(DISTINCT DATE_FORMAT(b.fecha, '%Y-%m')), 2) AS consumo_promedio_mensual,
        ROUND(MIN(b.cantidad), 2) AS consumo_minimo,
        ROUND(MAX(b.cantidad), 2) AS consumo_maximo,
        ROUND(STDDEV(b.cantidad), 2) AS desv_estandar
    FROM boletas b
    JOIN vehiculos v ON b.vehiculo_id = v.vehiculo_id
    WHERE b.estado = 'APROBADO'
    GROUP BY v.vehiculo_id, v.nombre, v.placa, v.marca
    ORDER BY consumo_promedio_mensual DESC
    """
    
    try:
        df = query_to_df(sql)
        if df.empty:
            return {"error": "Sin datos disponibles"}
        
        # Clasificación
        promedio_flota = df['consumo_promedio_mensual'].mean()
        
        def clasificar(consumo):
            if consumo > promedio_flota * 1.5:
                return "🔴 ALTO CONSUMO"
            elif consumo > promedio_flota:
                return "🟠 CONSUMO NORMAL"
            else:
                return "🟢 BAJO CONSUMO"
        
        df['clasificacion'] = df['consumo_promedio_mensual'].apply(clasificar)
        
        return {
            "titulo": "CONSUMO POR VEHÍCULO",
            "datos": df.to_dict('records'),
            "estadisticas": {
                "promedio_flota": float(promedio_flota),
                "total_vehiculos": len(df),
                "consumo_maximo": float(df['consumo_promedio_mensual'].max()),
                "consumo_minimo": float(df['consumo_promedio_mensual'].min()),
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
#  2. CONSUMO POR ÁREA
# ═══════════════════════════════════════════════════════════════════════════

def kpi_consumo_area():
    """
    ¿Qué áreas de trabajo gastan más combustible?
    Análisis por departamentos/programas municipales
    """
    sql = """
    SELECT 
        a.apertura_id,
        a.nombre AS area,
        COUNT(DISTINCT DATE_FORMAT(b.fecha, '%Y-%m')) AS meses_activos,
        COUNT(DISTINCT b.vehiculo_id) AS vehiculos_asignados,
        SUM(b.cantidad) AS consumo_total,
        ROUND(SUM(b.cantidad) / COUNT(DISTINCT DATE_FORMAT(b.fecha, '%Y-%m')), 2) AS consumo_promedio_mensual,
        ROUND(SUM(b.total), 2) AS costo_total_bs,
        ROUND(SUM(b.total) / COUNT(DISTINCT DATE_FORMAT(b.fecha, '%Y-%m')), 2) AS costo_promedio_mensual
    FROM boletas b
    JOIN aperturas a ON b.apertura_id = a.apertura_id
    WHERE b.estado = 'APROBADO'
    GROUP BY a.apertura_id, a.nombre
    ORDER BY consumo_promedio_mensual DESC
    """
    
    try:
        df = query_to_df(sql)
        if df.empty:
            return {"error": "Sin datos disponibles"}
        
        promedio = df['consumo_promedio_mensual'].mean()
        
        def clasificar(consumo):
            if consumo > promedio * 1.3:
                return "🔴 EXCESIVO"
            elif consumo > promedio:
                return "🟠 ELEVADO"
            else:
                return "🟢 NORMAL"
        
        df['clasificacion'] = df['consumo_promedio_mensual'].apply(clasificar)
        
        return {
            "titulo": "CONSUMO POR ÁREA",
            "datos": df.to_dict('records'),
            "estadisticas": {
                "total_areas": len(df),
                "promedio_area": float(promedio),
                "area_mayor_consumo": df.iloc[0]['area'],
                "consumo_mayor_area": float(df.iloc[0]['consumo_promedio_mensual']),
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
#  3. RENDIMIENTO km/litro
# ═══════════════════════════════════════════════════════════════════════════

def kpi_eficiencia():
    """
    ¿Qué vehículos son más eficientes en consumo (km/litro)?
    Retorna TODOS los vehículos con su rendimiento
    """
    sql = """
    SELECT 
        v.vehiculo_id,
        v.nombre AS vehiculo,
        v.placa,
        COUNT(b.boleta_id) AS viajes,
        SUM(b.cantidad) AS litros_consumidos,
        SUM(COALESCE(b.km_final, 0) - COALESCE(b.km_inicial, 0)) AS km_recorridos,
        CASE 
            WHEN SUM(b.cantidad) > 0 
            THEN ROUND((SUM(COALESCE(b.km_final, 0) - COALESCE(b.km_inicial, 0)) / SUM(b.cantidad)), 2)
            ELSE 0
        END AS km_por_litro
    FROM boletas b
    JOIN vehiculos v ON b.vehiculo_id = v.vehiculo_id
    WHERE b.estado = 'APROBADO'
    GROUP BY v.vehiculo_id, v.nombre, v.placa
    ORDER BY km_por_litro DESC
    """
    
    try:
        df = query_to_df(sql)
        if df.empty:
            return {"error": "Sin datos disponibles"}
        
        # Filtrar vehículos con rendimiento válido para estadísticas
        df_valido = df[df['km_por_litro'] > 0]
        
        if len(df_valido) > 0:
            promedio = df_valido['km_por_litro'].mean()
        else:
            promedio = 0
        
        def clasificar(kmpl):
            if kmpl <= 0:
                return "SIN DATOS km"
            elif promedio > 0 and kmpl > promedio * 1.2:
                return "✅ MUY EFICIENTE"
            elif promedio > 0 and kmpl > promedio:
                return "✓ EFICIENTE"
            else:
                return "❌ BAJO RENDIMIENTO"
        
        df['clasificacion'] = df['km_por_litro'].apply(clasificar)
        
        # Filtrar solo vehículos con datos válidos de km
        df_filtrado = df[df['km_por_litro'] > 0]
        
        return {
            "titulo": "RENDIMIENTO (km/litro) - VEHÍCULOS CON DATOS",
            "datos": df_filtrado.to_dict('records'),
            "estadisticas": {
                "promedio_flota": float(promedio) if promedio > 0 else 0,
                "maximo": float(df_valido['km_por_litro'].max()) if len(df_valido) > 0 else 0,
                "minimo": float(df_valido['km_por_litro'].min()) if len(df_valido) > 0 else 0,
                "desvio": float(df_valido['km_por_litro'].std()) if len(df_valido) > 0 else 0,
                "total_vehiculos": len(df),
                "vehiculos_con_datos_km": len(df_valido),
                "vehiculos_mostrando": len(df_filtrado),
                "nota": f"Mostrando solo {len(df_filtrado)} de {len(df)} vehículos con datos de kilometraje"
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
#  4. DESVIACIÓN CONSUMO (Esperado vs Real)
# ═══════════════════════════════════════════════════════════════════════════

def kpi_desviacion():
    """
    ¿Hay desviaciones en el consumo?
    Compara consumo histórico vs consumo actual - RETORNA TODOS LOS VEHÍCULOS
    """
    sql = """
    SELECT 
        v.vehiculo_id,
        v.nombre AS vehiculo,
        v.placa,
        DATE_FORMAT(b.fecha, '%Y-%m') AS mes,
        SUM(b.cantidad) AS consumo_mes,
        COUNT(b.boleta_id) AS transacciones
    FROM boletas b
    JOIN vehiculos v ON b.vehiculo_id = v.vehiculo_id
    WHERE b.estado = 'APROBADO'
    GROUP BY v.vehiculo_id, v.nombre, v.placa, mes
    ORDER BY v.vehiculo_id, mes DESC
    """
    
    try:
        df = query_to_df(sql)
        if df.empty:
            return {"error": "Sin datos disponibles"}
        
        anomalias = []
        
        for vehiculo_id in df['vehiculo_id'].unique():
            df_veh = df[df['vehiculo_id'] == vehiculo_id].sort_values('mes', ascending=False)
            
            if len(df_veh) < 2:
                continue
            
            # Últimos 2 meses vs promedio histórico
            mes_actual = df_veh.iloc[0]['consumo_mes']
            mes_anterior = df_veh.iloc[1]['consumo_mes'] if len(df_veh) > 1 else mes_actual
            
            promedio_historico = df_veh.iloc[2:]['consumo_mes'].mean() if len(df_veh) > 2 else mes_anterior
            
            desviacion_pct = ((mes_actual - promedio_historico) / promedio_historico * 100) if promedio_historico > 0 else 0
            
            # RETORNA TODOS LOS VEHÍCULOS, no solo los que superan umbral
            anomalias.append({
                "vehiculo": df_veh.iloc[0]['vehiculo'],
                "placa": df_veh.iloc[0]['placa'],
                "mes_actual": df_veh.iloc[0]['mes'],
                "consumo_actual": float(mes_actual),
                "promedio_historico": float(promedio_historico),
                "desviacion_pct": float(desviacion_pct),
                "estado": "AUMENTO" if desviacion_pct > 0 else "DISMINUCION"
            })
        
        return {
            "titulo": "DESVIACION CONSUMO",
            "anomalias": sorted(anomalias, key=lambda x: x['desviacion_pct'], reverse=True),  # Ordenado de mayor a menor desviación
            "estadisticas": {
                "total_vehiculos": len(anomalias),
                "con_aumento": len([a for a in anomalias if a['desviacion_pct'] > 0]),
                "con_disminucion": len([a for a in anomalias if a['desviacion_pct'] <= 0]),
                "promedio_desviacion": float(np.mean([a['desviacion_pct'] for a in anomalias])) if anomalias else 0,
                "promedio_aumento": float(np.mean([a['desviacion_pct'] for a in anomalias if a['desviacion_pct'] > 0])) if any(a['desviacion_pct'] > 0 for a in anomalias) else 0,
                "promedio_disminucion": float(np.mean([a['desviacion_pct'] for a in anomalias if a['desviacion_pct'] <= 0])) if any(a['desviacion_pct'] <= 0 for a in anomalias) else 0,
                "muy_aumentado_15plus": len([a for a in anomalias if a['desviacion_pct'] > 15]),
                "aumentado_5_15": len([a for a in anomalias if a['desviacion_pct'] > 5 and a['desviacion_pct'] <= 15]),
                "lig_aumentado_0_5": len([a for a in anomalias if a['desviacion_pct'] > 0 and a['desviacion_pct'] <= 5]),
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
#  5. DETECCIÓN DE ANOMALÍAS (Fuga, Robo, Mal Uso)
# ═══════════════════════════════════════════════════════════════════════════

def kpi_anomalias():
    """
    Detecta:
    - FUGA: Consumo > media + 3σ
    - ROBO: Una transacción muy grande (>50% media)
    - MAL USO: Muchas transacciones O transacciones muy desiguales
    
    Retorna con JUSTIFICACIÓN CLARA del por qué
    """
    sql = """
    SELECT 
        v.vehiculo_id,
        v.nombre AS vehiculo,
        v.placa,
        DATE_FORMAT(b.fecha, '%Y-%m') AS mes,
        COUNT(b.boleta_id) AS num_transacciones,
        SUM(b.cantidad) AS consumo_total,
        AVG(b.cantidad) AS consumo_promedio_transaccion,
        MAX(b.cantidad) AS consumo_maximo_transaccion,
        MIN(b.cantidad) AS consumo_minimo_transaccion
    FROM boletas b
    JOIN vehiculos v ON b.vehiculo_id = v.vehiculo_id
    WHERE b.estado = 'APROBADO'
    GROUP BY v.vehiculo_id, v.nombre, v.placa, mes
    ORDER BY consumo_total DESC
    """
    
    try:
        df = query_to_df(sql)
        if df.empty:
            return {"error": "Sin datos disponibles"}
        
        anomalias = []
        
        # Calcular estadísticas globales
        media_consumo = df['consumo_total'].mean()
        std_consumo = df['consumo_total'].std()
        media_transacciones = df['num_transacciones'].mean()
        media_consumo_global = media_consumo  # Para criterio ROBO
        
        for _, row in df.iterrows():
            razones = []
            criterios = []  # Para justificación clara
            tipo_principal = None
            severidad = "BAJA"
            
            # DETECTOR 1: FUGA (consumo > media + 3σ) - MÁS GRAVE
            threshold_fuga = media_consumo + 3 * std_consumo
            if row['consumo_total'] > threshold_fuga:
                razones.append("FUGA")
                criterios.append(f"Consumo {row['consumo_total']:.0f}L > {threshold_fuga:.0f}L (media+3σ)")
                tipo_principal = "FUGA"
                severidad = "CRITICA"
            
            # DETECTOR 2: ROBO (transacción muy grande - mayor al 50% de media global) - MUY GRAVE
            threshold_robo = media_consumo_global * 0.5
            if row['consumo_maximo_transaccion'] > threshold_robo:
                razones.append("ROBO")
                criterios.append(f"Transacción máxima: {row['consumo_maximo_transaccion']:.0f}L > {threshold_robo:.0f}L (50% media)")
                if tipo_principal is None:
                    tipo_principal = "ROBO"
                    severidad = "ALTA"
            
            # DETECTOR 3: MAL USO (muchas transacciones O consumo muy desigual)
            consumo_medio_transaccion = row['consumo_total'] / row['num_transacciones'] if row['num_transacciones'] > 0 else 0
            desigualdad = row['consumo_maximo_transaccion'] / consumo_medio_transaccion if consumo_medio_transaccion > 0 else 0
            
            mal_uso_detectado = False
            if row['num_transacciones'] > media_transacciones:
                razones.append("MAL_USO")
                criterios.append(f"{int(row['num_transacciones'])} transacciones > {media_transacciones:.0f} (promedio)")
                mal_uso_detectado = True
            elif desigualdad > 3:
                razones.append("MAL_USO")
                criterios.append(f"Desigualdad: {desigualdad:.1f}x > 3 (Max/Prom transacción)")
                mal_uso_detectado = True
            
            if mal_uso_detectado and tipo_principal is None:
                tipo_principal = "MAL_USO"
                severidad = "MEDIA"
            
            if razones:
                anomalias.append({
                    "vehiculo": row['vehiculo'],
                    "placa": row['placa'],
                    "mes": row['mes'],
                    "consumo": float(row['consumo_total']),
                    "transacciones": int(row['num_transacciones']),
                    "consumo_maximo": float(row['consumo_maximo_transaccion']),
                    "consumo_promedio_transaccion": float(consumo_medio_transaccion),
                    "razones": " | ".join(razones),
                    "tipo_principal": tipo_principal,
                    "severidad": severidad,
                    "criterio": criterios[0] if criterios else "Anomalía detectada",
                    "detalles": f"Transacciones: {int(row['num_transacciones'])}"
                })
        
        # Ordenar por severidad (CRITICA > ALTA > MEDIA) y luego por consumo
        orden_severidad = {"CRITICA": 3, "ALTA": 2, "MEDIA": 1}
        anomalias_ordenadas = sorted(anomalias, 
                                     key=lambda x: (orden_severidad.get(x['severidad'], 0), x['consumo']), 
                                     reverse=True)
        
        # Estadísticas
        consumo_total_anomalas = sum([a['consumo'] for a in anomalias])
        consumo_total_flota = df['consumo_total'].sum()
        
        return {
            "titulo": "ANOMALÍAS DETECTADAS",
            "anomalias": anomalias_ordenadas,
            "estadisticas": {
                "total": len(anomalias),
                "total_criticas": len([a for a in anomalias if a['severidad'] == 'CRITICA']),
                "total_robos": len([a for a in anomalias if a['tipo_principal'] == 'ROBO']),
                "total_mal_uso": len([a for a in anomalias if a['tipo_principal'] == 'MAL_USO']),
                "total_fugas": len([a for a in anomalias if a['tipo_principal'] == 'FUGA']),
                "criticas": len([a for a in anomalias if a['severidad'] == 'CRITICA']),
                "altas": len([a for a in anomalias if a['severidad'] == 'ALTA']),
                "medias": len([a for a in anomalias if a['severidad'] == 'MEDIA']),
                "consumo_total_anomalas": consumo_total_anomalas,
                "consumo_total_flota": float(consumo_total_flota),
                "vehiculo_critico": max(anomalias, key=lambda x: x['consumo']) if anomalias else None,
                "porcentaje_impacto": (consumo_total_anomalas / consumo_total_flota * 100) if consumo_total_flota > 0 else 0
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
#  6. ANÁLISIS ESTACIONAL (¿Consumo sube en ciertos meses?)
# ═══════════════════════════════════════════════════════════════════════════

def kpi_estacionalidad():
    """
    Identifica patrones mensuales y estacionales
    """
    sql = """
    SELECT 
        DATE_FORMAT(b.fecha, '%m') AS mes_numero,
        MONTHNAME(b.fecha) AS nombre_mes,
        DATE_FORMAT(b.fecha, '%Y-%m') AS mes_año,
        SUM(b.cantidad) AS consumo_total,
        COUNT(DISTINCT b.vehiculo_id) AS vehiculos_activos
    FROM boletas b
    WHERE b.estado = 'APROBADO'
    GROUP BY mes_numero, nombre_mes, mes_año
    ORDER BY mes_año DESC
    """
    
    try:
        df = query_to_df(sql)
        if df.empty:
            return {"error": "Sin datos disponibles"}
        
        promedio_general = df['consumo_total'].mean()
        
        # Agrupar por mes calendario (sin año)
        df_por_mes = df.groupby('mes_numero').agg({
            'consumo_total': ['mean', 'min', 'max', 'std'],
            'nombre_mes': 'first'
        }).reset_index()
        
        df_por_mes.columns = ['mes_numero', 'promedio', 'minimo', 'maximo', 'desvio', 'nombre_mes']
        df_por_mes = df_por_mes.sort_values('mes_numero')
        
        return {
            "titulo": "ANÁLISIS ESTACIONAL",
            "datos": df_por_mes.to_dict('records'),
            "estadisticas": {
                "promedio_mensual": float(promedio_general),
                "mes_pico": df.loc[df['consumo_total'].idxmax()]['nombre_mes'],
                "mes_bajo": df.loc[df['consumo_total'].idxmin()]['nombre_mes'],
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
#  7. ANÁLISIS FINES DE SEMANA
# ═══════════════════════════════════════════════════════════════════════════

def kpi_fines_semana():
    """
    ¿Qué unidades gastan más en fines de semana?
    """
    sql = """
    SELECT 
        v.vehiculo_id,
        v.nombre AS vehiculo,
        v.placa,
        CASE 
            WHEN DAYOFWEEK(b.fecha) IN (1,7) THEN 'FIN DE SEMANA'
            ELSE 'ENTRE SEMANA'
        END AS tipo_dia,
        SUM(b.cantidad) AS consumo,
        COUNT(b.boleta_id) AS transacciones
    FROM boletas b
    JOIN vehiculos v ON b.vehiculo_id = v.vehiculo_id
    WHERE b.estado = 'APROBADO'
    GROUP BY v.vehiculo_id, v.nombre, v.placa, tipo_dia
    ORDER BY consumo DESC
    """
    
    try:
        df = query_to_df(sql)
        if df.empty:
            return {"error": "Sin datos disponibles"}
        
        # Pivotar para comparar
        pivot = df.pivot_table(index=['vehiculo_id', 'vehiculo', 'placa'], 
                               columns='tipo_dia', 
                               values='consumo', 
                               fill_value=0)
        pivot['diferencia'] = pivot.get('FIN DE SEMANA', 0) - pivot.get('ENTRE SEMANA', 0)
        pivot = pivot.reset_index()
        pivot = pivot.sort_values('FIN DE SEMANA', ascending=False).head(15)
        
        return {
            "titulo": "CONSUMO FINES DE SEMANA",
            "datos": pivot.to_dict('records'),
            "estadisticas": {
                "mayor_consumo_fds": float(pivot['FIN DE SEMANA'].max()),
                "vehiculo": pivot.iloc[0]['vehiculo'] if len(pivot) > 0 else "N/A"
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
#  8. ÁREAS MENOS EFICIENTES
# ═══════════════════════════════════════════════════════════════════════════

def kpi_areas_eficiencia():
    """
    ¿Qué áreas son menos eficientes?
    Calcula consumo promedio mensual por vehículo en cada área
    """
    sql = """
    SELECT 
        a.nombre AS area,
        COUNT(DISTINCT b.vehiculo_id) AS vehiculos,
        COUNT(DISTINCT DATE_FORMAT(b.fecha, '%Y-%m')) AS meses_activos,
        SUM(b.cantidad) AS litros_totales,
        ROUND(SUM(b.cantidad) / COUNT(DISTINCT DATE_FORMAT(b.fecha, '%Y-%m')), 2) AS consumo_promedio_mes,
        ROUND((SUM(b.cantidad) / COUNT(DISTINCT DATE_FORMAT(b.fecha, '%Y-%m'))) / COUNT(DISTINCT b.vehiculo_id), 2) AS consumo_promedio_mes_por_vehiculo,
        SUM(b.total) AS costo_total_bs,
        ROUND(SUM(b.total) / COUNT(DISTINCT DATE_FORMAT(b.fecha, '%Y-%m')), 2) AS costo_promedio_mes
    FROM boletas b
    JOIN aperturas a ON b.apertura_id = a.apertura_id
    WHERE b.estado = 'APROBADO'
    GROUP BY a.apertura_id, a.nombre
    ORDER BY consumo_promedio_mes_por_vehiculo DESC
    """
    
    try:
        df = query_to_df(sql)
        if df.empty:
            return {"error": "Sin datos disponibles"}
        
        return {
            "titulo": "EFICIENCIA POR ÁREA",
            "datos": df.to_dict('records'),
            "estadisticas": {
                "area_mas_eficiente": df.iloc[-1]['area'],
                "area_menos_eficiente": df.iloc[0]['area'],
                "consumo_promedio_mes_por_veh": float(df['consumo_promedio_mes_por_vehiculo'].mean()),
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
#  9. PREDICCIÓN DE CONSUMO (Próximo mes)
# ═══════════════════════════════════════════════════════════════════════════

def kpi_prediccion():
    """
    Predice el consumo del próximo mes basado en tendencia
    """
    sql = """
    SELECT 
        DATE_FORMAT(b.fecha, '%Y-%m') AS mes,
        SUM(b.cantidad) AS consumo_total
    FROM boletas b
    WHERE b.estado = 'APROBADO'
    GROUP BY DATE_FORMAT(b.fecha, '%Y-%m')
    ORDER BY mes DESC
    LIMIT 12
    """
    
    try:
        df = query_to_df(sql)
        if len(df) < 2:
            return {"error": "Datos insuficientes para predicción"}
        
        # Calcular tendencia simple
        df = df.sort_values('mes')
        x = np.arange(len(df))
        y = df['consumo_total'].values.astype(float)
        
        # Regresión lineal simple
        z = np.polyfit(x, y, 1)
        pendiente = z[0]
        
        # Predicción próximo mes
        prediccion = y[-1] + pendiente
        
        tendencia = "CRECIENTE" if pendiente > 0 else "DECRECIENTE"
        
        # Calcular promedio histórico
        promedio_historico = np.mean(y)
        
        # Comparación con promedio
        diferencia_promedio = ((prediccion - promedio_historico) / promedio_historico) * 100
        
        return {
            "titulo": "PREDICCIÓN CONSUMO",
            "prediccion_proximo_mes": float(prediccion),
            "consumo_actual": float(y[-1]),
            "tendencia": tendencia,
            "cambio_porcentaje": float((pendiente / y[-1] * 100) if y[-1] > 0 else 0),
            "promedio_historico": float(promedio_historico),
            "diferencia_promedio": float(diferencia_promedio),
            "historial_meses": df.to_dict('records'),
            "pendiente": float(pendiente),
            "minimo_historico": float(np.min(y)),
            "maximo_historico": float(np.max(y)),
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
#  DASHBOARD INTEGRAL
# ═══════════════════════════════════════════════════════════════════════════

def dashboard_completo():
    """
    Retorna todos los KPIs integrados
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "titulo": "DASHBOARD KPI - SISTEMA INTEGRAL DE COMBUSTIBLE",
        "subtitulo": "Municipio de Caranavi",
        "kpis": {
            "consumo_vehiculo": kpi_consumo_vehiculo(),
            "consumo_area": kpi_consumo_area(),
            "eficiencia": kpi_eficiencia(),
            "desviacion": kpi_desviacion(),
            "anomalias": kpi_anomalias(),
            "estacionalidad": kpi_estacionalidad(),
            "fines_semana": kpi_fines_semana(),
            "areas_eficiencia": kpi_areas_eficiencia(),
            "prediccion": kpi_prediccion(),
        }
    }


if __name__ == "__main__":
    result = dashboard_completo()
    import json
    print(json.dumps(result, indent=2, default=str))
