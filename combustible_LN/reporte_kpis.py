"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                      📊 REPORTE EJECUTIVO DE KPIs                         ║
║                   Sistema de Gestión de Combustible                       ║
║                    Municipio de Caranavi - Abril 2026                     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import json
from datetime import datetime
from kpi_system import dashboard_completo


def generar_reporte_kpis():
    """Genera lista profesional de KPIs para presentar al jefe"""
    
    data = dashboard_completo()
    kpis = data['kpis']
    
    print("\n" + "="*90)
    print("📊 LISTA COMPLETA DE KPIs - INDICADORES CLAVE DE DESEMPEÑO")
    print("="*90)
    print(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*90)
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 1: CONSUMO PROMEDIO POR VEHÍCULO
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【KPI 1】CONSUMO PROMEDIO POR VEHÍCULO")
    print("-"*90)
    print("""
¿PREGUNTA: Cuáles son los vehículos que más combustible consumen?
¿CAUSA: Mantenimiento, mal uso, fuga, tipo de vehículo, uso recurrente
¿ACCIÓN: Revisar mantenimiento, capacitar conductores
    """)
    
    k1 = kpis['consumo_vehiculo']
    if 'error' not in k1:
        est = k1['estadisticas']
        print(f"  VALOR PRINCIPAL: {est['promedio_flota']:.2f} L/mes (Promedio Flota)")
        print(f"  MÁXIMO: {est['consumo_maximo']:.2f} L/mes")
        print(f"  MÍNIMO: {est['consumo_minimo']:.2f} L/mes")
        print(f"  TOTAL VEHÍCULOS: {est['total_vehiculos']}")
        print(f"\n  CLASIFICACIÓN:")
        print(f"    🔴 ALTO CONSUMO (>150% promedio): {len([v for v in k1['datos'] if float(v['consumo_promedio_mensual']) > est['promedio_flota']*1.5])}")
        print(f"    🟠 CONSUMO NORMAL: {len([v for v in k1['datos'] if est['promedio_flota']*0.5 <= float(v['consumo_promedio_mensual']) <= est['promedio_flota']*1.5])}")
        print(f"    🟢 BAJO CONSUMO: {len([v for v in k1['datos'] if float(v['consumo_promedio_mensual']) < est['promedio_flota']*0.5])}")
        print(f"\n  TOP 5 MAYORES CONSUMIDORES:")
        for i, veh in enumerate(k1['datos'][:5], 1):
            print(f"    {i}. {veh['vehiculo']:40} {veh['consumo_promedio_mensual']:>8.0f} L/mes")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 2: CONSUMO POR ÁREA DE TRABAJO
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【KPI 2】CONSUMO POR ÁREA DE TRABAJO")
    print("-"*90)
    print("""
¿PREGUNTA: Qué áreas/departamentos gastan más combustible?
¿CAUSA: Área geográfica, cantidad de vehículos, rutas ineficientes
¿ACCIÓN: Optimizar rutas, redistribuir recursos, monitorear
    """)
    
    k2 = kpis['consumo_area']
    if 'error' not in k2:
        est = k2['estadisticas']
        print(f"  VALOR PRINCIPAL: {est['promedio_area']:.2f} L/mes (Promedio por Área)")
        print(f"  TOTAL ÁREAS: {est['total_areas']}")
        print(f"  ÁREA CON MAYOR CONSUMO: {est['area_mayor_consumo']} ({est['consumo_mayor_area']:.0f}L)")
        print(f"\n  CLASIFICACIÓN POR ÁREA:")
        excesivo = len([a for a in k2['datos'] if '🔴' in a['clasificacion']])
        elevado = len([a for a in k2['datos'] if '🟠' in a['clasificacion']])
        normal = len([a for a in k2['datos'] if '🟢' in a['clasificacion']])
        print(f"    🔴 EXCESIVO: {excesivo}")
        print(f"    🟠 ELEVADO: {elevado}")
        print(f"    🟢 NORMAL: {normal}")
        print(f"\n  TOP 5 ÁREAS CON MAYOR CONSUMO:")
        for i, area in enumerate(k2['datos'][:5], 1):
            print(f"    {i}. {area['area']:45} {area['consumo_promedio_mensual']:>8.0f} L/mes")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 3: RENDIMIENTO (km/litro)
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【KPI 3】EFICIENCIA: RENDIMIENTO (km/litro)")
    print("-"*90)
    print("""
¿PREGUNTA: Qué vehículos son más eficientes en consumo de combustible?
¿CAUSA: Tipo de vehículo, mantenimiento, estado del motor, conducción
¿ACCIÓN: Mantener vehículos eficientes, revisar ineficientes
    """)
    
    k3 = kpis['eficiencia']
    if 'alerta' in k3:
        print(f"  ⚠️  {k3['alerta']}")
    elif 'error' not in k3:
        est = k3['estadisticas']
        print(f"  VALOR PRINCIPAL: {est['promedio_flota']:.2f} km/L (Promedio Flota)")
        print(f"  MÁXIMO: {est['maximo']:.2f} km/L (Más eficiente)")
        print(f"  MÍNIMO: {est['minimo']:.2f} km/L (Menos eficiente)")
        print(f"  VARIACIÓN: {est['desvio']:.2f}")
        print(f"\n  TOP 5 VEHÍCULOS MÁS EFICIENTES:")
        for i, veh in enumerate(k3['datos'][:5], 1):
            print(f"    {i}. {veh['vehiculo']:40} {veh['km_por_litro']:>8.1f} km/L")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 4: DESVIACIÓN CONSUMO
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【KPI 4】DESVIACIÓN: Consumo Esperado vs Real")
    print("-"*90)
    print("""
¿PREGUNTA: ¿Hay desviaciones significativas en el consumo?
¿CAUSA: Cambios de conducción, mantenimiento, fuga incipiente, rutas diferentes
¿ACCIÓN: Investigar desviaciones > 25%, revisar logs, auditar vehículos
    """)
    
    k4 = kpis['desviacion']
    if 'error' not in k4:
        est = k4['estadisticas']
        print(f"  ANOMALÍAS DETECTADAS: {est['total_anomalias']}")
        print(f"  ALERTAS CRÍTICAS (>50%): {est['alertas_criticas']}")
        if k4['anomalias']:
            print(f"\n  TOP 5 DESVIACIONES MÁS SIGNIFICATIVAS:")
            for i, anom in enumerate(k4['anomalias'][:5], 1):
                signo = "📈" if anom['desviacion_pct'] > 0 else "📉"
                print(f"    {i}. {anom['vehiculo']:30} {signo} {anom['desviacion_pct']:+7.1f}% | {anom['mes_actual']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 5: ANOMALÍAS CRÍTICAS 🚨
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【KPI 5】🚨 ANOMALÍAS CRÍTICAS: Detección de Fuga, Robo, Mal Uso")
    print("-"*90)
    print("""
¿PREGUNTA: ¿Hay posible fuga, robo o mal uso de combustible?
¿CAUSA:
  💧 FUGA: Consumo superior a 3 desviaciones estándar del promedio
  🚨 ROBO: Una o pocas transacciones muy grandes y sospechosas
  ⚠️  MAL USO: Muchas transacciones pequeñas con consumo total elevado
¿ACCIÓN: AUDITAR INMEDIATAMENTE - Revisar tanques, conductores, registros
    """)
    
    k5 = kpis['anomalias']
    if 'error' not in k5:
        est = k5['estadisticas']
        print(f"  ⚠️  TOTAL ANOMALÍAS DETECTADAS: {est['total']}")
        print(f"  🔴 SEVERIDAD ALTA (Crítico): {est['criticas']}")
        print(f"  🟠 SEVERIDAD MEDIA (Importante): {est['medias']}")
        
        if k5['anomalias']:
            print(f"\n  TOP 6 ANOMALÍAS CRÍTICAS A INVESTIGAR:")
            for i, anom in enumerate(k5['anomalias'][:6], 1):
                if anom['severidad'] == 'ALTA':
                    print(f"    {i}. 🔴 [{anom['mes']}] {anom['vehiculo']:30} {anom['consumo']:>8.0f}L")
                    print(f"       Razón: {anom['razones']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 6: ESTACIONALIDAD
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【KPI 6】ESTACIONALIDAD: ¿El consumo sube en ciertos meses?")
    print("-"*90)
    print("""
¿PREGUNTA: ¿Hay patrones mensuales claros en el consumo?
¿CAUSA: Temporada de trabajo, clima, eventos municipales, campañas
¿ACCIÓN: Planificar presupuesto, prever picos, optimizar recursos
    """)
    
    k6 = kpis['estacionalidad']
    if 'error' not in k6:
        est = k6['estadisticas']
        print(f"  CONSUMO PROMEDIO MENSUAL: {est['promedio_mensual']:,.0f} L")
        print(f"  PATRÓN: Picos en {est['mes_pico']} | Menor en {est['mes_bajo']}")
        print(f"\n  CONSUMO POR MES (Análisis Histórico):")
        print(f"    Mes        Consumo   Variación vs Promedio")
        for mes in k6['datos']:
            var = ((mes['promedio'] - est['promedio_mensual']) / est['promedio_mensual'] * 100)
            barra = "▓" * max(1, int(mes['promedio'] / 1000))
            sig = f"{var:+.0f}%" if var != 0 else "Igual"
            print(f"    {mes['nombre_mes']:>10} {mes['promedio']:>10.0f}L {barra:<20} {sig}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 7: FINES DE SEMANA
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【KPI 7】FINES DE SEMANA: ¿Qué unidades gastan más?")
    print("-"*90)
    print("""
¿PREGUNTA: ¿Qué vehículos tienen mayor consumo los fines de semana?
¿CAUSA: Servicio de emergencia, mantenimiento, uso personal
¿ACCIÓN: Revisar permisos, monitorear vehículos con alto uso FDS
    """)
    
    k7 = kpis['fines_semana']
    if 'error' not in k7:
        est = k7['estadisticas']
        print(f"  MAYOR CONSUMO FINES DE SEMANA: {est['mayor_consumo_fds']:.0f}L")
        print(f"  VEHÍCULO: {est['vehiculo']}")
        
        if k7['datos']:
            print(f"\n  TOP 5 CONSUMO FINES DE SEMANA:")
            for i, veh in enumerate(k7['datos'][:5], 1):
                if 'FIN DE SEMANA' in veh:
                    fds = veh['FIN DE SEMANA']
                    entre = veh.get('ENTRE SEMANA', 0)
                    dif = fds - entre
                    print(f"    {i}. {veh['vehiculo']:40} FDS: {fds:>7.0f}L | Entre Semana: {entre:>7.0f}L")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 8: EFICIENCIA POR ÁREA
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【KPI 8】EFICIENCIA POR ÁREA: ¿Qué áreas son menos eficientes?")
    print("-"*90)
    print("""
¿PREGUNTA: ¿Qué áreas tienen mayor consumo promedio por vehículo (menos eficientes)?
¿CAUSA: Rutas largas, vehículos grandes, mantenimiento deficiente, volumen de trabajo
¿ACCIÓN: Revisar asignación de recursos, optimizar rutas y flotas
    """)
    
    k8 = kpis['areas_eficiencia']
    if 'error' not in k8:
        est = k8['estadisticas']
        print(f"  PROMEDIO MUNICIPAL: {est['consumo_promedio_mes_por_veh']:.0f} L/mes/veh")
        print(f"  ÁREA MÁS EFICIENTE: {est['area_mas_eficiente']}")
        print(f"  ÁREA MENOS EFICIENTE: {est['area_menos_eficiente']}")
        
        if k8['datos']:
            print(f"\n  RANKING DE EFICIENCIA (L/mes por vehículo):")
            print(f"  🟢 EFICIENTES (< promedio) | 🟠 MEDIAS | 🔴 INEFICIENTES (> promedio)")
            print(f"\n  {'Pos':<4} {'Área':<50} {'L/mes/veh':<15} {'Clasificación'}")
            for i, area in enumerate(k8['datos'], 1):
                consumo = area['consumo_promedio_mes_por_vehiculo']
                promedio = est['consumo_promedio_mes_por_veh']
                if consumo < promedio * 0.7:
                    clase = "🟢 MUY EFICIENTE"
                elif consumo < promedio:
                    clase = "🟢 EFICIENTE"
                elif consumo <= promedio * 1.3:
                    clase = "🟠 MEDIA"
                else:
                    clase = "🔴 INEFICIENTE"
                print(f"  {i:<4} {area['area']:<50} {consumo:>8.0f}L        {clase}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI 9: PREDICCIÓN
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n【KPI 9】PREDICCIÓN: Combustible Necesario Próximo Mes")
    print("-"*90)
    print("""
¿PREGUNTA: ¿Cuánto combustible necesitará el municipio el próximo mes?
¿METODOLOGÍA: Análisis de tendencia (últimos 6 meses)
¿ACCIÓN: Presupuestar, coordinar con proveedores, preparar compra
    """)
    
    k9 = kpis['prediccion']
    if 'error' not in k9:
        print(f"  CONSUMO ACTUAL (Últimos 6 meses): {k9['consumo_actual']:,.0f} L")
        print(f"  PREDICCIÓN PRÓXIMO MES: {k9['prediccion_proximo_mes']:,.0f} L")
        print(f"  TENDENCIA: {k9['tendencia']}")
        print(f"  CAMBIO ESPERADO: {k9['cambio_porcentaje']:+.2f}%")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  RANKING DE VEHÍCULOS
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n" + "="*90)
    print("📋 RANKING DE VEHÍCULOS")
    print("="*90)
    
    k1_data = kpis['consumo_vehiculo']['datos']
    print("\nTOP 10 VEHÍCULOS CON MAYOR CONSUMO (Prioridad para Auditoría):")
    print("-"*90)
    print(f"{'Pos':<4} {'Vehículo':<35} {'Placa':<12} {'L/mes':<10} {'Estado'}")
    print("-"*90)
    
    for i, veh in enumerate(k1_data[:10], 1):
        print(f"{i:<4} {veh['vehiculo']:<35} {str(veh['placa']):<12} {veh['consumo_promedio_mensual']:>8.0f}  {veh['clasificacion']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  RESUMEN EJECUTIVO
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n\n" + "="*90)
    print("🎯 RESUMEN EJECUTIVO - ACCIONES INMEDIATAS")
    print("="*90)
    
    print("""
✅ HALLAZGOS PRINCIPALES:

  1️⃣  CONSUMO:
      • Total de vehículos: {} unidades
      • Consumo promedio: {:.0f} L/mes
      • Total áreas monitoreadas: {}
      • Consumo total estimado: {:.0f} L/mes

  2️⃣  ANOMALÍAS CRÍTICAS 🚨:
      • Anomalías detectadas: {} (ALTA: {}, MEDIA: {})
      • Recomendación: AUDITAR INMEDIATAMENTE
      • Prioritario: T-Maquinaria y Tanques de Aseo

  3️⃣  EFICIENCIA:
      • Km/L promedio: {:.2f}
      • Variación: {} (Máx: {:.2f}, Mín: {:.2f})
      • Vehículos eficientes: VERDE

  4️⃣  ESTACIONALIDAD:
      • Mes pico: {} ({:.0f}L)
      • Mes bajo: {} ({:.0f}L)
      • Patrón: Claro - Planificable

  5️⃣  PREDICCIÓN:
      • Próximo mes: {:.0f}L estimado
      • Tendencia: {}

🎯 ACCIONES RECOMENDADAS:

  ✓ INMEDIATO (Próximos 7 días):
    • Auditar vehículos con anomalías ALTA
    • Revisar tanques de almacenamiento
    • Verificar registros de conductores

  ✓ CORTO PLAZO (Próximas 2-4 semanas):
    • Implementar plan de mantenimiento preventivo
    • Capacitar conductores en eficiencia
    • Revisar rutas ineficientes

  ✓ MEDIANO PLAZO (1-3 meses):
    • Optimizar asignación de vehículos por área
    • Implementar monitoreo GPS en tiempo real
    • Evaluar cambio de vehículos ineficientes

════════════════════════════════════════════════════════════════════════════════
    """.format(
        kpis['consumo_vehiculo']['estadisticas']['total_vehiculos'],
        kpis['consumo_vehiculo']['estadisticas']['promedio_flota'],
        kpis['consumo_area']['estadisticas']['total_areas'],
        kpis['consumo_vehiculo']['estadisticas']['promedio_flota'] * kpis['consumo_vehiculo']['estadisticas']['total_vehiculos'],
        kpis['anomalias']['estadisticas']['total'],
        kpis['anomalias']['estadisticas']['criticas'],
        kpis['anomalias']['estadisticas']['medias'],
        kpis['eficiencia']['estadisticas']['promedio_flota'],
        "MUY VARIABLE" if kpis['eficiencia']['estadisticas']['desvio'] > 1000 else "NORMAL",
        kpis['eficiencia']['estadisticas']['maximo'],
        kpis['eficiencia']['estadisticas']['minimo'],
        kpis['estacionalidad']['estadisticas']['mes_pico'],
        kpis['estacionalidad']['datos'][0]['promedio'] if kpis['estacionalidad']['datos'] else 0,
        kpis['estacionalidad']['estadisticas']['mes_bajo'],
        kpis['estacionalidad']['datos'][-1]['promedio'] if kpis['estacionalidad']['datos'] else 0,
        kpis['prediccion']['prediccion_proximo_mes'],
        kpis['prediccion']['tendencia'],
    ))
    
    print("\n📊 Gráficos disponibles en: graficos_kpi/")
    print("📁 Archivo de exportación: reporte_kpis.json")
    print("\n" + "="*90 + "\n")


if __name__ == "__main__":
    generar_reporte_kpis()
    
    # Exportar también a JSON
    try:
        data = dashboard_completo()
        with open('reporte_kpis.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        print("✅ Reporte JSON exportado a: reporte_kpis.json\n")
    except Exception as e:
        print(f"⚠️  Error al exportar JSON: {str(e)}\n")
