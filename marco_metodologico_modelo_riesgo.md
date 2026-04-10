# Marco Metodológico para un Modelo de Riesgo en Minas de Cobre

## 1. Problema real

El problema no es simplemente "predecir riesgo" para minas de cobre. El problema serio es construir una herramienta de apoyo a decisión que permita cuantificar downside económico y deterioro operativo bajo incertidumbre de mercado, geología y ejecución.

En su estado actual, el libro [Copper_mining_risk_model.xlsm](D:/Cursos/Proyecto/copper_minning_risk_model/Copper_mining_risk_model.xlsm) se parece más a un motor de valuación y simulación que a un modelo empírico de riesgo generalizable. Eso no invalida el trabajo; solo obliga a definir con precisión qué tipo de inferencia es defendible.

## 2. Dominio y contexto de decisión

- `Dominio principal`: economía minera, riesgo operativo y evaluación de activos de cobre.
- `Decisión relevante`: priorizar activos, monitorear deterioro, estresar planes mineros y cuantificar pérdida económica bajo escenarios adversos.
- `Usuarios plausibles`: planeamiento minero, finanzas corporativas, estrategia, evaluación de proyectos, comité de inversión.

La salida útil no debe ser un score abstracto. Debe responder algo como:

- ¿Cuál es la probabilidad de incumplir el plan económico u operativo en el próximo horizonte?
- ¿Qué combinación de precio, ley, recuperación y throughput destruye valor?
- ¿Qué minas o periodos están más expuestos a downside económico?

## 3. Qué muestran los datos actuales y qué no muestran

La estructura observada del workbook ya separa capas que no deben mezclarse analíticamente:

- `Market_Data`: trayectorias de precio, toneladas procesadas y ley por año.
- `Empírical_Data`: precios históricos de cobre y transformaciones estadísticas.
- `Base_Model`: traducción de supuestos a producción de cobre fino y precio neto efectivo.
- `Expansion_Model`: escenario de expansión con throughput, ley y recuperación.
- `Monte_carlo`: simulación de factores para precio, ley, recuperación y VAN.

Esto sugiere que parte de la "data" es observacional y parte es generada por el propio modelo. Metodológicamente, eso impide tratar todo como evidencia empírica homogénea.

### Lo que los datos sí permiten

- análisis de sensibilidad
- simulación de escenarios
- cuantificación de downside económico condicional a supuestos
- monitoreo estructurado si se agregan series operativas históricas

### Lo que los datos no permiten por sí solos

- inferencia causal fuerte
- validación externa de un score de riesgo general para minas de cobre
- claims tipo "el modelo predice riesgo minero" si el target no está definido con eventos históricos observados

## 4. Clasificación correcta del problema

La clasificación correcta depende de cómo se defina la variable objetivo.

### Caso A: con la información actual del workbook

El problema es principalmente de:

- `decision support`
- `scenario analysis`
- `economic risk simulation`

No es todavía un problema supervisado de predicción robusta.

### Caso B: si se arma una base histórica mina-periodo

Entonces sí puede formularse como:

- `predicción de deterioro económico-operativo`
- `predicción de incumplimiento de plan`
- `estimación de severidad de pérdida`

Pero solo si existe una variable objetivo observada, fechada y coherente con el uso real de decisión.

## 5. Variable objetivo correcta

No recomiendo comenzar con un score único de riesgo. Recomiendo definir primero uno o más targets explícitos.

### Target primario recomendado

`Riesgo económico de downside a horizonte h`

Ejemplos defendibles:

- probabilidad de que EBITDA, margen operativo o flujo de caja caigan por debajo de un umbral
- probabilidad de VAN negativo bajo una distribución explícita de escenarios
- shortfall relativo frente al plan: `resultado real - resultado planificado`

### Target secundario recomendado

`Riesgo operativo`

Ejemplos:

- probabilidad de que throughput caiga bajo cierto percentil del plan
- probabilidad de recuperación metalúrgica anómalamente baja
- probabilidad de desviación material entre ley planificada y ley reconciliada

### Target terciario opcional

`Riesgo de valor integrado`

Un target compuesto solo sería aceptable después de modelar por separado:

- exposición de mercado
- deterioro geológico
- deterioro operativo
- traducción económica del deterioro

Si esos componentes no se separan, el score final será arbitrario.

## 6. Unidad de análisis

La unidad de análisis debe reflejar el proceso real.

### Si solo hay un activo y el workbook actual

La unidad de análisis útil es:

- `activo-año` para simulación estratégica
- `activo-escenario-año` para análisis probabilístico

Eso sirve para valuación y downside económico, no para entrenar un modelo general entre minas.

### Si se quiere un modelo transferible entre minas

La unidad recomendable es:

- `mina-mes`
- `mina-trimestre`

No recomiendo `mina-año` si el objetivo es capturar deterioro operativo, porque puede ocultar shocks de mantenimiento, blending, dureza, agua, stripping o recuperación.

## 7. Mapa conceptual de variables

### Dimensión de mercado

- precio del cobre
- tipo de cambio
- costos energéticos
- costos de insumos críticos
- tratamiento y refinación si aplican

Estas variables no miden "calidad de mina". Miden exposición exógena y condiciones del entorno.

### Dimensión geológica y de recurso

- ley del mineral
- variabilidad de ley
- dureza
- mineralogía
- strip ratio
- reconciliación plan vs real
- indicadores de incertidumbre geológica

Estas variables miden la calidad física y la incertidumbre del material procesado o planificado.

### Dimensión operativa

- toneladas procesadas
- disponibilidad de planta
- utilización
- recuperación
- consumo de energía
- paradas no programadas
- dilución
- cumplimiento del plan de mina

Estas variables capturan ejecución y restricciones del sistema.

### Dimensión económica

- cash cost
- AISC si aplica
- margen por libra
- EBITDA
- flujo de caja
- VAN

Estas son salidas económicas, no inputs primitivos. Deben tratarse como outcomes o variables derivadas.

## 8. Arquitectura analítica recomendada

La arquitectura más defendible es modular:

1. `Módulo de exposición de mercado`
2. `Módulo de desempeño geológico-operativo`
3. `Módulo de traducción económica`
4. `Módulo de simulación y downside`

Esto evita un error común: dejar que el precio explique casi todo y luego llamar a eso "riesgo de la mina".

### Estructura mínima sugerida

- `Capa 1`: estimar o imputar estado operativo y geológico por mina-periodo
- `Capa 2`: modelar outcomes operativos a horizonte h
- `Capa 3`: traducir outcomes a pérdidas económicas
- `Capa 4`: simular escenarios de mercado y combinarlos con vulnerabilidad operativa

## 9. Validación correcta

La validación debe depender del target.

### Si el output es escenario económico

Validar con:

- auditoría estructural del modelo
- chequeo de unidades y timing
- sensibilidad a supuestos
- estrés de combinaciones adversas
- plausibilidad de parámetros frente a historia y rangos de ingeniería

No corresponde hablar de accuracy ni de AUC como validación principal.

### Si el output es predicción de deterioro o incumplimiento

Validar con:

- backtesting temporal estricto
- corte train/test por tiempo, nunca aleatorio
- validación por mina fuera de muestra si hay varias operaciones
- evaluación por régimen de precio
- calibración probabilística
- comparación contra benchmarks simples

### Benchmarks mínimos

- regla ingenua por persistencia
- promedio histórico por mina
- percentiles por régimen de precio
- score heurístico operativo simple

Si el modelo no mejora esto de forma estable, no hay justificación para complejidad adicional.

## 10. Riesgos metodológicos centrales

### Riesgo 1: leakage

Usar variables geológicas o reconciliaciones observadas ex post para predecir un evento que en tiempo real aún no era conocido.

### Riesgo 2: mezclar supuestos con observaciones

No se puede entrenar o validar como si una trayectoria proyectada del workbook fuera evidencia observada.

### Riesgo 3: score arbitrario

Combinar precio, ley y recuperación con pesos ad hoc produce una métrica vistosa pero analíticamente débil.

### Riesgo 4: confundir riesgo de mercado con riesgo minero

Si el precio del cobre domina todo, el output puede ser básicamente un proxy del ciclo del commodity.

### Riesgo 5: exceso de agregación

Promedios anuales pueden ocultar heterogeneidad crítica en frentes, fases, campañas, blend y disponibilidad.

### Riesgo 6: sobreinterpretación

Un modelo predictivo no autoriza lenguaje causal. Un motor de simulación no autoriza claims de capacidad predictiva empíricamente validada.

## 11. Qué sería un resultado engañoso

El resultado sería engañoso si:

- se reporta un score sin target explícito
- se usa lenguaje de predicción sin labels históricos
- se validan periodos futuros con información no disponible en tiempo real
- se mezcla una sola mina con claims sobre "minas de cobre" en general
- se omiten riesgos institucionales como permisos, agua, regalías, demoras o cambios tributarios
- se reporta precisión estadística sin discutir sensibilidad a supuestos

## 12. Diseño mínimo viable recomendado

### Etapa 1: formular el problema

Definir una de estas tres rutas:

1. `Riesgo económico bajo escenarios`
2. `Predicción de incumplimiento operativo`
3. `Modelo híbrido`: vulnerabilidad operativa + simulación económica

La ruta 3 es la más defendible si el objetivo es un producto serio de riesgo minero.

### Etapa 2: construir la tabla maestra

Tabla tipo panel con:

- mina
- fecha
- variables de mercado observables al inicio del periodo
- variables geológicas conocidas al inicio del periodo
- variables operativas rezagadas
- plan del periodo
- outcome real del periodo
- outcome económico derivado

### Etapa 3: definir horizontes

- `corto plazo`: 1 a 3 meses para deterioro operativo
- `mediano plazo`: 6 a 12 meses para desempeño económico
- `largo plazo`: vida de mina para evaluación estratégica y VAN

Cada horizonte requiere un target y validación distintos.

### Etapa 4: modelar por capas

- primero baseline interpretable
- después especificaciones más ricas
- al final simulación de escenarios

No al revés.

## 13. Recomendación final

La forma más sólida de continuar es definir el proyecto como un `modelo híbrido de riesgo económico-operativo para minas de cobre`, no como un score único genérico.

Secuencia recomendada:

1. fijar target explícito
2. fijar unidad de análisis
3. separar variables exógenas, geológicas, operativas y económicas
4. construir panel histórico limpio
5. validar temporalmente
6. recién después integrar simulación de downside

## 14. Próximo paso defendible

El próximo paso no es elegir algoritmo. El próximo paso es diseñar el `data model` del problema.

Entregable recomendado inmediato:

- diccionario de variables
- definición del target primario
- unidad de análisis
- ventana temporal
- reglas anti-leakage
- esquema de validación

Sin eso, cualquier modelado posterior tendrá más complejidad que credibilidad.
