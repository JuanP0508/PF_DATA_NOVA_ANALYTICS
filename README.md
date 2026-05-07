# 📊 Sistema de Recomendación para E-commerce de Electrónica 

## 🧠 Descripción del Proyecto

Este proyecto desarrolla un sistema de recomendación para un e-commerce de productos electrónicos (celulares, accesorios, computadores, entre otros).

El problema identificado es la baja personalización en la recomendación de productos, lo que impacta negativamente la tasa de conversión y el valor promedio de compra (ticket promedio).

Como solución, se implementa un sistema que sugiere productos relevantes a los usuarios, incluyendo estrategias para abordar el problema de cold start en nuevos clientes.

## 🎯 Objetivo

Desarrollar un sistema de recomendación que:

Sugiera productos relevantes a los usuarios
Mejore la experiencia de compra
Aumente la tasa de conversión
Incremente el valor promedio de compra

## ⚙️ Tecnologías y Herramientas
Lenguaje: Python
Análisis de datos: pandas, numpy
Modelado: reglas de asociación (Apriori)
Evaluación:
Precision@K
Recall@K
Support
Confidence
Lift
Visualización / App: Streamlit


## 🏗️ Estructura del Proyecto

```bash
pf_data_nova_analytics/
│
├── data/
│   ├── raw/            # Datos originales
│   ├── processed/      # Datos limpios y transformados
│   └── final/          # Dataset final para modelado
│
├── notebooks/          # Análisis exploratorio (EDA)
│
├── src/
│   ├── carga.py               # Carga de datos
│   ├── preprocessing.py       # Limpieza y transformación
│   ├── recomendador.py        # Lógica del sistema de recomendación
│   ├── reglas_asociacion.py   # Implementación de Apriori
│   ├── evaluacion.py          # Métricas del modelo
│   └── utils.py               # Funciones auxiliares
│
├── models/             # Modelos entrenados
│
├── app/
│   └── streamlit_app.py       # Aplicación interactiva
│
├── reports/            # Reportes y resultados
│
├── requirements.txt    # Dependencias
├── README.md           # Documentación
├── main.py             # Ejecución principal del pipeline
└── .gitignore
```

## 🔄 Metodología

El proyecto fue desarrollado bajo un enfoque Agile (Scrum), simulando un entorno real de trabajo colaborativo.

Se trabajó de manera iterativa, incluyendo:

Definición del problema
Análisis exploratorio de datos (EDA)
Preprocesamiento
Modelado
Evaluación
Despliegue en aplicación interactiva

## 🤖 Modelo de Recomendación

El sistema se basa en reglas de asociación (Apriori) para identificar patrones de compra entre productos.

Esto permite:

Recomendar productos frecuentemente comprados juntos
Generar recomendaciones personalizadas
Implementar estrategias para usuarios nuevos (cold start)

## 📏 Evaluación del Modelo

El rendimiento del sistema se mide mediante:

Precision@K: proporción de recomendaciones relevantes dentro del top K
Recall@K: proporción de productos relevantes recuperados
Support: frecuencia de aparición de un conjunto de productos
Confidence: probabilidad de compra conjunta
Lift: grado de asociación entre productos

## 🚀 Ejecución del Proyecto
Clonar el repositorio:
git clone <url-del-repositorio>
cd pf_data_nova_analytics
Instalar dependencias:
pip install -r requirements.txt
Ejecutar el pipeline:
python main.py
Ejecutar la aplicación:
streamlit run app/streamlit_app.py

## 📌 Resultados Esperados
Mejora en la personalización de recomendaciones
Incremento en la conversión de usuarios
Aumento del ticket promedio
Sistema escalable para entornos reales

## 👥 Equipo de Trabajo

Proyecto desarrollado como parte de una simulación académica en entorno ágil (Scrum).
