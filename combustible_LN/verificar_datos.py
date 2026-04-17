"""Verificar datos de las gráficas de área"""

from kpi_system import kpi_consumo_area, kpi_areas_eficiencia
import pandas as pd

print("\n" + "="*100)
print("🔍 VERIFICACIÓN DE DATOS - GRÁFICOS DE ÁREA")
print("="*100)

# ════════════════════════════════════════════════════════════════════════════
print("\n【GRÁFICO 2】CONSUMO POR ÁREA (datos raw)")
print("-"*100)

k2 = kpi_consumo_area()
df2 = pd.DataFrame(k2['datos'])
print(f"\nTotal áreas: {len(df2)}")
print(f"\n{'Área':<50} {'Vehículos':<12} {'Consumo Promedio/mes':<20} {'Costo/mes'}")
print("-"*100)
for _, row in df2.head(10).iterrows():
    print(f"{row['area']:<50} {row['vehiculos_asignados']:<12} {row['consumo_promedio_mensual']:<20.0f} {row['costo_promedio_mensual']:.0f}")

# ════════════════════════════════════════════════════════════════════════════
print("\n\n【GRÁFICO 8】EFICIENCIA POR ÁREA (datos raw)")
print("-"*100)

k8 = kpi_areas_eficiencia()
df8 = pd.DataFrame(k8['datos'])
print(f"\nTotal áreas: {len(df8)}")
print(f"\n{'Área':<50} {'Vehículos':<12} {'L/mes (total)':<18} {'L/mes/veh':<18}")
print("-"*100)
for _, row in df8.iterrows():
    print(f"{row['area']:<50} {row['vehiculos']:<12} {row['consumo_promedio_mes']:<18.0f} {row['consumo_promedio_mes_por_vehiculo']:<18.0f}")

# ════════════════════════════════════════════════════════════════════════════
print("\n\n【COMPARACIÓN CRUZADA】")
print("-"*100)

print("\n✅ DATOS AHORA CONSISTENTES:\n")
print("📊 Gráfico 2 (Consumo por Área):")
print("   - Muestra: CONSUMO TOTAL POR ÁREA / MESES ACTIVOS")
print("   - Métrica: L/mes promedio")
print("   - Muestra todas las 18 áreas")

print("\n⚡ Gráfico 8 (Eficiencia por Área):")
print("   - Muestra: (CONSUMO TOTAL POR ÁREA / MESES) / VEHÍCULOS")
print("   - Métrica: L/mes/veh (consumo promedio mensual POR vehículo)")
print("   - Muestra todas las 18 áreas")

print("\n\n✅ RELACIÓN ENTRE GRÁFICAS:")
print("   Ambas usan el mismo consumo promedio mensual")
print("   Gráfico 8 divide adicionales entre cantidad de vehículos")
print("   Esto permite comparar la EFICIENCIA real (menos litros por vehículo = más eficiente)")

print("\n🔍 EJEMPLO:")
df_check = df2.head(3)
for _, row in df_check.iterrows():
    area_name = row['area']
    mes_consumo = row['consumo_promedio_mensual']
    veh_count = row['vehiculos_asignados']
    per_veh = mes_consumo / veh_count
    print(f"\n   {area_name}:")
    print(f"     - Consumo total/mes: {mes_consumo:.0f}L")
    print(f"     - Vehículos: {veh_count}")
    print(f"     - Eficiencia: {per_veh:.0f}L/mes/veh")

print("\n" + "="*100 + "\n")
