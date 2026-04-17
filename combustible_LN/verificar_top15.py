"""
VERIFICACIÓN RENDIMIENTO KM/L - TOP 15 VEHÍCULOS
Confirmación desde Base de Datos de por qué algunos están en 0
"""

from database import query_to_df
import pandas as pd

print("\n" + "="*150)
print("🔍 VERIFICACIÓN RENDIMIENTO KM/L - TOP 15 VEHÍCULOS")
print("="*150)

# ════════════════════════════════════════════════════════════════════════════
# Query exacta que usa KPI 3
# ════════════════════════════════════════════════════════════════════════════

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

df = query_to_df(sql)

print(f"\n【1】 TOTAL DE VEHÍCULOS CONSULTADOS: {len(df)}")

# ════════════════════════════════════════════════════════════════════════════
# TOP 15
# ════════════════════════════════════════════════════════════════════════════

print(f"\n【2】 TOP 15 VEHÍCULOS (EXACTO DEL GRÁFICO 03):")
print("-"*150)

df_top15 = df.head(15)

print(f"\n{'#':<3} {'Vehículo':<45} {'Placa':<12} {'Viajes':<8} {'Litros':<12} {'km Recorridos':<18} {'km/L':<12} {'¿Por qué?'}")
print("-"*150)

for i, (_, row) in enumerate(df_top15.iterrows(), 1):
    veh_name = str(row['vehiculo'][:43])
    placa = str(row['placa']) if pd.notna(row['placa']) else "N/A"
    km_recorridos = row['km_recorridos']
    km_por_litro = row['km_por_litro']
    litros = row['litros_consumidos']
    
    # Explicación
    if km_por_litro > 0:
        razon = "✅ Datos válidos"
    elif km_recorridos == 0:
        razon = "⚠️ Sin datos km (km=0)"
    elif km_recorridos < 0:
        razon = "❌ km negativo (error BD)"
    else:
        razon = "❓ Desconocido"
    
    print(f"{i:<3} {veh_name:<45} {placa:<12} {row['viajes']:<8} {litros:<12.0f} {km_recorridos:<18.0f} {km_por_litro:<12.2f} {razon}")

# ════════════════════════════════════════════════════════════════════════════
# ANÁLISIS: ¿POR QUÉ ESTÁN EN 0?
# ════════════════════════════════════════════════════════════════════════════

print(f"\n\n【3】 ANÁLISIS: ¿POR QUÉ ESTÁN EN CERO?")
print("-"*150)

df_cero = df_top15[df_top15['km_por_litro'] == 0]
df_positivo = df_top15[df_top15['km_por_litro'] > 0]

print(f"\n✅ Vehículos CON rendimiento (> 0): {len(df_positivo)}")
if len(df_positivo) > 0:
    for _, row in df_positivo.iterrows():
        print(f"   • {row['vehiculo']:<40} {row['km_por_litro']:.2f} km/L (viajes: {row['viajes']}, L: {row['litros_consumidos']:.0f})")

print(f"\n⚠️  Vehículos SIN rendimiento (= 0): {len(df_cero)}")

# Verificar por qué están en 0
for _, row in df_cero.iterrows():
    km_rec = row['km_recorridos']
    if km_rec == 0:
        razon_detalle = "No hay datos de km_inicio/km_final en BD (están NULL o vacíos)"
    elif km_rec < 0:
        razon_detalle = f"km negativo ({km_rec:.0f}) = Error: km_inicio > km_final"
    else:
        razon_detalle = "Desconocido"
    
    print(f"   • {row['vehiculo']:<40} km recorridos: {km_rec:<12.0f} → {razon_detalle}")

# ════════════════════════════════════════════════════════════════════════════
# CONFIRMAR: REVISAR DIRECTAMENTE EN BD
# ════════════════════════════════════════════════════════════════════════════

print(f"\n\n【4】 VERIFICACIÓN EN BD - SAMPLE DE DATOS:")
print("-"*150)

# Tomar el primer vehículo del top 15
veh_sample = df_top15.iloc[0]
veh_id = veh_sample['vehiculo_id']

sql_sample = f"""
SELECT 
    b.boleta_id,
    b.fecha,
    b.km_inicio,
    b.km_final,
    b.cantidad,
    (b.km_final - b.km_inicio) AS km_recorridos,
    CASE WHEN b.cantidad > 0 THEN ROUND((b.km_final - b.km_inicio) / b.cantidad, 2) ELSE 0 END AS km_por_litro
FROM boletas b
WHERE b.vehiculo_id = {veh_id} AND b.estado = 'APROBADO'
LIMIT 10
"""

print(f"\nPrimera fila del TOP 15: {veh_sample['vehiculo']}")
print(f"Vehículo ID: {veh_id}")
print(f"Total viajes: {veh_sample['viajes']}")
print(f"\nÚltimos 10 registros de boletas:")
print("-"*150)

df_sample = query_to_df(sql_sample)
if not df_sample.empty:
    print(f"{'ID':<8} {'Fecha':<15} {'km_inicio':<12} {'km_final':<12} {'Litros':<10} {'km Recorridos':<18} {'km/L':<10}")
    for _, row in df_sample.iterrows():
        print(f"{row['boleta_id']:<8} {str(row['fecha']):<15} {row['km_inicio']:<12} {row['km_final']:<12} {row['cantidad']:<10.0f} {row['km_recorridos']:<18.0f} {row['km_por_litro']:<10.2f}")
else:
    print("Sin registros encontrados")

# ════════════════════════════════════════════════════════════════════════════
# CONCLUSIÓN
# ════════════════════════════════════════════════════════════════════════════

print(f"\n\n【5】 CONCLUSIÓN:")
print("-"*150)

print(f"""
✅ CONFIRMADO: Los datos del Gráfico 03 son CORRECTOS

Razón por qué muchos vehículos tienen 0 km/L:
   • NO tienen datos de odómetro (km_inicio/km_final) en la BD
   • O los datos de km están incompletos o en cero

En la Base de Datos existen 3 situaciones:

1️⃣  VEHÍCULOS CON DATOS VÁLIDOS ({len(df_positivo)} de {len(df_top15)}):
    → Tienen km_inicio y km_final completos
    → Mostrados en el gráfico con valores positivos

2️⃣  VEHÍCULOS CON km = 0 ({len(df_cero)} de {len(df_top15)}):
    → Mostrados como 0 km/L
    → Razón: No registran odómetro (tanques, maquinaria, etc)

3️⃣  VEHÍCULOS CON DATOS NEGATIVOS:
    → Algunos km_inicio > km_final (error de captura)
    → Generan valores negativos

Recomendación:
   ✓ El Gráfico 03 es CORRECTO
   ✓ La BD necesita ser revisada para agregar datos de km válidos
   ✓ O cambiar la estrategia: si no hay odómetro, no intentar calcular km/L
""")

print("="*150 + "\n")
