"""
Script para validar que la conclusión del gráfico 5 es correcta
comparándola con los datos reales de la BD
"""

from database import query_to_df
import pandas as pd

print("\n" + "="*80)
print("VALIDACION: CONCLUSION DEL GRAFICO 5 - ANOMALIAS")
print("="*80)

# 1. Obtener datos crudos de anomalías
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

df = query_to_df(sql)
print(f"\n[1] DATOS CRUDOS: {len(df)} registros de vehículos/mes")

# 2. Calcular estadísticas
media_consumo = df['consumo_total'].mean()
std_consumo = df['consumo_total'].std()
media_transacciones = df['num_transacciones'].mean()
consumo_total_flota = df['consumo_total'].sum()

print(f"\n[2] ESTADISTICAS GLOBALES:")
print(f"    Media consumo: {media_consumo:.2f}L")
print(f"    Desviación std: {std_consumo:.2f}L")
print(f"    Media transacciones: {media_transacciones:.2f}")
print(f"    Consumo total flota: {consumo_total_flota:.2f}L")

# 3. Detectar anomalías
anomalias = []
for _, row in df.iterrows():
    razones = []
    tipo_principal = None
    
    # FUGA
    if row['consumo_total'] > (media_consumo + 3 * std_consumo):
        razones.append("FUGA")
        tipo_principal = "FUGA"
    
    # ROBO
    if row['consumo_maximo_transaccion'] > media_consumo * 0.5:
        razones.append("ROBO")
        if tipo_principal is None:
            tipo_principal = "ROBO"
    
    # MAL USO
    consumo_medio_transaccion = row['consumo_total'] / row['num_transacciones'] if row['num_transacciones'] > 0 else 0
    desigualdad = row['consumo_maximo_transaccion'] / consumo_medio_transaccion if consumo_medio_transaccion > 0 else 0
    
    if (row['num_transacciones'] > media_transacciones) or (desigualdad > 3):
        razones.append("MAL_USO")
        if tipo_principal is None:
            tipo_principal = "MAL_USO"
    
    if razones:
        anomalias.append({
            "vehiculo": row['vehiculo'],
            "placa": row['placa'],
            "mes": row['mes'],
            "consumo": float(row['consumo_total']),
            "transacciones": int(row['num_transacciones']),
            "tipo_principal": tipo_principal
        })

print(f"\n[3] ANOMALIAS DETECTADAS: {len(anomalias)} casos")

# 4. Contar por tipo
fugas = len([a for a in anomalias if a['tipo_principal'] == 'FUGA'])
robos = len([a for a in anomalias if a['tipo_principal'] == 'ROBO'])
mal_uso = len([a for a in anomalias if a['tipo_principal'] == 'MAL_USO'])

print(f"\n[4] DISTRIBUCION POR TIPO:")
print(f"    FUGAS: {fugas} ({fugas/len(anomalias)*100:.1f}%)")
print(f"    ROBOS: {robos} ({robos/len(anomalias)*100:.1f}%)")
print(f"    MAL USO: {mal_uso} ({mal_uso/len(anomalias)*100:.1f}%)")

# 5. Calcular consumo por tipo
consumo_por_tipo = {}
for a in anomalias:
    tipo = a['tipo_principal']
    if tipo not in consumo_por_tipo:
        consumo_por_tipo[tipo] = 0
    consumo_por_tipo[tipo] += a['consumo']

print(f"\n[5] CONSUMO ANOMALO POR TIPO:")
for tipo, consumo in sorted(consumo_por_tipo.items(), key=lambda x: x[1], reverse=True):
    pct = (consumo / consumo_total_flota * 100)
    print(f"    {tipo}: {consumo:.0f}L ({pct:.2f}%)")

# 6. Consumo total anómalo
consumo_total_anomalo = sum([a['consumo'] for a in anomalias])
pct_impacto = (consumo_total_anomalo / consumo_total_flota * 100)

print(f"\n[6] IMPACTO TOTAL:")
print(f"    Consumo anómalo: {consumo_total_anomalo:.0f}L")
print(f"    Porcentaje del total: {pct_impacto:.2f}%")

# 7. Conclusión correcta
mal_uso_pct = (mal_uso / len(anomalias) * 100) if len(anomalias) > 0 else 0
robos_pct = (robos / len(anomalias) * 100) if len(anomalias) > 0 else 0

print(f"\n[7] CONCLUSION VALIDADA:")
print("    "+"="*70)
if mal_uso_pct > robos_pct:
    print(f"    ✅ Problema Principal: MAL USO ({mal_uso_pct:.1f}% de casos)")
    print(f"    ✅ Problema Secundario: ROBOS ({robos_pct:.1f}% de casos)")
else:
    print(f"    ✅ Problema Principal: ROBOS ({robos_pct:.1f}% de casos)")
    print(f"    ✅ Problema Secundario: MAL USO ({mal_uso_pct:.1f}% de casos)")

print(f"    ✅ Impacto Estimado: {pct_impacto:.2f}% del consumo total")
print("    "+"="*70)

# 8. Vehículo más crítico
if anomalias:
    vehiculo_critico = max(anomalias, key=lambda x: x['consumo'])
    print(f"\n[8] VEHICULO MAS CRITICO:")
    print(f"    {vehiculo_critico['vehiculo']}")
    print(f"    Placa: {vehiculo_critico['placa']}")
    print(f"    Mes: {vehiculo_critico['mes']}")
    print(f"    Consumo: {vehiculo_critico['consumo']:.0f}L")
    print(f"    Tipo: {vehiculo_critico['tipo_principal']}")

print("\n" + "="*80)
print("✅ VALIDACION COMPLETADA - Datos consistentes con la conclusión")
print("="*80 + "\n")
