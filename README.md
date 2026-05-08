# 🔄 Pipeline de Limpieza, Transformación y Feature Engineering

## 🧹 Inferencia de Categorías (Data Cleaning)

En esta etapa del pipeline se aborda el problema de productos sin category_code, lo cual afecta directamente la calidad del sistema de recomendación.

🎯 Objetivo

Asignar una categoría inferida a los productos que no cuentan con category_code, utilizando información disponible como el category_id y las marcas dominantes dentro de cada grupo.

### ⚙️ Proceso Paso a Paso

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

### 🏷️ Manejo de Categorías No Inferidas

A pesar del proceso de inferencia basado en category_id, algunos registros no pudieron ser clasificados debido a la falta de patrones claros o información suficiente.

Para garantizar la consistencia del dataset y evitar la pérdida de información, se asignó una categoría genérica a estos casos, permitiendo:

- Mantener todos los registros dentro del sistema
- Evitar valores nulos que puedan afectar el modelo
- Agrupar productos ambiguos bajo una categoría controlada

### 🧠 Identificación de Registros Inferidos

Se creó una nueva variable category_inferred para identificar qué registros fueron afectados por el proceso de inferencia, permitiendo

- Trazabilidad del proceso de limpieza
- Análisis posterior del impacto de la inferencia
- Evaluar el comportamiento del modelo sobre datos 
- inferidos vs originales

### 🏷️ Inferencia de Marca (brand)

En esta etapa se aborda el problema de productos que no cuentan con información de marca (brand), lo cual puede afectar la calidad del sistema de recomendación y el análisis de comportamiento de compra.

🎯 Objetivo

Asignar una marca inferida a los productos sin brand, utilizando como referencia su category_code, con el fin de mantener la consistencia del dataset y evitar valores nulos.

🧠 Estrategia de Inferencia

Para los registros sin marca, se define una regla basada en la estructura de la categoría:

Se asigna una marca genérica compuesta por el prefijo "generic." seguido del último nivel de la categoría.

## 🧩 Análisis y Estructuración de Categorías

Después del proceso de limpieza e inferencia de `category_code`, se realizó un análisis de su estructura jerárquica para comprender cómo están organizadas las categorías y preparar el dataset para su posterior transformación.

Las categorías siguen un formato jerárquico delimitado por puntos (`.`), donde cada nivel representa un mayor grado de especificidad (por ejemplo: `electronics.telephone.accessory`).

### ⚙️ Análisis de la estructura

Para identificar la profundidad de las categorías, se contabilizó el número de puntos (`.`) presentes en cada valor de `category_code`, lo cual permite determinar el número de niveles jerárquicos.

Adicionalmente, se exploraron ejemplos representativos por cada nivel para validar la consistencia de la estructura.

### 📊 Resultados

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

### 🧠 Interpretación

A partir de estos resultados se concluye que:

* No existen categorías sin jerarquía, lo que indica una estructura consistente en el dataset.
* La mayor concentración de datos se encuentra en el **nivel 2**, lo que lo convierte en el nivel más adecuado para el análisis y modelado.
* El **nivel 1** agrupa categorías más generales, útiles para segmentaciones amplias.
* El **nivel 3**, aunque más específico, tiene muy baja representación, lo que puede generar problemas de dispersión (sparsity) en el modelo.

### ⚠️ Implicaciones para el modelado

La variabilidad en la profundidad de las categorías hace necesario estandarizar su estructura. Utilizar niveles demasiado específicos podría afectar negativamente el rendimiento del sistema de recomendación, mientras que niveles muy generales pueden perder capacidad descriptiva.

### 🚀 Decisión de transformación

Con base en este análisis, se definió la siguiente estrategia:

* Dividir `category_code` en múltiples niveles jerárquicos (`nivel1`, `nivel2`, `nivel3`)
* Priorizar el uso del **nivel 2** para el modelado, debido a su equilibrio entre granularidad y representatividad
* Mantener niveles más profundos como información complementaria
* Para el nivel más detallado se conserva dentro de la variable **nivel 3** y que no se pierde información relevante al estandarizar la jerarquía

Esta transformación permite mejorar la calidad del feature engineering, facilitar el análisis por categorías y fortalecer el desempeño del sistema de recomendación.

### 🧠 Normalización Contextual de Categorías

Durante el proceso de análisis se identificaron categorías con ambigüedad semántica, ya que aparecían en múltiples niveles jerárquicos (por ejemplo, términos como "accessories", "generic" o "storage").

Este comportamiento genera inconsistencias, ya que una misma etiqueta puede tener diferentes significados dependiendo del contexto en el que se encuentre, afectando la calidad del sistema de recomendación.

🎯 Objetivo

Reducir la ambigüedad semántica mediante una normalización contextual, incorporando información de niveles superiores para generar categorías más específicas y coherentes.

⚙️ Estrategia

Se aplicó una transformación selectiva sobre categorías problemáticas:

En nivel 2, se integra el contexto de nivel1
En nivel 3, se utiliza el contexto de nivel2_norm previamente ajustado

Esto permite diferenciar categorías que, aunque comparten nombre, pertenecen a contextos distintos.

## 🧹Eliminación de Registros Duplicados

Como parte del proceso inicial de limpieza, se realizó la identificación y eliminación de registros duplicados en el dataset, con el fin de garantizar la integridad y calidad de la información.

La eliminación de duplicados se realizó únicamente sobre filas completamente iguales, evitando eliminar registros que, aunque similares, representen eventos distintos (por ejemplo, múltiples interacciones de un mismo usuario).
