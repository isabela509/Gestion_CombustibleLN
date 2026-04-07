"""
GENERACIÓN DE GRÁFICOS - REPORTES TD
Sistema de Control de Combustible - Municipio de Caranavi

Genera y guarda todos los gráficos en la carpeta /graficos/
Ejecuta: python graficos.py
"""

import matplotlib
matplotlib.use("Agg")  # Sin interfaz gráfica, solo guarda archivos
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats  # Para regresión estadística avanzada

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
    eficiencia_vehiculos,
)


#  Configuración visual general
COLORES_GASOLINA = "#007C1F"
COLORES_DIESEL   = "#0B388B"
PALETA           = ["#1565C0","#1976D2","#42A5F5","#90CAF9","#BBDEFB",
                    "#E65100","#F57C00","#FFA726","#FFCC02","#FFE082"]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.family":       "DejaVu Sans",
    "axes.titlesize":    14,
    "axes.titleweight":  "bold",
    "axes.labelsize":    11,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
})

SALIDA = Path("graficos")
SALIDA.mkdir(exist_ok=True)


def guardar(nombre: str):
    path = SALIDA / nombre
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Guardado: {path}")


#  GRÁFICO 1 — Consumo de litros por área

def grafico_consumo_por_area():
    print("\n[1] Consumo por área...")
    df = consumo_por_area()
    if df.empty:
        print("    Sin datos."); return

    # Pivotear para tener gasolina y diesel como columnas
    pivot = df.pivot_table(
        index="area", columns="tipo_combustible",
        values="litros_consumidos", aggfunc="sum"
    ).fillna(0)
    pivot["TOTAL"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("TOTAL", ascending=True).tail(15)

    fig, ax = plt.subplots(figsize=(14, 8))
    y_pos = np.arange(len(pivot))
    bar_h = 0.35

    cols = [c for c in pivot.columns if c != "TOTAL"]
    color_map = {"GASOLINA": COLORES_GASOLINA, "DIESEL": COLORES_DIESEL}

    for i, col in enumerate(cols):
        offset = (i - len(cols)/2 + 0.5) * bar_h
        vals = pivot[col].values
        bars = ax.barh(y_pos + offset, vals, bar_h * 0.9,
                       label=col, color=color_map.get(col, PALETA[i]))
        for bar in bars:
            if bar.get_width() > 0:
                ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                        f"{bar.get_width():,.0f}L", va="center", fontsize=8)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([a[:35] for a in pivot.index], fontsize=9)
    ax.set_xlabel("Litros consumidos")
    ax.set_title("Consumo de Combustible por Área / Programa Municipal")
    ax.legend(title="Tipo")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    guardar("01_consumo_por_area.png")



#  GRÁFICO 2 — Top 10 vehículos con mayor consumo
def grafico_top_vehiculos():
    print("[2] Top 10 vehículos...")
    df = top10_vehiculos()
    if df.empty:
        print("    Sin datos."); return

    # Reemplazar NULL en placas
    df["placa"] = df["placa"].fillna("SIN-PLACA")
    df["placa"] = df["placa"].replace("nan", "SIN-PLACA")
    
    # Etiqueta corta: Placa + nombre corto
    df["etiqueta"] = df.apply(
        lambda r: f"{r['placa']}\n({r['vehiculo'][:12]}...)" 
        if len(r['vehiculo']) > 12 
        else f"{r['placa']}\n({r['vehiculo']})", 
        axis=1
    )

    fig, ax = plt.subplots(figsize=(14, 6))  # ← Más ancho (era 12)
    
    # Colores según tipo
    colores = ["#0D47A1" if "DIESEL" in str(t).upper() else "#2E7D32" 
               for t in df["tipo_combustible"]]
    
    bars = ax.bar(range(len(df)), df["litros_consumidos"], color=colores)
    
    # Rotar etiquetas 45 grados
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df["etiqueta"], rotation=45, ha="right", fontsize=8)  # ← CAMBIO CLAVE
    
    ax.set_ylabel("Litros consumidos")
    ax.set_title("Top 10 Vehículos con Mayor Consumo de Combustible")
    
    # Agregar línea de promedio
    promedio = df["litros_consumidos"].mean()
    ax.axhline(promedio, color="red", linestyle="--", alpha=0.5, 
               label=f"Promedio: {promedio:,.0f}L")

    for bar, val in zip(bars, df["litros_consumidos"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                f"{val:,.0f}L", ha="center", fontsize=8)

    # Leyenda manual
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(color="#0D47A1", label="Diesel"),
        Patch(color="#2E7D32", label="Gasolina"),
        plt.Line2D([0],[0], color="red", linestyle="--", label=f"Promedio: {promedio:,.0f}L")
    ])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    guardar("02_top10_vehiculos.png")


#  GRÁFICO 3 — Evolución mensual de consumo (línea)
def grafico_consumo_mensual():
    print("[3] Consumo mensual...")
    df = consumo_mensual()
    if df.empty:
        print("    Sin datos."); return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), sharex=True)

    for tipo, color, ax in [
        ("GASOLINA", COLORES_GASOLINA, ax1),
        ("DIESEL",   COLORES_DIESEL,   ax2),
    ]:
        sub = df[df["tipo_combustible"] == tipo].copy()
        if sub.empty:
            ax.set_title(f"Sin datos de {tipo}"); continue
        ax.fill_between(sub["mes"], sub["litros_consumidos"],
                        alpha=0.2, color=color)
        ax.plot(sub["mes"], sub["litros_consumidos"],
                marker="o", color=color, linewidth=2, label=tipo)
        ax.set_ylabel("Litros")
        ax.set_title(f"Consumo Mensual — {tipo}")
        ax.tick_params(axis="x", rotation=45)
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
        ax.legend()

    plt.suptitle("Evolución Mensual del Consumo de Combustible",
                 fontsize=14, fontweight="bold", y=1.01)
    guardar("03_consumo_mensual.png")



#  GRÁFICO 4 — Consumo por conductor (barras)
def grafico_conductores():
    print("[4] Consumo por conductor...")
    df = consumo_por_conductor()
    if df.empty:
        print("    Sin datos."); return

    # Top 15 conductores
    top = df.groupby("conductor")["litros_consumidos"].sum()\
            .sort_values(ascending=False).head(15)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(range(len(top)), top.values, color=PALETA[0], alpha=0.8, edgecolor="black", linewidth=0.8)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels([n[:35] for n in top.index], fontsize=9)
    ax.set_xlabel("Litros consumidos", fontsize=11, fontweight="bold")
    ax.set_title("Top 15 Conductores por Consumo de Combustible", fontsize=12, fontweight="bold")

    for bar, val in zip(bars, top.values):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                f"{val:,.0f}L", va="center", fontsize=8, fontweight="bold")

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    ax.grid(axis="x", alpha=0.3, linestyle=":")
    guardar("04_consumo_conductores.png")



#  GRÁFICO 5 — Stock actual por área (barras)
def grafico_stock_actual():
    print("[5] Stock actual...")
    df = stock_actual()
    if df.empty:
        print("    Sin datos."); return

    # Pivotar para tener Gasolina y Diesel como columnas
    pivot = df.pivot_table(
        index="area", columns="tipo_combustible",
        values="stock_disponible_lts", aggfunc="sum"
    ).fillna(0)
    
    # Ordenar por total y tomar top 15
    pivot["TOTAL"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("TOTAL", ascending=True).tail(15)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    y_pos = np.arange(len(pivot))
    bar_h = 0.35
    
    # Identificar columnas de combustible
    cols = [c for c in pivot.columns if c != "TOTAL"]
    color_map = {}
    for col in cols:
        if "GASOLINA" in col.upper():
            color_map[col] = COLORES_GASOLINA
        elif "DIESEL" in col.upper():
            color_map[col] = COLORES_DIESEL
        else:
            color_map[col] = PALETA[0]
    
    # Graficar barras apiladas
    for i, col in enumerate(cols):
        offset = (i - len(cols)/2 + 0.5) * bar_h
        vals = pivot[col].values
        bars = ax.barh(y_pos + offset, vals, bar_h * 0.9,
                       label=col, color=color_map.get(col, PALETA[i]))
        for bar in bars:
            if bar.get_width() > 0:
                ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
                        f"{bar.get_width():,.0f}L", va="center", fontsize=8)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([a[:40] for a in pivot.index], fontsize=9)
    ax.set_xlabel("Litros disponibles")
    ax.set_title("Stock Actual de Combustible por Área")
    ax.legend(title="Tipo", loc="lower right")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    guardar("05_stock_actual.png")


#  GRÁFICO 6 — Costos mensuales acumulados
def grafico_costos_mensuales():
    print("[6] Costos mensuales...")
    df = consumo_mensual()
    if df.empty:
        print("    Sin datos."); return

    pivot = df.pivot_table(
        index="mes", columns="tipo_combustible",
        values="costo_total_bs", aggfunc="sum"
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(14, 6))
    bottom = np.zeros(len(pivot))
    colores = {"GASOLINA": COLORES_GASOLINA, "DIESEL": COLORES_DIESEL}

    for col in pivot.columns:
        ax.bar(pivot.index, pivot[col], bottom=bottom,
               label=col, color=colores.get(col, PALETA[2]))
        bottom += pivot[col].values

    ax.set_xlabel("Mes")
    ax.set_ylabel("Costo (Bs.)")
    ax.set_title("Costo Total de Combustible por Mes (Bs.)")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(title="Tipo de combustible")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x,_: f"Bs. {x:,.0f}"))
    guardar("06_costos_mensuales.png")


#  GRÁFICO 7 — Predicción de tendencia (CON BANDAS DE CONFIANZA)
def grafico_tendencia_predictiva():
    print("[7] Predicción de tendencia...")

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    for ax, tipo, color in [
        (axes[0], "GASOLINA", COLORES_GASOLINA),
        (axes[1], "DIESEL",   COLORES_DIESEL),
    ]:
        df = tendencia_predictiva(tipo)
        if df.empty or len(df) < 3:
            ax.text(0.5, 0.5, f"Datos insuficientes\npara {tipo}",
                    ha="center", va="center", transform=ax.transAxes)
            ax.set_title(f"Tendencia {tipo}"); continue

        x = np.arange(len(df))
        y = df["litros"].values

        # Regresión lineal CON estadísticas (scipy)
        if len(df) >= 6:
            # Regresión robusta
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            r_squared = r_value ** 2
            
            # Predicción para próximos 3 meses
            x_future = np.arange(len(df) + 3)
            y_pred = slope * x_future + intercept
            
            # Bandas de confianza al 95%
            confidence = 1.96 * std_err * np.sqrt(1 + 1/len(df) + 
                                                  (x_future - x.mean())**2 / np.sum((x - x.mean())**2))
            upper = y_pred + confidence
            lower = y_pred - confidence
            
            # Graficar datos reales
            ax.plot(x, y, "o", color=color, markersize=8, 
                   label="Consumo real", zorder=3)
            
            # Tendencia + bandas de confianza
            ax.plot(x_future, y_pred, "--", color="black", linewidth=2.5,
                   label=f"Tendencia (R²={r_squared:.3f})", zorder=2)
            ax.fill_between(x_future, lower, upper, alpha=0.15, color=color, 
                           label="Intervalo de confianza 95%", zorder=1)
            
            # Anotaciones para predicciones
            meses_pred = pd.date_range(
                start=pd.to_datetime(df["mes"].iloc[-1] + "-01") + pd.DateOffset(months=1),
                periods=3, freq="MS"
            ).strftime("%Y-%m").tolist()
            
            for i, (xi, yi) in enumerate(zip(x_future[-3:], y_pred[-3:])):
                ax.annotate(
                    f"{meses_pred[i]}\n{yi:,.0f}L",
                    xy=(xi, yi), xytext=(xi, yi + max(y)*0.08),
                    fontsize=8, ha="center", fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color="black", lw=1),
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.2)
                )
            
            # Estadísticas en el gráfico
            stats_text = f"Pendiente: {slope:.1f}L/mes\nP-value: {p_value:.4f}"
            ax.text(0.02, 0.95, stats_text, transform=ax.transAxes, 
                   fontsize=9, verticalalignment="top", fontweight="bold",
                   bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="gray", linewidth=1.5))
        
        else:
            # Si hay pocos datos, usar regresión simple
            coef = np.polyfit(x, y, 1)
            poly = np.poly1d(coef)
            x_future = np.arange(len(df), len(df) + 3)
            
            ax.plot(x, y, "o-", color=color, linewidth=2, markersize=8, label="Consumo real")
            ax.plot(list(range(len(df))) + list(x_future),
                    list(poly(range(len(df)))) + list(poly(x_future)),
                    "--", color="gray", linewidth=1.5, label="Tendencia")
            ax.text(0.02, 0.95, "⚠️ Pocos datos\n(regresión simple)", 
                   transform=ax.transAxes, fontsize=9, verticalalignment="top", fontweight="bold",
                   bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.4, edgecolor="orange"))

        # Mostrar solo cada 3 meses en las etiquetas para evitar sobreposición
        all_months = list(df["mes"]) + (meses_pred if len(df) >= 6 else 
                     pd.date_range(
                         start=pd.to_datetime(df["mes"].iloc[-1] + "-01") + pd.DateOffset(months=1),
                         periods=3, freq="MS"
                     ).strftime("%Y-%m").tolist())
        
        # Mostrar cada 3 meses (decimonónico)
        step = max(1, len(all_months) // 8)  # Máximo 8 etiquetas
        tick_positions = list(range(0, len(all_months), step))
        if len(all_months) - 1 not in tick_positions:
            tick_positions.append(len(all_months) - 1)
        
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([all_months[i] for i in tick_positions], rotation=45, fontsize=10, fontweight="bold")
        ax.set_ylabel("Litros", fontsize=12, fontweight="bold")
        ax.set_title(f"Análisis de Tendencia — {tipo}", fontsize=13, fontweight="bold")
        ax.legend(loc="best", fontsize=10)
        ax.grid(True, alpha=0.3, linestyle=":")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))

    plt.suptitle("Proyección de Consumo de Combustible con Intervalo de Confianza",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    guardar("07_prediccion_tendencia.png")


#  GRÁFICO 8 — Alertas de exceso de consumo (MEJORADO)
def grafico_excesos():
    print("[8] Alertas de exceso...")
    df = detectar_excesos()
    if df.empty:
        print("    Sin boletas con consumo excesivo."); return

    # Calcular promedio para clasificar severidad
    promedio_general = df["litros"].mean()
    
    # Función para asignar color según severidad
    def get_color_severidad(litros):
        if litros > promedio_general * 3:
            return "#d32f2f"  # Rojo crítico: > 3x promedio
        elif litros > promedio_general * 2.5:
            return "#f57c00"  # Naranja oscuro: 2.5-3x
        else:
            return "#fbc02d"  # Amarillo: 2-2.5x

    colores = [get_color_severidad(l) for l in df["litros"]]
    
    fig, ax = plt.subplots(figsize=(14, 7))
    bars = ax.bar(range(len(df)), df["litros"], color=colores, 
                  edgecolor="black", linewidth=1.2, alpha=0.9)
    
    # Etiquetas con identificación y alerta
    etiquetas = []
    for _, r in df.iterrows():
        if r["litros"] > promedio_general * 3:
            etiqueta = f"⚠️ #{r['nro_solicitud']}\n{r['area'][:18]}"
        else:
            etiqueta = f"#{r['nro_solicitud']}\n{r['area'][:18]}"
        etiquetas.append(etiqueta)
    
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(etiquetas, fontsize=7, fontweight="bold")
    ax.set_ylabel("Litros consumidos", fontsize=11, fontweight="bold")
    ax.set_title("ALERTA: CONSUMO EXCESIVO",
                 fontsize=14, fontweight="bold", color="#d32f2f", pad=20)
    
    # Líneas de referencia de severidad
    ax.axhline(promedio_general, color="gray", linestyle="--", 
               linewidth=1.5, alpha=0.5, label=f"Promedio: {promedio_general:,.0f}L")
    ax.axhline(promedio_general * 2, color="orange", linestyle="--", 
               linewidth=1.5, alpha=0.6, label=f"Alerta (2x): {promedio_general*2:,.0f}L")
    ax.axhline(promedio_general * 3, color="red", linestyle="--", 
               linewidth=2, alpha=0.7, label=f"Crítico (3x): {promedio_general*3:,.0f}L")
    
    # Valores en las barras
    for i, (bar, val) in enumerate(zip(bars, df["litros"])):
        altura = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, altura + 5,
                f"{val:,.0f}L\n({val/promedio_general:.1f}x)",
                ha="center", va="bottom", fontsize=7, fontweight="bold")
    
    # Leyenda mejorada
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(color="#d32f2f", label="CRÍTICO (> 3x promedio)", alpha=0.9),
        Patch(color="#f57c00", label="ALERTA (2.5-3x promedio)", alpha=0.9),
        Patch(color="#fbc02d", label="PRECAUCIÓN (> 2x promedio)", alpha=0.9),
        plt.Line2D([0],[0], color="gray", linestyle="--", linewidth=1.5, label="Promedio general"),
    ], loc="upper left", fontsize=9, title="Niveles de Severidad", title_fontsize=10)
    
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    ax.grid(axis="y", alpha=0.3, linestyle=":")
    guardar("08_alertas_exceso.png")


#  GRÁFICO 9 — Comparativo gasolina vs diesel (por mes)
def grafico_comparativo_combustibles():
    print("[9] Comparativo gasolina vs diesel...")
    df = consumo_mensual()
    if df.empty:
        print("    Sin datos."); return

    pivot = df.pivot_table(
        index="mes", columns="tipo_combustible",
        values="litros_consumidos", aggfunc="sum"
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(pivot))
    w = 0.35

    for i, (col, color) in enumerate(
        [("GASOLINA", COLORES_GASOLINA), ("DIESEL", COLORES_DIESEL)]
    ):
        if col in pivot.columns:
            ax.bar(x + (i-0.5)*w, pivot[col], w, label=col, color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index, rotation=45, fontsize=8)
    ax.set_ylabel("Litros")
    ax.set_title("Comparativo Mensual: Gasolina vs Diésel")
    ax.legend()
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    guardar("09_comparativo_combustibles.png")



#  GRÁFICO 10 — Eficiencia de vehículos (km/litro)
def grafico_eficiencia_vehiculos():
    print("[10] Eficiencia de vehículos...")
    df = eficiencia_vehiculos()
    if df.empty:
        print("    Sin datos de kilometraje."); return

    # Top 15 vehículos con peor rendimiento (menos km/litro)
    df = df.sort_values("km_por_litro").head(15)

    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Código de colores: Rojo (< 5 km/L) = muy ineficiente,
    #                     Naranja (5-8) = moderado,
    #                     Verde (> 8) = eficiente
    colores = ["#d32f2f" if km < 5 
               else "#ff9800" if km < 8 
               else "#4caf50"
               for km in df["km_por_litro"]]
    
    bars = ax.barh(range(len(df)), df["km_por_litro"], color=colores, alpha=0.8)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(
        [f"{r['placa']}\n{r['vehiculo'][:20]}" 
         for _, r in df.iterrows()],
        fontsize=8
    )
    ax.set_xlabel("Kilómetros por Litro (km/L)")
    ax.set_title("Eficiencia de Vehículos - Rendimiento de Combustible")
    
    # Línea de meta (8 km/litro es eficiencia aceptable)
    ax.axvline(8, color="green", linestyle="--", linewidth=2, 
               alpha=0.6, label="Meta: 8 km/L")
    
    # Etiquetas de valores
    for bar, val in zip(bars, df["km_por_litro"]):
        ax.text(val + 0.15, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}", va="center", fontsize=8, fontweight="bold")
    
    # Leyenda con interpretación de colores
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(color="#d32f2f", label="Muy ineficiente (< 5 km/L)", alpha=0.8),
        Patch(color="#ff9800", label="Moderado (5-8 km/L)", alpha=0.8),
        Patch(color="#4caf50", label="Eficiente (> 8 km/L)", alpha=0.8),
        plt.Line2D([0],[0], color="green", linestyle="--", linewidth=2, label="Meta"),
    ])
    guardar("10_eficiencia_vehiculos.png")


#  GRÁFICO 11 — Resumen ejecutivo (KPI cards visual)
def grafico_resumen_ejecutivo():
    print("[11] Resumen ejecutivo...")
    datos = resumen_ejecutivo()
    if not datos:
        print("    Sin datos."); return

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis("off")

    headers = ["Tipo", "Total Litros", "Costo Total (Bs.)",
               "Vehículos Activos", "Áreas Activas", "Solicitudes"]
    rows = [
        [
            d.get("tipo",""),
            f"{d.get('total_litros',0):,.0f}",
            f"Bs. {d.get('total_bs',0):,.0f}",
            str(d.get("vehiculos_activos",0)),
            str(d.get("areas_activas",0)),
            str(d.get("total_solicitudes",0)),
        ]
        for d in datos
    ]

    tabla = ax.table(
        cellText=rows, colLabels=headers,
        cellLoc="center", loc="center"
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(11)
    tabla.scale(1.3, 2.5)

    # Colorear encabezados
    for j in range(len(headers)):
        tabla[0, j].set_facecolor("#1565C0")
        tabla[0, j].set_text_props(color="white", fontweight="bold")

    # Colorear filas por tipo
    color_fila = {"GASOLINA": "#E3F2FD", "DIESEL": "#FFF3E0"}
    for i, d in enumerate(datos):
        for j in range(len(headers)):
            tabla[i+1, j].set_facecolor(
                color_fila.get(d.get("tipo",""), "white"))

    ax.set_title("Resumen Ejecutivo — Sistema de Control de Combustible",
                 fontsize=14, fontweight="bold", pad=20)
    guardar("11_resumen_ejecutivo.png")


#  EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    print("=" * 55)
    print("  GENERANDO GRÁFICOS DE REPORTES TD")
    print("  Sistema de Combustible — Municipio de Caranavi")
    print("=" * 55)

    grafico_consumo_por_area()
    grafico_top_vehiculos()
    grafico_consumo_mensual()
    grafico_conductores()
    grafico_stock_actual()
    grafico_costos_mensuales()
    grafico_tendencia_predictiva()
    grafico_excesos()
    grafico_comparativo_combustibles()
    grafico_eficiencia_vehiculos()
    grafico_resumen_ejecutivo()

    print("\n" + "=" * 55)
    print(f"  ✅ Listo. {11} gráficos guardados en /graficos/")
    print("=" * 55)
