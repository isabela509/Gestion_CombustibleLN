"""
VALIDACIÓN DE DATOS - Sistema de Combustible
"""

import pandas as pd
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

# Suprimir warnings de pandas
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*70)
print("  VALIDACIÓN DE DATOS - SISTEMA DE COMBUSTIBLE")
print("="*70)

resultados = []

# 1. CONSUMO POR ÁREA
print("\n[1] Consumo por área...")
try:
    df = consumo_por_area()
    resultados.append({
        "Función": "consumo_por_area()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "consumo_por_area()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 2. CONSUMO POR VEHÍCULO
print("[2] Consumo por vehículo...")
try:
    df = consumo_por_vehiculo()
    resultados.append({
        "Función": "consumo_por_vehiculo()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "consumo_por_vehiculo()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 3. CONSUMO MENSUAL
print("[3] Consumo mensual...")
try:
    df = consumo_mensual()
    resultados.append({
        "Función": "consumo_mensual()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "consumo_mensual()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 4. CONSUMO POR CONDUCTOR
print("[4] Consumo por conductor...")
try:
    df = consumo_por_conductor()
    resultados.append({
        "Función": "consumo_por_conductor()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "consumo_por_conductor()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 5. STOCK ACTUAL
print("[5] Stock actual...")
try:
    df = stock_actual()
    resultados.append({
        "Función": "stock_actual()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "stock_actual()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 6. TOP 10 VEHÍCULOS
print("[6] Top 10 vehículos...")
try:
    df = top10_vehiculos()
    resultados.append({
        "Función": "top10_vehiculos()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "top10_vehiculos()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 7. DETECTAR EXCESOS
print("[7] Detectar excesos...")
try:
    df = detectar_excesos()
    resultados.append({
        "Función": "detectar_excesos()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "detectar_excesos()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 8. DETECTAR ANOMALÍAS POR VEHÍCULO
print("[8] Detectar anomalías por vehículo...")
try:
    df = detectar_anomalias_por_vehiculo()
    resultados.append({
        "Función": "detectar_anomalias_por_vehiculo()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "detectar_anomalias_por_vehiculo()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 9. EFICIENCIA VEHÍCULOS
print("[9] Eficiencia vehículos...")
try:
    df = eficiencia_vehiculos()
    resultados.append({
        "Función": "eficiencia_vehiculos()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "eficiencia_vehiculos()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 10. BENCHMARKS
print("[10] Benchmarks por tipo vehículo...")
try:
    df = benchmarks_por_tipo_vehiculo()
    resultados.append({
        "Función": "benchmarks_por_tipo_vehiculo()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "benchmarks_por_tipo_vehiculo()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 11. TENDENCIA PREDICTIVA
print("[11] Tendencia predictiva (DIESEL)...")
try:
    df = tendencia_predictiva("DIESEL")
    resultados.append({
        "Función": "tendencia_predictiva()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "tendencia_predictiva()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 12. COSTOS POR MES ÁREA
print("[12] Costos por mes-área...")
try:
    df = costos_por_mes_area()
    resultados.append({
        "Función": "costos_por_mes_area()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "costos_por_mes_area()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 13. INGRESOS COMBUSTIBLE
print("[13] Ingresos combustible...")
try:
    df = ingresos_combustible()
    resultados.append({
        "Función": "ingresos_combustible()",
        "Estado": "✅ OK",
        "Filas": len(df),
        "Columnas": ", ".join(df.columns.tolist()),
        "Ejemplo": f"{df.iloc[0].to_dict()}" if len(df) > 0 else "Sin datos"
    })
    print(f"  ✓ {len(df)} filas")
except Exception as e:
    resultados.append({
        "Función": "ingresos_combustible()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# 14. RESUMEN EJECUTIVO
print("[14] Resumen ejecutivo...")
try:
    datos = resumen_ejecutivo()
    resultados.append({
        "Función": "resumen_ejecutivo()",
        "Estado": "✅ OK",
        "Filas": len(datos),
        "Columnas": ", ".join(datos[0].keys()) if datos else "N/A",
        "Ejemplo": str(datos[0]) if datos else "Sin datos"
    })
    print(f"  ✓ {len(datos)} registros")
except Exception as e:
    resultados.append({
        "Función": "resumen_ejecutivo()",
        "Estado": "❌ ERROR",
        "Filas": 0,
        "Columnas": "",
        "Ejemplo": str(e)
    })
    print(f"  ✗ {str(e)[:60]}...")

# TABLA RESUMEN
print("\n" + "="*70)
print("  TABLA RESUMEN DE RESULTADOS")
print("="*70 + "\n")

df_resultados = pd.DataFrame(resultados)
print(df_resultados.to_string(index=False))

# Guardar en CSV
df_resultados.to_csv("validacion_resultados.csv", index=False, encoding="utf-8-sig")
print(f"\n✓ Tabla guardada en: validacion_resultados.csv")

# Estadísticas
ok = (df_resultados["Estado"] == "✅ OK").sum()
error = (df_resultados["Estado"] == "❌ ERROR").sum()
total_filas = df_resultados[df_resultados["Estado"] == "✅ OK"]["Filas"].sum()

print(f"\n📊 ESTADÍSTICAS:")
print(f"  • Funciones OK: {ok}/14")
print(f"  • Funciones con ERROR: {error}/14")
print(f"  • Total de filas disponibles: {total_filas:,}")

print("\n" + "="*70 + "\n")
