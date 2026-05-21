# 🚀 Arquitectura y Desarrollo de un Sistema Híbrido de Recomendación para E-commerce

## 📑 Índice

1. Introducción
2. Objetivo del Proyecto
3. Arquitectura General del Sistema
4. Pipeline de Limpieza y Transformación
5. Exploratory Data Analysis (EDA)
6. Feature Engineering
7. Segmentación de Usuarios
   - K-Means
   - Gaussian Mixture Model (GMM)
8. Sistema Híbrido de Recomendación
9. Semantic Re-ranking
10. Evaluación Experimental
11. API REST — Arquitectura y Endpoints
12. Frontend Streamlit — Tienda Interactiva y Monitor de Salud
13. Resultados y Hallazgos
14. Limitaciones del Proyecto
15. Futuras Mejoras
16. Conclusiones


# 1. 📌 Introducción

Este documento describe el diseño, desarrollo y evaluación experimental de un sistema híbrido de recomendación para e-commerce de electrónica.

El proyecto integra:
- análisis exploratorio,
- clustering,
- filtrado colaborativo,
- semantic re-ranking,
- estrategias cold start,
- y evaluación experimental.

# 2. 📌 Objetivo del Proyecto

Desarrollar un sistema de recomendación que:

- Sugiera productos relevantes a los usuarios
- Mejore la experiencia de compra
- Aumente la tasa de conversión
- Incremente el valor promedio de compra

# 3. 📌 Arquitectura General del Sistema

```bash
Raw Data
   ↓
Cleaning
   ↓
EDA
   ↓
Feature Engineering
   ↓
Clustering
   ↓
ALS
   ↓
Semantic Re-ranking
   ↓
API
   ↓
Streamlit
```

# 4. 📊 Pipeline de Limpieza, Transformación y Feature Engineering

### Inferencia de Categorías (Data Cleaning)

En esta etapa del pipeline se aborda el problema de productos sin category_code, lo cual afecta directamente la calidad del sistema de recomendación.

### Objetivo

Asignar una categoría inferida a los productos que no cuentan con category_code, utilizando información disponible como el category_id y las marcas dominantes dentro de cada grupo.

###  Proceso Paso a Paso

**1.** Carga y limpieza inicial
Interpretación:

Se cargan los datos desde el archivo events.csv.
Se eliminan registros donde user_session es nulo.

**2.** Problema: categorías faltantes

Muchos productos no tienen category_code, lo que genera:

Pérdida de información semántica
Dificultad para agrupar productos
Peor desempeño del recomendador

**3.** Estrategia de solución: inferencia por category_id

Se construye un diccionario que asigna una categoría inferida a cada category_id.

**4.** Aplicación del Mapa de Inferencia

Una vez construido el diccionario de inferencia, se aplicó sobre los registros con valores nulos en category_code con el objetivo de recuperar información faltante sin alterar los datos ya existentes.

Para ello, se evaluó inicialmente la cantidad de valores nulos y posteriormente se realizó una asignación condicional: si un registro no tenía categoría, se intentaba inferir a partir de su category_id utilizando el mapa previamente definido; en caso contrario, se mantenía el valor original.

Este proceso permitió cuantificar el impacto de la limpieza mediante tres métricas clave:

- Número de valores nulos antes del proceso
- Cantidad y porcentaje de registros recuperados
- Valores que permanecen sin inferir

La aplicación de esta estrategia mejora la calidad del dataset, incrementa la cobertura de categorías y fortalece la capacidad del sistema de recomendación para generar resultados más precisos y coherentes.

Adicionalmente, se garantiza que la transformación sea no intrusiva, ya que solo se modifican los registros incompletos, preservando la integridad de los datos originales.

### Manejo de Categorías No Inferidas

A pesar del proceso de inferencia basado en category_id, algunos registros no pudieron ser clasificados debido a la falta de patrones claros o información suficiente.

Para garantizar la consistencia del dataset y evitar la pérdida de información, se asignó una categoría genérica a estos casos, permitiendo:

- Mantener todos los registros dentro del sistema
- Evitar valores nulos que puedan afectar el modelo
- Agrupar productos ambiguos bajo una categoría controlada

### Identificación de Registros Inferidos

Se creó una nueva variable category_inferred para identificar qué registros fueron afectados por el proceso de inferencia, permitiendo

- Trazabilidad del proceso de limpieza
- Análisis posterior del impacto de la inferencia
- Evaluar el comportamiento del modelo sobre datos 
- inferidos vs originales

### Inferencia de Marca (brand)

En esta etapa se aborda el problema de productos que no cuentan con información de marca (brand), lo cual puede afectar la calidad del sistema de recomendación y el análisis de comportamiento de compra.

### Objetivo

Asignar una marca inferida a los productos sin brand, utilizando como referencia su category_code, con el fin de mantener la consistencia del dataset y evitar valores nulos.

### Estrategia de Inferencia

Para los registros sin marca, se define una regla basada en la estructura de la categoría:

Se asigna una marca genérica compuesta por el prefijo "generic." seguido del último nivel de la categoría.

### Análisis y Estructuración de Categorías

Después del proceso de limpieza e inferencia de `category_code`, se realizó un análisis de su estructura jerárquica para comprender cómo están organizadas las categorías y preparar el dataset para su posterior transformación.

Las categorías siguen un formato jerárquico delimitado por puntos (`.`), donde cada nivel representa un mayor grado de especificidad (por ejemplo: `electronics.telephone.accessory`).

### Análisis de la estructura

Para identificar la profundidad de las categorías, se contabilizó el número de puntos (`.`) presentes en cada valor de `category_code`, lo cual permite determinar el número de niveles jerárquicos.

Adicionalmente, se exploraron ejemplos representativos por cada nivel para validar la consistencia de la estructura.

### Resultados

La distribución de los niveles jerárquicos fue la siguiente:

* **Nivel 0 (0 puntos):** 0 registros
* **Nivel 1 (1 punto):** 250,245 registros
* **Nivel 2 (2 puntos):** 634,304 registros
* **Nivel 3 (3 puntos):** 415 registros

Ejemplos identificados:

* **Nivel 1:**
  `electronics.telephone`, `computers.desktop`, `accessories.generic`

* **Nivel 2:**
  `computers.components.cooler`, `electronics.telephone.accessory`

* **Nivel 3:**
  `electronics.audio.music_tools.piano`

### Interpretación

A partir de estos resultados se concluye que:

* No existen categorías sin jerarquía, lo que indica una estructura consistente en el dataset.
* La mayor concentración de datos se encuentra en el **nivel 2**, lo que lo convierte en el nivel más adecuado para el análisis y modelado.
* El **nivel 1** agrupa categorías más generales, útiles para segmentaciones amplias.
* El **nivel 3**, aunque más específico, tiene muy baja representación, lo que puede generar problemas de dispersión (sparsity) en el modelo.

### Implicaciones para el modelado

La variabilidad en la profundidad de las categorías hace necesario estandarizar su estructura. Utilizar niveles demasiado específicos podría afectar negativamente el rendimiento del sistema de recomendación, mientras que niveles muy generales pueden perder capacidad descriptiva.

### Decisión de transformación

Con base en este análisis, se definió la siguiente estrategia:

* Dividir `category_code` en múltiples niveles jerárquicos (`nivel1`, `nivel2`, `nivel3`)
* Priorizar el uso del **nivel 2** para el modelado, debido a su equilibrio entre granularidad y representatividad
* Mantener niveles más profundos como información complementaria
* para el nivel más detallado se conserva dentro de la variable **nivel 3** y que No se pierde información relevante al estandarizar la jerarquía

Esta transformación permite mejorar la calidad del feature engineering, facilitar el análisis por categorías y fortalecer el desempeño del sistema de recomendación.

### Normalización Contextual de Categorías

Durante el proceso de análisis se identificaron categorías con ambigüedad semántica, ya que aparecían en múltiples niveles jerárquicos (por ejemplo, términos como "accessories", "generic" o "storage").

Este comportamiento genera inconsistencias, ya que una misma etiqueta puede tener diferentes significados dependiendo del contexto en el que se encuentre, afectando la calidad del sistema de recomendación.

### Objetivo

Reducir la ambigüedad semántica mediante una normalización contextual, incorporando información de niveles superiores para generar categorías más específicas y coherentes.

### Estrategia

Se aplicó una transformación selectiva sobre categorías problemáticas:

En nivel 2, se integra el contexto de nivel1
En nivel 3, se utiliza el contexto de nivel2_norm previamente ajustado

Esto permite diferenciar categorías que, aunque comparten nombre, pertenecen a contextos distintos.

### Eliminación de Registros Duplicados

Como parte del proceso inicial de limpieza, se realizó la identificación y eliminación de registros duplicados en el dataset, con el fin de garantizar la integridad y calidad de la información.

La eliminación de duplicados se realizó únicamente sobre filas completamente iguales, evitando eliminar registros que, aunque similares, representen eventos distintos (por ejemplo, múltiples interacciones de un mismo usuario).

## Conclusiones del Pipeline de Datos 

   El pipeline de limpieza, transformación y feature engineering permitió mejorar significativamente la calidad, consistencia y valor analítico del dataset. 
   
   A través de la inferencia de category_code y brand, se redujeron los valores nulos de forma no intrusiva, aumentando la cobertura semántica sin comprometer la integridad de los datos. Además, la incorporación de variables de trazabilidad permite evaluar el impacto de estas transformaciones en el modelado. 
   
   El análisis de la estructura jerárquica de categorías evidenció que el nivel 2 ofrece el mejor equilibrio entre granularidad y representatividad, por lo que se definió como base para el modelado, complementado con niveles adicionales para preservar información. 
   
   Asimismo, la normalización contextual permitió reducir ambigüedades semánticas, mejorando la coherencia de las categorías y fortaleciendo la capacidad del sistema de recomendación. 
   
   En conjunto, este pipeline establece una base sólida que optimiza el rendimiento del modelo, mejora la interpretabilidad y habilita análisis más precisos y escalables.
---

# 5. 📊 EDA: Análisis del Comportamiento de Compra en E-commerce

Este módulo contiene el Análisis Exploratorio de Datos (EDA) aplicado a un dataset de comercio electrónico, utilizando el archivo optimizado `inferido_limpio.csv` tras el pipeline de limpieza. El objetivo principal es identificar patrones de comportamiento, analizar el embudo de conversión de los usuarios y detectar los principales puntos de fricción en el flujo de compra (`view` ➔ `cart` ➔ `purchase`).


### Análisis del Embudo de Conversión (EDA)

Este módulo contiene el Análisis Exploratorio de Datos (EDA) aplicado al comportamiento de los usuarios en la plataforma, evaluando el flujo desde la visualización de productos hasta la conversión final.

###  Gráficos del Flujo de Usuarios

En la siguiente ilustración se presenta la distribución total de los eventos registrados y el embudo de conversión correspondiente:

![embudo](https://i.postimg.cc/P5nfPr2z/embudo.png)

El análisis del comportamiento del usuario revela las siguientes tasas de conversión entre etapas:

*   **Visualización a Carrito (`view` ➔ `cart`):** **6.8%**
*   **Carrito a Compra (`cart` ➔ `purchase`):** **69.1%**
*   **Conversión Total (`view` ➔ `purchase`):** **4.7%**

## Análisis de Actividad por Usuario y Diagnóstico de Cold Start

Para entender la recurrencia y el nivel de interacción en la plataforma, se analizó la distribución de eventos generados por cada usuario único. Este análisis es fundamental para identificar la presencia de usuarios con baja actividad históricos (*Cold Start*).

### Gráficos de Distribución de Actividad

Los siguientes gráficos detallan la frecuencia de eventos por usuario y la segmentación por tramos de actividad:

![distribución](https://i.postimg.cc/cHnfMJyp/embudo.png)



*   **Usuarios Únicos Totales:** **407,237**
*   **Mediana de Eventos:** **1** (El usuario típico realiza una sola acción y no regresa)
*   **Media de Eventos:** **2.2** (Sesgada positivamente por un grupo muy reducido de usuarios hiperactivos)
*   **Usuarios en Escenario de Cold Start (≤ 5 eventos):** **382,745** (**94.0%** del total)


El dato más crítico del dataset es que **94 de cada 100 usuarios tienen 5 o menos interacciones en total**. La plataforma se enfrenta a un problema masivo de arranque en frío (*Cold Start*). 

 Existe una desconexión severa en la retención inmediata. La primera impresión o la relevancia de la página de aterrizaje inicial no está logrando enganchar al usuario para que explore más productos dentro de la misma sesión.


## Análisis Jerárquico de la Estructura de Categorías

Se analizar el catálogo de productos a través de sus tres niveles de granularidad. permite entender la especialización del comercio electrónico y cómo se distribuye el volumen de eventos en la jerarquía comercial.

### Gráficos de Distribución por Niveles

La concentración de la actividad en los tres niveles se detalla en las siguientes visualizaciones:

![nivel 1](https://i.postimg.cc/h4dZr9Lq/nivel-1.png)

![nivel 2](https://i.postimg.cc/k52v5mwm/nivel-2.png)

![nivel 3](https://i.postimg.cc/3JrpRhJy/nivel-3.png)


*   **Nivel 1 (Macrocategorías):** **14** categorías únicas.
*   **Nivel 2 (Subcategorías):** **79** categorías únicas (Crecimiento de **5.6x** en granularidad).
*   **Nivel 3 (Microcategorías/Productos específicos):** **155** categorías únicas (Crecimiento de **2x** respecto al Nivel 2).

A pesar de que el dataset cuenta con categorías diversas como `furniture`, `medicine` o `kids`, el negocio está gobernado casi exclusivamente por el sector tecnológico.

*   **Nivel 1:** `computers` (372,460 eventos) y `electronics` (251,661 eventos) dominan de manera absoluta el tráfico, dejando a las categorías no tecnológicas con una participación minima.
*   **Nivel 2:** El subsector de `components` lidera con 222,807 eventos, duplicando a la subcategoría de `telephone`.
*   **Nivel 3:** Las tarjetas de video (`videocards`) son el motor principal de interacción en la plataforma con 116,606 eventos, seguidas de lejos por `printer` (43,188 eventos).


## Análisis de Evolución Temporal y Estacionalidad

Se analiza el comportamiento de la plataforma a lo largo del tiempo (septiembre 2020 a febrero 2021) de manera semanal y mensual. El objetivo es identificar picos de tráfico, estacionalidad en las ventas y evaluar la estabilidad de las conversiones a lo largo del periodo.

## Gráficos de Tendencia Temporal

Las fluctuaciones del tráfico y de las transacciones se detallan en las siguientes series temporales y distribuciones mensuales:

![estacionalidad](https://i.postimg.cc/HW60bnKW/estacionalidad.png)

###  1. El Pico de Noviembre (Black Friday / Cyber Monday)
Se evidencia una aceleración masiva del tráfico en la primera mitad de noviembre, alcanzando el pico histórico de la serie con **más de 40,000 visualizaciones semanales** (`views`) y cerrando el mes con un volumen récord superior a los 160,000 eventos de visualización.

###  2. La Anomalía de Diciembre: Caída de Tráfico pero Estabilidad de Compra
Contrario a los comercios minoristas tradicionales que explotan en Navidad, este set de datos experimenta una **contracción de visualizaciones** en diciembre (bajando a ~135,000 eventos). Sin embargo, al observar las líneas de carrito (`cart`) y compra (`purchase`):

Los usuarios que entraron en diciembre tenían una intención de compra mucho más directa y menos exploratoria que los de noviembre. El tráfico residual de "curiosos" disminuyó, pero los compradores reales se mantuvieron.

### 3. El Efecto de Datos Incompletos en Septiembre
El mes de septiembre de 2020 muestra barras de actividad drásticamente bajas. Esto no representa una crisis del negocio, sino un truncamiento en la recolección de datos (el registro comienza a finales de ese mes).

## Análisis de Patrones Horarios y Semanales (Hábitos del Usuario)

Este análisis desglosa la actividad de la plataforma en ciclos diarios (por horas) y semanales (por días) con el fin de identificar las ventanas de tiempo óptimas de interacción y entender la rutina de navegación de la audiencia.

![eventos día](https://i.postimg.cc/MTBGy4NS/Eventos-dia.png)

La distribución horaria revela un comportamiento de navegación fuertemente concentrado durante el día, con características muy marcadas:

*   **Pico de Actividad Constante:** El volumen de eventos explota a partir de las 05:00 y se mantiene en una meseta de máxima actividad entre las **09:00 y las 18:00**, superando consistentemente los 50,000 eventos por hora. El pico absoluto ocurre a las **11:00**.
*   **Comportamiento de Oficina/Estudio:** La actividad no desciende al mediodía (almuerzo) ni muestra un pico nocturno exagerado; cae en picada drásticamente después de las 19:00 hasta alcanzar su mínimo a las 01:00.
*   **Insight:** Al ser una plataforma orientada a componentes tecnológicos y hardware (como se descubrió en el análisis categórico), los usuarios tienden a buscar, cotizar o interactuar con el catálogo durante sus horas productivas, laborales o de estudio académico.

A diferencia de los comercios tradicionales de ocio que repuntan los sábados y domingos, este dataset muestra un comportamiento inverso:

*   **Lunes de Máxima Actividad:** El día con mayor volumen de interacción es el **Lunes** (~133,000 eventos). La actividad desciende de forma ligera pero escalonada a lo largo de los días laborables (Martes a Viernes).
*   **El "Valle" del Sábado:** El punto más bajo de la semana ocurre el **Sábado** (~117,000 eventos), recuperándose levemente el Domingo.
*   **Insight:** La audiencia percibe la adquisición o investigación de este tipo de productos como una tarea planificada de inicio de semana y no como una actividad recreativa de fin de semana.

## Análisis Conversión por Categoría (Nivel 1)

Aunque el catálogo general está dominado en tráfico por la tecnología, las eficiencias de conversión final (`view` ➔ `purchase`) muestran dinámicas opuestas según el nicho:

![CONVERSIÓN](https://i.postimg.cc/7YygLCZC/CONVERSION.png)

*   **`stationery` (Líder Absoluto - 7.82% de conversión total):** Presenta el mejor desempeño del ecosistema. Logra que un **8.80%** agregue al carrito y un impresionante **88.87%** concrete la compra. Al cruzarlo con el *boxplot*, se observa que sus precios son sumamente bajos y concentrados (cercanos a 0-50). Es un comportamiento de **compra por impulso o de baja deliberación**, donde el precio no representa una barrera.
*   **`computers` (Segundo Lugar - 5.89% de conversión total):** Es el hallazgo más sorprendente del cruce de datos. A pesar de tener **el rango de precios más alto y disperso del catálogo** (con una mediana cercana a 150 y un tercer cuartil rozando los 300), mantiene la tasa de agregación al carrito más alta de la tienda (**9.33%**). 


## Matriz de Interacciones (Heatmap)

Se evalúa la intensidad de las interacciones cruzando una muestra de los 30 usuarios más activos con los 30 productos con mayor tráfico del catálogo. Este mapa de calor es una herramienta diagnóstica fundamental para auditar la densidad de los datos antes de diseñar algoritmos de filtrado colaborativo.

![alt text](https://i.postimg.cc/66ZmSGPc/heatmap.png)

A pesar de aislar artificialmente a los 30 usuarios y productos con mayor volumen del dataset (el percentil más alto de actividad), el gráfico muestra un predominio absoluto de celdas blancas o de color azul muy tenue (0 a 10 interacciones).

Si la matriz del "Top 30" ya exhibe este nivel de dispersión, la matriz global de la plataforma con los **407,237 usuarios** y **53,452 productos** calculados previamente tendrá un porcentaje de *sparsity* superior al **99.9%**.

## Conclusiones del EDA

1. Desbalance del Embudo y Señal de Conversión. El 89% de los eventos son visualizaciones (`views`) y solo el 4% son compras (`purchase`).

2. Predominio Masivo de Cold Start de Usuarios. El 94% de la audiencia registra $\le$ 5 interacciones (Mediana = 1 evento).

3. Alta Concentración de Popularidad en Productos. El catálogo exhibe una distribución de Cola Larga (*Long Tail*) donde pocos artículos concentran el tráfico.

4. Selección del Nivel 2 como Pivote Taxonómico. Nivel 1 es generalista (14 nodos) y Nivel 3 sufre de dispersión extrema (155 nodos).

5. Estacionalidad Comercial No Navideña. Pico histórico en noviembre (~165k eventos por Black Friday), contracción en diciembre (~138k) y rebote en enero (~163k).

6. Hábitos Diurnos y Estabilidad Semanal. Concentración de tráfico en horario laboral (10:00 a 18:00; ~53k eventos/hora). Variación intersemanal baja (Lunes ~133k vs. Sábado ~117k; diferencia de solo 14%).

7. Necesidad de Normalización de Precios. Variación extrema en los rangos de precios entre sectores (Mediana de `furniture`: 16 vs. `computers`: 147).

8. Priorización por Eficiencia de Conversión.`stationery` (7.82%) y `computers` (5.89%) lideran la conversión total de vistas a ventas. `medicine` registra el mínimo (1.61%).

9. Dispersión Crítica de la Matriz (Sparsity). La matriz de interacciones directas usuario-producto presenta una esparcida extrema del **99.9974%**.

10. Independencia del Comportamiento vs. Taxonomía. Alta asociación Categoría-Marca (0.94) que confirma la segmentación nativa del catálogo. El tipo de evento (view/cart/purchase) es independiente de la categoría/marca (0.07–0.13).

# 6. 📊Feature Engineering

Esta sección documenta el script inicial de preparación de datos. El objetivo de este bloque de código es establecer una tubería (*pipeline*) de carga robusta, normalizar las variables temporales y extraer los componentes de tiempo base necesarios para construir los perfiles de comportamiento de usuarios y productos.

Dado que el dataset de comercio electrónico no cuenta con calificaciones explícitas (como estrellas de 1 a 5), se diseñó un sistema de **puntuación por comportamiento implícito**. Se asignó un peso numérico incremental a cada tipo de interacción (`event_type`), reflejando de forma proporcional el nivel de compromiso (*engagement*) e intención de compra del usuario:

*   **`view` ➔ Peso: 1** (Señal de interés bajo/exploratorio).
*   **`cart` ➔ Peso: 2** (Señal de interés medio/intención de compra).
*   **`purchase` ➔ Peso: 3** (Señal de interés alto/conversión efectiva).

A continuación la justificación Técnica y de Negocio

#### 📈 1. Compensación de Clases Desbalanceadas
Como se descubrió en las conclusiones del EDA, el 89% del set de datos está compuesto por interacciones de visualización (`views`), mientras que las compras representan una minoría. Si el modelo entrenara con un valor idéntico para todas las interacciones (ej. "1" para cualquier evento), las recomendaciones se saturarían de productos que la gente solo mira por curiosidad pero nunca compra. Al otorgar un **peso triple a la compra**, se obliga al algoritmo a priorizar la conversión sobre la simple navegación.

#### 🧠 2. Construcción de Matrices de Factorización Implícita
Este mapeo numérico transforma una columna categórica de eventos en una variable continua de utilidad. Esta variable sirve como base directa para alimentar algoritmos de recomendación basados en **Feedback Implícito** (como *Implicit Alternating Least Squares - iALS*). El modelo interpretará los valores más altos como una certeza estadística de que el usuario tiene una afinidad real con el producto.

#### 🔄 3. Lógica Numérica Monótona Creciente
La escala asegura consistencia matemática en los agregados de datos. Si un usuario visualiza un producto, lo agrega al carrito y finalmente lo compra en la misma sesión, la agregación posterior del perfil de interacción reflejará un valor acumulado sólido (1 + 2 + 3 = 6), aislando orgánicamente a estos pares usuario-producto como relaciones de máxima relevancia.

##  Construcción del Perfil de Usuario (User Profiling Pipeline)

Este script consolida el historial transaccional disperso del conjunto de datos original y lo convierte en una matriz de características agregadas por usuario único (`user_id`). El objetivo principal es estructurar el dataset definitivo (`user_clustering_dataset.csv`) necesario para alimentar modelos de aprendizaje no supervisado (**Clustering**) y segmentación de clientes.

### Mapa de Características del Dataset Final (`user_df`)

El pipeline genera **21 columnas estructuradas** que capturan tres dimensiones fundamentales del comportamiento humano en el comercio electrónico:


| Categoría de Métrica | Variables Generadas | Propósito en el Modelo / Insight |
| :--- | :--- | :--- |
| **Volumetría e Interacción** | `total_events`, `unique_products`, `view`, `cart`, `purchase`, `avg_events_per_product` | Mide la intensidad de navegación y el nivel de exploración del catálogo frente al comportamiento directo de compra. |
| **Financieras y Valor** | `avg_price`, `avg_purchase_price`, `weighted_score` | Determina el poder adquisitivo del usuario. Separa el precio promedio de lo que el usuario solo mira (`avg_price`) de lo que efectivamente paga (`avg_purchase_price`). |
| **Patrones Temporales** | `recency_days`, `pct_morning`, `pct_afternoon`, `pct_evening`, `pct_night`, `pct_weekday`, `pct_weekend` | Identifica la ventana de inactividad del cliente y calcula proporciones normalizadas para mapear sus rutinas de compra (diurno/nocturno, laboral/fin de semana). |
| **Afinidad Categórica** | `proportion_tech`, `proportion_fashion_lifestyle`, `proportion_home`, `proportion_welfare` | Agrupa las 14 macrocategorías del Nivel 1 en 4 clusters temáticos unificados, definiendo el perfil de intereses preferenciales de cada cliente. |

---

###  Desglose y Lógica de Ingeniería de Datos

#### 1. Control de Idempotencia y Robustez (Fallback Inicial)
*   El script incluye un bloque de control condicional que verifica si la columna `peso` ya existe. Esto garantiza la idempotencia del cuaderno (*idempotency*), previniendo excepciones lógicas de duplicación de columnas si la celda es ejecutada fuera de orden por el desarrollador.
*   Fuerza la homologación del tiempo a formato estándar mediante `pd.to_datetime(..., utc=True)`, eliminando zonas horarias nativas antes de calcular métricas de ventana temporal.

####  2. Desglose del Embudo y Frecuencias Cruzadas
*   A través del método `.groupby()` y tablas dinámicas (`.pivot_table()`), el script descompone la interacción agregando las cuentas independientes de clics para `view`, `cart` y `purchase`.
*   Crea la variable de densidad `avg_events_per_product` (Eventos Totales / Productos Únicos). Valores cercanos a 1 indican navegación superficial (un clic por artículo); valores altos denotan un interés recurrente u obsesivo por productos específicos.

#### 3. Variable de Recencia (`recency_days`)
*   Calcula los días transcurridos entre la última interacción registrada de cada usuario específico (`last_event`) y la fecha máxima absoluta de recolección en toda la plataforma (`dataset_end_date`).
*   **Valor para Machine Learning:** Es el pilar fundamental del análisis RFM (Recencia, Frecuencia, Valor Monetario), crítico para predecir tasas de abandono (*churn prediction*).

####  4. Normalización Vectorial de Hábitos (Proporciones Relativas)
*   En lugar de inyectar las cuentas brutas de clics por horarios o días (que sesgarían el modelo hacia los usuarios hiperactivos), el script normaliza las filas aplicando una división matricial cruzada mediante `.div(..., axis=0)`.
*   Las variables transformadas a porcentajes independientes (`pct_morning`, `pct_weekend`, etc.) suman exactamente 1.0 por usuario. Esto permite a los algoritmos de agrupamiento evaluar hábitos puros de tiempo, sin importar si el usuario realizó 2 o 2,000 clics en total.

####  5. Reducción de Dimensionalidad Taxonómica (Macro-Agrupaciones)
Debido a la esparcida (*sparsity*) y desbalance analizado en el EDA, mapear las 14 categorías del Nivel 1 dispersaría la señal del modelo. Se aplicó un mapeo de dominio experto estructurado en cuatro grandes familias de mercado:
*   **`tech`:** Computadores, electrónica de consumo y accesorios automotrices.
*   **`fashion_lifestyle`:** Ropa, accesorios de vestir, joyería y artículos infantiles.
*   **`home`:** Muebles, electrodomésticos, materiales de construcción, papelería y patio.
*   **`welfare`:** Artículos deportivos, salud y productos medicinales.

###  Almacenamiento e Integridad del Output
El conjunto de datos procesado se exporta de manera limpia en la ruta física `data/final/user_clustering_dataset.csv`.
*   Se remueven índices numéricos artificiales (`index=False`) para optimizar el almacenamiento.
*   Se aplica codificación con máscara de bits de firma `utf-8-sig` para blindar la lectura correcta del archivo ante caracteres especiales en cualquier sistema operativo (Windows/Linux/macOS).

## Interacciones Usuario-Producto y Decaimiento Temporal

construcción de la matriz dispersa de preferencias (`interacciones`). A diferencia del perfil de usuario global, este script calcula la fuerza del vínculo para cada par único **Usuario-Artículo**, introduciendo una función de penalización por tiempo para modelar la pérdida de interés o el olvido del usuario.

A continuación la justificación de Algoritmos

#### 1. Consolidación del Historial Cruzado (`score` acumulado)
*   **Mecanismo:** El método `.groupby(['user_id', 'product_id'])` colapsa todas las filas repetidas de un usuario interactuando con un mismo artículo. Sumar los pesos implícitos creados anteriormente (`view=1`, `cart=2`, `purchase=3`) genera un valor de utilidad continuo. Un usuario con un `score` alto refleja un ciclo de vida completo de conversión o una insistencia exploratoria sobre ese ítem.

#### 2. Modelado del Olvido Mediante Decaimiento Exponencial (`score_temporal`)
*   **Problema que resuelve:** En el comercio electrónico, los intereses de los usuarios son altamente volátiles. Un producto comprado o visto hace 90 días no tiene la misma relevancia para el usuario que uno interactuado hace 24 horas. 

#### Mapeo de Variables para Modelos de Producción

El reporte de columnas en consola confirma que los conjuntos de datos están listos para sus respectivas arquitecturas de modelado:

1.  **Pipeline de Segmentación (Clustering):**
    *   **Identificador:** `user_id` (Se excluirá del entrenamiento y actuará como llave de mapeo).
    *   **Features:** Desde `total_events` hasta `proportion_welfare`. Al ser variables continuas y de proporciones (0.0 a 1.0), se encuentran en el formato matemático ideal para pasar a la fase de escalamiento y cálculo de distancias euclidianas.
2.  **Pipeline de Recomendación (Filtrado Colaborativo / Híbrido):**
    *   **Llaves de Intersección:** `user_id` y `product_id` (Coordenadas de la matriz dispersa).
    *   **Características de Apoyo:** `n_interacciones` y `dias_desde_interaccion`.
    *   **Variable Objetivo (Target):** `score_temporal`. Esta columna condensa el comportamiento histórico y el decaimiento por tiempo, sirviendo como la variable continua de preferencia para el entrenamiento de los algoritmos de recomendación.

##  Conclusiones del Feature Engineering

### 1. Superación del Sesgo de Navegación (Feedback Implícito)
* **Resolución del desbalance:** El diseño del sistema de puntuación incremental (`view`: 1, `cart`: 2, `purchase`: 3) neutraliza el dominio del 89% de vistas del dataset.
* **Priorización de conversión:** Multiplicar por tres el peso de la compra obliga a los algoritmos a recomendar productos con intención real de pago, no solo por curiosidad.

### 2. Preparación Óptima para Modelos de Machine Learning
* **Dataset de Segmentación:** Las 21 variables continuas de `user_df` están normalizadas vectorialmente, previniendo sesgos por usuarios hiperactivos antes del cálculo de distancias euclidianas.
* **Reducción de ruido:** Agrupar las 14 macrocategorías en 4 familias temáticas condensa la señal de afinidad, eliminando el problema de dispersión (*sparsity*) detectado en el EDA.

### 3. Modelado de Interés Dinámico y Volatilidad
* **Introducción de Time Decay:** La aplicación de la función exponencial con $\lambda = 0.01$ evita que el comportamiento histórico estático ensucie las recomendaciones actuales.
* **Reflejo del olvido:** Al reducir a la mitad el valor de los impactos a los 70 días, el target final (`score_temporal`) prioriza de forma natural las tendencias y necesidades del momento actual.

### 4. Robustez del Pipeline de Datos
* **Idempotencia garantizada:** Los bloques de control condicional previenen fallos lógicos por ejecuciones fuera de orden en entornos de producción o desarrollo.
* **Integridad transplataforma:** La exportación final con máscara `utf-8-sig` y eliminación de índices artificiales asegura compatibilidad absoluta entre sistemas Windows, Linux y macOS.
---
# 7. 📊 K-Means para Segmentación de Usuarios

### Descripción general
Una vez transformado el dataset original de eventos a un dataset user-centered, se procedió a realizar un proceso de segmentación de usuarios mediante modelos probabilísticos de clustering. Para ello se utilizó K-Means, y en paralelo con Gaussian Mixture Model (GMM), (también conocido como Normal Mixture Model (NMM)), con el objetivo de identificar grupos de usuarios con patrones de comportamiento similares dentro del e-commerce, mediante la inercia mirando qué tan compactos son los grupos generados.

### Objetivo del modelo
El objetivo principal del modelo fue:
* identificar segmentos naturales de usuarios
* detectar patrones de navegación y compra
* enriquecer el entendimiento comportamental de los usuarios
* generar una base analítica para futuros sistemas de recomendación

El clustering no busca predecir una variable objetivo, sino descubrir estructuras ocultas dentro de los datos.

### Dataset utilizado
El modelo fue entrenado sobre el dataset user-centered construido previamente a partir de eventos de e-commerce, usando las variables descritas anteriormente.

### Preprocesamiento
Antes del entrenamiento del modelo se realizó un proceso de normalización de variables mediante: `StandardScaler()`

Esto fue necesario porque las variables tenían escalas muy distintas. Por ejemplo:
* `total_events` puede tomar valores muy altos
* las proporciones toman valores entre 0 y 1
* `recency_days` maneja otra escala temporal

La estandarización permitió que todas las variables contribuyeran de manera equilibrada al modelo.

### Selección del número de clusters
Para determinar el número óptimo de cluster (k) se evaluó el Método del Codo, donde se probaron valores de: k = 1 hasta k = 10

El análisis mostró que:

![CODO](https://i.postimg.cc/pT5T2Y7z/codo.png)

* una disminución pronunciada de la inercia entre K=2 y K=4, lo que indica una mejora significativa en la compactación de los clusters.
* A partir de K=4, la reducción de la inercia continúa, pero de manera mucho más gradual, evidenciando rendimientos decrecientes.

Tras este resultado, para validar la calidad de la segmentación obtenida mediante K-Means, se utilizó el Silhouette Score, con una muestra de 10.000 permitiendo evaluar qué tan bien están definidos los clusters.

![SILUETA](https://i.postimg.cc/8cHVD71y/silueta.png)

En la imagen se evidencia que K = 2 presenta un valor extremadamente alto (0.9741)
* Indica una separación casi perfecta entre dos grupos
* Y que a partir de K ≥ 3, los valores caen drásticamente (~0.30 - 0.35),
* Lo que sugiere que los clusters comienzan a solaparse y pierden definición

Por lo que finalmente se seleccionó: k = 2 como número final de clusters para el modelo.

### Justificación de k = 2
La elección de k = 2 respondió tanto a criterios cuantitativos como interpretativos.

Desde el punto de vista analítico:
* se priorizó la calidad estructural del modelo, optando por el valor de K que garantiza clusters más definidos y confiables
* Reduce el riesgo de sobresegmentación
* Facilita la interpretación inicial de los resultado

### Entrenamiento del modelo final de clustering
El modelo K-Means fue entrenado utilizando el número óptimo de clusters derivado del análisis de silueta K=2, permitiendo segmentar el dataset en grupos homogéneos.
* **Cluster 0:** 28.5% de los clientes
* **Cluster 1:** 71.5% de los clientes

Indica que la mayoría de los usuarios se concentran en un solo grupo, mientras que existe un segmento más pequeño con características diferenciadas.

### Características principales por cluster

#### Cluster 0 – Usuarios de bajo valor / baja interacción
Este cluster agrupa usuarios con bajo nivel de engagement, menor frecuencia de compra y menor valor económico. Además, su mayor recencia sugiere que son clientes menos activos o potencialmente inactivos.

#### Cluster 1 – Usuarios de alto valor / alta interacción
Este cluster corresponde a usuarios con alto nivel de engagement, mayor frecuencia de interacción y mayor valor económico.

### PCA y visualización de clusters
Después de entrenar el modelo K-Means con k = 2, se utilizó PCA como técnica de reducción de dimensionalidad para visualizar los resultados del clustering en dos dimensiones. El PCA se utilizó con fines de visualización e interpretación gráfica.

## Resultados de la Segmentación de Clientes (PCA + Clustering)
Se aplicó un Análisis de Componentes Principales (PCA) para reducir la dimensionalidad de los datos de comportamiento de clientes en el E-commerce de Electrónica, permitiendo la visualización de dos segmentos mediante algoritmos de clustering, mediante una muestra de 10.000 usuarios lo cual permite observar de forma exploratoria:

![PCA](https://i.postimg.cc/5tCdy74V/PCA.png)

* **Cluster 0 (Rosa):** Grupo concentrado en valores bajos/negativos de PC2. Muestra un comportamiento homogéneo en la base principal con una extensión de clientes dispersos hacia la derecha.
* **Cluster 1 (Verde):** Grupo ubicado en valores positivos de PC2. Presenta mayor dispersión vertical y concentra la mayoría de los casos atípicos del análisis.

El Biplot revelar qué categorías de productos definen la posición y separación de cada cluster:

![BiplotPCA](https://i.postimg.cc/kGZv2cX9/Biplot-PCA.png)

* **Proporción Tech (`proportion_tech`):** El vector apunta directamente hacia arriba en el eje vertical (PC2 positivo). Es la variable clave que define la parte superior del gráfico.
* **Proporción Hogar (`proportion_home`):** El vector apunta directamente hacia abajo en el eje vertical (PC2 negativo). Es la fuerza que arrastra los datos hacia la parte inferior.
* **Moda y Estilo de Vida (`proportion_fashion_lifestyle`):** Se orienta de forma horizontal y sutilmente hacia abajo, alineándose más con el comportamiento general de dispersión.

#### Definición y Significado de los Clusters obtenidos
* **Cluster 1 (Verde) = Clientes Tecnológicos:** Su posición en la parte superior (PC2 positivo) está fuertemente determinada por una alta proporción de compras en la categoría **Tech**. Los clientes atípicos más altos son compradores extremos de tecnología.
* **Cluster 0 (Rosa) = Clientes de Hogar y Estilo de Vida:** Su concentración en la parte baja (PC2 negativo) está dictada por su afinidad hacia las categorías **Home** y **Fashion/Lifestyle**.

### Conclusión del K-Means

La segmentación demuestra que el comportamiento de los usuarios en el e-commerce no es homogéneo, sino que se divide principalmente en usuarios de alto valor orientados a tecnología y usuarios de bajo valor enfocados en categorías más generales. Esta diferenciación permite diseñar estrategias altamente personalizadas, optimizar la conversión y construir una base sólida para futuros modelos de recomendación y crecimiento del negocio.

---
# 8. 📊 Gaussian Mixture Model (GMM) para Segmentación de Usuarios

### Descripción general
Una vez transformado el dataset original de eventos a un dataset user-centered, se procedió a realizar un proceso de segmentación de usuarios mediante modelos probabilísticos de clustering. Para ello y en paralelo con K-Means, se utilizó un Gaussian Mixture Model (GMM), (también conocido como Normal Mixture Model (NMM)), con el objetivo de identificar grupos latentes de usuarios con patrones de comportamiento similares dentro del e-commerce. A diferencia de métodos como K-Means, los GMM permiten modelar clusters con formas más flexibles y asignar probabilidades de pertenencia a cada usuario, en lugar de realizar asignaciones completamente rígidas.

### Objetivo del modelo
El objetivo principal del modelo fue:
* identificar segmentos naturales de usuarios
* detectar patrones de navegación y compra
* enriquecer el entendimiento comportamental de los usuarios
* generar una base analítica para futuros sistemas de recomendación

El clustering no busca predecir una variable objetivo, sino descubrir estructuras ocultas dentro de los datos.

### Dataset utilizado
El modelo fue entrenado sobre el dataset user-centered construido previamente a partir de eventos de e-commerce, usando las variables descritas anteriormente.

### Preprocesamiento
Antes del entrenamiento del modelo se realizó un proceso de normalización de variables mediante: `StandardScaler()`

Esto fue necesario porque las variables tenían escalas muy distintas. Por ejemplo:
* `total_events` puede tomar valores muy altos
* las proporciones toman valores entre 0 y 1
* `recency_days` maneja otra escala temporal

La estandarización permitió que todas las variables contribuyeran de manera equilibrada al modelo.

### Selección del número de clusters
Para determinar el número óptimo de componentes (k) se evaluaron distintos modelos Gaussian Mixture utilizando:
* AIC (Akaike Information Criterion)
* BIC (Bayesian Information Criterion)

Se probaron valores de: k = 1 hasta k = 10

El análisis mostró que:
* el comportamiento de AIC y BIC comenzaba a estabilizarse a partir de valores bajos de k
* valores altos aumentaban complejidad sin aportar separación significativamente interpretable

Finalmente se seleccionó: k = 2 como número final de clusters para el modelo.

### Justificación de k = 2
La elección de k = 2 respondió tanto a criterios cuantitativos como interpretativos.

Desde el punto de vista analítico:
* el modelo mostró estabilidad y mostró un codo marcado (luego de una caída despues de k=1, dejó de bajar considerablemente)
* evitó sobresegmentación
* tuvo un pico en el índice de silueta con un valor que indicaba segmentación moderada

Desde el punto de vista de negocio y comportamiento: los clusters obtenidos representaban dos perfiles claramente distintos de usuarios.

![AIC](https://i.postimg.cc/MZdWhLX4/AIC.png)

![BIC](https://i.postimg.cc/fT1hsQs8/BIC.png)

![BIC-GMM](https://i.postimg.cc/SKDTyc8F/SILUETA-GMM.png)

### Entrenamiento del modelo
El modelo fue entrenado utilizando: `GaussianMixture()` con dos componentes gaussianos.

El modelo estima:
* medias
* covarianzas
* probabilidades de pertenencia para cada cluster.

Posteriormente, cada usuario fue asignado al cluster con mayor probabilidad.

### PCA y visualización de clusters
Después de entrenar el Gaussian Mixture Model con `k = 2`, se utilizó PCA como técnica de reducción de dimensionalidad para visualizar los resultados del clustering en dos dimensiones. Es importante aclarar que el PCA no reemplaza las variables originales utilizadas para entrenar el modelo. El GMM fue entrenado con el conjunto completo de variables estandarizadas. El PCA se utilizó únicamente con fines de visualización e interpretación gráfica.

Con las dos primeras componentes principales se construyó una visualización 2D, coloreando cada usuario según el cluster asignado por el modelo GMM. Esta visualización permitió observar de forma exploratoria:
* la distribución general de los usuarios
* la separación aproximada entre los dos clusters
* posibles zonas de solapamiento
* usuarios con comportamientos intermedios
* posibles outliers o usuarios con actividad atípica

![VISUAL](https://i.postimg.cc/3JTcFr36/Visual-GMM.png)

La gráfica PCA mostró que los usuarios podían representarse en dos grandes grupos, consistentes con la decisión de utilizar `k = 2`. Sin embargo, al tratarse de una proyección bidimensional, la visualización debe interpretarse con precaución. La separación observada en el plano PCA no necesariamente representa toda la estructura aprendida por el GMM en el espacio completo de variables.

In teoría:
* el GMM asignó clusters usando todas las variables estandarizadas
* el PCA solo permitió visualizar una versión resumida de esa estructura
* algunas diferencias entre usuarios pueden no ser completamente visibles en dos dimensiones

### Interpretación general de los clusters

#### Cluster 0
Corresponde a usuarios con:
* menor actividad general
* menor profundidad dentro del funnel
* menor intensidad de interacción
* menor volumen de eventos
* comportamiento más exploratorio o esporádico

En muchos casos representan:
* usuarios ocasionales
* usuarios con baja conversión
* usuarios de navegación ligera

#### Cluster 1
Corresponde a usuarios con:
* mayor actividad
* mayor interacción con productos
* mayor número de compras
* mayor profundidad en el funnel
* comportamiento más consistente y recurrente

Este cluster representa usuarios más comprometidos con la plataforma.

### Ventajas del uso de Gaussian Mixture Models
A diferencia de K-Means, los GMM ofrecen:
* **Clusters más flexibles:** Los clusters no necesitan ser esféricos ni tener el mismo tamaño.
* **Modelado probabilístico:** Cada usuario tiene probabilidades de pertenencia a cada cluster. Esto permite representar incertidumbre y perfiles híbridos.
* **Mayor capacidad de representación:** El modelo puede adaptarse mejor a distribuciones complejas y comportamientos heterogéneos.

### Aplicaciones posteriores
Los clusters obtenidos pueden utilizarse para:
* personalización de estrategias de marketing
* segmentación de usuarios
* análisis de comportamiento
* sistemas de recomendación híbridos
* campañas diferenciadas
* detección de usuarios de alto valor

### Conclusión del Gaussian Mixture Model (GMM)
El Gaussian Mixture Model permitió transformar variables agregadas de comportamiento en segmentos interpretables de usuarios. El resultado final constituye una base sólida para análisis avanzados de usuarios y un complemento o refuerzo para el sistema de recomendaciones personalizadas.

---
# 9. 📊 Sistema Híbrido de Recomendación con ALS, Clustering y Re-ranking Taxonómico

## Descripción general

Este módulo implementa un sistema híbrido de recomendación para e-commerce basado en múltiples estrategias complementarias:

- Collaborative Filtering mediante ALS (Alternating Least Squares)
- Cold-start basado en clustering
- Segmentación conductual mediante GMM (Gaussian Mixture Models o Normal Mixture Models)
- Re-ranking semántico basado en clasificación jerárquica de productos

El objetivo principal del sistema es resolver distintos escenarios de recomendación dependiendo de la cantidad de información disponible sobre el usuario. Para ello, el flujo divide los usuarios en distintos ***tiers*** según su nivel de interacción histórica.

El sistema se encuentra implementado en el archivo:

```python
modelo_recomendaciones.ipynb
```
## Arquitectura general del sistema

El flujo completo del sistema puede resumirse así:

```text
Usuario entra al sistema
│
├── Usuario desconocido
│   └── Cold Start (Tier 0)
│
└── Usuario conocido
    │
    ├── Tier 1 (1–5 interacciones)
    │   └── Híbrido:
    │       (ALS + semantic reranking ) + clustering
    │
    └── Tier 2 (>5 interacciones)
        └── ALS + semantic reranking
```
### Objetivo general del enfoque híbrido

El sistema parte de una premisa importante:

> Los modelos colaborativos funcionan mejor con suficiente historial.

Modelos como ALS aprenden relaciones entre usuarios y productos a partir de patrones de co-consumo. Sin embargo, cuando un usuario tiene pocas interacciones:

- la matriz usuario-producto se vuelve extremadamente dispersa,
- aparecen problemas de cold start parcial,
- disminuye la calidad del collaborative filtering.

Para mitigar esto, el sistema incorpora:

1. Recomendaciones basadas en clustering.
2. Información semántica derivada de taxonomía de productos.

### Importaciones y configuración base

El sistema utiliza:

- `pickle` para cargar modelos serializados.
- `numpy` y `pandas` para manipulación de datos.
- `Path` para manejo de rutas relativas.

La variable `BASE_DIR` permite construir rutas relativas hacia modelos, datasets y archivos auxiliares.

## Construcción de perfiles por clasificación de productos

### Objetivo

Construir perfiles semánticos de usuario basados en las categorías jerárquicas de los productos con los que interactúa.

---

### Función `_build_taxonomy_profile()`

Esta función genera preferencias taxonómicas para cada usuario y nivel jerárquico de categorías.

---

### Lógica utilizada

Cada interacción recibe un peso según su importancia:

- `view = 1`
- `cart = 2`
- `purchase = 3`

La lógica detrás de esto es asumir que:

- una compra representa una afinidad más fuerte,
- agregar al carrito representa intención intermedia,
- visualizar representa interés leve.

---

### Construcción de preferencias

Para cada usuario y categoría:

1. Se suman los pesos de interacción.
2. Se calcula el peso total del usuario.
3. Se normaliza cada categoría respecto al total.

Esto genera la tabla de `taxonomy_preference`, que representa qué porcentaje de las interacciones del usuario pertenecen a una categoría específica.

---

### Niveles de clasificación de productos

El sistema utiliza tres niveles jerárquicos:

| Nivel | Descripción |
|---|---|
| nivel1 | Categoría amplia |
| nivel2_norm | Categoría intermedia |
| nivel3_norm | Categoría específica |

Estas categorías se extraen desde `category_code` mediante separación por `"."`.

## Carga de modelos y datos auxiliares

La función `_load()` centraliza toda la carga de recursos del sistema.

---

### Modelos cargados

### ALS model

```python
als_model.pkl
```

Modelo colaborativo principal basado en ALS.

---

### User profile ALS

```python
user_profile_als.pkl
```

Contiene metadatos de usuario: tier, cluster, índice ALS e historial.

---

### ID maps

```python
id_maps_als.pkl
```

Mapeos entre índices internos y IDs reales.

---

### Cold-start recommendations

```python
recomendaciones_cold_start.csv
```

Lista de productos frecuentes por cluster para usuarios nuevos.

---

### GMM clustering

```python
user_clustering_gmm_results.csv
```

Segmentación conductual de usuarios activo/pasivo, basado en un modelo de clustering por GMM que resulto en separación de grupos mediado por features relacionadas con intensidad de interacciones.

---

## Construcción de clasificación jerárquica de productos

El sistema construye `product_taxonomy` que funciona como:

```text
product_id → categorías
```

Esto permite conectar recomendaciones con semántica de producto.

*   Helpers ALS: El sistema implementa varias funciones auxiliares para interactuar con ALS.

*   _user_vec(): Obtiene el embedding del usuario.

*   _item_matrix(): Obtiene la matriz de embeddings de productos.

*   _score_items(): Calcula el score ALS mediante `item_matrix @ user_vector` produciendo afinidad usuario-producto.

## RE-RANKING SEMÁNTICO

## Objetivo

Aplicar una capa semántica (de clasificación de productos) sobre los candidatos generados por ALS.

## Función `_semantic_rerank()`

Esta función recibe:

| Columna | Descripción |
|---|---|
| user_id | Usuario |
| product_id | Producto |
| score | Score ALS |

### Paso 1 — Normalización del score ALS

El score ALS puede variar entre usuarios. Por ello, primero se normaliza entre 0 y 1.

Esto genera `score_norm`.

### Paso 2 — Agregar taxonomía

Cada producto recomendado recibe:

- `nivel1`
- `nivel2_norm`
- `nivel3_norm`

### Paso 3 — Agregar preferencias del usuario

El sistema consulta el perfil taxonómico del usuario y obtiene:

- `pref_nivel1`
- `pref_nivel2`
- `pref_nivel3`

### Paso 4 — Construcción del score taxonómico

El score taxonómico se calcula mediante:

```text
(0.2 * nivel1) + (0.3 * nivel2) + (0.5 * nivel3)
```

Los pesos fueron obtenidos experimentalmente mediante Grid Search (ver notebook `Evaluacion_reranking_semantico.ipynb`).

### Paso 5 — Score híbrido final

El score final combina:

| Componente | Peso |
|---|---|
| ALS | 0.4 |
| Taxonomía | 0.6 |

Estos pesos también fueron obtenidos experimentalmente de manera que optimizaran las métricas de desempeño del modelo (ver notebook `Evaluacion_reranking_semantico.ipynb`).

### Paso 6 — Re-ranking final

Los productos son ordenados por `score_final` y `score_norm`.

## Tier 0. Usuarios nuevos

## Objetivo

Resolver cold start total.

*  Función `_recomendar_nuevo_usuario()`: Si el usuario no existe en `_user_profile` el sistema recomienda productos populares del cluster dominante.
*  Recomendación por cluster: La función `_recomendar_por_cluster()` permite obtener recomendaciones específicas por cluster.
*  Función principal `recomendar()`: Esta función controla toda la lógica de decisión del sistema.

## Tier 1. Usuarios con 1–5 interacciones

## Objetivo

Combinar ALS, re-ranking semántico (por clasificación de productos) y clustering.

### Paso 1 — Clasificación GMM

El usuario es clasificado como activo o pasivo (los dos clusters resultantes del modelo GMM).

### Paso 2 — Generación ALS

El sistema genera el top100 candidatos ALS.

El uso de 100 candidatos permite que la capa taxonómica tenga margen para modificar el ranking.

### Paso 3 — Semantic reranking

```python
als_df = _semantic_rerank(als_df, user_id)
```
### Paso 4 — Mezcla ALS + cluster

### Usuarios activos

- 70% ALS
- 30% cluster

### Usuarios pasivos

- 30% ALS
- 70% cluster

### Paso 5 — Combinación final

Las recomendaciones ALS re-rankeadas y cluster se concatenan.

## Tier 2. Usuarios con suficiente historial

### Objetivo

Aplicar ALS completo + semantic reranking.

### Flujo:  
```text 
ALS → top100 → semantic reranking → top final  
```
## Interfaz API

`get_top_n_recommendations()`: Convierte recomendaciones a formato serializable.

## Onboarding

`get_onboarding_products()`:

*  Selecciona productos representativos por cluster para onboarding.

*  El sistema intenta evitar productos repetidos y categorías repetidas.

## Funciones auxiliares finales

`recomendar_por_cluster()`: Obtiene recomendaciones específicas de cluster.

`is_known_user()`: Verifica si un usuario existe en el sistema.

## Conclusión del Sistema Híbrido de Recomendación

El sistema híbrido implementado combina collaborative filtering, dos tipos de clustering, y reranking semántico para construir un sistema de recomendación más robusto frente a escenarios de sparse data y cold start parcial.

Los resultados experimentales demostraron que la incorporación de información de clasificación del producto mejora el desempeño del sistema sin reemplazar el modelo colaborativo principal.

---
# 10. 📊 Evaluación Experimental del Re-ranking Semántico

## Descripción general

Este notebook (`Evaluacion_reranking_semantico.ipynb`) implementa el proceso experimental completo para evaluar una capa de semantic re-ranking aplicada sobre un sistema de recomendación basado en ALS (Alternating Least Squares).

El objetivo principal del experimento fue determinar si la incorporación de información de clasificación de productos podía mejorar el desempeño del sistema de recomendación.

La evaluación se realizó utilizando las métricas estándar de sistemas de recomendación, `Precision@10` y `Recall@10`, comparando ALS puro y ALS + re-ranking semántico.

## Hipótesis del experimento

La hipótesis principal fue:

> Los modelos colaborativos como ALS presentan limitaciones. Incorporar afinidad categórica basada en categorías de producto puede ayudar a rescatar coherencia semántica y mejorar las recomendaciones.

## Motivación conceptual

Los modelos colaborativos tradicionales aprenden patrones de co-consumo entre usuarios y productos. Sin embargo, usuarios con pocas interacciones generan señales débiles, y consecuentemente muchos productos nunca coinciden explícitamente en patrones colaborativos.

La idea del re-ranking taxonómico fue incorporar información estructural sobre los productos mediante una jerarquía de categorías:

```text
nivel1 → categoría amplia
nivel2 → categoría intermedia
nivel3 → categoría específica
```

## Objetivo del notebook

El notebook tiene dos objetivos principales. Luego de construir perfiles de clasificación de productos por usuario y de aplicar un re-ranking semántico, se pretende:

1. Evaluar experimentalmente el impacto en `Precision@10` y `Recall@10`, comparándolo con las recomendaciones de ALS sin re-ranking semántico.
2. Optimizar pesos mediante grid search.

## Estructura general del pipeline

El flujo experimental implementado fue:

```text
Train/Test split temporal
↓
Entrenamiento ALS
↓
Generación top100 candidatos
↓
Construcción perfiles taxonómicos
↓
Semantic re-ranking
↓
Top10 final
↓
Evaluación Precision@10 / Recall@10
```

## 1. Split temporal Train/Test

### Objetivo

Evitar data leakage y garantizar evaluación realista.

### Estrategia utilizada

El dataset se dividió temporalmente:

| Dataset | Condición |
|---|---|
| Train | eventos antes del cutoff |
| Test | eventos después del cutoff |

Esto asegura que:

- ALS solo aprenda del pasado,
- los perfiles de clasificación de productos se construyan solo con train,
- el test represente interacciones futuras reales.

### Ground truth

El conjunto de test se utilizó como un “ground truth” temporal para evaluar si los productos recomendados coincidían con productos realmente consumidos posteriormente por el usuario.

## 2. Construcción de interacciones ponderadas

### Objetivo

Asignar distinta importancia a distintos tipos de interacción.

## Pesos utilizados

| Evento | Peso |
|---|---|
| view | 1 |
| cart | 2 |
| purchase | 3 |

La lógica detrás de esta ponderación es asumir que una compra representa una afinidad más fuerte que una simple visualización.

### Resultado

Se construyó una matriz usuario-producto ponderada utilizada posteriormente para entrenar ALS.

## 3. Entrenamiento ALS

### Objetivo

Construir el recomendador colaborativo base.

### Modelo utilizado

### Alternating Least Squares (ALS)

ALS fue seleccionado tras compararse contra SVD debido a mejores métricas sobre el dataset.

### Rol de ALS

ALS actúa como generador inicial de candidatos. No produce directamente las recomendaciones finales del experimento, sino el top100 candidatos que posteriormente son refinados por la capa de clasificación de productos.

## 4. Construcción de perfiles taxonómicos

### Objetivo

Construir preferencias semánticas de usuario basadas en categorías de producto.

### Niveles taxonómicos

El sistema utilizó tres niveles:

| Nivel | Descripción |
|---|---|
| nivel1 | Categoría amplia |
| nivel2_norm | Categoría intermedia |
| nivel3_norm | Categoría específica |

### Construcción del perfil

Para cada usuario:

1. Se sumaron pesos de interacción por categoría.
2. Se calculó el total de interacción del usuario.
3. Se normalizó cada categoría respecto al total.

Esto produjo la tabla (`dataframe`) `taxonomy_preference`, representando afinidad relativa hacia cada categoría.

Los perfiles taxonómicos fueron construidos solo usando TRAIN y nunca utilizando interacciones futuras del test. Esto garantiza una evaluación válida y libre de data leakage.

## 5. Construcción del score taxonómico

### Objetivo

Asignar un score semántico a cada recomendación ALS.

### Proceso

Cada producto recomendado fue conectado con:

- `nivel1`
- `nivel2_norm`
- `nivel3_norm`

Posteriormente, se consultó el perfil taxonómico del usuario para obtener:

- afinidad hacia `nivel1`,
- afinidad hacia `nivel2`,
- afinidad hacia `nivel3`.

### Score taxonómico

El score taxonómico (de clasificación de productos) se calculó como:

```text
taxonomic_score =
W1 * nivel1 +
W2 * nivel2 +
W3 * nivel3
```

## 6. Score híbrido final

### Objetivo

Combinar señal colaborativa y señal semántica.

### Fórmula

```text
score_final = (alpha * ALS) + (beta * clasificación)
```
### Normalización ALS

El score ALS fue normalizado entre 0 y 1 por usuario antes de combinarlo con la señal taxonómica.

Esto permitió que ambas señales operaran sobre la misma escala.

## 7. Re-ranking final

### Objetivo

Reordenar candidatos ALS utilizando el score híbrido.

### Flujo final

```text
ALS top100
↓
score taxonómico
↓
score híbrido
↓
re-ranking
↓
top10 final
```

### ¿Por qué top100?

Inicialmente se consideró usar ALS top10. Sin embargo, esto no permite que la taxonomía modifique realmente el conjunto final de recomendaciones.

Usando ALS top100, la capa taxonómica puede rescatar productos inicialmente ubicados fuera del top10.

## 8. Evaluación experimental

### Métricas utilizadas

*  ### Precision@10

Mide qué proporción de los 10 productos recomendados fueron realmente relevantes.

*  ### Recall@10

Mide qué proporción de todos los productos relevantes del usuario fueron recuperados dentro del top10.

## Resultados iniciales

La incorporación de la clasificación de los productos produjo mejoras simultáneas en ambas métricas:

- aumento de `Precision@10`,
- aumento de `Recall@10`.

Esto fue particularmente importante porque normalmente mejorar una métrica suele degradar la otra.

## 9. Grid Search — pesos ALS vs Clasificación

### Objetivo

Determinar cuánto peso asignar a:

- ALS,
- taxonomía.

### Hallazgo principal

El sistema híbrido superó al ALS puro. El mejor punto encontrado fue:

| Componente | Peso |
|---|---|
| ALS | 0.4 |
| Taxonomía | 0.6 |

Esto indica que la taxonomía aporta señal muy fuerte, pero ALS sigue aportando refinamiento colaborativo útil.

## 10. Grid Search — pesos internos taxonomía

### Objetivo

Determinar qué nivel taxonómico aporta más información.

### Hallazgo principal

El mejor desempeño se obtuvo con:

| Nivel | Peso |
|---|---|
| nivel1 | 0.2 |
| nivel2 | 0.3 |
| nivel3 | 0.5 |

Inicialmente se esperaba que los niveles más específicos fueran demasiado dispersos. Sin embargo, el experimento mostró que el nivel3 aportó la señal más informativa.

Esto sugiere que los usuarios mantienen preferencias muy específicas y consistentes dentro del catálogo.

## 11. Evaluación por tipo de usuario

### Objetivo

Determinar en qué tipo de usuario la taxonomía aporta más valor.

### Segmentación

Los usuarios fueron separados en:

| Tipo | Definición |
|---|---|
| Sparse | ≤5 interacciones |
| Activos | >5 interacciones |

### Hallazgo principal

La capa de clasificación de productos mejoró ambos grupos, pero mejoró más a los usuarios sparse.

### Interpretación conceptual

Esto valida directamente la hipótesis principal del proyecto:

> La información taxonómica compensa parcialmente las limitaciones del collaborative filtering en escenarios de baja interacción.

## Conclusión de la Evaluación Experimental del Re-ranking Semántico

El experimento validó que la clasificación jerárquica aporta una señal útil a la hora de predecir y generar recomendaciones, siendo este complementario con el modelo ALS, y que las mejoras son especialmente relevantes en usuarios sparse.

El notebook demuestra experimentalmente que incorporar estructura semántica mediante taxonomía de productos puede mejorar significativamente sistemas de recomendación colaborativos en escenarios reales de e-commerce.

---
# 11. 🌐 API REST — Arquitectura y Endpoints

Click & Tech es una plataforma de e-commerce con recomendaciones personalizadas basadas en machine learning. El proyecto combina dos componentes principales: una API REST construida con FastAPI que funciona como el motor de recomendaciones y gestión de datos, y un frontend desarrollado con Streamlit que proporciona la interfaz visual interactiva para los clientes. El objetivo central es predecir y sugerir productos relevantes a cada usuario basándose en su historial de navegación, compras e intereses.

## Arquitectura y Propósito de los Componentes

El proyecto está dividido en dos partes fundamentales que trabajan juntas pero de manera independiente. La API REST actúa como el corazón computacional del sistema, permitiendo que la lógica de recomendación sea reutilizable por múltiples clientes y fácilmente escalable en entornos de producción. Esta separación arquitectónica permite que otros sistemas o aplicaciones móviles puedan consumir el mismo motor de recomendaciones sin necesidad de reimplementar la lógica. La API es stateless, puede ser containerizada con Docker y desplegada en servidores cloud sin complicaciones, proporcionando una solución enterprise-grade.

```
ARQUITECTURA DE COMPONENTES

┌──────────────────────────────────────────────────────────────┐
│                   FRONTEND (Streamlit)                       │
│   - Interfaz visual interactiva                              │
│   - Gestión de sesiones de usuario                           │
│   - Carrito de compras                                       │
│   - Registro de eventos locales                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ HTTP Requests
                       │ (GET /recommend/{user_id})
                       │ (GET /onboarding/products)
                       │ (POST /records)
                       │ (GET /products)
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                  API REST (FastAPI)                          │
│   - Lógica de recomendación                                  │
│   - Gestión de datos                                         │
│   - Endpoints públicos                                       │
│   - Caché de productos                                       │
└──────────────────────┬───────────────────────────────────────┘
                       │
                ┌──────┴──────┐
                │             │
                ▼             ▼
        ┌──────────────┐  ┌──────────────┐
        │ SVD Model    │  │ K-Means      │
        │ (usuarios    │  │ (nuevos      │
        │ conocidos)   │  │  usuarios)   │
        └──────────────┘  └──────────────┘
                │             │
                └──────┬──────┘
                       │
                ┌──────┴──────┐
                │             │
                ▼             ▼
        ┌──────────────┐  ┌──────────────┐
        │ Product Data │  │ User Events  │
        └──────────────┘  └──────────────┘
```

Streamlit, por su parte, es una herramienta diseñada especialmente para crear interfaces web sin necesidad de conocimientos profundos en desarrollo frontend. Proporciona una experiencia de usuario amigable donde usuarios no técnicos pueden interactuar completamente con el sistema. Los cambios en el código se reflejan inmediatamente en la interfaz sin necesidad de recargar, lo que hace que sea ideal para prototipado rápido y demostración del sistema. Streamlit se conecta directamente a la API mediante HTTP requests, consumiendo sus endpoints para obtener recomendaciones, catálogo de productos y guardando eventos de usuario.

La decisión de usar ambas tecnologías juntas responde a un principio de arquitectura de software: separación de responsabilidades. El backend (API) se enfoca exclusivamente en lógica de negocio y cálculos complejos, mientras que el frontend (Streamlit) se encarga únicamente de presentación e interacción con el usuario. Esta separación también permite que el equipo de ciencia de datos pueda desarrollar y mejorar los modelos sin tocar el código de la interfaz de usuario.

## Funcionalidades de la API

La API REST proporciona cuatro funcionalidades principales que son el corazón del sistema de recomendación. El primer endpoint es GET /recommend/{user_id}, que retorna los productos más relevantes para un usuario conocido, utilizando un modelo de descomposición en valores singulares (SVD). Este endpoint requiere que el usuario tenga un historial previo en el sistema y considera múltiples factores como el historial de navegación, patrones de compra y similitud con otros usuarios.

```
FLUJO: GET /recommend/{user_id}

1. Cliente solicita: GET /recommend/12345
                       |
                       v
2. API recibe user_id=12345, n=20
   |
   ├─→ ¿Usuario está en la base de datos?
   |   ├─ NO → Retorna error o lista vacía
   |   └─ SÍ → Continúa
   |
   ├─→ Carga matriz de interacciones usuario-producto
   |   |
   |   ├─ Rows: usuarios
   |   ├─ Cols: productos
   |   └─ Valores: puntuación (0-5)
   |
   ├─→ Aplica modelo SVD
   |   |
   |   ├─ Descompone matriz en factores latentes
   |   ├─ Calcula similitud usuario 12345 vs resto
   |   └─ Identifica productos similares a los que compró
   |
   ├─→ Clasifica productos por puntuación
   |
   ├─→ Retorna top 20 productos
                       |
                       v
3. JSON Response con recomendaciones
   {
     "user_id": 12345,
     "known_user": true,
     "recommendations": [
       {"product_id": 101, "score": 0.95},
       {"product_id": 245, "score": 0.87},
       ...
     ]
   }
```

El segundo conjunto de endpoints está diseñado para el onboarding de nuevos usuarios. La ruta GET /onboarding/products devuelve un producto representativo de cada cluster de usuario, permitiendo que nuevos visitantes seleccionen el cluster que mejor representa sus intereses. Una vez que seleccionan su cluster, el endpoint GET /onboarding/recommend/{cluster_id} proporciona recomendaciones específicas basadas en ese grupo, permitiendo que usuarios sin historial obtengan sugerencias personalizadas desde su primer uso.

```
FLUJO: Onboarding de Nuevos Usuarios

1. Usuario nuevo accede a Streamlit
                       |
                       v
2. API: GET /onboarding/products
   |
   ├─→ Carga modelo K-Means (4 clusters)
   |
   ├─→ Por cada cluster (0, 1, 2, 3):
   |   ├─ Selecciona producto más representativo
   |   └─ Retorna su información
   |
   └─→ JSON con 4 productos (uno por cluster)
                       |
                       v
3. Streamlit muestra 4 opciones de producto al usuario
   [Cluster 0] [Cluster 1] [Cluster 2] [Cluster 3]
                       |
                       v
4. Usuario selecciona el cluster que prefiere
                       |
                       v
5. API: GET /onboarding/recommend/{cluster_id}?n=20
   |
   ├─→ user_id = cluster_id (0, 1, 2 ó 3)
   |
   ├─→ Retorna top 20 productos del cluster
   |   (productos populares entre usuarios de ese cluster)
   |
   └─→ JSON con recomendaciones personalizadas
                       |
                       v
6. Streamlit muestra dashboard con productos recomendados
```

El tercero es el catálogo de productos, accesible mediante GET /products que retorna todos los productos disponibles, y GET /products/lookup?ids=1,2,3 que permite búsquedas específicas por identificadores. Estos endpoints son fundamentales para que el frontend pueda mostrar información completa de cada producto, incluyendo precio, marca y categoría.

Finalmente, está el sistema de registro de eventos con los endpoints GET /records/{user_id} que retorna el historial de interacciones de un usuario y POST /records que guarda nuevos eventos. Los eventos pueden ser visualizaciones de producto, clicks, agregar al carrito o compras completadas. Este registro es crítico porque alimenta continuamente el modelo con datos nuevos, permitiendo que las recomendaciones mejoren con el tiempo a medida que se acumula más información sobre el comportamiento de los usuarios.

```
FLUJO: Registro de Eventos (POST /records)

Usuario en Streamlit hace acción
(view, click, add_to_cart, purchase)
                       |
                       v
Evento se construye en memoria:
{
  "event_time": "2026-05-20 14:30:45",
  "event_type": "click",
  "product_id": 245,
  "user_id": 12345,
  "price": 29.99,
  "brand": "TechBrand",
  "category_code": "electronics.telephone.accessory"
}
                       |
                       v
POST /records con evento
                       |
                       v
API recibe y valida evento
                       |
                       v
Agrega fila a events_final.csv
                       |
                       v
Retorna confirmación:
{"message": "Record saved successfully"}
```

## Descripción General

La capa de acceso al sistema de recomendación está implementada como una API REST con **FastAPI**. Se comunica directamente con el módulo `src/recommender/svd_recommender.py`, que carga los modelos entrenados (ALS, GMM) en memoria al iniciar el servidor.

## Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| Framework | FastAPI 0.136+ |
| Servidor ASGI | Uvicorn |
| Validación | Pydantic v2 |
| Motor de recomendación | ALS (implicit 0.7.3) |

## Estructura de Módulos

```
api/
├── main.py                  # Punto de entrada, configuración de la app
├── models/
│   └── record.py            # Schema EventRecord (Pydantic)
├── routes/
│   └── recommendations.py   # Definición de todos los endpoints
└── services/
    └── recommender_service.py  # Lógica de negocio: recomendar, guardar eventos
```

## Endpoints

### Sistema de recomendación

#### `GET /recommend/{user_id}`

Genera recomendaciones personalizadas para un usuario conocido.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `user_id` | int (path) | — | ID del usuario |
| `n` | int (query) | 20 | Cantidad de recomendaciones |

**Lógica interna:**
- Tier 1 (usuarios activos): ALS top-100 → semantic reranking → 70% ALS + 30% cluster
- Tier 2 (usuarios pasivos): ALS top-100 → semantic reranking → head(n)
- Score final: `0.4 × score_norm + 0.6 × taxonomic_score`

**Respuesta:**
```json
{
  "user_id": 1515915625353226922,
  "known_user": true,
  "recommendations": [
    {
      "product_id": 1005135,
      "score": 0.87,
      "method": "ALS+semantic",
      "brand": "samsung",
      "price": 299.99,
      "category": "electronics.smartphone"
    }
  ]
}
```

#### `GET /onboarding/products`

Devuelve un producto representativo por cluster para la pantalla de onboarding de nuevos usuarios. Filtra automáticamente productos de baja relevancia visual (cartuchos, tóner, papel) usando `_NIVEL3_SKIP`.

#### `GET /onboarding/recommend/{cluster_id}`

Recomendaciones para un usuario nuevo en base al cluster que eligió en el onboarding. Aplica diversificación con máximo 3 productos por `nivel3` para evitar sesgo de categoría.

#### `GET /users/{user_id}/exists`

Verifica si un usuario tiene historial en el sistema (distinción usuario conocido / usuario nuevo).

### Productos

#### `GET /products`

Catálogo completo de productos desde `data/processed/product_catalog.csv`.

#### `GET /products/lookup?ids=1,2,3`

Información básica (brand, price, category) para una lista de IDs de productos. Sin parámetro devuelve todos.

### Eventos

#### `GET /records`
#### `GET /records/{user_id}`

Consulta eventos registrados. Permite ver el historial de interacciones acumulado en `data/final/events_final.csv`.

#### `POST /records`

Registra un nuevo evento de interacción. Es el mecanismo por el cual el frontend Streamlit guarda las acciones del usuario en producción.

**Body (EventRecord):**
```json
{
  "event_time": "2026-05-20T10:00:00Z",
  "event_type": "view",
  "product_id": 1005135,
  "category_id": 2053013555631882655,
  "category_code": "electronics.smartphone",
  "brand": "samsung",
  "price": 299.99,
  "user_id": 1515915625353226922,
  "user_session": "abc-123",
  "category_inferred": false,
  "brand_inferred": false
}
```

## Ejecución

```bash
# Desde la raíz del proyecto con el entorno activado
uvicorn api.main:app --reload
```

- API disponible en: `http://localhost:8000`
- Documentación interactiva (Swagger UI): `http://localhost:8000/docs`

---

# 12. 🌐 Frontend Streamlit — Tienda Interactiva y Monitor de Salud

Streamlit implementa la interfaz visual que consume todos los servicios proporcionados por la API. El sistema maneja dos flujos de usuario completamente diferentes basados en si el usuario es nuevo o si tiene un historial previo en la plataforma. Para usuarios nuevos, el sistema detecta automáticamente que no tiene información previa y los lleva a un onboarding guiado donde se presentan productos representativos de cuatro clusters diferentes, identificados mediante K-Means. El usuario explora estas cuatro opciones y selecciona la que mejor refleja su perfil o interés, momento en el cual el sistema obtiene recomendaciones especializadas para ese cluster.

```
FLUJO DE USUARIO EN STREAMLIT

┌─────────────────────────────────────────┐
│   Usuario accede a Streamlit             │
│   (http://localhost:8501)                │
└────────────┬────────────────────────────┘
             │
             v
    ¿Ingresa User ID?
    /        |        \
   /         |         \
NO/       VACÍO      SÍ/
 /          |         \
v           v          v
│    ┌─────────────┐   │
│    │ ¿Es nuevo?  │   │
│    └─────────────┘   │
│      SÍ/    \NO      │
│      /       \       │
│     v         v      │
│    ONBOARDING    USUARIO CONOCIDO
│    │             │
│    │             ├─→ Obtiene recomendaciones
│    │             │   basadas en historial
│    │             │   (GET /recommend/{user_id})
│    │             │
│    │             └─→ Muestra grid de
│    │                 productos personalizados
│    │
│    └─→ Muestra 4 productos
│        (uno por cluster)
│        │
│        v
│    Usuario selecciona
│    cluster de interés
│    │
│    ├─→ Obtiene top 20 productos
│    │   del cluster elegido
│    │   (GET /onboarding/recommend/{cluster_id})
│    │
│    └─→ Transición a Dashboard

DASHBOARD (Ambos flujos convergen aquí)
│
├─→ Grid de productos personalizados
│   - Imagen (con variantes rotadas)
│   - Precio
│   - Marca
│   - Categoría
│   - Botón: Agregar al carrito
│
├─→ Carrito de compras
│   - Resumen de artículos
│   - Total de monto
│
├─→ Historial de eventos
│   - Tabla de interacciones
│   - Timestamps
│   - Tipos de evento
│
└─→ Todas las interacciones se registran
    y se envían a la API (POST /records)
```

Para usuarios conocidos cuyo identificador es reconocido en el sistema, la experiencia es significativamente más personalizada. El sistema inmediatamente obtiene recomendaciones basadas en el análisis completo del historial del usuario, considerando todas sus interacciones previas. La interfaz muestra un grid de productos relevantes con información detallada de cada uno, incluyendo precio, marca y categoría. Una característica ingeniosa del sistema es la rotación automática de variantes de productos: si existe cable1.jpg, cable2.jpg y así sucesivamente, el sistema alterna entre estas variantes automáticamente para mostrar diferentes perspectivas del mismo producto.

El carrito de compras integrado permite que los usuarios agreguen productos de interés y vean un resumen del total de monto. Cada interacción del usuario, ya sea una visualización de producto, un click, agregar al carrito o una compra completada, se registra como un evento que se envía a la API. Este registro continuo de eventos es fundamental para el sistema porque permite que el modelo de recomendación se mantenga actualizado y mejore continuamente a medida que aprende nuevos patrones de comportamiento. El historial de eventos se visualiza en la interfaz permitiendo que usuarios entiendan qué interacciones ha registrado el sistema.

## Proceso de Ejecución

Antes de ejecutar cualquier componente, es necesario instalar todas las dependencias del proyecto utilizando pip install -r requirements.txt. Este comando instalará FastAPI, Streamlit, scikit-learn, pandas y todas las otras librerías necesarias para que el sistema funcione correctamente.

El siguiente paso importante es ejecutar el pipeline de datos mediante python run_pipeline.py. Este script ejecuta en secuencia varios notebooks Jupyter que realizan tareas críticas del proyecto. El pipeline comienza con la limpieza de los datos originales, inferencia de categorías faltantes, y transformación de características. Luego entrena el modelo K-Means para generar clusters de usuarios y el modelo ALS para recomendaciones personalizadas. Este paso puede tomar entre 5 y 15 minutos dependiendo de la capacidad del equipo y el tamaño del dataset. Es importante ejecutar este paso solo una vez, después de lo cual los datos procesados y modelos entrenados estarán listos.

Una vez completado el pipeline, es necesario abrir dos terminales diferentes porque tanto la API como Streamlit necesitan ejecutarse en paralelo.

```
SECUENCIA DE EJECUCIÓN

TERMINAL 1 (PowerShell / CMD)
┌─────────────────────────────────┐
│ $ pip install -r requirements.txt│
│ (instala todas las librerías)    │
│                                 │
│ $ python run_pipeline.py         │
│ (entrena modelos, procesa datos) │
│ (⏱  5-15 minutos)                │
│                                 │
│ ✓ Pipeline completado           │
│                                 │
│ $ uvicorn api.main:app \         │
│   --reload \                     │
│   --host 0.0.0.0 \              │
│   --port 8000                   │
│                                 │
│ Uvicorn running on              │
│ http://127.0.0.1:8000           │
│                                 │
│ ✓ API ACTIVA                    │
└─────────────────────────────────┘
         ↓
    ESPERA A QUE
    API esté lista
         ↓
┌─────────────────────────────────┐
│ TERMINAL 2 (PowerShell / CMD)    │
│                                 │
│ $ streamlit run \               │
│   frontend_streamlit/app.py      │
│                                 │
│ Streamlit app opened in browser │
│ Local URL: http://localhost:8501│
│                                 │
│ ✓ FRONTEND ACTIVO               │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ ✓ SISTEMA COMPLETAMENTE ACTIVO  │
│                                 │
│ http://localhost:8501           │
│ (Interfaz de usuario)           │
│                                 │
│ http://localhost:8000/docs      │
│ (API documentation)             │
└─────────────────────────────────┘
```

En la primera terminal, ejecute uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 para iniciar el servidor API. Verá un mensaje indicando que Uvicorn está corriendo en http://127.0.0.1:8000. Puede verificar que la API está funcionando accediendo a http://localhost:8000 en su navegador, donde verá un mensaje de confirmación, o visitando http://localhost:8000/docs para acceder a la documentación interactiva de Swagger que permite probar todos los endpoints manualmente.

En la segunda terminal, ejecute streamlit run frontend_streamlit/app.py para iniciar la interfaz de usuario. Streamlit abrirá automáticamente una ventana del navegador en http://localhost:8501 donde puede ver la aplicación completa. Es importante que ambos procesos estén ejecutándose simultáneamente para que el sistema funcione correctamente: si la API se detiene, Streamlit no podrá obtener recomendaciones y mostrará errores de conexión.

## Estructura de Datos

El proyecto organiza sus datos en tres niveles de procesamiento. La carpeta data/raw contiene el archivo events.csv que son los datos originales sin procesar, exactamente como fueron recolectados del sistema de e-commerce. La carpeta data/processed contiene los datos después de la transformación inicial, incluyendo el archivo inferido_listo.csv que contiene los datos con categorías inferidas para productos que tenían valores faltantes, el archivo product_catalog.csv que es una tabla indexada de productos únicos con sus atributos, y ver.ipynb que es un notebook de verificación para validar la integridad de los datos procesados. Finalmente, la carpeta data/final contiene events_final.csv que es el conjunto de datos listo para ser consumido por los modelos y por la API en tiempo de ejecución.

```
FLUJO DE TRANSFORMACIÓN DE DATOS

data/raw/events.csv
(Datos originales, tal como fueron recolectados)
│
├─ Columnas: event_time, event_type, product_id, category_id,
│            category_code, brand, price, user_id, user_session
│
├─ Problemas:
│  ├─ Algunos category_code = NULL
│  ├─ Algunos brand = NULL
│  ├─ Posibles duplicados
│  └─ Inconsistencias en formato
│
v
[PIPELINE DE LIMPIEZA Y TRANSFORMACIÓN]
│
├─ Step 1: Cargar y validar
├─ Step 2: Inferir categorías (category_code)
├─ Step 3: Inferir marcas (brand)
├─ Step 4: Crear niveles jerárquicos
├─ Step 5: Feature engineering
├─ Step 6: Validar integridad
│
v
data/processed/
│
├─ inferido_listo.csv
│  └─ Datos con categorías e inferencias realizadas
│     Columnas: todas las originales + category_inferred + brand_inferred
│
├─ product_catalog.csv
│  └─ Catálogo único de productos
│     (deduplicado, información agregada)
│
└─ ver.ipynb
   └─ Notebook de verificación y validación
│
v
[INGENIERÍA DE CARACTERÍSTICAS]
│
├─ Crear variaciones de categoría (nivel1, nivel2, nivel3)
├─ Normalizar precios
├─ Codificar marcas
├─ Crear timestamps
│
v
data/final/events_final.csv
(Datos listos para modelos)
│
├─ Columnas enriquecidas
├─ Sin valores faltantes críticos
├─ Categorías estandarizadas
├─ Listo para ALS y K-Means
│
v
[CONSUMIDO POR]
├─ api/main.py (endpoints de datos)
├─ Modelo ALS (recomendaciones usuarios conocidos)
└─ Modelo K-Means (clustering de nuevos usuarios)
```

## Modelos de Machine Learning

El proyecto utiliza dos algoritmos complementarios de machine learning. El primero es SVD (Descomposición en Valores Singulares), que es una técnica de factorización matricial que descubre patrones latentes en la matriz de interacciones usuario-producto. SVD es especialmente efectivo para usuarios conocidos porque puede identificar relaciones implícitas entre usuarios y productos. Por ejemplo, si el usuario A compró productos similares al usuario B, entonces el modelo puede inferir que el usuario A probablemente también estaría interesado en otros productos que compró el usuario B. Este enfoque se denomina filtrado colaborativo y es el corazón de sistemas de recomendación modernos.

```
CÓMO FUNCIONA SVD (Descomposición en Valores Singulares)

MATRIZ ORIGINAL (usuario x producto)
        P1   P2   P3   P4   P5   P6   P7
U1  [   5    0    3    0    0    0    0  ]
U2  [   0    4    0    0    0    0    2  ]
U3  [   2    0    0    5    0    0    0  ]
U4  [   0    0    1    0    4    5    0  ]
...

Significado: U1 compró P1 (5 estrellas), P3 (3 estrellas), no vio P2, etc.

    DESCOMPOSICIÓN
         │
         v
┌─────────────────────────────────────┐
│  U = Matriz de factores usuario     │  cada usuario se representa
│  Σ = Matriz de valores singulares   │  como un vector de características
│  V = Matriz de factores producto    │  latentes (gustos implícitos)
└─────────────────────────────────────┘

    PROCESO
         │
         v
Para recomendar a usuario U1:
1. Obtener su vector latente (fila en U)
2. Calcular similitud con todos los vectores de producto (columnas en V)
3. Ordenar productos por similitud
4. Retornar top-N productos que el usuario no ha visto

RESULTADO: Recomendaciones personalizadas basadas en gustos implícitos
```

El segundo algoritmo es **K-Means Clustering** con **k=4 clusters**, que es específicamente utilizado para el onboarding de nuevos usuarios. K-Means agrupa usuarios en cuatro segmentos distintos basados en similitudes en su comportamiento y preferencias. Esta segmentación es particularmente valiosa para nuevos usuarios sin historial previo, ya que permite clasificarlos automáticamente en uno de estos cuatro grupos de usuarios similares y recomendar productos que otros usuarios en ese mismo cluster han encontrado interesantes.

```
CÓMO FUNCIONA K-MEANS (Clustering para Onboarding)

DATOS DE ENTRENAMIENTO
Usuarios históricos con sus características:
- Total de eventos
- Productos únicos vistos
- Views, cart adds, purchases
- Precio promedio
- Recencia (días)
- Proporciones por hora del día y día de semana
- Proporciones por categorías temáticas (tech, fashion_lifestyle, home, welfare)
... (21 variables normalizadas)

    ALGORITMO K-MEANS (K=4 clusters)
         │
    ┌────┴────┐
    v         v
1. Inicializar 4 centros    2. Asignar usuarios a centros
   aleatoriamente              más cercanos (distancia euclidiana)
         │                      │
         ├──────┬───────────────┘
         v      v
    3. Recalcular centros basado
       en promedio de usuarios
       en cada cluster
         │
         └─→ ¿Convergió?
             NO: volver a 2
             SÍ: terminar

RESULTADO: 4 clusters de usuarios (Cluster 0, 1, 2, 3)
┌────────────────────────────────────────────────────┐
│ Cluster 0: Usuarios con perfil 0                   │
│   - Características comportamentales distintivas    │
│   - Preferencias y patrones de compra únicos        │
│   - Afinidad específica por categorías              │
├────────────────────────────────────────────────────┤
│ Cluster 1: Usuarios con perfil 1                   │
│   - Características comportamentales diferentes     │
│   - Afinidad por otras categorías                   │
│   - Volumen de actividad distinto                   │
├────────────────────────────────────────────────────┤
│ Cluster 2: Usuarios con perfil 2                   │
│   - Patrones únicos de navegación                   │
│   - Comportamiento diferenciado                     │
├────────────────────────────────────────────────────┤
│ Cluster 3: Usuarios con perfil 3                   │
│   - Comportamiento adicional distinto               │
│   - Segmento especializado de usuarios              │
└────────────────────────────────────────────────────┘

PARA NUEVOS USUARIOS EN ONBOARDING:
Usuario nuevo → Presenta 4 productos (uno por cluster) → Usuario selecciona preferencia
→ Sistema asigna al cluster elegido → Retorna recomendaciones del cluster
```

Adicionalmente, el proyecto incluye un **Gaussian Mixture Model (GMM)** como modelo de clustering alternativo para análisis comparativo y exploración de patrones. Mientras que K-Means es el modelo que impacta directamente la experiencia del usuario en Streamlit durante el onboarding, GMM permite investigar segmentaciones probabilísticas con mayor flexibilidad. GMM utiliza k=2 componentes gaussianos para identificar dos perfiles principales de usuarios: aquellos con bajo engagement (28.5% de usuarios) y aquellos con alto engagement (71.5% de usuarios). Este modelo alternativo enriquece el análisis de datos del proyecto sin interferir con el flujo principal de recomendaciones.


## Análisis Jerárquico de Categorías

Después de los procesos de limpieza e inferencia, se realizó un análisis profundo de la estructura de las categorías para entender cómo estaban organizadas jerárquicamente. Las categorías seguían un formato delimitado por puntos donde cada nivel representaba un mayor grado de especificidad, por ejemplo electronics.telephone.accessory o computers.components.cooler.

```
ESTRUCTURA JERÁRQUICA DE CATEGORÍAS

electronics.telephone.accessory
|           |         |
|           |         +-- Nivel 3 (accessory)
|           +---------- Nivel 2 (telephone)
+---------------------- Nivel 1 (electronics)

Profundidad = 3 niveles
Delimitador = punto (.)
```

El análisis identificó que la mayoría de categorías se distribuía en tres niveles de profundidad. El nivel 1 contenía categorías muy generales como electronics o computers. El nivel 2, como telephone o components, proporcionaba especificidad media. El nivel 3, como accessory o cooler, era extremadamente específico. La distribución de datos mostró concentración en el nivel 2 con más de 634 mil registros, mientras que el nivel 3 tenía apenas 415 registros. Esta disparidad fue crítica para tomar decisiones de modelado.

```
DISTRIBUCIÓN DE REGISTROS POR NIVEL JERÁRQUICO

Nivel 1 (1 punto):        250,245 registros (19%)
Nivel 2 (2 puntos):       634,304 registros (76%)
Nivel 3 (3 puntos):       415 registros    (0.03%)
Nivel 0 (sin puntos):     0 registros      (0%)

RECOMENDACIÓN: Usar Nivel 2 como principal para modelado
```

## Decisión de Transformación Categórica

Con base en este análisis jerárquico, se definió una estrategia clara de transformación. El sistema dividió cada category_code en múltiples columnas representando cada nivel: nivel1, nivel2 y nivel3. La decisión arquitectónica fue priorizar el nivel 2 para el modelado principal porque ofrecía el equilibrio óptimo entre granularidad y representatividad. Usar el nivel 3 habría causado problemas de dispersión (sparsity) dado que muchas categorías específicas tienen muy pocas instancias, lo que dificulta que el modelo aprenda patrones significativos. Por el contrario, el nivel 1 habría sido demasiado general, perdiendo capacidad descriptiva.

Esta transformación permitió que el sistema de recomendación operara con características categóricas bien distribuidas, mejorando significativamente la calidad de los clusters y las predicciones de similitud entre productos. Los niveles más profundos se mantuvieron como información complementaria para análisis posterior, garantizando que ninguna información valiosa se perdía en el proceso de estandarización.

### DIAGRAMA DE DIAGNÓSTICO Y SOLUCIÓN

```
ERROR: ConnectionError (Streamlit no puede conectar a API)
│
├─→ Causa 1: API no está corriendo
│   Síntoma: Puerto 8000 no responde
│   Solución: 
│   Terminal 1 $ uvicorn api.main:app --reload --port 8000
│
├─→ Causa 2: IP o puerto incorrecto
│   Síntoma: URL http://localhost:8000 no es accesible
│   Solución:
│   - Verificar que API = "http://localhost:8000" en app.py
│   - Probar en navegador: http://localhost:8000/docs
│
└─→ Causa 3: Firewall bloqueando puerto
    Solución:
    - Permitir puerto 8000 en firewall de Windows
    - O cambiar a --port 9000 y actualizar en Streamlit

─────────────────────────────────────────

ERROR: FileNotFoundError (events_final.csv no encontrado)
│
├─→ Causa: Pipeline no ejecutado
│   Síntoma: Carpeta data/final está vacía
│   Solución:
│   Terminal $ python run_pipeline.py
│   (esperar 5-15 minutos)
│
└─→ Verificación:
    - Comprobar: data/final/events_final.csv existe
    - Si existe, reiniciar API y Streamlit

─────────────────────────────────────────

ERROR: Port 8000 already in use
│
├─→ Opción 1: Encontrar y matar proceso
│   Windows: taskkill /PID <PID> /F
│   PowerShell: Get-Process -Id <PID> | Stop-Process -Force
│
├─→ Opción 2: Usar puerto diferente
│   Comando: uvicorn api.main:app --port 8001
│   Actualizar en app.py: API = "http://localhost:8001"
│
└─→ Opción 3: Reiniciar PC (nuclear option)

─────────────────────────────────────────

ERROR: ModuleNotFoundError
│
├─→ Causa: Dependencia no instalada
│   Síntoma: "No module named 'fastapi'" u otra librería
│
├─→ Solución 1: Reinstalar todo
│   $ pip install -r requirements.txt
│
├─→ Solución 2: Instalar específica
│   $ pip install fastapi uvicorn streamlit scikit-learn pandas
│
└─→ Solución 3: Verificar ambiente
    $ python -m pip list
    (asegurar que estén todas las librerías)
```

## Descripción General

El frontend está construido con **Streamlit** como aplicación multipágina. Se comunica con la API REST mediante `httpx` para obtener recomendaciones y registrar eventos.

## Estructura

```
frontend_streamlit/
├── app.py                        # Página principal — Tienda Click & Tech
└── pages/
    └── 1_Monitor_de_Salud.py     # Página de monitoreo — Data Drift
```

## Página 1: Tienda Click & Tech (`app.py`)

### Características

- Carrito de compras persistente en `st.session_state`
- Registro de eventos `view`, `cart`, `purchase` en tiempo real vía API
- Onboarding para nuevos usuarios: muestra un producto por cluster y permite elegir preferencia
- Diversificación de recomendaciones: máximo 3 productos por subcategoría (nivel3)

### Cuello de botella: imágenes de productos

El dataset no incluye URLs de imágenes individuales por producto, y descargar una imagen por cada uno de los ~17,000 productos del catálogo no era viable (tiempo de descarga, almacenamiento, límites de APIs de imágenes).

**Solución adoptada:** sistema de imágenes por categoría con pool rotativo.

- Se descargó manualmente un conjunto de imágenes representativas por categoría (`smartphone.jpg`, `cable.jpg`, `laptop.jpg`, etc.) almacenadas en `assets/images/`
- Para categorías con muchos productos se agregaron variantes numeradas (`smartphone1.jpg`, `smartphone2.jpg`, …) que rotan cíclicamente
- La función `_build_image_pools()` construye automáticamente el pool a partir del naming convention `{base}{número}.{ext}`
- La función `pick_image()` selecciona la siguiente variante en el pool usando un contador, evitando que todos los productos de la misma categoría muestren la misma imagen

```
assets/images/
├── smartphone.jpg       ← imagen base
├── smartphone1.jpg      ← variante 1
├── smartphone2.jpg      ← variante 2
├── cable.jpg
├── laptop.jpg
└── ...
```

Esta decisión implica que los productos de la misma categoría comparten imágenes genéricas en lugar de fotos reales del producto, lo cual es una limitación visual pero permite que la demo funcione con todo el catálogo sin infraestructura adicional.

## Página 2: Monitor de Salud (`pages/1_Monitor_de_Salud.py`)

### Descripción

Panel de monitoreo de **data drift** que compara la distribución de los datos de entrenamiento versus los datos de producción (eventos nuevos registrados por la aplicación).

### Metodología

Se utiliza el **Population Stability Index (PSI)** para medir el nivel de desvío entre distribuciones:

| PSI | Semáforo | Interpretación |
|-----|----------|----------------|
| < 0.10 | 🟢 | Sin cambio significativo |
| 0.10 – 0.25 | 🟡 | Cambio moderado — monitorear |
| ≥ 0.25 | 🔴 | Cambio severo — reentrenar modelo |

### Corte temporal

- **Entrenamiento (referencia):** eventos anteriores a `2021-03-01` (~884,312 eventos)
- **Producción:** eventos posteriores (interacciones registradas desde la app)

### Tabs del dashboard

1. **Categorías** — Comparación de distribución por `nivel1` y `nivel2_norm` entre entrenamiento y producción (gráfico de barras agrupadas con Plotly)
2. **Tipo de interacción** — Distribución de `event_type` (view / cart / purchase)
3. **Tabla de alertas** — PSI por categoría con colorización: verde / amarillo / rojo según umbral

### Reentrenamiento

Cuando el PSI supera 0.25 en categorías relevantes, se debe ejecutar el pipeline de reentrenamiento:

```bash
python run_pipeline.py
```

Esto ejecuta en orden: `PipelineV_3.0.ipynb` → `feature_engineering_final.ipynb` → `Clustering_Kmeans.ipynb` → `Notebook_Clustering_NMM.ipynb`

## Ejecución

```bash
# Desde la raíz del proyecto con el entorno activado
streamlit run frontend_streamlit/app.py
```

- Aplicación disponible en: `http://localhost:8501`
- Navegación entre páginas desde el sidebar izquierdo

## Conclusión streamlit

Click & Tech representa una aplicación completa de machine learning aplicado, combinando ciencia de datos, ingeniería backend y desarrollo frontend en una plataforma cohesiva. El sistema demuestra cómo organizar un proyecto de machine learning siguiendo principios profesionales de arquitectura de software, manteniendo claridad en la separación de responsabilidades entre componentes. Tanto la API como Streamlit están diseñados para ser fáciles de mantener, escalar y extender con nuevas funcionalidades, permitiendo que el sistema crezca junto con las necesidades del negocio.

---
# 13. 📌 Resultados y Hallazgos

El proyecto permitió construir un sistema híbrido de recomendación capaz de abordar problemas típicos de e-commerce como:

- baja personalización,
- sparse data,
- y cold start de usuarios.

A través de técnicas de clustering, collaborative filtering y re-ranking semántico, se logró mejorar la relevancia de las recomendaciones y comprender mejor el comportamiento de los usuarios.

### 1. Hallazgos del Negocio (EDA)

El principal problema no está en finalizar la compra, sino en lograr que el usuario encuentre productos suficientemente relevantes para agregarlos al carrito.

Esto justifica directamente la necesidad de un sistema de recomendación más preciso.

### 2. Problema Crítico: Cold Start

Métrica	Resultado
Usuarios con ≤ 5 eventos	94%
Mediana de eventos por usuario	1

Esto indica que la mayoría de usuarios tienen muy poca interacción histórica, generando un escenario extremo de cold start y alta dispersión en la matriz usuario-producto.

### 3. Resultados del Pipeline de Datos

El pipeline permitió:

reducir valores nulos,
recuperar categorías faltantes mediante inferencia,
mejorar consistencia semántica,
y estructurar las categorías jerárquicas para el modelado.

Además, se identificó que el:

nivel 2

representaba el mejor equilibrio entre granularidad y estabilidad para el sistema de recomendación

### 4. Resultados del Clustering

Los modelos K-Means y GMM identificaron consistentemente:

k=2

segmentos principales de usuarios.

***Cluster 1:***
- Usuarios Tecnológicos / Alto Valor
- mayor interacción,
- mayor actividad de compra,
- afinidad hacia tecnología,
- comportamiento más recurrente.

***Cluster 0:***
- Usuarios Generales / Bajo Valor
- menor engagement,
- navegación más superficial,
- menor frecuencia de compra.
- Hallazgo principal

Los usuarios con afinidad tecnológica mostraron mayor valor comercial y mayor profundidad dentro del funnel.

### 5. Resultados del Sistema de Recomendación

ALS fue seleccionado como modelo principal tras superar a SVD en desempeño y estabilidad sobre datos implícitos.

Sin embargo, el hallazgo más importante fue que:

la incorporación de información semántica mejoró el rendimiento del recomendador.

### 6. Éxito del Re-ranking Semántico

El sistema híbrido ALS + taxonomía logró mejorar simultáneamente:

**Precision@K** y **Recall@K**

Esto demuestra que la clasificación jerárquica de productos aporta señal útil complementaria al collaborative filtering.

### 7. Hallazgo Más Importante

El Grid Search mostró que el mejor balance fue:

| Componente | Peso |
|---|---|
| ALS | 0.4 |
| Taxonomía | 0.6 |

Esto indica que la estructura semántica del catálogo aporta una señal extremadamente fuerte para la recomendación.

### La API REST permitió desacoplar el sistema de recomendación

La implementación de FastAPI permitió transformar el modelo en un servicio consumible y escalable.

- El sistema quedó preparado para integrarse con aplicaciones externas.
- La arquitectura desacoplada facilita mantenimiento y escalabilidad.
- Los endpoints permiten consultar recomendaciones en tiempo real.
- La serialización estructurada facilita interoperabilidad entre backend y frontend

### El Frontend Streamlit permitió visualizar el sistema como producto real

La construcción de la tienda interactiva permitió simular una experiencia cercana a un entorno real de e-commerce.

- Se logró visualizar recomendaciones dinámicas por usuario.
- El monitor de salud permitió supervisar:
* estado del sistema,
* carga de modelos,
* disponibilidad de endpoints,
* y funcionamiento general del recomendador.
La interfaz facilita validación funcional y demostración del proyecto.

### 8. Conclusión General

El proyecto demuestra que combinar:

- ALS,
- clustering,
- feedback implícito,
- y semantic re-ranking
- API y Streamlit

permite construir un sistema de recomendación más robusto, interpretable, escalable y adaptable a escenarios reales de e-commerce con sparse data y cold start.

---
# 12. 📌Limitaciones del Proyecto

el proyecto presenta varias limitaciones técnicas y analíticas propias de los sistemas de recomendación basados en datos implícitos y escenarios reales de e-commerce.

### 1. Sparse Data Extrema

La principal limitación del proyecto es la alta dispersión de la matriz usuario-producto.

La mayoría de usuarios presentan muy pocas interacciones:

94% ≤ 5 interacciones

Esto limita significativamente la capacidad de los modelos colaborativos para aprender patrones robustos y generalizables.

### 2. Dataset Limitado Temporalmente

El dataset cubre un periodo relativamente corto:

septiembre 2020 → febrero 2021.

Esto limita: el análisis de comportamiento a largo plazo,
la detección de cambios estacionales más complejos,
y el modelado de ciclos prolongados de consumo.

### 3. Falta de Variables Contextuales

El sistema no incorpora variables externas como:

- ubicación geográfica,
- dispositivo,
- campañas de marketing,
- clima,
- promociones,
- o contexto de navegación.

Por lo tanto, las recomendaciones se basan únicamente en comportamiento histórico e interacción con productos.

---
# 13. 📌 Futuras Mejoras

Aunque el sistema híbrido desarrollado logró resultados sólidos en escenarios de sparse data y cold start, existen múltiples oportunidades de mejora tanto a nivel técnico como de negocio.

### 1. Incorporación de Modelos Deep Learning

Una posible evolución del sistema consiste en integrar arquitecturas más avanzadas basadas en Deep Learning, como:

- Neural Collaborative Filtering (NCF),
- Autoencoders,
- Transformers para recomendación,
- o modelos secuenciales como LSTM/GRU.

Estos enfoques permitirían capturar patrones de comportamiento más complejos y relaciones no lineales entre usuarios y productos.

### 3. Evaluación Online y A/B Testing

El proyecto fue evaluado únicamente en entorno offline. Una mejora importante sería implementar:

- pruebas A/B,
- métricas de negocio reales,
- y monitoreo en producción.

Esto permitiría medir impacto real sobre:

- CTR,
- conversión,
- retención,
- ticket promedio,
- y satisfacción del usuario.

### 4. Sistema de Recomendación en Tiempo Real

Actualmente el sistema funciona principalmente sobre datos históricos procesados por lotes (batch processing).

Una mejora futura sería incorporar:

- streaming de eventos,
- actualización online de perfiles,
- y recomendaciones en tiempo real.

Esto permitiría reaccionar inmediatamente a cambios recientes en el comportamiento del usuario.

### 5. Incorporación de Variables Contextuales

El sistema podría enriquecerse incluyendo información adicional como:

- ubicación geográfica,
- dispositivo utilizado,
- temporalidad,
- promociones activas,
- campañas de marketing,
- o contexto de navegación.

Esto permitiría evolucionar hacia sistemas de recomendación context-aware.

### 4. Sistema Híbrido Más Complejo

El sistema actual combina ALS + clustering + semantic re-ranking. Futuramente podrían integrarse nuevas señales como:

- popularidad temporal,
- tendencias,
- co-visitas,
- sesiones de navegación,
- o grafos usuario-producto.

Esto permitiría construir un recomendador aún más robusto y dinámico.

### 5. Escalabilidad Productiva de la API
Evolucionar la API hacia un entorno más robusto mediante:

- Docker,
- balanceo de carga,
- autenticación,
- caché,
- y despliegue cloud.

### 6. Evolución del Frontend

Transformar el prototipo Streamlit en una aplicación más completa con:

- autenticación de usuarios,
- historial personalizado,
- dashboards analíticos,
- y métricas comerciales en tiempo real.


---
# 14. 📌 Conclusiones

El desarrollo de este proyecto permitió construir un sistema híbrido de recomendación orientado a un entorno real de e-commerce, integrando procesos de limpieza de datos, análisis exploratorio, feature engineering, segmentación de usuarios y modelos avanzados de recomendación.

A lo largo del análisis se identificó que la plataforma presenta un escenario extremo de ***sparse data*** y ***cold start***, donde la mayoría de los usuarios tienen muy pocas interacciones históricas. Este hallazgo fue determinante para diseñar una arquitectura híbrida capaz de complementar las limitaciones del collaborative filtering tradicional.

El pipeline de datos permitió mejorar significativamente la calidad y consistencia del dataset mediante procesos de inferencia de categorías, normalización jerárquica y construcción de variables de comportamiento. Estas transformaciones hicieron posible representar de forma más precisa los patrones de navegación y consumo de los usuarios.

La segmentación mediante K-Means y Gaussian Mixture Models demostró que el comportamiento de los clientes no es homogéneo, identificando perfiles claramente diferenciados entre usuarios tecnológicos de alto valor y usuarios de interacción más general o exploratoria. Esto genera oportunidades importantes para estrategias de personalización y marketing segmentado.

En cuanto al sistema de recomendación, ALS mostró un mejor desempeño frente a SVD en escenarios de feedback implícito. Sin embargo, el hallazgo más importante del proyecto fue comprobar experimentalmente que la incorporación de información semántica basada en taxonomía de productos mejora el desempeño del recomendador.

El semantic re-ranking logró aumentar simultáneamente métricas como Precision@10 y Recall@10, especialmente en usuarios con pocas interacciones, validando que la información categórica ayuda a compensar parcialmente las debilidades del collaborative filtering en escenarios sparse.

el proyecto permitió evidenciar que los usuarios mantienen afinidades muy específicas dentro del catálogo, y que las categorías más detalladas aportan una señal semántica altamente relevante para la recomendación.

Adicionalmente, la implementación de una API REST con FastAPI permitió transformar el modelo en un servicio desacoplado, escalable y listo para integraciones futuras, mientras que el frontend desarrollado en Streamlit permitió visualizar el recomendador como una solución funcional e interactiva cercana a un entorno real de negocio

Finalmente, el sistema desarrollado demuestra que combinar:

- Ingenieria de datos
- Arquitectuta Backend
- collaborative filtering,
- clustering,
- feedback implícito,
- re-ranking semántico
- y Visualización interactiva

permite construir soluciones de recomendación más robustas, interpretables, escalables y adaptadas a problemas reales de e-commerce.

El proyecto establece una base sólida para futuras mejoras orientadas a sistemas en tiempo real, modelos basados en Deep Learning y arquitecturas escalables de producción.

---
