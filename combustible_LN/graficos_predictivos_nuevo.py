"""
GRÁFICOS PREDICTIVOS V2 — SISTEMA DE COMBUSTIBLE
Municipio de Caranavi

Versión simplificada: 6 gráficos accionables para toma de decisiones.
Elimina: mapas de calor, radar, semáforo corrupto, proyecciones técnicas inútiles.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from pathlib import Path

from logica_negocio_predictiva import (
    plan_compras_mensual,
    presupuesto_anual_escenarios,
    distribucion_stock_decision,
    vehiculos_costo_y_reemplazo,
    simulador_ahorro_escenarios,
    calendario_compras_con_precios,
    estimacion_costos_futuros,
    tabla_resumen_ejecutivo,
)

# ══════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN VISUAL
# ══════════════════════════════════════════════════════════════════════
COLOR_DIESEL = "#1565C0"
COLOR_GASOLINA = "#2E7D32"
COLOR_ALERTA = "#F57F17"
COLOR_CRITICO = "#C62828"
COLOR_OK = "#43A047"
COLOR_NARANJA = "#FF9800"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.family": "DejaVu Sans",
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

SALIDA = Path("graficos_v2")
SALIDA.mkdir(exist_ok=True)


def guardar(nombre: str):
    path = SALIDA / nombre
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Guardado: {path}")


# ══════════════════════════════════════════════════════════════════════
#  G1. PLAN DE COMPRAS MENSUAL (reemplaza proyección lineal inútil)
# ══════════════════════════════════════════════════════════════════════

def grafico_plan_compras():
    print("\n[G1] Plan de compras mensual...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    for idx, (tipo, color) in enumerate([("DIESEL", COLOR_DIESEL), ("GASOLINA", COLOR_GASOLINA)]):
        ax = axes[idx]
        datos = plan_compras_mensual(tipo)
        
        if "error" in datos:
            ax.text(0.5, 0.5, f"Sin datos - {tipo}", ha="center", va="center")
            continue
        
        # Crear visualización de rangos
        promedio = datos["promedio_historico"]
        maximo = datos["maximo_historico"]
        minimo = datos["minimo_historico"]
        recomendacion = datos["recomendacion_compra"]
        
        # Zonas de riesgo
        ax.axhspan(0, minimo, alpha=0.1, color=COLOR_OK, label=f"Mínimo histórico: {minimo:,.0f}L")
        ax.axhspan(minimo, promedio, alpha=0.2, color=COLOR_OK, label=f"Zona normal")
        ax.axhspan(promedio, recomendacion, alpha=0.3, color=COLOR_NARANJA, label=f"Recomendación: {recomendacion:,.0f}L")
        ax.axhspan(recomendacion, maximo, alpha=0.2, color=COLOR_ALERTA, label=f"Máximo histórico: {maximo:,.0f}L")
        
        # Líneas clave
        ax.axhline(promedio, color="gray", linestyle="--", linewidth=2, label=f"Promedio: {promedio:,.0f}L")
        ax.axhline(recomendacion, color=color, linestyle="-", linewidth=3, label=f"COMPRAR: {recomendacion:,.0f}L")
        
        # Punto de recomendación
        ax.scatter([0.5], [recomendacion], s=200, c=color, zorder=5, marker="D")
        ax.annotate(f"COMPRAR\n{recomendacion:,.0f}L\nBs {datos['costo_estimado_bs']:,.0f}",
                   xy=(0.5, recomendacion), xytext=(0.7, recomendacion + maximo*0.1),
                   fontsize=12, fontweight="bold", color=color,
                   ha="center", va="bottom",
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor=color, linewidth=2))
        
        # Configuración
        ax.set_xlim(0, 1)
        ax.set_ylim(0, maximo * 1.2)
        ax.set_ylabel("Litros", fontsize=12)
        ax.set_title(f"PLAN DE COMPRAS - {tipo}\n{datos['justificacion'][:60]}...", fontsize=12)
        ax.set_xticks([])
        ax.legend(loc="upper left", fontsize=9)
        ax.grid(axis="y", alpha=0.3, linestyle=":")
        
        # Panel de información
        info_text = (f"📊 DATOS REALES\n"
                    f"• Promedio: {promedio:,.0f}L\n"
                    f"• Máximo: {maximo:,.0f}L\n"
                    f"• Mínimo: {minimo:,.0f}L\n"
                    f"• Variación: {datos['variacion_tipica']:.0f}%\n\n"
                    f"💡 ACCIÓN\n"
                    f"Comprar: {recomendacion:,.0f}L\n"
                    f"Costo: Bs {datos['costo_estimado_bs']:,.0f}\n"
                    f"Cubre 84% de meses")
        
        ax.text(1.02, 0.5, info_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='center', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8, pad=1))
    
    plt.suptitle("PLAN DE COMPRAS MENSUAL DE COMBUSTIBLE\nBasado en estadísticas históricas reales (no proyecciones)",
                fontsize=16, fontweight="bold", y=1.02)
    plt.subplots_adjust(right=0.85)
    guardar("G1_plan_compras_mensual.png")


# ══════════════════════════════════════════════════════════════════════
#  G2. PRESUPUESTO ANUAL CON ESCENARIOS (mejorado)
# ══════════════════════════════════════════════════════════════════════

def grafico_presupuesto_anual():
    print("[G2] Presupuesto anual con escenarios...")
    
    datos = presupuesto_anual_escenarios()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), gridspec_kw={"width_ratios": [1, 1.2]})
    
    # Gráfico de barras: comparación de escenarios
    escenarios = ["Optimista\n(-15% eficiencia)", "Base\n(recomendado)", "Pesimista\n(peor mes x12)"]
    valores = [datos["total_optimista_bs"], datos["total_base_bs"], datos["total_pesimista_bs"]]
    colores = [COLOR_OK, COLOR_DIESEL, COLOR_ALERTA]
    
    bars = ax1.bar(escenarios, valores, color=colores, alpha=0.8, edgecolor="black", linewidth=1.5)
    
    # Destacar el recomendado
    bars[1].set_linewidth(3)
    bars[1].set_edgecolor("black")
    
    # Valores sobre barras
    for bar, val in zip(bars, valores):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(valores)*0.01,
                f"Bs {val:,.0f}", ha="center", va="bottom", fontsize=12, fontweight="bold")
    
    # Línea de recomendación
    ax1.axhline(datos["recomendacion_solicitud"], color=COLOR_CRITICO, linestyle="--", linewidth=2,
               label=f"Solicitar: Bs {datos['recomendacion_solicitud']:,.0f}")
    
    ax1.set_ylabel("Bolivianos (Bs)", fontsize=12)
    ax1.set_title("PRESUPUESTO ANUAL 2026\nEscenarios de inversión", fontsize=13, fontweight="bold")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Bs {x/1000:.0f}K"))
    ax1.legend(fontsize=10)
    ax1.grid(axis="y", alpha=0.3, linestyle=":")
    
    # Tabla detallada
    ax2.axis("off")
    
    # Crear tabla de datos
    filas_tabla = []
    for tipo, info in datos["por_tipo"].items():
        filas_tabla.append([
            tipo,
            f"{info['litros_anual_base']:,.0f} L",
            f"Bs {info['costo_optimista_bs']:,.0f}",
            f"Bs {info['costo_base_bs']:,.0f}",
            f"Bs {info['costo_pesimista_bs']:,.0f}"
        ])
    
    # Totales
    filas_tabla.append([
        "TOTAL",
        "",
        f"Bs {datos['total_optimista_bs']:,.0f}",
        f"Bs {datos['total_base_bs']:,.0f}",
        f"Bs {datos['total_pesimista_bs']:,.0f}"
    ])
    
    tabla = ax2.table(cellText=filas_tabla,
                     colLabels=["Tipo", "Litros/Año", "Optimista", "Base", "Pesimista"],
                     cellLoc="center", loc="center",
                     colWidths=[0.2, 0.25, 0.2, 0.2, 0.2])
    
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    tabla.scale(1.2, 2.5)
    
    # Colores
    for j in range(5):
        tabla[0, j].set_facecolor("#1565C0")
        tabla[0, j].set_text_props(color="white", fontweight="bold")
    
    # Destacar fila total
    for j in range(5):
        tabla[len(filas_tabla), j].set_facecolor("#FFF9C4")
        tabla[len(filas_tabla), j].set_text_props(fontweight="bold")
    
    # Destacar columna base
    for i in range(1, len(filas_tabla) + 1):
        tabla[i, 3].set_facecolor("#E3F2FD")
    
    ax2.set_title("DETALLE POR TIPO DE COMBUSTIBLE\n(Y precio de referencia)",
                 fontsize=13, fontweight="bold", pad=20)
    
    # Texto de recomendación
    ax2.text(0.5, 0.02, f"💡 RECOMENDACIÓN: Solicitar Bs {datos['recomendacion_solicitud']:,.0f}\n"
                        f"(Escenario base + 5% contingencia)",
            transform=ax2.transAxes, ha="center", va="bottom", fontsize=12,
            fontweight="bold", color=COLOR_CRITICO,
            bbox=dict(boxstyle="round,pad=0.7", facecolor="white", edgecolor=COLOR_CRITICO))
    
    plt.suptitle(f"PRESUPUESTO ANUAL PARA COMBUSTIBLE - {datos['anio']}",
                fontsize=16, fontweight="bold")
    guardar("G2_presupuesto_anual.png")


# ══════════════════════════════════════════════════════════════════════
#  G3. DISTRIBUCIÓN DE STOCK (decisión práctica)
# ══════════════════════════════════════════════════════════════════════

def grafico_distribucion_stock(litros_disponibles: float = 5000):
    print(f"[G3] Distribución de stock ({litros_disponibles:,.0f}L)...")
    
    datos = distribucion_stock_decision(litros_disponibles, "DIESEL")
    
    if "error" in datos:
        print(f"    Error: {datos['error']}")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw={"width_ratios": [1.5, 1]})
    
    # Gráfico de barras horizontales
    df = pd.DataFrame(datos["tabla_asignacion"])
    df = df.head(10)  # Top 10 áreas
    
    y_pos = np.arange(len(df))
    
    # Colores según prioridad
    colores = []
    for _, row in df.iterrows():
        if "CRÍTICO" in row["prioridad"]:
            colores.append(COLOR_CRITICO)
        elif "ALERTA" in row["prioridad"]:
            colores.append(COLOR_ALERTA)
        else:
            colores.append(COLOR_OK)
    
    bars = ax1.barh(y_pos, df["litros_asignados"], color=colores, alpha=0.8, edgecolor="black")
    
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([a[:30] for a in df["area"]], fontsize=10)
    ax1.set_xlabel("Litros asignados", fontsize=11)
    ax1.set_title(f"DISTRIBUCIÓN DE {litros_disponibles:,.0f}L DE DIESEL\nPor área según consumo histórico",
                 fontsize=13, fontweight="bold")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    
    # Etiquetas con días de cobertura
    for i, (bar, row) in enumerate(zip(bars, df.itertuples())):
        ax1.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
                f"{row.litros_asignados:,.0f}L ({row.dias_cobertura:.0f} días)",
                va="center", fontsize=9, fontweight="bold")
    
    ax1.grid(axis="x", alpha=0.3, linestyle=":")
    
    # Panel informativo
    ax2.axis("off")
    
    info = (f"📊 RESUMEN DE DECISIÓN\n\n"
           f"Stock disponible: {datos['litros_disponibles']:,.0f}L\n"
           f"Necesidad total mensual: {datos['necesidad_total_mensual']:,.0f}L\n"
           f"Cobertura: {datos['porcentaje_cubierto']:.1f}%\n"
           f"Cobertura promedio: {datos['cobertura_promedio_dias']:.0f} días\n\n"
           f"🚨 ÁREAS CRÍTICAS: {datos['areas_criticas_count']}\n\n"
           f"💡 RECOMENDACIÓN:\n{datos['recomendacion'][:150]}...")
    
    ax2.text(0.1, 0.5, info, transform=ax2.transAxes, fontsize=11,
            verticalalignment='center', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9, pad=1))
    
    # Leyenda
    leyenda = [
        mpatches.Patch(color=COLOR_CRITICO, label="🔴 < 7 días (CRÍTICO)"),
        mpatches.Patch(color=COLOR_ALERTA, label="🟡 7-15 días (ALERTA)"),
        mpatches.Patch(color=COLOR_OK, label="🟢 > 15 días (OK)")
    ]
    ax1.legend(handles=leyenda, loc="lower right", fontsize=9)
    
    plt.suptitle("¿A QUÉ ÁREAS DISTRIBUIR EL COMBUSTIBLE DISPONIBLE?",
                fontsize=16, fontweight="bold")
    guardar("G3_distribucion_stock.png")


# ══════════════════════════════════════════════════════════════════════
#  G4. VEHÍCULOS: COSTO Y REEMPLAZO (unificado)
# ══════════════════════════════════════════════════════════════════════

def grafico_vehiculos_costo_reemplazo():
    print("[G4] Vehículos costosos y alertas de reemplazo...")
    
    datos = vehiculos_costo_y_reemplazo(costo_vehiculo_nuevo_bs=120_000, meses_futuro=6)
    
    if "error" in datos:
        print(f"    Error: {datos['error']}")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), gridspec_kw={"height_ratios": [2, 1]})
    
    # Gráfico superior: Top vehículos
    top = pd.DataFrame(datos["top_15_vehiculos"])
    
    x_pos = np.arange(len(top))
    
    # Colores según alerta
    colores = []
    for alerta in top["alerta_reemplazo"]:
        if "🔴" in alerta:
            colores.append(COLOR_CRITICO)
        elif "🟡" in alerta:
            colores.append(COLOR_ALERTA)
        elif "🟠" in alerta:
            colores.append(COLOR_NARANJA)
        else:
            colores.append(COLOR_OK)
    
    bars = ax1.bar(x_pos, top["costo_proyectado_6m"], color=colores, alpha=0.85, edgecolor="black")
    
    # Línea de promedio
    promedio = top["costo_proyectado_6m"].mean()
    ax1.axhline(promedio, color="gray", linestyle="--", linewidth=2, label=f"Promedio: Bs {promedio:,.0f}")
    
    # Etiquetas
    etiquetas = [f"{p}\n{v[:15]}" for p, v in zip(top["placa"], top["vehiculo"])]
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(etiquetas, rotation=45, ha="right", fontsize=9)
    ax1.set_ylabel("Costo proyectado 6 meses (Bs)", fontsize=11)
    ax1.set_title("TOP 15 VEHÍCULOS MÁS COSTOSOS - Próximo Semestre\nColor = alerta de reemplazo",
                 fontsize=13, fontweight="bold")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Bs {x/1000:.0f}K"))
    ax1.legend(fontsize=10)
    ax1.grid(axis="y", alpha=0.3, linestyle=":")
    
    # Anotaciones de alerta
    for i, (bar, row) in enumerate(zip(bars, top.itertuples())):
        if "🔴" in row.alerta_reemplazo:
            ax1.annotate("REEMPLAZAR", 
                       xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                       xytext=(0, 10), textcoords="offset points",
                       ha="center", fontsize=8, fontweight="bold", color=COLOR_CRITICO,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8))
    
    # Panel inferior: Resumen de alertas
    ax2.axis("off")
    
    resumen = datos["resumen_alertas"]
    info = (f"🚨 RESUMEN DE ALERTAS DE VEHÍCULOS\n\n"
           f"🔴 REEMPLAZO URGENTE: {resumen['reemplazar_urgente']} vehículos\n"
           f"   (Costo combustible > valor vehículo nuevo)\n\n"
           f"🟡 EVALUAR REEMPLAZO: {resumen['evaluar']} vehículos\n"
           f"   (>75% del valor del vehículo en combustible)\n\n"
           f"🟠 ALTO CONSUMO: {resumen['alto_consumo']} vehículos\n"
           f"   (>Bs 30,000 en 6 meses proyectados)\n\n"
           f"💰 INVERSIÓN PROYECTADA (Top 15):\n"
           f"   Bs {datos['inversion_proyectada_6m_top15']:,.0f} en 6 meses\n\n"
           f"📋 ACCIÓN RECOMENDADA:\n"
           f"   Evaluar técnica y económicamente los {resumen['reemplazar_urgente']} \n"
           f"   vehículos marcados para reemplazo inmediato.")
    
    ax2.text(0.5, 0.5, info, transform=ax2.transAxes, fontsize=12,
            verticalalignment='center', horizontalalignment='center',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='#FFEBEE', alpha=0.9, pad=1.5))
    
    plt.suptitle("ANÁLISIS DE VEHÍCULOS: ¿REEMPLAZAR O MANTENER?",
                fontsize=16, fontweight="bold", y=0.98)
    guardar("G4_vehiculos_reemplazo.png")


# ══════════════════════════════════════════════════════════════════════
#  G5. SIMULADOR DE AHORRO (mantener - ya está bien)
# ══════════════════════════════════════════════════════════════════════

def grafico_simulador_ahorro():
    print("[G5] Simulador de ahorro...")
    
    datos = simulador_ahorro_escenarios([5, 10, 15, 20], 12)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Gráfico 1: Escenarios de ahorro
    escenarios = datos["escenarios"]
    x_labels = [f"-{e['reduccion_porcentaje']}%" for e in escenarios]
    ahorros = [e["ahorro_anual_bs"] for e in escenarios]
    
    bars = ax1.bar(x_labels, ahorros, color=[COLOR_OK, COLOR_GASOLINA, COLOR_ALERTA, COLOR_NARANJA],
                   alpha=0.85, edgecolor="black", linewidth=1.5)
    
    # Destacar el de 10%
    bars[1].set_linewidth(3)
    bars[1].set_edgecolor("black")
    
    # Etiquetas
    for bar, esc in zip(bars, escenarios):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(ahorros)*0.01,
                f"Bs {esc['ahorro_anual_bs']:,.0f}\n({esc['ahorro_litros']:,.0f} L)\n"
                f"≈ {esc['equivalente_salarios_minimos']:.0f} SMN",
                ha="center", va="bottom", fontsize=10, fontweight="bold")
    
    ax1.set_ylabel("Ahorro anual (Bs)", fontsize=12)
    ax1.set_xlabel("Reducción de consumo", fontsize=12)
    ax1.set_title("AHORRO PROYECTADO SEGÚN REDUCCIÓN\n¿Cuánto ahorramos si reducimos X%?",
                 fontsize=13, fontweight="bold")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Bs {x/1000:.0f}K"))
    ax1.grid(axis="y", alpha=0.3, linestyle=":")
    
    # Gráfico 2: Comparación base vs 10%
    esc_10 = escenarios[1] if len(escenarios) > 1 else escenarios[0]
    
    categorias = ["Costo actual\n(sin cambios)", "Con reducción\ndel 10%"]
    valores = [datos["costo_base_anual_bs"], esc_10["nuevo_costo_anual"]]
    colores_comp = [COLOR_CRITICO, COLOR_OK]
    
    bars2 = ax2.bar(categorias, valores, color=colores_comp, alpha=0.85, 
                    edgecolor="black", linewidth=2, width=0.5)
    
    # Flecha de ahorro
    ax2.annotate(f"AHORRO:\nBs {esc_10['ahorro_anual_bs']:,.0f}",
                xy=(1, esc_10["nuevo_costo_anual"]),
                xytext=(0.5, (datos["costo_base_anual_bs"] + esc_10["nuevo_costo_anual"])/2),
                fontsize=14, fontweight="bold", color=COLOR_GASOLINA, ha="center",
                arrowprops=dict(arrowstyle="->", color=COLOR_GASOLINA, lw=3),
                bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor=COLOR_GASOLINA, linewidth=2))
    
    # Valores
    for bar, val in zip(bars2, valores):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(valores)*0.02,
                f"Bs {val:,.0f}", ha="center", va="bottom", fontsize=14, fontweight="bold")
    
    ax2.set_ylabel("Costo anual (Bs)", fontsize=12)
    ax2.set_title("IMPACTO DE REDUCIR 10% EL CONSUMO\nAhorro significativo con esfuerzo moderado",
                 fontsize=13, fontweight="bold")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Bs {x/1000:.0f}K"))
    ax2.grid(axis="y", alpha=0.3, linestyle=":")
    
    plt.suptitle("SIMULADOR DE AHORRO - POLÍTICAS DE REDUCCIÓN DE CONSUMO",
                fontsize=16, fontweight="bold")
    guardar("G5_simulador_ahorro.png")


# ══════════════════════════════════════════════════════════════════════
#  G6. CALENDARIO DE COMPRAS CON PROYECCIÓN DE PRECIOS (nuevo)
# ══════════════════════════════════════════════════════════════════════

def grafico_calendario_precios():
    print("[G6] Calendario de compras con proyección de precios...")
    
    datos = calendario_compras_con_precios(meses=6, inflacion_mensual=0.0025)  # 3% anual
    
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    
    for idx, (tipo, color_base) in enumerate([("DIESEL", COLOR_DIESEL), ("GASOLINA", COLOR_GASOLINA)]):
        ax = axes[idx]
        
        # Filtrar datos
        df_tipo = [d for d in datos["calendario_detalle"] if d["tipo_combustible"] == tipo]
        if not df_tipo:
            continue
        
        meses = [d["mes"] for d in df_tipo]
        consumos = [d["consumo_litros"] for d in df_tipo]
        reservas = [d["reserva_seguridad_litros"] for d in df_tipo]
        compras = [d["cantidad_comprar_litros"] for d in df_tipo]
        precios = [d["precio_proyectado_bs"] for d in df_tipo]
        
        x = np.arange(len(meses))
        width = 0.25
        
        # Barras apiladas
        b1 = ax.bar(x - width, consumos, width, label="Consumo necesario", color=color_base, alpha=0.6)
        b2 = ax.bar(x, reservas, width, label="Reserva 15%", color=COLOR_ALERTA, alpha=0.7)
        b3 = ax.bar(x + width, compras, width, label="Compra recomendada", color=COLOR_CRITICO if tipo=="DIESEL" else COLOR_GASOLINA, alpha=0.9)
        
        # Línea de precio proyectado (eje secundario)
        ax2 = ax.twinx()
        line = ax2.plot(x, precios, 'o-', color='black', linewidth=2, markersize=6, label=f"Precio proyectado")
        ax2.set_ylabel("Precio Bs/L", fontsize=10, color='black')
        ax2.tick_params(axis='y', labelcolor='black')
        
        # Etiquetas de precio
        for i, p in enumerate(precios):
            ax2.annotate(f"Bs {p:.2f}", xy=(i, p), xytext=(0, 10), 
                        textcoords="offset points", ha="center", fontsize=8, color='black')
        
        ax.set_xticks(x)
        ax.set_xticklabels(meses, rotation=45, ha="right")
        ax.set_ylabel("Litros", fontsize=11)
        ax.set_title(f"CALENDARIO DE COMPRAS - {tipo}\nCon proyección de precios (inflación 3% anual)",
                    fontsize=12, fontweight="bold")
        ax.legend(loc="upper left", fontsize=9)
        ax2.legend(loc="upper right", fontsize=9)
        ax.grid(axis="y", alpha=0.3, linestyle=":")
        
        # Total a invertir en este tipo
        total_tipo = sum(d["costo_compra_bs"] for d in df_tipo)
        ax.text(0.98, 0.95, f"Inversión {tipo}: Bs {total_tipo:,.0f}",
               transform=ax.transAxes, ha="right", va="top", fontsize=11,
               fontweight="bold", color=color_base,
               bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor=color_base))
    
    plt.suptitle(f"CALENDARIO DE COMPRAS 6 MESES - CON PROYECCIÓN DE PRECIOS\n"
                f"Inversión total proyectada: Bs {datos['inversion_total_bs']:,.0f} | "
                f"Impacto inflación: Bs {sum(r['impacto_inflacion_bs'] for r in datos['resumen_por_tipo'].values()):,.0f}",
                fontsize=14, fontweight="bold")
    plt.tight_layout()
    guardar("G6_calendario_precios.png")


# ══════════════════════════════════════════════════════════════════════
#  G7. ESTIMACIÓN DE COSTOS FUTUROS (nuevo - solicitado)
# ══════════════════════════════════════════════════════════════════════

def grafico_estimacion_costos_futuros():
    print("[G7] Estimación de costos futuros con proyección de precios...")
    
    # Obtener datos para 3 escenarios
    esc_conservador = estimacion_costos_futuros(12, "conservador")
    esc_moderado = estimacion_costos_futuros(12, "moderado")
    esc_pesimista = estimacion_costos_futuros(12, "pesimista")
    
    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # Gráfico grande: Evolución mensual de costos
    ax_main = fig.add_subplot(gs[:, 0])
    
    meses = list(range(1, 13))
    
    # Datos para cada escenario
    costos_cons = [m["costo_total_mes_bs"] for m in esc_conservador["proyeccion_mensual"]]
    costos_mod = [m["costo_total_mes_bs"] for m in esc_moderado["proyeccion_mensual"]]
    costos_pes = [m["costo_total_mes_bs"] for m in esc_pesimista["proyeccion_mensual"]]
    
    ax_main.fill_between(meses, costos_cons, costos_pes, alpha=0.2, color=COLOR_ALERTA, 
                        label="Rango de incertidumbre")
    ax_main.plot(meses, costos_cons, 'o-', color=COLOR_OK, linewidth=2, label="Conservador (sin inflación)")
    ax_main.plot(meses, costos_mod, 's-', color=COLOR_DIESEL, linewidth=3, label="Moderado (3% anual)")
    ax_main.plot(meses, costos_pes, '^-', color=COLOR_CRITICO, linewidth=2, label="Pesimista (8% + shock)")
    
    ax_main.set_xlabel("Mes", fontsize=12)
    ax_main.set_ylabel("Costo mensual (Bs)", fontsize=12)
    ax_main.set_title("PROYECCIÓN DE INVERSIÓN MENSUAL EN COMBUSTIBLE\n"
                     "3 escenarios de precios internacionales/locales",
                     fontsize=13, fontweight="bold")
    ax_main.legend(fontsize=10, loc="upper left")
    ax_main.grid(alpha=0.3, linestyle=":")
    ax_main.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Bs {x/1000:.0f}K"))
    
    # Anotaciones
    ax_main.annotate(f"Shock de precios\nmes 6", xy=(6, costos_pes[5]), 
                    xytext=(8, costos_pes[5] + 20000),
                    fontsize=10, ha="center",
                    arrowprops=dict(arrowstyle="->", color=COLOR_CRITICO),
                    bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.7))
    
    # Gráfico superior derecha: Comparación anual
    ax_comp = fig.add_subplot(gs[0, 1])
    
    escenarios = ["Conservador", "Moderado", "Pesimista"]
    totales = [esc_conservador["total_anual_proyectado_bs"],
              esc_moderado["total_anual_proyectado_bs"],
              esc_pesimista["total_anual_proyectado_bs"]]
    colores = [COLOR_OK, COLOR_DIESEL, COLOR_CRITICO]
    
    bars = ax_comp.bar(escenarios, totales, color=colores, alpha=0.8, edgecolor="black", linewidth=1.5)
    bars[1].set_linewidth(3)  # Destacar moderado
    
    for bar, val in zip(bars, totales):
        ax_comp.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(totales)*0.01,
                    f"Bs {val:,.0f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    
    ax_comp.set_ylabel("Total anual (Bs)", fontsize=11)
    ax_comp.set_title("INVERSIÓN ANUAL TOTAL\nPor escenario de precios", fontsize=12, fontweight="bold")
    ax_comp.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Bs {x/1000:.0f}K"))
    ax_comp.grid(axis="y", alpha=0.3, linestyle=":")
    
    # Panel inferior derecha: Tabla de trimestres (escenario moderado)
    ax_tabla = fig.add_subplot(gs[1, 1])
    ax_tabla.axis("off")
    
    trimestres = esc_moderado["resumen_trimestral"]
    filas = [[f"Q{t['trimestre']}", 
             f"Bs {t['costo_bs']:,.0f}",
             f"Bs {t['precio_promedio_diesel']:.2f}",
             f"Bs {t['precio_promedio_gasolina']:.2f}"] for t in trimestres]
    
    tabla = ax_tabla.table(cellText=filas,
                          colLabels=["Trimestre", "Inversión", "Precio Diesel", "Precio Gasolina"],
                          cellLoc="center", loc="center",
                          colWidths=[0.25, 0.35, 0.2, 0.2])
    
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    tabla.scale(1.2, 2.5)
    
    for j in range(4):
        tabla[0, j].set_facecolor("#1565C0")
        tabla[0, j].set_text_props(color="white", fontweight="bold")
    
    # Destacar trimestre más caro
    max_q = max(trimestres, key=lambda x: x["costo_bs"])["trimestre"]
    for i, t in enumerate(trimestres):
        if t["trimestre"] == max_q:
            for j in range(4):
                tabla[i+1, j].set_facecolor("#FFEBEE")
    
    ax_tabla.set_title("DETALLE TRIMESTRAL (Escenario Moderado)\nResaltado = trimestre más costoso",
                      fontsize=12, fontweight="bold", pad=20)
    
    # Texto de recomendación general
    fig.text(0.5, 0.02, 
            f"💡 RECOMENDACIÓN: Solicitar presupuesto por Bs {esc_moderado['total_anual_proyectado_bs']:,.0f} "
            f"(escenario moderado). Riesgo de alza: Bs {esc_pesimista['total_anual_proyectado_bs'] - esc_moderado['total_anual_proyectado_bs']:,.0f} adicionales. "
            f"Considerar compras anticipadas antes del mes 6.",
            ha="center", fontsize=12, fontweight="bold", color=COLOR_CRITICO,
            bbox=dict(boxstyle="round,pad=0.7", facecolor="lightyellow", edgecolor=COLOR_CRITICO))
    
    plt.suptitle("ESTIMACIÓN DE COSTOS FUTUROS - PROYECCIÓN DE INVERSIÓN ANUAL",
                fontsize=16, fontweight="bold", y=0.98)
    guardar("G7_estimacion_costos_futuros.png")


# ══════════════════════════════════════════════════════════════════════
#  G8. TABLERO RESUMEN EJECUTIVO (nuevo - una página)
# ══════════════════════════════════════════════════════════════════════

def grafico_resumen_ejecutivo():
    print("[G8] Tablero resumen ejecutivo...")
    
    datos = tabla_resumen_ejecutivo()
    kpis = datos["indicadores_clave"]
    
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor('white')
    
    # Título principal
    fig.text(0.5, 0.95, "DASHBOARD EJECUTIVO - GESTIÓN DE COMBUSTIBLE",
            ha="center", fontsize=20, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.8", facecolor="#1565C0", edgecolor="black", linewidth=2),
            color="white")
    
    fig.text(0.5, 0.91, f"Generado: {datos['fecha_generacion']} | Municipio de Caranavi",
            ha="center", fontsize=12, style="italic")
    
    # KPIs principales (4 cajas)
    kpi_data = [
        ("COMPRA MENSUAL\nRECOMENDADA", 
         f"{kpis['compra_mensual_recomendada_diesel_litros'] + kpis['compra_mensual_recomendada_gasolina_litros']:,.0f} L",
         f"Bs {kpis['costo_mensual_estimado_bs']:,.0f}/mes"),
        ("PRESUPUESTO ANUAL\nA SOLICITAR", 
         f"Bs {kpis['presupuesto_anual_solicitar_bs']:,.0f}",
         f"≈ Bs {kpis['presupuesto_anual_solicitar_bs']/12:,.0f}/mes"),
        ("INVERSIÓN ANUAL\nPROYECTADA", 
         f"Bs {kpis['inversion_anual_moderada_bs']:,.0f}",
         f"Escenario moderado"),
        ("VEHÍCULOS EN\nALERTA CRÍTICA", 
         f"{kpis['vehiculos_reemplazar_urgente']}",
         f"Requieren reemplazo"),
    ]
    
    positions = [(0.15, 0.75), (0.40, 0.75), (0.65, 0.75), (0.85, 0.75)]
    
    for (titulo, valor, subtitulo), (x, y) in zip(kpi_data, positions):
        ax = fig.add_axes([x-0.1, y-0.08, 0.2, 0.12])
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        # Caja
        rect = plt.Rectangle((0, 0), 1, 1, facecolor="#E3F2FD", edgecolor="#1565C0", linewidth=2)
        ax.add_patch(rect)
        
        ax.text(0.5, 0.7, titulo, ha="center", va="center", fontsize=10, fontweight="bold")
        ax.text(0.5, 0.4, valor, ha="center", va="center", fontsize=16, fontweight="bold", color="#1565C0")
        ax.text(0.5, 0.15, subtitulo, ha="center", va="center", fontsize=9, style="italic")
    
    # Alertas prioritarias
    ax_alertas = fig.add_axes([0.1, 0.45, 0.35, 0.22])
    ax_alertas.axis("off")
    ax_alertas.set_xlim(0, 1)
    ax_alertas.set_ylim(0, 1)
    
    alertas_text = "🚨 ALERTAS PRIORITARIAS\n\n" + "\n\n".join(datos["alertas_prioritarias"])
    ax_alertas.text(0.05, 0.95, alertas_text, transform=ax_alertas.transAxes,
                   fontsize=11, verticalalignment='top', fontfamily='monospace',
                   bbox=dict(boxstyle='round', facecolor='#FFEBEE', alpha=0.9, pad=1))
    
    # Recomendaciones de acción
    ax_rec = fig.add_axes([0.55, 0.45, 0.35, 0.22])
    ax_rec.axis("off")
    ax_rec.set_xlim(0, 1)
    ax_rec.set_ylim(0, 1)
    
    rec_text = "✅ ACCIONES RECOMENDADAS\n\n" + "\n".join([f"• {r}" for r in datos["recomendaciones_accion"]])
    ax_rec.text(0.05, 0.95, rec_text, transform=ax_rec.transAxes,
               fontsize=11, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='#E8F5E9', alpha=0.9, pad=1))
    
    # Detalle por combustible
    ax_det = fig.add_axes([0.1, 0.08, 0.8, 0.30])
    ax_det.axis("off")
    
    diesel = plan_compras_mensual("DIESEL")
    gasolina = plan_compras_mensual("GASOLINA")
    
    detalle_text = (f"📊 DETALLE DE COMPRAS MENSUALES\n\n"
                   f"DIESEL:\n"
                   f"  • Recomendación: {diesel.get('recomendacion_compra', 0):,.0f} L "
                   f"(Promedio: {diesel.get('promedio_historico', 0):,.0f}L, "
                   f"Máx: {diesel.get('maximo_historico', 0):,.0f}L)\n"
                   f"  • Costo estimado: Bs {diesel.get('costo_estimado_bs', 0):,.0f} "
                   f"@ Bs {diesel.get('precio_actual', 0)}/L\n\n"
                   f"GASOLINA:\n"
                   f"  • Recomendación: {gasolina.get('recomendacion_compra', 0):,.0f} L "
                   f"(Promedio: {gasolina.get('promedio_historico', 0):,.0f}L, "
                   f"Máx: {gasolina.get('maximo_historico', 0):,.0f}L)\n"
                   f"  • Costo estimado: Bs {gasolina.get('costo_estimado_bs', 0):,.0f} "
                   f"@ Bs {gasolina.get('precio_actual', 0)}/L")
    
    ax_det.text(0.05, 0.95, detalle_text, transform=ax_det.transAxes,
               fontsize=11, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9, pad=1))
    
    guardar("G8_resumen_ejecutivo.png")

## ══════════════════════════════════════════════════════════════════════
#  G9. TABLA GRÁFICA DE CONSUMO PROYECTADO (nuevo - solicitado)
# ══════════════════════════════════════════════════════════════════════

def grafico_tabla_consumo_proyectado():
    print("[G9] Tabla de consumo proyectado...")
    
    from logica_negocio_predictiva import tabla_consumo_proyectado_detallado, exportar_tabla_excel_format
    
    datos = tabla_consumo_proyectado_detallado(12)
    
    # Imprimir en consola para copiar a Excel
    print("\n" + "=" * 80)
    print("TABLA DE CONSUMO PROYECTADO (para copiar a Excel)")
    print("=" * 80)
    print(exportar_tabla_excel_format(datos))
    print("=" * 80 + "\n")
    
    fig, (ax_tabla, ax_grafico) = plt.subplots(2, 1, figsize=(16, 12), 
                                               gridspec_kw={"height_ratios": [1.5, 1]})
    
    # Parte 1: Tabla visual
    ax_tabla.axis("tight")
    ax_tabla.axis("off")
    
    # Preparar datos de tabla
    df = pd.DataFrame(datos["tabla_mensual_detallada"])
    meses = df['mes'].unique()
    
    # Crear filas para la tabla
    filas_tabla = []
    for mes in meses:
        row_diesel = df[(df['mes'] == mes) & (df['tipo_combustible'] == 'DIESEL')]
        row_gas = df[(df['mes'] == mes) & (df['tipo_combustible'] == 'GASOLINA')]
        
        # CORRECCIÓN DEFINITIVA: Usar .empty sin paréntesis (es una propiedad, no método)
        diesel_vacio = row_diesel.empty
        gas_vacio = row_gas.empty
        
        if not diesel_vacio and not gas_vacio:
            l_diesel = float(row_diesel['litros_base'].values[0])
            c_diesel = float(row_diesel['costo_base_bs'].values[0])
            l_gas = float(row_gas['litros_base'].values[0])
            c_gas = float(row_gas['costo_base_bs'].values[0])
            total_l = l_diesel + l_gas
            total_c = c_diesel + c_gas
            
            filas_tabla.append([
                mes,
                f"{l_diesel:,.0f}",
                f"Bs {c_diesel:,.0f}",
                f"{l_gas:,.0f}",
                f"Bs {c_gas:,.0f}",
                f"{total_l:,.0f}",
                f"Bs {total_c:,.0f}"
            ])
    
    # Agregar totales
    tot = datos["totales_generales"]
    tot_diesel = datos["totales_por_tipo"]["DIESEL"]
    tot_gas = datos["totales_por_tipo"]["GASOLINA"]
    
    filas_tabla.append([
        "TOTAL AÑO",
        f"{tot_diesel['litros_base']:,.0f}",
        f"Bs {tot_diesel['costo_base_bs']:,.0f}",
        f"{tot_gas['litros_base']:,.0f}",
        f"Bs {tot_gas['costo_base_bs']:,.0f}",
        f"{tot['litros_base']:,.0f}",
        f"Bs {tot['costo_base_bs']:,.0f}"
    ])
    
    # Crear tabla
    tabla = ax_tabla.table(
        cellText=filas_tabla,
        colLabels=["Mes", "Diesel (L)", "Diesel (Bs)", "Gasolina (L)", "Gasolina (Bs)", "Total (L)", "Total (Bs)"],
        cellLoc="center",
        loc="center",
        colWidths=[0.12, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14]
    )
    
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    tabla.scale(1.2, 2)
    
    # Colorear encabezado
    for j in range(7):
        tabla[0, j].set_facecolor("#1565C0")
        tabla[0, j].set_text_props(color="white", fontweight="bold")
    
    # Colorear fila de totales
    for j in range(7):
        tabla[len(filas_tabla), j].set_facecolor("#FFF9C4")
        tabla[len(filas_tabla), j].set_text_props(fontweight="bold")
    
    # Alternar colores de filas
    for i in range(1, len(filas_tabla)):
        for j in range(7):
            if i % 2 == 0:
                tabla[i, j].set_facecolor("#F5F5F5")
    
    # Título de tabla
    ax_tabla.set_title(f"TABLA DE CONSUMO PROYECTADO - {datos['periodo_proyeccion']}\n"
                      f"Escenario BASE (recomendado para planificación)",
                      fontsize=14, fontweight="bold", pad=20)
    
    # Parte 2: Gráfico de barras acumulado
    meses_graf = [f[:7] for f in meses]  # Acortar nombres
    
    # Extraer valores numéricos de las filas (excluyendo totales)
    diesel_vals = []
    gasolina_vals = []
    for fila in filas_tabla[:-1]:  # Excluir fila de totales
        diesel_vals.append(float(fila[1].replace(",", "")))
        gasolina_vals.append(float(fila[3].replace(",", "")))
    
    x = np.arange(len(meses_graf))
    width = 0.35
    
    b1 = ax_grafico.bar(x - width/2, diesel_vals, width, label="Diesel", color=COLOR_DIESEL, alpha=0.8)
    b2 = ax_grafico.bar(x + width/2, gasolina_vals, width, label="Gasolina", color=COLOR_GASOLINA, alpha=0.8)
    
    # Línea de promedio
    promedio_mensual = datos["promedio_mensual"]["litros_base"]
    ax_grafico.axhline(promedio_mensual, color="red", linestyle="--", linewidth=2, 
                      label=f"Promedio mensual total: {promedio_mensual:,.0f} L")
    
    ax_grafico.set_xlabel("Mes", fontsize=12)
    ax_grafico.set_ylabel("Litros", fontsize=12)
    ax_grafico.set_title("EVOLUCIÓN MENSUAL DEL CONSUMO PROYECTADO\nComparación Diesel vs Gasolina",
                        fontsize=13, fontweight="bold")
    ax_grafico.set_xticks(x)
    ax_grafico.set_xticklabels(meses_graf, rotation=45, ha="right")
    ax_grafico.legend(fontsize=10)
    ax_grafico.grid(axis="y", alpha=0.3, linestyle=":")
    ax_grafico.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    
    # Anotaciones de totales
    for i, (d, g) in enumerate(zip(diesel_vals, gasolina_vals)):
        total = d + g
        if i % 2 == 0:  # Cada 2 meses para no saturar
            ax_grafico.annotate(f"{total:,.0f}L", xy=(i, total), xytext=(0, 10),
                              textcoords="offset points", ha="center", fontsize=8, alpha=0.7)
    
    # Texto de escenarios
    esc_text = (f"ESCENARIOS ANUALES:\n"
               f"  🟢 Optimista:  {datos['totales_generales']['litros_optimista']:>10,.0f} L  "
               f"(Bs {datos['totales_generales']['costo_optimista_bs']:,.0f})\n"
               f"  🔵 Base:       {datos['totales_generales']['litros_base']:>10,.0f} L  "
               f"(Bs {datos['totales_generales']['costo_base_bs']:,.0f}) ← RECOMENDADO\n"
               f"  🔴 Pesimista:  {datos['totales_generales']['litros_pesimista']:>10,.0f} L  "
               f"(Bs {datos['totales_generales']['costo_pesimista_bs']:,.0f})")
    
    fig.text(0.5, 0.02, esc_text, ha="center", fontsize=11,
            fontweight="bold", fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.8", facecolor="lightyellow", 
                     edgecolor="black", linewidth=2))
    
    plt.suptitle("CONSUMO PROYECTADO DE COMBUSTIBLE - PRÓXIMOS 12 MESES\n"
                "Tabla detallada para planificación de compras y presupuesto",
                fontsize=16, fontweight="bold", y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.12)
    guardar("G9_tabla_consumo_proyectado.png")
    
    # También guardar como CSV para Excel
    csv_path = SALIDA / "tabla_consumo_proyectado.csv"
    df_export = pd.DataFrame(datos["tabla_mensual_detallada"])
    df_export.to_csv(csv_path, index=False)
    print(f"  📊 CSV exportado: {csv_path}")
    
    # Guardar resumen de texto
    txt_path = SALIDA / "tabla_consumo_proyectado.txt"
    with open(txt_path, 'w') as f:
        f.write(exportar_tabla_excel_format(datos))
    print(f"  📄 Texto exportado: {txt_path}")


# ══════════════════════════════════════════════════════════════════════
#  EJECUCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  GENERANDO GRÁFICOS PREDICTIVOS V2")
    print("  Sistema de Combustible - Municipio de Caranavi")
    print("  Versión simplificada y accionable")
    print("=" * 70)
    
    grafico_plan_compras()                    # G1
    grafico_presupuesto_anual()               # G2
    grafico_distribucion_stock(5000)          # G3
    grafico_vehiculos_costo_reemplazo()       # G4
    grafico_simulador_ahorro()                # G5
    grafico_calendario_precios()              # G6
    grafico_estimacion_costos_futuros()       # G7
    grafico_resumen_ejecutivo()               # G8
    grafico_tabla_consumo_proyectado()
    
    print("\n" + "=" * 70)
    print("  ✅ 9 gráficos generados en /graficos_v2/")
    print("  📊 Archivos CSV y TXT exportados para Excel")
    print("=" * 70)