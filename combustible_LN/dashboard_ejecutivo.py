"""
╔════════════════════════════════════════════════════════════════════════════╗
║ DASHBOARD EJECUTIVO - PRESENTACIÓN AL CLIENTE                            ║
║ Interfaz limpia y profesional con todos los KPIs integrados              ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import json
from datetime import datetime
from kpi_system import dashboard_completo


def mostrar_dashboard():
    """Muestra el dashboard ejecutivo en terminal"""
    
    data = dashboard_completo()
    
    print("\n" + "="*90)
    print("╔" + "="*88 + "╗")
    print("║" + " "*88 + "║")
    print("║" + f"  DASHBOARD KPI - SISTEMA INTEGRAL DE COMBUSTIBLE".center(88) + "║")
    print("║" + f"  Municipio de Caranavi | {data['timestamp']}".center(88) + "║")
    print("║" + " "*88 + "║")
    print("╚" + "="*88 + "╝")
    
    kpis = data['kpis']
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 1: CONSUMO POR VEHÍCULO
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【1】CONSUMO POR VEHÍCULO")
    print("-" * 90)
    k = kpis['consumo_vehiculo']
    
    if 'error' not in k:
        est = k['estadisticas']
        print(f"  📊 Total Vehículos: {est['total_vehiculos']}")
        print(f"  📈 Promedio Flota: {est['promedio_flota']:.2f} L/mes")
        print(f"  🔴 Máximo Consumo: {est['consumo_maximo']:.2f} L/mes")
        print(f"  🟢 Mínimo Consumo: {est['consumo_minimo']:.2f} L/mes")
        print(f"\n  Top 5 Mayores Consumidores:")
        for i, veh in enumerate(k['datos'][:5], 1):
            print(f"    {i}. {veh['vehiculo']} ({veh['placa']}): {veh['consumo_promedio_mensual']:.0f}L")
    else:
        print(f"  ❌ {k['error']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 2: CONSUMO POR ÁREA
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【2】CONSUMO POR ÁREA DE TRABAJO")
    print("-" * 90)
    k = kpis['consumo_area']
    
    if 'error' not in k:
        est = k['estadisticas']
        print(f"  📍 Total Áreas: {est['total_areas']}")
        print(f"  📈 Promedio Área: {est['promedio_area']:.2f} L/mes")
        print(f"  🔴 Área Mayor Consumo: {est['area_mayor_consumo']}")
        print(f"     Consumo: {est['consumo_mayor_area']:.2f} L/mes")
        print(f"\n  Top 5 Áreas Mayor Consumo:")
        for i, area in enumerate(k['datos'][:5], 1):
            print(f"    {i}. {area['area']}: {area['consumo_promedio_mensual']:.0f}L ({area['clasificacion']})")
    else:
        print(f"  ❌ {k['error']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 3: EFICIENCIA
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【3】RENDIMIENTO (km/litro) - EFICIENCIA")
    print("-" * 90)
    k = kpis['eficiencia']
    
    if 'alerta' in k:
        print(f"  ⚠️  {k['alerta']}")
    elif 'error' in k:
        print(f"  ❌ {k['error']}")
    else:
        est = k['estadisticas']
        print(f"  📊 Promedio Flota: {est['promedio_flota']:.2f} km/L")
        print(f"  ✅ Máximo: {est['maximo']:.2f} km/L")
        print(f"  ❌ Mínimo: {est['minimo']:.2f} km/L")
        print(f"  📐 Desviación: {est['desvio']:.2f}")
        print(f"\n  Top 5 Vehículos Más Eficientes:")
        for i, veh in enumerate(k['datos'][:5], 1):
            print(f"    {i}. {veh['vehiculo']} ({veh['placa']}): {veh['km_por_litro']:.1f} km/L")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 4: DESVIACIÓN
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【4】DESVIACIÓN: Consumo Esperado vs Real")
    print("-" * 90)
    k = kpis['desviacion']
    
    if 'error' not in k:
        est = k['estadisticas']
        print(f"  ⚠️  Total Anomalías Detectadas: {est['total_anomalias']}")
        print(f"  🔴 Alertas Críticas (>50%): {est['alertas_criticas']}")
        if k['anomalias']:
            print(f"\n  Principales Desviaciones:")
            for i, anom in enumerate(k['anomalias'][:5], 1):
                print(f"    {i}. {anom['vehiculo']} ({anom['placa']}) - {anom['mes_actual']}")
                print(f"       Desviación: {anom['desviacion_pct']:+.1f}% | {anom['estado']}")
    else:
        print(f"  ❌ {k['error']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 5: ANOMALÍAS CRÍTICAS
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【5】🚨 ANOMALÍAS CRÍTICAS: Fuga, Robo, Mal Uso")
    print("-" * 90)
    k = kpis['anomalias']
    
    if 'error' not in k:
        est = k['estadisticas']
        print(f"  Total Anomalías Detectadas: {est['total']}")
        print(f"  🔴 Severidad ALTA: {est['criticas']}")
        print(f"  🟠 Severidad MEDIA: {est['medias']}")
        
        if k['anomalias']:
            print(f"\n  Anomalías Críticas:")
            for i, anom in enumerate(k['anomalias'][:6], 1):
                if anom['severidad'] == 'ALTA':
                    print(f"    {i}. 🔴 {anom['vehiculo']} ({anom['placa']}) - {anom['mes']}")
                    print(f"       Consumo: {anom['consumo']:.0f}L | Transacciones: {anom['transacciones']}")
                    print(f"       Razón: {anom['razones']}")
    else:
        print(f"  ❌ {k['error']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 6: ESTACIONALIDAD
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【6】ESTACIONALIDAD: ¿Consumo sube en ciertos meses?")
    print("-" * 90)
    k = kpis['estacionalidad']
    
    if 'error' not in k:
        est = k['estadisticas']
        print(f"  📊 Consumo Promedio Mensual: {est['promedio_mensual']:,.0f}L")
        print(f"  🔴 Mes Pico: {est['mes_pico']}")
        print(f"  🟢 Mes Bajo: {est['mes_bajo']}")
        print(f"\n  Consumo Promedio por Mes:")
        for i, mes in enumerate(k['datos'], 1):
            barra = "█" * int(mes['promedio'] / 1000)
            print(f"    {mes['nombre_mes']:>10}: {barra} {mes['promedio']:,.0f}L")
    else:
        print(f"  ❌ {k['error']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 7: FINES DE SEMANA
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【7】FINES DE SEMANA: ¿Qué unidades gastan más?")
    print("-" * 90)
    k = kpis['fines_semana']
    
    if 'error' not in k:
        est = k['estadisticas']
        print(f"  🚗 Mayor Consumo Fin de Semana: {est['mayor_consumo_fds']:.0f}L")
        print(f"  🚙 Vehículo: {est['vehiculo']}")
        print(f"\n  Top 5 Consumo Fin de Semana:")
        for i, veh in enumerate(k['datos'][:5], 1):
            if 'FIN DE SEMANA' in veh:
                fds = veh['FIN DE SEMANA']
                entre = veh.get('ENTRE SEMANA', 0)
                print(f"    {i}. {veh['vehiculo']}: FDS={fds:.0f}L | Entre Semana={entre:.0f}L")
    else:
        print(f"  ❌ {k['error']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 8: ÁREAS EFICIENCIA
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【8】EFIENCIA POR ÁREA: ¿Qué áreas son menos eficientes?")
    print("-" * 90)
    k = kpis['areas_eficiencia']
    
    if 'error' not in k:
        est = k['estadisticas']
        print(f"  💰 Costo Promedio: {est['costo_promedio']:.2f} Bs/vehículo")
        print(f"  🔴 Área Más Costosa: {est['area_mas_costosa']}")
        print(f"\n  Top 10 Áreas con Mayor Costo:")
        for i, area in enumerate(k['datos'][:10], 1):
            print(f"    {i}. {area['area']}: {area['costo_por_vehiculo']:.2f} Bs/veh")
    else:
        print(f"  ❌ {k['error']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 9: PREDICCIÓN
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【9】📊 PREDICCIÓN: Combustible Necesario Próximo Mes")
    print("-" * 90)
    k = kpis['prediccion']
    
    if 'error' not in k:
        print(f"  📈 Consumo Actual (últimas 6 meses): {k['consumo_actual']:,.0f}L")
        print(f"  🔮 Predicción Próximo Mes: {k['prediccion_proximo_mes']:,.0f}L")
        print(f"  📊 Tendencia: {k['tendencia']}")
        print(f"  📉 Cambio: {k['cambio_porcentaje']:+.2f}%")
    else:
        print(f"  ❌ {k['error']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  RESUMEN EJECUTIVO
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n" + "="*90)
    print("【 RESUMEN EJECUTIVO 】")
    print("="*90)
    
    print(f"""
  ✅ HALLAZGOS PRINCIPALES:
   
    1️⃣  Consumo por Vehículo:
        - Total de vehículos monitoreados: {kpis['consumo_vehiculo']['estadisticas']['total_vehiculos']}
        - Promedio de consumo: {kpis['consumo_vehiculo']['estadisticas']['promedio_flota']:.0f}L/mes
    
    2️⃣  Detección de Anomalías:
        - Anomalías críticas detectadas: {kpis['anomalias']['estadisticas']['criticas']}
        - Recomendación: REVISAR MANTENIMIENTO Y COMBUSTIBLES
    
    3️⃣  Eficiencia (km/L):
        - Sistema operando {"normalmente ✅" if 'alerta' not in kpis['eficiencia'] else "⚠️  CON LIMITACIONES"}
    
    4️⃣  Predicción:
        - Consumo estimado próximo mes: {kpis['prediccion']['prediccion_proximo_mes']:,.0f}L
        - Tendencia: {kpis['prediccion']['tendencia']}
  
  🎯 RECOMENDACIONES:
    • Revisar vehículos con mayor consumo
    • Investigar anomalías críticas (posible fuga/robo)
    • Optimizar rutas en áreas de alto consumo
    • Implementar planes de mantenimiento preventivo
    • Capacitar conductores en eficiencia de combustible

""")
    
    print("="*90 + "\n")


if __name__ == "__main__":
    mostrar_dashboard()
