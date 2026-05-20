
# 📊 Sistema de Recomendación para E-commerce de Electrónica 

## 🧠 Descripción del Proyecto

Este proyecto desarrolla un sistema de recomendación para un e-commerce de productos electrónicos (celulares, accesorios, computadores, entre otros).

El problema identificado es la baja personalización en la recomendación de productos, lo que impacta negativamente la tasa de conversión y el valor promedio de compra (ticket promedio).

Como solución, se implementa un sistema que sugiere productos relevantes a los usuarios, incluyendo estrategias para abordar el problema de ***Cold Start*** en nuevos clientes.

## 🎯 Objetivo

Desarrollar un sistema de recomendación que:

- Sugiera productos relevantes a los usuarios
- Mejore la experiencia de compra
- Aumente la tasa de conversión
- Incremente el valor promedio de compra


## 💻 Dataset

El dataset original no se incluye en el repositorio debido a las restricciones de tamaño de GitHub.

Dataset obtenido desde kaggle. Puede descargarse desde el siguiente enlace:

- [Descargar dataset](https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-electronics-store)

Una vez descargado, colocar el archivo:

`events.csv`

en la carpeta:

```bash
data/raw/
```

## ⚙️ Tecnologías y Herramientas
* Lenguaje: Python
* Análisis de datos: pandas, numpy
* Machine Learning: Scikit-learn
* Modelado: K-Means, Gaussian Mixture Model (GMM), ALS
* NLP / Embeddings: Sentence Transformers
* Evaluación: Precision@K, Recall@K, Coverage
* Backend API: FastAPI
* Visualización / Frontend: Streamlit
* Versionamiento: Git & GitHub
* Gestión y colaboración: Trello, WhatsApp


## 🏗️ Estructura del Proyecto

```bash
PF_DATA_NOVA_ANALYTICS/
│
├── api/                         # Backend con FastAPI
│   ├── models/                  # Modelos de datos
│   │   └── record.py
│   │
│   ├── routes/                  # Endpoints de la API
│   │   └── recommendations.py
│   │
│   ├── services/                # Lógica de recomendación
│   │   └── recommender_service.py
│   │
│   └── main.py                  # Punto de entrada FastAPI
│
├── assets/                      # Recursos visuales
│   ├── images/
│   └── logo/
│
├── data/
│   ├── raw/                     # Datos originales
│   ├── processed/               # Datos procesados
│   └── final/                   # Dataset final para modelado
│
├── frontend_streamlit/          # Frontend interactivo
│   └── app.py
│
├── models/                      # Modelos entrenados
│   └── gmm_k2.pkl
│
├── notebooks/
│   ├── recmodels/
│   │   ├── comparacion_svd_als.ipynb
│   │   ├── modelo_recomendaciones_als.ipynb
│   │   └── modelo_recomendaciones.ipynb
│   │
│   ├── Clustering_Kmeans.ipynb
│   ├── Notebook_Clustering_NMM.ipynb
│   ├── Evaluacion_reranking_semantico.ipynb
│   ├── feature_engineering_final.ipynb
│   ├── PipelineV_3.0.ipynb
│   └── eda.ipynb
│
├── src/
│   └── recommender/
│       ├── __init__.py
│       └── svd_recommender.py
│
├── venv/                        # Entorno virtual
│
├── requirements.txt             # Dependencias del proyecto
├── run_pipeline.py              # Ejecución principal del pipeline
├── README.md                    # Documentación principal
├── LICENSE
├── docs.md                      # Documentación de la rama  
├── .gitignore
└── .gitkeep
```

## 🔄 Metodología

El proyecto fue desarrollado bajo una metodología Agile (Scrum), simulando un entorno colaborativo de trabajo en Data Science y Machine Learning.

El flujo de trabajo que se desarrolló de manera iterativa incluyó las siguientes etapas:

- Definición del problema de negocio
- Análisis exploratorio de datos (EDA)
- Limpieza y transformación de datos
- Feature Engineering
- Segmentación de usuarios mediante clustering (K-Means y GMM)
- Construcción y comparación de modelos de recomendación (SVD vs ALS)
- Implementación de semantic re-ranking utilizando embeddings
- Evaluación de métricas de desempeño
- Desarrollo de API con FastAPI
- Despliegue de aplicación interactiva con Streamlit

## 🤖 Sistema de Recomendación

El sistema de recomendación se construye utilizando modelos de filtrado colaborativos basados en:

- ALS (Alternating Least Squares)
- SVD (Singular Value Decomposition)

Adicionalmente, se implementa una capa de semantic re-ranking utilizando embeddings semánticos con Sentence Transformers para mejorar la relevancia de las recomendaciones.

El sistema permite:

- Generar recomendaciones personalizadas
- Mejorar la similitud semántica entre productos
- Comparar desempeño entre modelos
- Mitigar parcialmente problemas de relevancia en recomendaciones tradicionales

## 📏 Evaluación del Modelo

El rendimiento del sistema se evalúa utilizando métricas estándar de sistemas de recomendación:

- **Precision@K:** proporción de recomendaciones relevantes dentro del Top-K
- **Recall@K:** capacidad del modelo para recuperar productos relevantes
- **Coverage:** proporción del catálogo que el modelo es capaz de recomendar
- Evaluación comparativa entre ALS, SVD y semantic re-ranking

## 🚀 Ejecución del Proyecto

1️⃣ Clonar repositorio

```bash
git clone https://github.com/JuanP0508/PF_DATA_NOVA_ANALYTICS.git
cd PF_DATA_NOVA_ANALYTICS
```

2️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

3️⃣ Ejecutar API FastAPI

```bash
uvicorn api.main:app --reload
```

4️⃣ Ejecutar Streamlit

```bash
streamlit run frontend_streamlit/app.py
```

5️⃣ Ejecutar pipeline principal

```bash
python run_pipeline.py
```

## 📌 Resultados Esperados
* Mejora en la personalización de recomendaciones
* Incremento en la relevancia semántica de productos sugeridos
* Segmentación estratégica de usuarios
* Comparación experimental entre modelos de recomendación
* Arquitectura escalable mediante FastAPI + Streamlit
* Simulación de entorno productivo de Machine Learning


## 👥 Equipo de Trabajo
Proyecto desarrollado como parte de una simulación académica en entorno Agile (Scrum), integrando procesos de Data Science, Machine Learning y despliegue de aplicaciones.

