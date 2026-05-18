import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# CONFIGURACIÓN PÁGINA
st.set_page_config(
    page_title="Nova Electronics",
    layout="wide"
)
#Logo y titulos
col1, col2 = st.columns([1, 3])

with col1:
    st.image(
        "assets/logo/nova.png",
        width=150
    )

with col2:
    st.title("Nova Electronics")
    st.write("Tu tienda tecnológica")
    
# TÍTULO
st.title("Catálogo de productos tecnológicos")
# Logo en navegador 
st.set_page_config(
    page_title="Nova Electronics",
    page_icon="assets/logo/nova.png",
    layout="wide"
)
# CARGAR CSV
# df = pd.read_csv("data/processed/product_catalog.csv")-en caso de usar el csv local
response = requests.get("http://localhost:8000/products")
df = pd.DataFrame(response.json())  

# SESSION STATE PARA CARRITO
if "cart" not in st.session_state:
    st.session_state.cart = []
# SESSION STATE PARA EVENTOS
if "events" not in st.session_state:
    st.session_state.events = []
# FUNCIONES
## FUNCION EVENTOS
def register_event(event_type, product_id):
    st.session_state.events.append({
        "event_time": datetime.now(),
        "event_type": event_type,
        "product_id ": product_id,
    })
## FUNCION CARRITO
def add_to_cart(product_id):
    st.session_state.cart.append(product_id)
    register_event("add_to_cart", product_id)
# SIDEBAR 
    ## CARRITO  
st.sidebar.title("🛒 Carrito")
st.sidebar.write(
    f"Productos agregados: {len(st.session_state.cart)}"
)  
    ## COMPRA
if st.sidebar.button("Finalizar compra"):

    if st.session_state.cart:

        for product_id in st.session_state.cart:

            register_event(
                "purchase",
                product_id
            )

        st.sidebar.success(
            "Compra finalizada con éxito!"
        )

        st.session_state.cart = []

    else:

        st.sidebar.warning(
            "Tu carrito está vacío."
        )
    ## VIEW
st.sidebar.subheader("Eventos registrados")
st.sidebar.write(st.session_state.events)

# MOSTRAR PRODUCTOS
cols = st.columns(3)

for index, row in df.iterrows():

    col = cols[index % 3]

    with col:

        # IMAGEN
        st.image(
            f"assets/images/{row['image']}",
            use_container_width=True
        )

        # NOMBRE
        st.subheader(row["product_name"])

        # MARCA
        st.write(f"Marca: {row['brand']}")

        # CATEGORÍA
        st.write(f"Categoría: {row['category']}")

        # PRECIO
        st.write(f"💲{row['price']}")

        # BOTONES
        ## BOTÓN AGREGAR AL CARRITO
        st.button(
            "Agregar al carrito",
            key=f"add_{row['product_id']}",
            on_click=add_to_cart,
            args=(row["product_id"],)
        )
        ## BOTÓN VIEW DETAILS
        if st.button(
        "Ver producto",
        key=f"view_{row['product_id']}"
        ):
            register_event(
            "view",
            row["product_id"]
            )

        