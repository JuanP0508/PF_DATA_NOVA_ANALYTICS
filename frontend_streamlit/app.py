import re
import streamlit as st
import pandas as pd
import requests
import base64
from pathlib import Path
from datetime import datetime


# ── Pool de imágenes por variante ─────────────────────────────────────────────
# Detecta automáticamente cable1.jpg, cable2.jpg, etc. y los agrupa.
# Así el frontend rota entre variantes sin tocar el CSV.
@st.cache_data
def _build_image_pools(img_folder: str) -> dict:
    """
    Para cada imagen base (cable.jpg) busca variantes numeradas (cable1.jpg, cable2.jpg…).
    Devuelve {base_filename: [variante1, variante2, …]} ordenado.
    Si no hay variantes, el pool solo contiene la base.
    """
    folder = Path(img_folder)
    if not folder.exists():
        return {}
    files = {f.name for f in folder.iterdir() if f.is_file()}
    pools: dict[str, list[str]] = {}
    for fname in files:
        stem, ext = Path(fname).stem, Path(fname).suffix
        m = re.match(r'^(.+?)(\d+)$', stem)
        if m:
            base_name = f"{m.group(1)}{ext}"
            pools.setdefault(base_name, []).append(fname)
    # Ordenar variantes y agregar la base si también existe
    for base, variants in pools.items():
        pool = ([base] if base in files else []) + sorted(variants)
        pools[base] = pool
    return pools


def pick_image(base_img: str, counters: dict, pools: dict) -> str:
    """Elige la siguiente imagen del pool rotando; si no hay pool usa la base."""
    pool = pools.get(base_img, [base_img])
    idx  = counters.get(base_img, 0)
    counters[base_img] = idx + 1
    return pool[idx % len(pool)]


@st.cache_data
def _logo_b64():
    with open(Path("assets/logo/nova.png"), "rb") as f:
        return base64.b64encode(f.read()).decode()

API = "http://localhost:8000"

st.set_page_config(
    page_title="Click & Tech",
    page_icon="assets/logo/nova.png",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stImage"] img {
    height: 200px;
    width: 100%;
    object-fit: contain;
    background-color: #f8f9fa;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("user_id", None),
    ("onboarding_cluster", None),
    ("onboarding_skipped", False),
    ("cart", []),
    ("events", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Helpers ───────────────────────────────────────────────────────────────────

def register_event(event_type: str, row: dict):
    if st.session_state.user_id is None:
        return
    if isinstance(row, pd.Series):
        row = row.to_dict()
    event = {
        "event_time":        str(datetime.now()),
        "event_type":        event_type,
        "product_id":        int(row["product_id"]),
        "category_id":       0,
        "category_code":     row.get("category") or "",
        "brand":             row.get("brand") or "",
        "price":             float(row["price"]) if pd.notna(row.get("price")) else 0.0,
        "user_id":           st.session_state.user_id,
        "user_session":      f"session_{st.session_state.user_id}",
        "category_inferred": False,
        "brand_inferred":    False,
    }
    st.session_state.events.append(event)
    try:
        requests.post(f"{API}/records", json=event, timeout=3)
    except Exception:
        pass


def add_to_cart(row):
    if isinstance(row, pd.Series):
        row = row.to_dict()
    st.session_state.cart.append(row["product_id"])
    register_event("cart", row)


@st.cache_data(ttl=30)
def get_catalog():
    try:
        r = requests.get(f"{API}/products", timeout=5)
        return pd.DataFrame(r.json())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_products_lookup(ids: tuple):
    """Info básica (brand, price, category) para los product_ids dados."""
    if not ids:
        return pd.DataFrame()
    try:
        ids_str = ",".join(str(i) for i in ids)
        r = requests.get(f"{API}/products/lookup?ids={ids_str}", timeout=10)
        return pd.DataFrame(r.json())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_recommendations(user_id: int, n: int = 20):
    try:
        r = requests.get(f"{API}/recommend/{user_id}?n={n}", timeout=5)
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=60)
def get_onboarding_products():
    try:
        r = requests.get(f"{API}/onboarding/products", timeout=5)
        return r.json().get("products", [])
    except Exception:
        return []


def get_onboarding_recs(cluster_id: int, n: int = 20):
    try:
        r = requests.get(f"{API}/onboarding/recommend/{cluster_id}?n={n}", timeout=5)
        return r.json().get("recommendations", [])
    except Exception:
        return []

# ── Header ────────────────────────────────────────────────────────────────────
col_header, col_cart = st.columns([5, 1])
with col_header:
    logo = _logo_b64()
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0f3460 0%, #16213e 60%, #1a1a2e 100%);
        padding: 1.2rem 2rem;
        border-radius: 14px;
        display: flex;
        align-items: center;
        gap: 1.4rem;
        margin-bottom: 0.5rem;
    ">
        <img src="data:image/png;base64,{logo}"
             style="height: 72px; background: white; border-radius: 10px;
                    padding: 6px; box-shadow: 0 2px 10px rgba(0,0,0,0.4);">
        <div>
            <h1 style="color: white; margin: 0; font-size: 2.1rem; font-weight: 800; letter-spacing: 0.5px;">
                Click &amp; Tech
            </h1>
            <p style="color: #90b8d8; margin: 0.3rem 0 0 0; font-size: 1rem;">
                Tu tienda tecnológica
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_cart:
    st.metric("🛒 Carrito", len(st.session_state.cart))

st.divider()

# ── LOGIN ─────────────────────────────────────────────────────────────────────
if st.session_state.user_id is None:
    st.subheader("Ingresá tu ID de usuario")
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        uid_input = st.text_input("User ID", placeholder="Ej: 1515915625519388267", label_visibility="collapsed")
    with col_btn:
        entrar = st.button("Entrar", use_container_width=True)

    if entrar and uid_input.strip():
        try:
            uid = int(uid_input.strip())
            st.session_state.user_id = uid
            st.session_state.onboarding_cluster = None
            st.session_state.onboarding_skipped = False
            st.rerun()
        except ValueError:
            st.error("El User ID debe ser un número.")

    st.info("¿No tenés cuenta? Ingresá cualquier ID nuevo y te guiamos.")
    st.stop()

# ── USUARIO LOGUEADO ──────────────────────────────────────────────────────────
uid = st.session_state.user_id

col_uid, col_logout = st.columns([5, 1])
with col_uid:
    st.caption(f"👤 Usuario: `{uid}`")
with col_logout:
    if st.button("Cerrar sesión"):
        for k in ["user_id", "onboarding_cluster", "onboarding_skipped", "cart", "events"]:
            st.session_state[k] = [] if k in ("cart", "events") else None
        st.rerun()

# ── CHECK si el usuario existe ────────────────────────────────────────────────
rec_data = get_recommendations(uid)
es_conocido = rec_data.get("known_user", False) if rec_data else False

# ── ONBOARDING (usuario nuevo) ────────────────────────────────────────────────
if not es_conocido and st.session_state.onboarding_cluster is None and not st.session_state.onboarding_skipped:
    st.warning("No encontramos historial para este usuario.")
    st.subheader("¿Qué tipo de productos te interesan?")
    st.caption("Elegí el que más te llame la atención para recibir recomendaciones personalizadas.")

    onboarding_prods = get_onboarding_products()
    catalog_df = get_catalog()

    if not onboarding_prods:
        st.error("No se pudo conectar con la API. Verificá que esté corriendo en localhost:8000")
        if st.button("🔄 Reintentar"):
            get_onboarding_products.clear()
            st.rerun()
    else:
        cols = st.columns(len(onboarding_prods))
        for i, prod in enumerate(onboarding_prods):
            pid = prod["product_id"]
            match = catalog_df[catalog_df["product_id"] == pid] if not catalog_df.empty else pd.DataFrame()
            with cols[i]:
                if not match.empty:
                    row = match.iloc[0]
                    st.image(f"assets/images/{row['image']}", use_container_width=True)
                    st.write(f"**{row['product_name']}**")
                    st.write(f"💲{row['price']}")
                else:
                    st.write(f"Producto {pid}")
                if st.button("Elegir este", key=f"ob_{pid}"):
                    st.session_state.onboarding_cluster = prod["cluster_id"]
                    st.rerun()

    if st.button("Saltar → ver productos populares"):
        st.session_state.onboarding_skipped = True
        st.rerun()

    st.stop()

# ── RECOMENDACIONES ───────────────────────────────────────────────────────────
st.subheader("⭐ Recomendaciones para vos")

if not es_conocido and st.session_state.onboarding_cluster is not None:
    cluster = st.session_state.onboarding_cluster
    recs = get_onboarding_recs(cluster)
    st.success(f"Recomendaciones basadas en tu elección (cluster {cluster})")
    method_label = f"Onboarding → cluster {cluster}"

elif not es_conocido:
    recs = rec_data.get("recommendations", []) if rec_data else []
    st.info("Mostrando los productos más populares.")
    method_label = "Popular global"

else:
    recs = rec_data.get("recommendations", []) if rec_data else []
    if recs:
        meta_tier  = recs[0].get("tier", "-")
        meta_gmm   = recs[0].get("gmm", "-")
        meta_clust = recs[0].get("cluster_id", "-")
        tier_label = {0: "Cold start", 1: "Híbrido (1-5 eventos)", 2: "ALS (>5 eventos)"}
        method_label = recs[0].get("method", "ALS")
        c1, c2, c3 = st.columns(3)
        c1.metric("Tier", tier_label.get(meta_tier, meta_tier))
        c2.metric("Cluster", meta_clust)
        c3.metric("GMM", meta_gmm)

catalog_df = get_catalog()

if recs and not catalog_df.empty:
    rec_ids = tuple(r["product_id"] for r in recs)

    # Base: recomendaciones en orden de score
    rec_df = pd.DataFrame(recs)[["product_id"]]

    # Enriquecer con catálogo (tiene imagen y nombre)
    rec_df = rec_df.merge(catalog_df, on="product_id", how="left")

    # Enriquecer con info de eventos para productos sin catálogo
    lookup_df = get_products_lookup(rec_ids)
    if not lookup_df.empty:
        rec_df = rec_df.merge(lookup_df, on="product_id", how="left", suffixes=("", "_ev"))
        rec_df["brand"]    = rec_df["brand"].fillna(rec_df.get("brand_ev"))
        rec_df["price"]    = rec_df["price"].fillna(rec_df.get("price_ev"))
        rec_df["category"] = rec_df["category"].fillna(rec_df.get("category_ev"))
        # Limpiar columnas auxiliares
        rec_df = rec_df[[c for c in rec_df.columns if not c.endswith("_ev")]]

    cols = st.columns(3)
    img_pools   = _build_image_pools("assets/images")
    img_counter = {}                 # base_img → cuántas veces se usó (para rotar variantes)
    for idx, (_, row) in enumerate(rec_df.iterrows()):
        row_dict = row.to_dict()
        with cols[idx % 3]:
            img_file = row.get("image") if pd.notna(row.get("image")) else None
            actual   = pick_image(img_file, img_counter, img_pools) if img_file else "no_image.jpg"
            st.image(f"assets/images/{actual}", use_container_width=True)
            name = row["product_name"] if pd.notna(row.get("product_name")) else f"Producto {int(row['product_id'])}"
            st.subheader(name)
            if pd.notna(row.get("brand")):
                st.write(f"Marca: {row['brand']}")
            if pd.notna(row.get("category")):
                st.write(f"Categoría: {row['category']}")
            if pd.notna(row.get("price")):
                st.write(f"💲{float(row['price']):.2f}")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.button("Agregar al carrito", key=f"rec_cart_{row['product_id']}",
                          on_click=add_to_cart, args=(row_dict,))
            with col_b2:
                if st.button("Ver producto", key=f"rec_view_{row['product_id']}"):
                    register_event("view", row_dict)
elif recs:
    st.dataframe(pd.DataFrame(recs)[["product_id", "score", "method"]], use_container_width=True)
else:
    st.info("No hay recomendaciones disponibles.")

st.divider()

# ── CATÁLOGO COMPLETO ─────────────────────────────────────────────────────────
st.subheader("🛍️ Catálogo completo")

if catalog_df.empty:
    st.error("No se pudo conectar con la API. Asegurate de que esté corriendo en localhost:8000")
else:
    CATALOG_PAGE_SIZE = 100
    total_products = len(catalog_df)
    page = st.number_input("Página", min_value=1,
                           max_value=max(1, (total_products - 1) // CATALOG_PAGE_SIZE + 1),
                           value=1, step=1)
    start = (page - 1) * CATALOG_PAGE_SIZE
    page_df = catalog_df.iloc[start:start + CATALOG_PAGE_SIZE]
    st.caption(f"Mostrando {start + 1}–{min(start + CATALOG_PAGE_SIZE, total_products)} de {total_products} productos")
    cols = st.columns(3)
    for index, row in page_df.iterrows():
        row_dict = row.to_dict()
        with cols[index % 3]:
            st.image(f"assets/images/{row['image']}", use_container_width=True)
            st.subheader(row["product_name"])
            st.write(f"Marca: {row['brand']}")
            st.write(f"Categoría: {row['category']}")
            st.write(f"💲{row['price']}")
            st.button("Agregar al carrito", key=f"add_{row['product_id']}",
                      on_click=add_to_cart, args=(row_dict,))
            if st.button("Ver producto", key=f"view_{row['product_id']}"):
                register_event("view", row_dict)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.title("🛒 Carrito")
st.sidebar.write(f"Productos agregados: {len(st.session_state.cart)}")

if st.sidebar.button("Finalizar compra"):
    if st.session_state.cart:
        for pid in st.session_state.cart:
            match = catalog_df[catalog_df["product_id"] == pid]
            if not match.empty:
                register_event("purchase", match.iloc[0])
        st.sidebar.success("¡Compra finalizada!")
        st.session_state.cart = []
    else:
        st.sidebar.warning("Tu carrito está vacío.")
