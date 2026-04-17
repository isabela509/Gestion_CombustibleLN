"""
╔════════════════════════════════════════════════════════════════════════════╗
║ GENERADOR DE GRÁFICOS PROFESIONALES - KPI SYSTEM                        ║
║ Gráficos visibles, fáciles y dinámicos para presentación al cliente      ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch, Rectangle
import numpy as np
import pandas as pd
from pathlib import Path

from kpi_system import (
    kpi_consumo_vehiculo,
    kpi_consumo_area,
    kpi_eficiencia,
    kpi_desviacion,
    kpi_anomalias,
    kpi_estacionalidad,
    kpi_fines_semana,
    kpi_areas_eficiencia,
    kpi_prediccion,
)


# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN VISUAL - COLORES PROFESIONALES
# ═══════════════════════════════════════════════════════════════════════════

COLORES = {
    "primario": "#1565C0",      # Azul profesional
    "exito": "#2E7D32",          # Verde
    "alerta": "#F57C00",         # Naranja
    "critico": "#C62828",        # Rojo
    "gris": "#616161",
    "fondo": "#FAFAFA",
}

PALETA = ["#1565C0", "#1976D2", "#42A5F5", "#90CAF9", "#BBDEFB",
          "#2E7D32", "#66BB6A", "#81C784", "#C8E6C9", "#E8F5E9"]

plt.rcParams.update({
    "figure.facecolor": COLORES["fondo"],
    "axes.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "font.family": "DejaVu Sans",
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})

SALIDA = Path("graficos_kpi")
SALIDA.mkdir(exist_ok=True)


def guardar(nombre: str, titulo: str = ""):
    """Guardar gráfico con nombre y mostrar progreso"""
    path = SALIDA / nombre
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight", facecolor=COLORES["fondo"])
    plt.close()
    print(f"  ✓ {nombre:<35} {titulo}")


# ═══════════════════════════════════════════════════════════════════════════
#  GRÁFICO 1: TOP 10 VEHÍCULOS CON MAYOR CONSUMO
# ═══════════════════════════════════════════════════════════════════════════

def grafico_consumo_vehiculo():
    """Top 10 vehículos - Ranking por consumo promedio"""
    print("\n[GRÁFICO 1] Top 10 Vehículos por Consumo...", end="")
    
    try:
        kpi = kpi_consumo_vehiculo()
        if "error" in kpi:
            print(f" ❌ {kpi['error']}")
            return
        
        df = pd.DataFrame(kpi['datos']).head(10)
        
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # Colores según clasificación
        colores = [COLORES["critico"] if "ALTO" in c else 
                    COLORES["alerta"] if "NORMAL" in c else 
                    COLORES["exito"]
                   for c in df['clasificacion']]
        
        x_pos = np.arange(len(df))
        bars = ax.bar(x_pos, df['consumo_promedio_mensual'], 
                      color=colores, edgecolor='black', linewidth=1.5, width=0.7)
        
        # Valores encima de barras
        for bar, val in zip(bars, df['consumo_promedio_mensual']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.0f}L',
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        # Etiquetas con placa y nombre (más corto)
        etiquetas = []
        for _, row in df.iterrows():
            placa = row['placa'] if pd.notna(row['placa']) and str(row['placa']).strip() else "SIN PLACA"
            nombre = row['vehiculo'][:12].strip() if row['vehiculo'] else "SIN NOMBRE"
            etiquetas.append(f"{placa}\n{nombre}")
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(etiquetas, fontsize=8, rotation=45, ha='right')
        ax.set_ylabel('Consumo Promedio Mensual (Litros)', fontweight='bold', fontsize=11)
        ax.set_title('TOP 10: Vehículos con Mayor Consumo Promedio Mensual', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Línea de promedio
        promedio = kpi['estadisticas']['promedio_flota']
        ax.axhline(promedio, color=COLORES["gris"], linestyle='--', linewidth=2, alpha=0.7)
        ax.text(len(df)-0.5, promedio + 50, f'Promedio flota: {promedio:.0f}L',
               fontsize=9, color=COLORES["gris"], fontweight='bold')
        
        # Formatos
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        
        # Leyenda
        handles = [
            Patch(color=COLORES["critico"], label="Alto consumo"),
            Patch(color=COLORES["alerta"], label="Consumo normal"),
            Patch(color=COLORES["exito"], label="Bajo consumo"),
        ]
        ax.legend(handles=handles, loc='upper right', fontsize=9)
        
        guardar("01_consumo_vehiculo_top10.png", "TOP 10 Vehículos")
        
    except Exception as e:
        print(f" ❌ {str(e)[:50]}")


# ═══════════════════════════════════════════════════════════════════════════
#  GRÁFICO 2: CONSUMO POR ÁREA DE TRABAJO
# ═══════════════════════════════════════════════════════════════════════════

def grafico_consumo_area():
    """Consumo por áreas/departamentos - Barras horizontales"""
    print("[GRÁFICO 2] Consumo por Área de Trabajo...", end="")
    
    try:
        kpi = kpi_consumo_area()
        if "error" in kpi:
            print(f" ❌ {kpi['error']}")
            return
        
        df = pd.DataFrame(kpi['datos']).head(12)
        df = df.sort_values('consumo_promedio_mensual')
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Colores por clasificación
        colores = [COLORES["critico"] if "EXCESIVO" in c else 
                    COLORES["alerta"] if "ELEVADO" in c else 
                    COLORES["exito"]
                   for c in df['clasificacion']]
        
        y_pos = np.arange(len(df))
        bars = ax.barh(y_pos, df['consumo_promedio_mensual'], 
                       color=colores, edgecolor='black', linewidth=1.2)
        
        # Valores al lado
        for i, (bar, val) in enumerate(zip(bars, df['consumo_promedio_mensual'])):
            ax.text(val + 20, bar.get_y() + bar.get_height()/2,
                   f'{val:.0f}L',
                   va='center', ha='left', fontweight='bold', fontsize=9)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(df['area'], fontsize=9)
        ax.set_xlabel('Consumo Promedio Mensual (Litros)', fontweight='bold', fontsize=11)
        ax.set_title('Consumo de Combustible POR ÁREA DE TRABAJO', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Leyenda de clasificación
        handles = [
            Patch(color=COLORES["critico"], label="Consumo Excesivo"),
            Patch(color=COLORES["alerta"], label="Consumo Elevado"),
            Patch(color=COLORES["exito"], label="Consumo Normal"),
        ]
        ax.legend(handles=handles, loc='lower right', fontsize=9)
        
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        
        guardar("02_consumo_area.png", "Consumo por Área")
        
    except Exception as e:
        print(f" ❌ {str(e)[:50]}")


# ═══════════════════════════════════════════════════════════════════════════
#  GRÁFICO 3: EFICIENCIA (km/litro)
# ═══════════════════════════════════════════════════════════════════════════

def grafico_eficiencia():
    """Rendimiento de combustible - Solo vehículos con datos de km"""
    print("[GRÁFICO 3] Eficiencia (km/litro)...", end="")
    
    try:
        kpi = kpi_eficiencia()
        if "alerta" in kpi or "error" in kpi:
            print(f" ! {kpi.get('alerta', kpi.get('error'))}") 
            return
        
        df = pd.DataFrame(kpi['datos'])
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Colores
        colores = [COLORES["exito"] if km > 0 else COLORES["gris"] 
                  for km in df['km_por_litro']]
        
        x_pos = np.arange(len(df))
        bars = ax.bar(x_pos, df['km_por_litro'], 
                      color=colores, edgecolor='black', linewidth=1.5)
        
        # Valores
        for bar, val in zip(bars, df['km_por_litro']):
            texto = f'{val:.1f}'
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                   texto, ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        etiquetas = [f"{row['placa'] if pd.notna(row['placa']) else 'N/A'}\n{row['vehiculo'][:18]}" 
                    for _, row in df.iterrows()]
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(etiquetas, fontsize=9)
        ax.set_ylabel('Rendimiento (km/litro)', fontweight='bold', fontsize=11)
        ax.set_title(f'⚡ EFICIENCIA: {len(df)} Vehículos con Datos - Rendimiento km/L', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Línea de promedio
        prom = kpi['estadisticas']['promedio_flota']
        if prom > 0:
            ax.axhline(prom, color=COLORES["primario"], linestyle='--', linewidth=2, alpha=0.7)
            ax.text(13.5, prom + 1, f'Promedio: {prom:.1f} km/L',
                   fontsize=10, color=COLORES["primario"], fontweight='bold')
        
        ax.grid(axis='y', alpha=0.3, linestyle=':')
        
        # Nota visual sobre falta de datos
        texto_nota = f"NOTA: De 58 vehículos en flota, solo {len(df)} tienen datos de kilometraje registrados.\n{58 - len(df)} vehículos sin datos de km_inicio/km_final en BD correspondiente."
        fig.text(0.5, 0.02, texto_nota, ha='center', fontsize=9, 
                style='italic', color='#FF6B6B', bbox=dict(boxstyle='round', facecolor='#FFE5E5', alpha=0.8))
        fig.subplots_adjust(bottom=0.12)
        
        guardar("03_eficiencia.png", f"Eficiencia km/L - {len(df)} Vehículos con datos")
        
    except Exception as e:
        print(f" ❌ {str(e)[:50]}")


# ═══════════════════════════════════════════════════════════════════════════
#  GRÁFICO 4: DESVIACIÓN DE CONSUMO
# ═══════════════════════════════════════════════════════════════════════════

def grafico_desviacion():
    """Desviación consumo actual vs histórico - SIMPLE Y CLARO"""
    print("[GRÁFICO 4] Desviación Consumo...", end="")
    
    try:
        kpi = kpi_desviacion()
        if "error" in kpi:
            print(f" ❌ {kpi['error']}")
            return
        
        anomalias = kpi['anomalias']  # SIN LIMITAR - TODOS LOS VEHÍCULOS
        if not anomalias:
            print(" ! Sin datos")
            return
        
        df = pd.DataFrame(anomalias)
        df = df.sort_values('desviacion_pct', ascending=True)
        
        # Obtener estadísticas directamente del KPI - AQUÍ GLOBALMENTE
        stats = kpi.get('estadisticas', {})
        con_aumento = stats.get('con_aumento', 0)
        con_disminucion = stats.get('con_disminucion', 0)
        promedio_dev = stats.get('promedio_desviacion', 0)
        total_veh = stats.get('total_vehiculos', 0)
        muy_aum = stats.get('muy_aumentado_15plus', 0)
        aum_medio = stats.get('aumentado_5_15', 0)
        lig_aum = stats.get('lig_aumentado_0_5', 0)
        promedio_aumento = stats.get('promedio_aumento', 0)
        promedio_disminucion = stats.get('promedio_disminucion', 0)
        
        # Tamaño dinámico BIEN GRANDE según cantidad de vehículos
        altura_dinamica = max(12, len(df) * 0.42)
        fig = plt.figure(figsize=(16, altura_dinamica))
        fig.patch.set_facecolor('white')
        
        # Espacios COMPACTOS - sin espacios en blanco innecesarios
        gs = fig.add_gridspec(4, 1, height_ratios=[0.5, 0.65, 0.55, max(2, len(df) * 0.15)], 
                              hspace=0.08, top=0.97, bottom=0.10, left=0.25, right=0.95)
        
        # ════════════════════════════════════════════════════════════════
        # SECCIÓN 1: TÍTULO
        # ════════════════════════════════════════════════════════════════
        ax_titulo = fig.add_subplot(gs[0])
        ax_titulo.axis('off')
        
        ax_titulo.text(0.5, 0.7, 'DESVIACION DE CONSUMO POR VEHICULO', 
                      ha='center', fontsize=15, fontweight='bold', transform=ax_titulo.transAxes)
        ax_titulo.text(0.5, 0.15, f'Total: {total_veh} vehiculos | Consumo Actual vs Promedio Historico',
                      ha='center', fontsize=9, style='italic', color='#666', transform=ax_titulo.transAxes)
        
        # ════════════════════════════════════════════════════════════════
        # SECCIÓN 2: EXPLICACIÓN DEDICADA
        # ════════════════════════════════════════════════════════════════
        ax_explicacion = fig.add_subplot(gs[1])
        ax_explicacion.axis('off')
        
        # Explicación del promedio con estadísticas detalladas
        if promedio_dev < 0:
            explicacion = f"Promedio NEGATIVO ({promedio_dev:.1f}%): La FLOTA EN GENERAL consume MENOS que antes - MEJORÍA\n"
            explicacion += f"{con_aumento} vehículos con AUMENTO promedio {promedio_aumento:+.1f}% | {con_disminucion} vehículos EFICIENTES promedio {promedio_disminucion:.1f}%"
            color_expl = '#2E7D32'
        else:
            explicacion = f"Promedio POSITIVO ({promedio_dev:.1f}%): La FLOTA EN GENERAL consume MÁS que antes - AUMENTO\n"
            explicacion += f"{con_aumento} vehículos con AUMENTO promedio {promedio_aumento:+.1f}% | {con_disminucion} vehículos eficientes promedio {promedio_disminucion:.1f}%"
            color_expl = '#C2185B'
        
        ax_explicacion.text(0.5, 0.5, explicacion, ha='center', va='center', fontsize=8.5, 
                      style='italic', color=color_expl, fontweight='bold', transform=ax_explicacion.transAxes,
                      bbox=dict(boxstyle='round,pad=0.7', facecolor='#F5F5F5', edgecolor=color_expl, linewidth=2))
        
        # ════════════════════════════════════════════════════════════════
        # SECCIÓN 3: KPI BOXES
        # ════════════════════════════════════════════════════════════════
        ax_kpi = fig.add_subplot(gs[2])
        ax_kpi.axis('off')
        
        from matplotlib.patches import Rectangle as RectPatch
        
        # KPI 1: Vehículos con aumento
        rect_kpi1 = RectPatch((0.05, 0.25), 0.25, 0.5, transform=ax_kpi.transAxes,
                             facecolor='#FFEBEE', edgecolor='#D32F2F', linewidth=2)
        ax_kpi.add_patch(rect_kpi1)
        ax_kpi.text(0.175, 0.6, f'{con_aumento}', fontsize=18, fontweight='bold', 
                      color='#D32F2F', ha='center', transform=ax_kpi.transAxes)
        ax_kpi.text(0.175, 0.38, 'Vehiculos con\nAUMENTO', fontsize=8, fontweight='bold',
                      color='#D32F2F', ha='center', va='center', transform=ax_kpi.transAxes)
        
        # KPI 2: Promedio desviación
        rect_kpi2 = RectPatch((0.375, 0.25), 0.25, 0.5, transform=ax_kpi.transAxes,
                             facecolor='#FFF3E0', edgecolor='#FF9800', linewidth=2)
        ax_kpi.add_patch(rect_kpi2)
        ax_kpi.text(0.5, 0.6, f'{promedio_dev:+.1f}%', fontsize=16, fontweight='bold',
                      color='#FF9800', ha='center', transform=ax_kpi.transAxes)
        ax_kpi.text(0.5, 0.38, 'PROMEDIO\nDesviacion', fontsize=8, fontweight='bold',
                      color='#FF9800', ha='center', va='center', transform=ax_kpi.transAxes)
        
        # KPI 3: Vehículos eficientes
        rect_kpi3 = RectPatch((0.7, 0.25), 0.25, 0.5, transform=ax_kpi.transAxes,
                             facecolor='#E8F5E9', edgecolor='#43A047', linewidth=2)
        ax_kpi.add_patch(rect_kpi3)
        ax_kpi.text(0.825, 0.6, f'{con_disminucion}', fontsize=18, fontweight='bold',
                      color='#43A047', ha='center', transform=ax_kpi.transAxes)
        ax_kpi.text(0.825, 0.38, 'Vehiculos\nEFICIENTES', fontsize=8, fontweight='bold',
                      color='#43A047', ha='center', va='center', transform=ax_kpi.transAxes)
        
        # ════════════════════════════════════════════════════════════════
        # SECCIÓN 4: GRÁFICO PRINCIPAL
        # ════════════════════════════════════════════════════════════════
        ax = fig.add_subplot(gs[3])
        
        # Colores por severidad - NUEVOS RANGOS
        colores = []
        for d in df['desviacion_pct']:
            if d > 15:
                colores.append('#C2185B')  # Rosado fuerte
            elif d > 5:
                colores.append('#E53935')  # Rojo
            elif d > 0:
                colores.append('#FFA726')  # Naranja
            else:
                colores.append('#43A047')  # Verde
        
        y_pos = np.arange(len(df))
        bars = ax.barh(y_pos, df['desviacion_pct'], color=colores, 
                       edgecolor='black', linewidth=0.5, height=0.65)
        
        # Etiquetas limpias y ordenadas - SOLO NOMBRES para claridad
        etiquetas = []
        for _, row in df.iterrows():
            nombre = row['vehiculo'][:12].strip() if row['vehiculo'] else "SIN NOMBRE"
            etiquetas.append(nombre)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(etiquetas, fontsize=8)
        ax.set_xlabel('Desviacion (%)', fontweight='bold', fontsize=10)
        
        # Línea referencia
        ax.axvline(0, color='black', linewidth=2.5, alpha=0.9)
        
        # Valores en las barras
        for bar, val in zip(bars, df['desviacion_pct']):
            ax.text(val + (1 if val > 0 else -1), bar.get_y() + bar.get_height()/2,
                   f'{val:+.1f}%', ha='left' if val > 0 else 'right', 
                   va='center', fontweight='bold', fontsize=8)
        
        ax.grid(axis='x', alpha=0.2, linestyle=':')
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Agregar leyenda abajo del gráfico
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#C2185B', edgecolor='black', label='+15%+ → Muy aumentado'),
            Patch(facecolor='#E53935', edgecolor='black', label='+5-15% → Aumentado'),
            Patch(facecolor='#FFA726', edgecolor='black', label='+0-5% → Ligeramente aumentado'),
            Patch(facecolor='#43A047', edgecolor='black', label='Negativo → Eficiente')
        ]
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.08),
                 ncol=4, fontsize=8, frameon=True, fancybox=True, shadow=False)
        
        # Nota de distribución
        distribucion_nota = f"Distribución: {muy_aum} veh +15% | {aum_medio} veh +5-15% | {lig_aum} veh +0-5% | {con_disminucion} veh eficientes"
        ax.text(0.5, -0.145, distribucion_nota, transform=ax.transAxes,
               fontsize=7.5, ha='center', style='italic', color='#555555',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#FAFAFA', edgecolor='#CCCCCC', linewidth=0.5))
        
        guardar("04_desviacion_consumo.png", f"Desviacion Consumo - {total_veh} vehiculos")
        
    except Exception as e:
        print(f" ❌ {str(e)[:80]}")


# ═══════════════════════════════════════════════════════════════════════════
#  GRÁFICO 5: ANOMALÍAS CRÍTICAS
# ═══════════════════════════════════════════════════════════════════════════

def grafico_anomalias():
    """Anomalías detectadas - CON KPIS Y JUSTIFICACIÓN CLARA"""
    print("[GRÁFICO 5] Anomalías Críticas...", end="")
    
    try:
        kpi = kpi_anomalias()
        if "error" in kpi:
            print(f" ❌ {kpi['error']}")
            return
        
        anomalias = kpi['anomalias']
        if not anomalias:
            print(" ✅ Sin anomalías detectadas")
            return
        
        stats = kpi['estadisticas']
        df = pd.DataFrame(anomalias)
        
        # Colores específicos por tipo - CLAROS Y PROFESIONALES
        colores_tipo = {
            "FUGA": "#1E88E5",      # Azul gota - CRÍTICO
            "ROBO": "#D32F2F",      # Rojo peligro - MUY GRAVE
            "MAL_USO": "#F57C00"   # Naranja alerta - GRAVE
        }
        
        # Figura con espacio para KPIs y tabla
        fig = plt.figure(figsize=(19, 14))
        fig.patch.set_facecolor('#FFFFFF')
        
        # ═════════════════════════════════════════════════════════════════
        # SECCIÓN 1: TÍTULO
        # ═════════════════════════════════════════════════════════════════
        
        fig.text(0.5, 0.97, "DETECCIÓN DE ANOMALÍAS - ANÁLISIS CON JUSTIFICACIÓN", 
                ha='center', fontsize=26, fontweight='bold', color='#1a1a1a')
        
        # ═════════════════════════════════════════════════════════════════
        # PREPARAR DATOS PRIMERO (para saber qué mostrar en KPIs)
        # ═════════════════════════════════════════════════════════════════
        
        # Obtener top de cada tipo para variedad
        mal_uso_top = df[df['tipo_principal'] == 'MAL_USO'].head(6)
        robo_top = df[df['tipo_principal'] == 'ROBO'].head(4)
        fuga_top = df[df['tipo_principal'] == 'FUGA'].head(3)
        
        # Contar cuántos de cada tipo se van a mostrar
        count_fugas_mostradas = len(fuga_top)
        count_robos_mostrados = len(robo_top)
        count_mal_uso_mostrados = len(mal_uso_top)
        
        display_df = pd.concat([fuga_top, robo_top, mal_uso_top]).reset_index(drop=True)
        vehiculo_critico = stats['vehiculo_critico']
        
        # ═════════════════════════════════════════════════════════════════
        # SECCIÓN 2: KPIs PEQUEÑOS Y ORDENADOS (DOS FILAS)
        # ═════════════════════════════════════════════════════════════════
        
        # FILA 1: TRES KPIs PRINCIPALES (MÁS PEQUEÑOS)
        y_fila1 = 0.905
        
        # Posiciones de columnas (3 columnas iguales)
        col_width = 0.30
        col1_center = 0.165
        col2_center = 0.5
        col3_center = 0.835
        
        # KPI 1: TOTAL
        fig.text(col1_center, y_fila1, f"{stats['total']}", 
                ha='center', fontsize=26, fontweight='bold', color='#1a1a1a')
        fig.text(col1_center, y_fila1 - 0.032, "ALERTAS\nTOTALES",
                ha='center', fontsize=7, fontweight='bold', color='#555555', linespacing=1.1)
        rect1 = Rectangle((col1_center - 0.125, y_fila1 - 0.065), 0.25, 0.085,
                         facecolor='#F5F5F5', edgecolor='#333333', linewidth=2, zorder=0)
        fig.add_artist(rect1)
        
        # KPI 2: CRÍTICAS
        color_critica = '#D32F2F'
        fig.text(col2_center, y_fila1, f"{stats['total_criticas']}", 
                ha='center', fontsize=26, fontweight='bold', color=color_critica, zorder=2)
        fig.text(col2_center, y_fila1 - 0.032, "CRÍTICAS",
                ha='center', fontsize=7, fontweight='bold', color=color_critica, zorder=2)
        rect2 = Rectangle((col2_center - 0.125, y_fila1 - 0.065), 0.25, 0.085,
                         facecolor='#FFEBEE', edgecolor=color_critica, linewidth=2, zorder=0)
        fig.add_artist(rect2)
        
        # KPI 3: IMPACTO
        color_impacto = '#FF6B00'
        fig.text(col3_center, y_fila1, f"{stats['porcentaje_impacto']:.1f}%", 
                ha='center', fontsize=24, fontweight='bold', color=color_impacto, zorder=2)
        fig.text(col3_center, y_fila1 - 0.020, "DEL CONSUMO",
                ha='center', fontsize=6.5, fontweight='bold', color=color_impacto, zorder=2)
        fig.text(col3_center, y_fila1 - 0.038, "EN ANOMALÍAS",
                ha='center', fontsize=6.5, fontweight='bold', color=color_impacto, zorder=2)
        rect3 = Rectangle((col3_center - 0.125, y_fila1 - 0.065), 0.25, 0.085,
                         facecolor='#FFE0B2', edgecolor=color_impacto, linewidth=2, zorder=0)
        fig.add_artist(rect3)
        
        # FILA 2: DESGLOSE MOSTRANDO CUÁNTOS SE VE (MÁS PEQUEÑOS Y CON ESPACIO)
        y_fila2 = 0.775
        
        # KPI: FUGAS (con proporción)
        color_fuga = '#1E88E5'
        fig.text(col1_center, y_fila2 + 0.010, f"TOP {count_fugas_mostradas}", 
                ha='center', fontsize=18, fontweight='bold', color=color_fuga, zorder=2)
        fig.text(col1_center, y_fila2 - 0.020, f"de {stats['total_fugas']} FUGAS",
                ha='center', fontsize=7, fontweight='bold', color=color_fuga, zorder=2)
        fig.text(col1_center, y_fila2 - 0.038, "DETECTADAS",
                ha='center', fontsize=6, style='italic', color=color_fuga, zorder=2)
        rect4 = Rectangle((col1_center - 0.125, y_fila2 - 0.060), 0.25, 0.085,
                         facecolor='#E3F2FD', edgecolor=color_fuga, linewidth=2, zorder=0)
        fig.add_artist(rect4)
        
        # KPI: ROBOS (con proporción)
        color_robo = '#D32F2F'
        fig.text(col2_center, y_fila2 + 0.010, f"TOP {count_robos_mostrados}", 
                ha='center', fontsize=18, fontweight='bold', color=color_robo, zorder=2)
        fig.text(col2_center, y_fila2 - 0.020, f"de {stats['total_robos']} ROBOS",
                ha='center', fontsize=7, fontweight='bold', color=color_robo, zorder=2)
        fig.text(col2_center, y_fila2 - 0.038, "DETECTADOS",
                ha='center', fontsize=6, style='italic', color=color_robo, zorder=2)
        rect5 = Rectangle((col2_center - 0.125, y_fila2 - 0.060), 0.25, 0.085,
                         facecolor='#FFEBEE', edgecolor=color_robo, linewidth=2, zorder=0)
        fig.add_artist(rect5)
        
        # KPI: MAL USO (con proporción)
        color_mal_uso = '#F57C00'
        fig.text(col3_center, y_fila2 + 0.010, f"TOP {count_mal_uso_mostrados}", 
                ha='center', fontsize=18, fontweight='bold', color=color_mal_uso, zorder=2)
        fig.text(col3_center, y_fila2 - 0.020, f"de {stats['total_mal_uso']} MAL USO",
                ha='center', fontsize=7, fontweight='bold', color=color_mal_uso, zorder=2)
        fig.text(col3_center, y_fila2 - 0.038, "DETECTADOS",
                ha='center', fontsize=6, style='italic', color=color_mal_uso, zorder=2)
        rect6 = Rectangle((col3_center - 0.125, y_fila2 - 0.060), 0.25, 0.085,
                         facecolor='#FFF3E0', edgecolor=color_mal_uso, linewidth=2, zorder=0)
        fig.add_artist(rect6)
        
        # ═════════════════════════════════════════════════════════════════
        # SECCIÓN 3: TABLA DE VEHÍCULOS (CON JUSTIFICACIÓN)
        # ═════════════════════════════════════════════════════════════════
        
        # GridSpec para tabla (SEPARADA DE LOS KPIs)
        gs_tabla = fig.add_gridspec(1, 1, top=0.70, bottom=0.08, left=0.04, right=0.96)
        ax_tabla = fig.add_subplot(gs_tabla[0])
        ax_tabla.axis('off')
        
        # Establecer límites de la tabla (AUMENTADO PARA ENCABEZADO)
        ax_tabla.set_xlim(0, 100)
        ax_tabla.set_ylim(-1, len(display_df) + 1.8)
        
        # Dibujar filas
        for i, (idx, row) in enumerate(display_df.iterrows()):
            y = len(display_df) - i - 1
            
            # Determinar si es vehículo crítico
            es_critico = (vehiculo_critico and 
                         row['vehiculo'] == vehiculo_critico['vehiculo'] and 
                         row['placa'] == vehiculo_critico['placa'])
            
            # Barra proporcional
            consumo_max = display_df['consumo'].max()
            ancho_barra = (row['consumo'] / consumo_max) * 60
            
            tipo = row['tipo_principal']
            color = colores_tipo[tipo]
            
            # Fondo alternado
            fondo_color = '#F9F9F9' if i % 2 == 0 else '#FFFFFF'
            if es_critico:
                fondo_color = '#FFE5E5'
            
            rect = Rectangle((0, y-0.4), 100, 0.8, 
                           facecolor=fondo_color, edgecolor='#CCCCCC', linewidth=1)
            ax_tabla.add_patch(rect)
            
            # Barra de consumo
            borde_ancho = 3 if es_critico else 1.5
            borde_color = '#000000' if es_critico else color
            
            rect_barra = Rectangle((0, y-0.35), ancho_barra, 0.7, 
                                  facecolor=color, edgecolor=borde_color, linewidth=borde_ancho, alpha=0.85)
            ax_tabla.add_patch(rect_barra)
            
            # Información
            nombre = row['vehiculo'][:12] if row['vehiculo'] else 'SIN NOMBRE'
            placa = row['placa'] if row['placa'] else 'N/A'
            mes = row['mes']
            consumo = row['consumo']
            trans = int(row['transacciones'])
            
            # Número
            numero = f"{i+1}."
            
            # Construcción del texto
            texto_principal = f"{numero:>3} {nombre} [{placa}] - {mes}"
            
            # Nombre del vehículo
            peso = 'bold' if es_critico else 'normal'
            ax_tabla.text(2, y, texto_principal, 
                        fontsize=9, fontweight=peso,
                        va='center', ha='left', color='#1a1a1a')
            
            # Tipo
            tipo_label = tipo
            ax_tabla.text(45, y, tipo_label,
                        fontsize=8, fontweight='bold',
                        va='center', ha='center',
                        bbox=dict(boxstyle='round,pad=0.35', facecolor=color, 
                                 alpha=0.25, edgecolor=color, linewidth=1))
            
            # CRITERIO/JUSTIFICACIÓN (lo importante)
            criterio_text = row['criterio'] if 'criterio' in row and row['criterio'] else f"{trans} trans."
            # Truncar si es muy largo
            if len(criterio_text) > 35:
                criterio_text = criterio_text[:32] + "..."
            
            ax_tabla.text(58, y, criterio_text,
                        fontsize=7.5, style='italic', color='#666666',
                        va='center', ha='left')
            
            # Consumo (derecha)
            consumo_text = f"{consumo:,.0f}L"
            if es_critico:
                consumo_text += " ⭐"
            
            ax_tabla.text(95, y, consumo_text,
                        fontsize=9 if es_critico else 8.5, fontweight=peso,
                        va='center', ha='right', color=color if es_critico else '#1a1a1a')
        
        # Encabezado de tabla - CLARA Y PROFESIONAL
        y_header = len(display_df)
        header_bgcolor = '#E8E8E8'
        
        # Rectángulo de encabezado COMPLETAMENTE GRANDE para contener todo el texto
        rect_header = Rectangle((0, y_header-0.8), 100, 1.6,
                               facecolor=header_bgcolor, edgecolor='#333333', linewidth=2)
        ax_tabla.add_patch(rect_header)
        
        # Textos centrados dentro del rectángulo
        ax_tabla.text(2, y_header, "VEHÍCULO", 
                     fontsize=10, fontweight='bold', va='center', ha='left', color='#1a1a1a')
        ax_tabla.text(45, y_header, "TIPO",
                     fontsize=10, fontweight='bold', va='center', ha='center', color='#1a1a1a')
        ax_tabla.text(58, y_header, "CRITERIO DE DETECCIÓN",
                     fontsize=9, fontweight='bold', va='center', ha='left', color='#333333')
        ax_tabla.text(95, y_header, "CONSUMO",
                     fontsize=10, fontweight='bold', va='center', ha='right', color='#1a1a1a')
        
        # ═════════════════════════════════════════════════════════════════
        # SECCIÓN 4: PIE - EXPLICACIÓN DE CRITERIOS
        # ═════════════════════════════════════════════════════════════════
        
        y_footer = 0.055
        
        fig.text(0.04, y_footer, 
                "💧 FUGA: Consumo > Media + 3σ (anormalmente alto)",
                fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#E3F2FD', 
                         edgecolor='#1E88E5', linewidth=2),
                color='#1E88E5', fontweight='bold')
        
        fig.text(0.35, y_footer,
                "ROBO: Transacción > 50% de media (extracción sospechosa)",
                fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFEBEE',
                         edgecolor='#D32F2F', linewidth=2),
                color='#D32F2F', fontweight='bold')
        
        fig.text(0.68, y_footer,
                "🚗 MAL USO: Transacciones > promedio O desigualdad > 3x",
                fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF3E0',
                         edgecolor='#F57C00', linewidth=2),
                color='#F57C00', fontweight='bold')
        
        guardar("05_anomalias_criticas.png", "Anomalias Detectadas - CON KPIS")
        
    except Exception as e:
        print(f" ❌ {str(e)[:80]}")


# ═══════════════════════════════════════════════════════════════════════════
#  GRÁFICO 6: ESTACIONALIDAD (Consumo por mes)
# ═══════════════════════════════════════════════════════════════════════════

def grafico_estacionalidad():
    """Consumo promedio por mes - Identifica picos y bajos"""
    print("[GRÁFICO 6] Estacionalidad...", end="")
    
    try:
        kpi = kpi_estacionalidad()
        if "error" in kpi:
            print(f" ❌ {kpi['error']}")
            return
        
        df = pd.DataFrame(kpi['datos']).sort_values('mes_numero')
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Colores según desviación del promedio
        promedio = kpi['estadisticas']['promedio_mensual']
        colores = [COLORES["critico"] if val > promedio * 1.1 else 
                   COLORES["exito"] if val < promedio * 0.9 else 
                   COLORES["alerta"]
                  for val in df['promedio']]
        
        x_pos = np.arange(len(df))
        bars = ax.bar(x_pos, df['promedio'], color=colores, 
                      edgecolor='black', linewidth=1.5, alpha=0.8)
        
        # Linea de promedio general
        ax.axhline(promedio, color=COLORES["gris"], linestyle='--', 
                  linewidth=2.5, alpha=0.7, label=f'Promedio: {promedio:,.0f}L')
        
        # Valores
        for bar, val in zip(bars, df['promedio']):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 100,
                   f'{val:,.0f}L',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(df['nombre_mes'], fontsize=10, rotation=45)
        ax.set_ylabel('Consumo Promedio (Litros)', fontweight='bold', fontsize=11)
        ax.set_title('ESTACIONALIDAD: Consumo Promedio por Mes (Análisis Histórico)', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Leyenda
        handles = [
            Patch(color=COLORES["critico"], label="Mes Pico"),
            Patch(color=COLORES["exito"], label="Mes Bajo"),
            Patch(color=COLORES["alerta"], label="Mes Normal"),
        ]
        ax.legend(handles=handles, loc='upper left', fontsize=9)
        
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        
        guardar("06_estacionalidad.png", "Análisis Estacional")
        
    except Exception as e:
        print(f" ❌ {str(e)[:50]}")


# ═══════════════════════════════════════════════════════════════════════════
#  GRÁFICO 7: FINES DE SEMANA
# ═══════════════════════════════════════════════════════════════════════════

def grafico_fines_semana():
    """Comparación consumo entre semana vs fin de semana"""
    print("[GRÁFICO 7] Consumo Fines de Semana...", end="")
    
    try:
        kpi = kpi_fines_semana()
        if "error" in kpi:
            print(f" ❌ {kpi['error']}")
            return
        
        df = pd.DataFrame(kpi['datos']).head(10)
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        x_pos = np.arange(len(df))
        width = 0.35
        
        # Barras comparativas
        bars1 = ax.bar(x_pos - width/2, df.get('ENTRE SEMANA', 0), width, 
                       label='Entre Semana', color=COLORES["primario"], 
                       edgecolor='black', linewidth=1)
        bars2 = ax.bar(x_pos + width/2, df.get('FIN DE SEMANA', 0), width,
                       label='Fin de Semana', color=COLORES["alerta"],
                       edgecolor='black', linewidth=1)
        
        # Valores
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}',
                       ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        etiquetas = [f"{row['placa']}\n{row['vehiculo'][:15]}" 
                    for _, row in df.iterrows()]
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(etiquetas, fontsize=8)
        ax.set_ylabel('Consumo (Litros)', fontweight='bold', fontsize=11)
        ax.set_title('Consumo: Entre Semana vs Fin de Semana', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=10, loc='upper right')
        
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        
        guardar("07_fines_semana.png", "Análisis Fines de Semana")
        
    except Exception as e:
        print(f" ❌ {str(e)[:50]}")


# ═══════════════════════════════════════════════════════════════════════════
#  GRÁFICO 8: EFICIENCIA POR ÁREA (Costo por Vehículo)
# ═══════════════════════════════════════════════════════════════════════════

def grafico_areas_eficiencia():
    """Eficiencia por área - Consumo promedio mensual por vehículo"""
    print("[GRÁFICO 8] Eficiencia por Área...", end="")
    
    try:
        kpi = kpi_areas_eficiencia()
        if "error" in kpi:
            print(f" ❌ {kpi['error']}")
            return
        
        df = pd.DataFrame(kpi['datos']).head(12)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Ordenar por consumo promedio mensual por vehículo (menor = más eficiente)
        df = df.sort_values('consumo_promedio_mes_por_vehiculo', ascending=True)
        
        # Colores según eficiencia
        colores_eficiencia = []
        max_consumo = df['consumo_promedio_mes_por_vehiculo'].max()
        min_consumo = df['consumo_promedio_mes_por_vehiculo'].min()
        
        for consumo in df['consumo_promedio_mes_por_vehiculo']:
            norm = (consumo - min_consumo) / (max_consumo - min_consumo) if max_consumo > min_consumo else 0.5
            if norm > 0.75:
                colores_eficiencia.append(COLORES["critico"])  # Rojo: muy ineficiente
            elif norm > 0.50:
                colores_eficiencia.append(COLORES["alerta"])   # Naranja: poco eficiente
            else:
                colores_eficiencia.append(COLORES["exito"])    # Verde: eficiente
        
        # Gráfico horizontal
        bars = ax.barh(df['area'], df['consumo_promedio_mes_por_vehiculo'], 
                       color=colores_eficiencia, edgecolor='black', linewidth=1.5)
        
        # Valores al final de las barras
        for i, (bar, val) in enumerate(zip(bars, df['consumo_promedio_mes_por_vehiculo'])):
            ax.text(val + 5, bar.get_y() + bar.get_height()/2.,
                   f' {val:.0f}L/mes',
                   ha='left', va='center', fontsize=10, fontweight='bold')
        
        # Línea de promedio
        promedio = df['consumo_promedio_mes_por_vehiculo'].mean()
        ax.axvline(promedio, color=COLORES["primario"], linestyle='--', 
                   linewidth=2.5, label=f'Promedio: {promedio:.0f}L/mes/veh', zorder=3)
        
        ax.set_xlabel('Consumo Promedio Mensual por Vehículo (Litros)', fontweight='bold', fontsize=11)
        ax.set_title('⚡ EFICIENCIA POR ÁREA: Consumo Promedio Mensual por Vehículo', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='lower right')
        
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}'))
        
        # Etiquetas en Y más pequeñas
        ax.tick_params(axis='y', labelsize=9)
        
        # Grid
        ax.grid(axis='x', alpha=0.3, linestyle=':')
        
        guardar("08_eficiencia_areas.png", "Eficiencia por Área")
        
    except Exception as e:
        print(f" ❌ {str(e)[:50]}")


# ═══════════════════════════════════════════════════════════════════════════
#  GRÁFICO 9: PREDICCIÓN
# ═══════════════════════════════════════════════════════════════════════════

def grafico_prediccion():
    """Predicción de consumo - Próximo mes CON ANÁLISIS DETALLADO"""
    print("[GRÁFICO 9] Predicción Consumo...", end="")
    
    try:
        kpi = kpi_prediccion()
        if "error" in kpi:
            print(f" ❌ {kpi['error']}")
            return
        
        # Datos de la predicción
        consumo_actual = kpi['consumo_actual']
        prediccion = kpi['prediccion_proximo_mes']
        historial = kpi['historial_meses']
        cambio_pct = kpi['cambio_porcentaje']
        promedio_hist = kpi['promedio_historico']
        tendencia = kpi['tendencia']
        minimo = kpi['minimo_historico']
        maximo = kpi['maximo_historico']
        diferencia_promedio = kpi['diferencia_promedio']
        
        # Crear figura con GridSpec
        fig = plt.figure(figsize=(16, 10))
        fig.patch.set_facecolor('white')
        
        gs = fig.add_gridspec(3, 1, height_ratios=[1, 2, 1.2], 
                              hspace=0.25, top=0.96, bottom=0.10, left=0.12, right=0.95)
        
        # ════════════════════════════════════════════════════════════════
        # SECCIÓN 1: TÍTULO Y RESPUESTA CLARA
        # ════════════════════════════════════════════════════════════════
        ax_titulo = fig.add_subplot(gs[0])
        ax_titulo.axis('off')
        
        # Título principal
        ax_titulo.text(0.5, 0.85, 'PREDICCIÓN: ¿Cuánto combustible necesitará el próximo mes?', 
                      ha='center', fontsize=16, fontweight='bold', transform=ax_titulo.transAxes)
        
        # RESPUESTA DIRECTA - KPI Principal
        respuesta = f"RESPUESTA: {prediccion:,.0f} Litros"
        color_respuesta = '#2E7D32' if cambio_pct < 5 else '#FFA726' if cambio_pct < 10 else '#E53935'
        
        ax_titulo.text(0.5, 0.45, respuesta, 
                      ha='center', fontsize=22, fontweight='bold', color=color_respuesta,
                      transform=ax_titulo.transAxes,
                      bbox=dict(boxstyle='round,pad=1', facecolor='#F5F5F5', 
                               edgecolor=color_respuesta, linewidth=3))
        
        # Subtítulo con contexto
        subtitulo = f"Tendencia: {tendencia} | Cambio esperado: {cambio_pct:+.1f}% vs mes anterior"
        ax_titulo.text(0.5, 0.05, subtitulo, 
                      ha='center', fontsize=11, style='italic', color='#666',
                      transform=ax_titulo.transAxes)
        
        # ════════════════════════════════════════════════════════════════
        # SECCIÓN 2: GRÁFICO CON TENDENCIA E HISTORIAL
        # ════════════════════════════════════════════════════════════════
        ax = fig.add_subplot(gs[1])
        
        # Preparar datos
        df_hist = pd.DataFrame(historial).sort_values('mes')
        meses = df_hist['mes'].values
        consumos = df_hist['consumo_total'].values
        
        # Línea del historial
        ax.plot(range(len(meses)), consumos, marker='o', linewidth=3, 
               markersize=8, color='#1976D2', label='Consumo histórico', zorder=3)
        
        # Línea de tendencia
        x_trend = np.arange(len(meses))
        z = np.polyfit(x_trend, consumos, 1)
        p = np.poly1d(z)
        ax.plot(x_trend, p(x_trend), '--', linewidth=2.5, color='#FF6F00', 
               alpha=0.7, label='Línea de tendencia', zorder=2)
        
        # Predicción (punto futuro)
        x_pred = len(meses)
        ax.plot(x_pred, prediccion, marker='*', markersize=30, color='#2E7D32', 
               label='Predicción próximo mes', zorder=4)
        
        # Línea de referencia promedio
        ax.axhline(y=promedio_hist, color='#999999', linestyle=':', linewidth=2, 
                  alpha=0.6, label=f'Promedio histórico: {promedio_hist:,.0f}L')
        
        # Área sombreada entre min y max
        ax.fill_between(range(len(meses)), minimo, maximo, alpha=0.1, color='#1976D2')
        
        # Etiquetas del eje x
        labels_x = [mes[-5:] if i % 2 == 0 else '' for i, mes in enumerate(meses)]
        labels_x.append('Próximo\nMes')
        ax.set_xticks(range(len(meses) + 1))
        ax.set_xticklabels(labels_x, fontsize=10)
        
        # Valores en los puntos del historial
        for i, (mes, val) in enumerate(zip(meses, consumos)):
            ax.text(i, val + 800, f'{val:,.0f}L', ha='center', va='bottom', 
                   fontsize=8, fontweight='bold')
        
        # Valor predicción
        ax.text(x_pred, prediccion + 800, f'{prediccion:,.0f}L\n(PREDICCIÓN)', 
               ha='center', va='bottom', fontsize=10, fontweight='bold', 
               color='#2E7D32', bbox=dict(boxstyle='round,pad=0.5', 
               facecolor='#E8F5E9', edgecolor='#2E7D32', linewidth=2))
        
        ax.set_ylabel('Consumo (Litros)', fontweight='bold', fontsize=12)
        ax.set_title('Histórico de Consumo y Predicción', fontweight='bold', fontsize=13, pad=15)
        ax.legend(loc='upper left', fontsize=10, frameon=True, fancybox=True)
        ax.grid(True, alpha=0.3, linestyle='--', zorder=1)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
        
        # ════════════════════════════════════════════════════════════════
        # SECCIÓN 3: INFORMACIÓN SIMPLE
        # ════════════════════════════════════════════════════════════════
        ax_info = fig.add_subplot(gs[2])
        ax_info.axis('off')
        
        # Información clave simple
        info_text = f"""
INFORMACIÓN CLAVE

Predicción Próximo Mes: {prediccion:,.0f} Litros
Mes Anterior: {consumo_actual:,.0f} Litros
Promedio Histórico (12 meses): {promedio_hist:,.0f} Litros
        
Cambio esperado: {cambio_pct:+.1f}%
Tendencia: {'CRECIENTE' if cambio_pct > 0 else 'DECRECIENTE'}
Rango histórico: {minimo:,.0f}L a {maximo:,.0f}L
        """
        
        ax_info.text(0.05, 0.95, info_text, transform=ax_info.transAxes,
                    fontsize=10, verticalalignment='top', family='monospace',
                    bbox=dict(boxstyle='round', facecolor='#F5F5F5', 
                             edgecolor='#999999', linewidth=1, alpha=0.8))
        
        guardar("09_prediccion.png", "Predicción de Consumo")
        
    except Exception as e:
        print(f" ❌ {str(e)[:50]}")


# ═══════════════════════════════════════════════════════════════════════════
#  EJECUCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def generar_todos():
    """Generar todos los gráficos"""
    print("\n" + "="*80)
    print("  🎨 GENERANDO GRÁFICOS PROFESIONALES - SISTEMA KPI")
    print("="*80)
    
    grafico_consumo_vehiculo()
    grafico_consumo_area()
    grafico_eficiencia()
    grafico_desviacion()
    grafico_anomalias()
    grafico_estacionalidad()
    grafico_fines_semana()
    grafico_areas_eficiencia()
    grafico_prediccion()
    
    print("\n" + "="*80)
    print("  ✅ GRÁFICOS GENERADOS EN: graficos_kpi/")
    print("="*80 + "\n")


if __name__ == "__main__":
    generar_todos()
