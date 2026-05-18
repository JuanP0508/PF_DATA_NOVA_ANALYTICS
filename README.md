# 📊 Pipeline de Limpieza, Transformación y Feature Engineering

## Inferencia de Categorías (Data Cleaning)

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

---

## Análisis y Estructuración de Categorías

Después del proceso de limpieza e inferencia de `category_code`, se realizó un análisis de su estructura jerárquica para comprender cómo están organizadas las categorías y preparar el dataset para su posterior transformación.

Las categorías siguen un formato jerárquico delimitado por puntos (`.`), donde cada nivel representa un mayor grado de especificidad (por ejemplo: `electronics.telephone.accessory`).

---

### Análisis de la estructura

Para identificar la profundidad de las categorías, se contabilizó el número de puntos (`.`) presentes en cada valor de `category_code`, lo cual permite determinar el número de niveles jerárquicos.

Adicionalmente, se exploraron ejemplos representativos por cada nivel para validar la consistencia de la estructura.

---

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

---

### Interpretación

A partir de estos resultados se concluye que:

* No existen categorías sin jerarquía, lo que indica una estructura consistente en el dataset.
* La mayor concentración de datos se encuentra en el **nivel 2**, lo que lo convierte en el nivel más adecuado para el análisis y modelado.
* El **nivel 1** agrupa categorías más generales, útiles para segmentaciones amplias.
* El **nivel 3**, aunque más específico, tiene muy baja representación, lo que puede generar problemas de dispersión (sparsity) en el modelo.

---

### Implicaciones para el modelado

La variabilidad en la profundidad de las categorías hace necesario estandarizar su estructura. Utilizar niveles demasiado específicos podría afectar negativamente el rendimiento del sistema de recomendación, mientras que niveles muy generales pueden perder capacidad descriptiva.

---

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

# 📊 EDA: Análisis del Comportamiento de Compra en E-commerce

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

# 📊Feature Engineering

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

#### ⏱ 3. Variable de Recencia (`recency_days`)
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
*   **Problema que resuelve:** En el comercio electrónico, los intereses de los usuarios son altamente volátiles. Un producto comprado o visto hace 90 días no tiene la misma relevancia para el usuario que uno interactuado hace 24 horas. El `score` bruto estático sobreestima el interés del pasado.
*   **Fórmula Matemática:** Se aplica una función de decaimiento exponencial con la estructura:
$$\text{score\_temporal} = \text{score} \times e^{-\lambda \cdot t}$$
Donde $t$ son los `dias_desde_interaccion` y $\lambda = 0.01$ es el factor de penalización diario.

#### 3. Impacto Numérico del Factor de Penalización ($\lambda = 0.01$)
La selección de la tasa de decaimiento del 1% diario modifica el comportamiento del target de la siguiente manera:
*   **Interacción Hoy ($t=0$):** $e^{0} = 1 \rightarrow$ El puntaje mantiene el 100% de su valor original.
*   **Interacción hace ~70 días ($t=69.3$):** $e^{-0.693} \approx 0.50 \rightarrow$ El puntaje se reduce exactamente a la **mitad (Vida Media)**.
*   **Interacción hace 150 días ($t=150$):** $e^{-1.5} \approx 0.22 \rightarrow$ El interés remanente cae al 22%, degradando el producto en el orden de recomendaciones.

#### Mapeo de Variables para Modelos de Producción

El reporte de columnas en consola confirma que los conjuntos de datos están listos para sus respectivas arquitecturas de modelado:

1.  **Pipeline de Segmentación (Clustering):**
    *   **Identificador:** `user_id` (Se excluirá del entrenamiento y actuará como llave de mapeo).
    *   **Features:** Desde `total_events` hasta `proportion_welfare`. Al ser variables continuas y de proporciones (0.0 a 1.0), se encuentran en el formato matemático ideal para pasar a la fase de escalamiento y cálculo de distancias euclidianas.
2.  **Pipeline de Recomendación (Filtrado Colaborativo / Híbrido):**
    *   **Llaves de Intersección:** `user_id` y `product_id` (Coordenadas de la matriz dispersa).
    *   **Características de Apoyo:** `n_interacciones` y `dias_desde_interaccion`.
    *   **Variable Objetivo (Target):** `score_temporal`. Esta columna condensa el comportamiento histórico y el decaimiento por tiempo, sirviendo como la variable continua de preferencia para el entrenamiento de los algoritmos de recomendación.

##  Conclusiones Clave del Feature Engineering

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

# 📊 K-Means para Segmentación de Usuarios

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

### Conclusión
La segmentación demuestra que el comportamiento de los usuarios en el e-commerce no es homogéneo, sino que se divide principalmente en usuarios de alto valor orientados a tecnología y usuarios de bajo valor enfocados en categorías más generales. Esta diferenciación permite diseñar estrategias altamente personalizadas, optimizar la conversión y construir una base sólida para futuros modelos de recomendación y crecimiento del negocio.

# 📊 Gaussian Mixture Model (GMM) para Segmentación de Usuarios

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

### Conclusión
El Gaussian Mixture Model permitió transformar variables agregadas de comportamiento en segmentos interpretables de usuarios. El resultado final constituye una base sólida para análisis avanzados de usuarios y un complemento o refuerzo para el sistema de recomendaciones personalizadas.
