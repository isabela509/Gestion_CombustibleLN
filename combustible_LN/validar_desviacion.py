#!/usr/bin/env python
"""Validar distribucion de desviaciones"""

from kpi_system import kpi_desviacion
import pandas as pd

kpi = kpi_desviacion()
df = pd.DataFrame(kpi['anomalias'])

print('=== ESTADISTICAS DE DESVIACION ===')
print(f'Total vehiculos: {len(df)}')
print(f'Desviacion minima: {df["desviacion_pct"].min():.2f}%')
print(f'Desviacion maxima: {df["desviacion_pct"].max():.2f}%')
print()
print('=== DISTRIBUCION POR RANGO (NUEVOS RANGOS) ===')
muy_aum = len(df[df["desviacion_pct"] > 15])
aum = len(df[(df["desviacion_pct"] > 5) & (df["desviacion_pct"] <= 15)])
lig_aum = len(df[(df["desviacion_pct"] > 0) & (df["desviacion_pct"] <= 5)])
dism = len(df[df["desviacion_pct"] <= 0])

print(f'Muy aumentado (+15%+): {muy_aum}')
print(f'Aumentado (+5-15%): {aum}')
print(f'Ligeramente aumentado (+0-5%): {lig_aum}')
print(f'Disminucion (negativo): {dism}')
print()
print('=== PRIMERAS 15 DESVIACIONES ===')
print(df[['vehiculo', 'placa', 'desviacion_pct']].head(15).to_string())
print()
print('=== VEHICULOS CON DESVIACION ENTRE 0-5% ===')
rango_5 = df[(df["desviacion_pct"] > 0) & (df["desviacion_pct"] <= 5)]
if len(rango_5) > 0:
    print(rango_5[['vehiculo', 'placa', 'desviacion_pct']].to_string())
else:
    print('NINGUNO ENCONTRADO')

print()
print('=== VEHICULOS CON DESVIACION ENTRE 5-15% ===')
rango_15 = df[(df["desviacion_pct"] > 5) & (df["desviacion_pct"] <= 15)]
if len(rango_15) > 0:
    print(rango_15[['vehiculo', 'placa', 'desviacion_pct']].to_string())
else:
    print('NINGUNO ENCONTRADO')
