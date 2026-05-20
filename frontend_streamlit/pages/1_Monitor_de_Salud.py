"""
Monitor de Salud del Sistema de Recomendaciones
Compara la distribución de categorías entre los datos de entrenamiento
y los eventos recientes registrados en producción.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Configuración de la página ────────────────────────────────────────────────
st.set_page_config(
    page_title="Monitor de Salud — Click & Tech",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Monitor de Salud del Sistema")
st.caption("Comparamos cómo se comportaban los usuarios cuando entrenamos el modelo versus cómo se comportan hoy.")

st.divider()

# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_datos():
    df = pd.read_csv(
        "data/final/events_final.csv",
        usecols=["event_time", "event_type", "category_code", "nivel1", "nivel2_norm", "nivel3_norm"],
    )
    df["event_time"] = pd.to_datetime(df["event_time"], format="mixed", utc=True)
    # Rellenar nivel1/nivel2_norm para eventos nuevos que no los tienen
    partes = df["category_code"].fillna("").str.split(".", expand=True).reindex(columns=[0, 1, 2])
    df["nivel1"]      = df["nivel1"].fillna(partes[0].str.lower().replace("", "other"))
    df["nivel2_norm"] = df["nivel2_norm"].fillna(partes[1].str.lower().replace("", "other"))
    df["nivel3_norm"] = df["nivel3_norm"].fillna(partes[2].str.lower().replace("", "other"))
    return df

with st.spinner("Cargando datos históricos..."):
    df = cargar_datos()

# ── Separar períodos ──────────────────────────────────────────────────────────
# Entrenamiento: Sep 2020 – Feb 2021 (datos originales del modelo)
# Producción:    eventos recientes (todo lo posterior a Feb 2021)
CORTE = pd.Timestamp("2021-03-01", tz="UTC")

df_ref = df[df["event_time"] < CORTE].copy()
df_act = df[df["event_time"] >= CORTE].copy()

# ── Encabezado con métricas clave ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Eventos de entrenamiento", f"{len(df_ref):,}")
col2.metric("Eventos recientes (producción)", f"{len(df_act):,}")
col3.metric("Categorías en entrenamiento", df_ref["nivel1"].nunique())
col4.metric("Categorías en producción", df_act["nivel1"].nunique())

st.divider()

# ── Explicación simple ────────────────────────────────────────────────────────
with st.expander("ℹ️ ¿Qué estamos midiendo y por qué importa?"):
    st.markdown("""
    **¿Qué es el desvío de datos (data drift)?**

    Cuando entrenamos el sistema de recomendaciones, lo "enseñamos" con un conjunto
    de comportamientos de usuarios: qué categorías miraban, qué agregaban al carrito,
    qué compraban.

    Con el tiempo, los gustos y hábitos de los usuarios pueden cambiar.
    Por ejemplo: antes se compraban muchos cartuchos de tinta, pero ahora el interés
    se volcó hacia auriculares y accesorios para gaming.

    Si eso pasa y no actualizamos el modelo, las recomendaciones se vuelven menos
    relevantes y los usuarios dejan de hacer clic en ellas.

    **¿Cómo lo detectamos?**

    Comparamos la distribución de categorías entre:
    - 📚 **Entrenamiento**: cómo eran los eventos cuando entrenamos el modelo
    - 🟢 **Producción**: cómo son los eventos que llegan hoy

    Si las distribuciones son muy distintas → hay desvío → hay que reentrenar el modelo.

    **Semáforo de alerta (índice PSI):**
    - 🟢 PSI < 0.10 → Sin cambio significativo
    - 🟡 PSI 0.10 – 0.25 → Cambio moderado, atención
    - 🔴 PSI > 0.25 → Cambio importante, considerar reentrenamiento
    """)

# ── Función para calcular PSI ─────────────────────────────────────────────────
def calcular_psi(ref: pd.Series, act: pd.Series, epsilon: float = 1e-6) -> float:
    """Calcula el Population Stability Index entre dos distribuciones."""
    cats = set(ref.index) | set(act.index)
    p_ref = ref.reindex(cats, fill_value=0).astype(float)
    p_act = act.reindex(cats, fill_value=0).astype(float)
    # Normalizar a proporciones
    p_ref = (p_ref + epsilon) / (p_ref.sum() + epsilon * len(cats))
    p_act = (p_act + epsilon) / (p_act.sum() + epsilon * len(cats))
    psi = float(np.sum((p_act - p_ref) * np.log(p_act / p_ref)))
    return psi


def semaforo(psi: float) -> str:
    if psi < 0.10:
        return "🟢 Sin cambio"
    elif psi < 0.25:
        return "🟡 Cambio moderado"
    else:
        return "🔴 Cambio importante"


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🗂️ Categorías", "🛒 Tipo de interacción", "📋 Tabla de alertas"])

# ─── Tab 1: Distribución de categorías ───────────────────────────────────────
with tab1:
    st.subheader("¿Qué categorías interesan a los usuarios?")
    st.caption("Comparamos el peso de cada categoría principal en el período de entrenamiento vs producción.")

    nivel = st.radio(
        "Nivel de detalle de categoría:",
        ["Nivel 1 — General (ej: computadoras, electrónica)",
         "Nivel 2 — Intermedio (ej: laptops, smartphones)"],
        horizontal=True,
    )
    col_cat = "nivel1" if "Nivel 1" in nivel else "nivel2_norm"

    top_n = st.slider("Mostrar las top N categorías", min_value=5, max_value=30, value=15)

    # Distribuciones normalizadas
    dist_ref = (df_ref[col_cat].value_counts(normalize=True).head(top_n) * 100).round(2)
    dist_act = (df_act[col_cat].value_counts(normalize=True).head(top_n) * 100).round(2) if len(df_act) > 0 else pd.Series(dtype=float)

    cats_mostrar = list(dict.fromkeys(dist_ref.index.tolist() + dist_act.index.tolist()))[:top_n]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="📚 Entrenamiento",
        x=cats_mostrar,
        y=[dist_ref.get(c, 0) for c in cats_mostrar],
        marker_color="#4A90D9",
        opacity=0.85,
    ))
    if len(df_act) > 0:
        fig.add_trace(go.Bar(
            name="🟢 Producción",
            x=cats_mostrar,
            y=[dist_act.get(c, 0) for c in cats_mostrar],
            marker_color="#E8734A",
            opacity=0.85,
        ))

    fig.update_layout(
        barmode="group",
        xaxis_title="Categoría",
        yaxis_title="Porcentaje del total de eventos (%)",
        legend_title="Período",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    psi_cat = calcular_psi(
        df_ref[col_cat].value_counts(normalize=True),
        df_act[col_cat].value_counts(normalize=True) if len(df_act) > 0 else pd.Series(dtype=float),
    )
    st.info(f"**Índice de desvío general (PSI) para esta categoría:** {psi_cat:.4f}  →  {semaforo(psi_cat)}")

# ─── Tab 2: Tipo de interacción ───────────────────────────────────────────────
with tab2:
    st.subheader("¿Cómo interactúan los usuarios?")
    st.caption("Un cambio en la proporción de 'vista → carrito → compra' puede indicar que el modelo está generando menos intención de compra.")

    dist_tipo_ref = (df_ref["event_type"].value_counts(normalize=True) * 100).round(2)
    dist_tipo_act = (df_act["event_type"].value_counts(normalize=True) * 100).round(2) if len(df_act) > 0 else pd.Series(dtype=float)

    tipos = ["view", "cart", "purchase"]
    nombres = {"view": "Vista", "cart": "Carrito", "purchase": "Compra"}

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name="📚 Entrenamiento",
        x=[nombres.get(t, t) for t in tipos],
        y=[dist_tipo_ref.get(t, 0) for t in tipos],
        marker_color="#4A90D9",
        opacity=0.85,
        text=[f"{dist_tipo_ref.get(t, 0):.1f}%" for t in tipos],
        textposition="auto",
    ))
    if len(df_act) > 0:
        fig2.add_trace(go.Bar(
            name="🟢 Producción",
            x=[nombres.get(t, t) for t in tipos],
            y=[dist_tipo_act.get(t, 0) for t in tipos],
            marker_color="#E8734A",
            opacity=0.85,
            text=[f"{dist_tipo_act.get(t, 0):.1f}%" for t in tipos],
            textposition="auto",
        ))

    fig2.update_layout(
        barmode="group",
        yaxis_title="Porcentaje (%)",
        legend_title="Período",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=380,
    )
    st.plotly_chart(fig2, use_container_width=True)

    psi_tipo = calcular_psi(
        df_ref["event_type"].value_counts(normalize=True),
        df_act["event_type"].value_counts(normalize=True) if len(df_act) > 0 else pd.Series(dtype=float),
    )
    st.info(f"**Índice de desvío en tipo de interacción (PSI):** {psi_tipo:.4f}  →  {semaforo(psi_tipo)}")

    if len(df_act) > 0:
        conv_ref = dist_tipo_ref.get("purchase", 0) / max(dist_tipo_ref.get("view", 1), 1)
        conv_act = dist_tipo_act.get("purchase", 0) / max(dist_tipo_act.get("view", 1), 1)
        delta = conv_act - conv_ref
        st.metric(
            label="Tasa de conversión (compras / vistas)",
            value=f"{conv_act:.2f}%",
            delta=f"{delta:+.2f}% vs entrenamiento",
        )

# ─── Tab 3: Tabla de alertas ──────────────────────────────────────────────────
with tab3:
    st.subheader("Resumen de alertas por categoría")
    st.caption("Para cada categoría principal, calculamos el PSI y mostramos si hay desvío.")

    if len(df_act) == 0:
        st.warning("No hay eventos de producción registrados aún. Usá la app para que aparezcan datos aquí.")
    else:
        cats_ref = df_ref["nivel1"].value_counts(normalize=True)
        cats_act = df_act["nivel1"].value_counts(normalize=True)
        todas = sorted(set(cats_ref.index) | set(cats_act.index))

        filas = []
        for cat in todas:
            p_ref = cats_ref.get(cat, 0) * 100
            p_act = cats_act.get(cat, 0) * 100
            psi_ind = calcular_psi(
                pd.Series({cat: cats_ref.get(cat, 0), "_resto": 1 - cats_ref.get(cat, 0)}),
                pd.Series({cat: cats_act.get(cat, 0), "_resto": 1 - cats_act.get(cat, 0)}),
            )
            filas.append({
                "Categoría": cat,
                "% en entrenamiento": round(p_ref, 2),
                "% en producción": round(p_act, 2),
                "Diferencia (pp)": round(p_act - p_ref, 2),
                "PSI": round(psi_ind, 4),
                "Estado": semaforo(psi_ind),
            })

        tabla = pd.DataFrame(filas).sort_values("PSI", ascending=False)

        # Colorear según estado
        def color_estado(val):
            if "🔴" in str(val):
                return "background-color: #5c1a1a; color: white"
            elif "🟡" in str(val):
                return "background-color: #4a3a00; color: white"
            else:
                return "background-color: #1a3a1a; color: white"

        st.dataframe(
            tabla.style.map(color_estado, subset=["Estado"]),
            use_container_width=True,
            height=500,
        )

        n_rojo    = (tabla["Estado"].str.contains("🔴")).sum()
        n_amarillo = (tabla["Estado"].str.contains("🟡")).sum()
        n_verde   = (tabla["Estado"].str.contains("🟢")).sum()

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("🔴 Alertas críticas", n_rojo)
        c2.metric("🟡 Alertas moderadas", n_amarillo)
        c3.metric("🟢 Sin cambio", n_verde)

        if n_rojo > 0:
            cats_criticas = tabla[tabla["Estado"].str.contains("🔴")]["Categoría"].tolist()
            st.error(f"⚠️ Se recomienda revisar el modelo para: **{', '.join(cats_criticas)}**")
        else:
            st.success("✅ El comportamiento de los usuarios es similar al período de entrenamiento. No se requiere acción inmediata.")

st.divider()
st.caption("Los datos de producción corresponden a los eventos registrados desde el 1 de marzo de 2021 en adelante. "
           "El umbral de reentrenamiento recomendado es PSI > 0.25 en dos o más categorías principales.")
