"""
Verificar rendimiento km/L de TODOS los vehículos en la BD
"""

from database import query_to_df
import pandas as pd

print("\n" + "="*120)
print("🔍 VERIFICACIÓN RENDIMIENTO KM/L - TODOS LOS VEHÍCULOS")
print("="*120)

# ════════════════════════════════════════════════════════════════════════════
# 1. CONTAR VEHÍCULOS EN BD
# ════════════════════════════════════════════════════════════════════════════

sql_total = """
SELECT COUNT(DISTINCT vehiculo_id) AS total_vehiculos
FROM boletas
WHERE estado = 'APROBADO'
"""

df_total = query_to_df(sql_total)
total_veh = df_total.iloc[0]['total_vehiculos']
print(f"\n【1】TOTAL DE VEHÍCULOS EN BD: {total_veh}")

# ════════════════════════════════════════════════════════════════════════════
# 2. OBTENER RENDIMIENTO DE TODOS LOS VEHÍCULOS
# ════════════════════════════════════════════════════════════════════════════

sql_rendimiento = """
SELECT 
    v.vehiculo_id,
    v.nombre AS vehiculo,
    v.placa,
    COUNT(DISTINCT b.boleta_id) AS viajes,
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

df_rend = query_to_df(sql_rendimiento)

print(f"\n【2】TODOS LOS VEHÍCULOS - RENDIMIENTO km/L:")
print("-"*120)
print(f"\n{'#':<4} {'Vehículo':<35} {'Placa':<12} {'Viajes':<8} {'Litros':<12} {'km Recorridos':<18} {'km/L':<10}")
print("-"*120)

for i, (_, row) in enumerate(df_rend.iterrows(), 1):
    km_litro = row['km_por_litro'] if row['km_por_litro'] else 0
    print(f"{i:<4} {str(row['vehiculo']):<35} {str(row['placa']):<12} {row['viajes']:<8} {row['litros_consumidos']:<12.0f} {row['km_recorridos']:<18.0f} {km_litro:<10.2f}")

# ════════════════════════════════════════════════════════════════════════════
# 3. ESTADÍSTICAS
# ════════════════════════════════════════════════════════════════════════════

print("\n" + "="*120)
print("📊 ESTADÍSTICAS DE RENDIMIENTO:")
print("="*120)

# Filtrar solo vehículos con rendimiento válido (litros > 0)
df_valido = df_rend[df_rend['litros_consumidos'] > 0]

print(f"\nTotal vehículos: {len(df_rend)}")
print(f"Vehículos con datos válidos: {len(df_valido)}")
print(f"Vehículos sin datos válidos: {len(df_rend) - len(df_valido)}")

if len(df_valido) > 0:
    print(f"\nPromedios:")
    print(f"  - Promedio km/L (toda flota): {df_valido['km_por_litro'].mean():.2f}")
    print(f"  - Máximo: {df_valido['km_por_litro'].max():.2f}")
    print(f"  - Mínimo: {df_valido['km_por_litro'].min():.2f}")
    print(f"  - Mediana: {df_valido['km_por_litro'].median():.2f}")

# ════════════════════════════════════════════════════════════════════════════
# 4. COMPARACIÓN CON KPI 3
# ════════════════════════════════════════════════════════════════════════════

print("\n" + "="*120)
print("🔄 COMPARACIÓN CON KPI 3:")
print("="*120)

from kpi_system import kpi_eficiencia

kpi3_result = kpi_eficiencia()
if 'datos' in kpi3_result:
    print(f"\nKPI 3 retorna: {len(kpi3_result['datos'])} registros")
    print(f"BD tiene: {len(df_rend)} vehículos")
    print(f"\n⚠️  DIFERENCIA: KPI 3 solo muestra {len(kpi3_result['datos'])} de {len(df_rend)} vehículos")
else:
    print(f"\nKPI 3 tiene error o no retorna datos")

print("\n" + "="*120 + "\n")

# Guardar para referencia
df_rend.to_csv('todos_vehiculos_rendimiento.csv', index=False, encoding='utf-8')
print("✅ Datos guardados en: todos_vehiculos_rendimiento.csv\n")
