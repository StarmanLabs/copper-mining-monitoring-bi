# Diseño de Target, Datos y Validación para el Modelo de Riesgo

## Respuesta corta a tu duda

Sí: para que el modelo sea serio, la base del sistema debe usar `datos reales observados`.

Pero no toda la arquitectura usa el mismo tipo de dato:

- `datos reales` para estimar relaciones, monitorear deterioro y validar desempeño
- `supuestos calibrados` para variables no observables directamente o para horizontes largos
- `simulación` para escenarios y downside, nunca como sustituto de evidencia empírica

La regla es simple: `no voy a entrenar ni validar el modelo final con datos inventados`.

Los datos sintéticos solo sirven para:

- probar pipelines
- hacer stress testing
- expandir escenarios condicionales
- correr Monte Carlo sobre parámetros ya calibrados

## 1. Qué tipo de sistema recomiendo construir

No recomiendo un único modelo plano. Recomiendo una arquitectura en tres capas.

### Capa A: base empírica observada

Panel histórico por mina y periodo con:

- mercado observado
- operación observada
- variables geológicas conocidas ex ante o reconciliadas según fecha
- resultado real del periodo

Esta capa es la base para:

- monitoreo
- predicción de deterioro
- validación empírica

### Capa B: traducción económica

Motor que convierta outcomes operativos en:

- cash cost
- margen
- flujo de caja
- VAN simplificado o rolling

Aquí puede convivir evidencia real con fórmulas económico-financieras.

### Capa C: simulación y downside

Motor de escenarios para:

- precio
- ley
- recuperación
- throughput
- shocks operativos

Esta capa no reemplaza la evidencia empírica. La extiende.

## 2. Qué datos deben ser reales

### Mercado

Esto sí debe ser real desde el inicio:

- precio del cobre
- tipo de cambio
- energía si es relevante al costo
- insumos importantes si impactan materialmente el cash cost

Ejemplos de uso:

- series históricas mensuales
- régimen de precios
- shocks extremos

### Operación

Esto también debe ser real si el modelo quiere decir algo sobre riesgo operativo:

- toneladas procesadas
- recuperación metalúrgica
- ley de cabeza procesada
- disponibilidad de planta
- utilización
- paradas no programadas
- cash cost o costo unitario si existe

Si estas variables no existen históricamente, no es honesto vender el resultado como un modelo predictivo operativo.

### Geología

Aquí hay que ser mucho más severos.

Variables geológicas útiles:

- ley planificada
- ley reconciliada
- desviación plan vs real
- dureza
- mineralogía
- strip ratio
- indicadores de variabilidad espacial

Problema central:

muchas variables geológicas no están disponibles de forma homogénea entre minas o solo se conocen ex post. Eso obliga a separar:

- `información conocida al inicio del periodo`
- `información conocida después de procesar`

Si no hacemos esa separación, aparece leakage.

## 3. Qué datos pueden ser supuestos calibrados

Hay variables que pueden entrar como supuestos, siempre que se documenten.

Ejemplos:

- ramp-up de expansión
- vida de mina futura
- recuperación en zonas todavía no explotadas
- escenarios de costo futuro
- curvas de producción de largo plazo

Eso no es un problema, pero entonces hay que decir con precisión:

- qué parte es observada
- qué parte es ingeniería/planeamiento
- qué parte es juicio experto

## 4. Qué parte puede ser sintética o simulada

Solo usaría datos sintéticos en tres casos.

### Caso 1: pruebas técnicas

Para probar ETL, paneles, uniones y validaciones de código.

### Caso 2: stress testing

Ejemplo:

- caída extrema del cobre
- deterioro simultáneo de ley y recuperación
- shock de throughput por mantenimiento

### Caso 3: Monte Carlo

Pero solo si las distribuciones salen de:

- historia real
- benchmarking creíble
- rangos de ingeniería
- juicio experto explícito

Si la simulación no está calibrada, el resultado deja de ser “riesgo estimado” y pasa a ser solo “escenario ilustrativo”.

## 5. Target primario recomendado

Te propongo partir con un target observable y útil.

### Opción recomendada

`Incumplimiento económico-operativo del plan a horizonte trimestral`

Definición ejemplo:

Una observación `mina-trimestre` entra en estado de riesgo si ocurre al menos una de estas condiciones:

- throughput real < 90% del plan
- recuperación real < plan - umbral técnico
- cash cost real > plan + umbral
- margen operativo real < 0

Esto tiene varias ventajas:

- es observable
- mezcla economía y operación de forma interpretable
- se puede validar
- no depende solo del precio

### Forma del target

Recomiendo dos versiones en paralelo:

- `target binario`: incumplió / no incumplió
- `target continuo`: severidad del shortfall

Ejemplos de target continuo:

- porcentaje de shortfall del margen
- desviación porcentual del EBITDA
- pérdida económica respecto al plan

## 6. Unidad de análisis recomendada

### Si habrá varias minas

La unidad recomendada es:

`mina-trimestre`

Por qué no mensual desde el inicio:

- mensual puede ser demasiado ruidoso si los datos públicos son pobres
- trimestral suele alinearse mejor con reporting corporativo
- trimestral reduce ruido operativo de muy corto plazo

### Si el proyecto arranca con una sola mina

La unidad seguirá siendo:

`activo-trimestre`

Pero en ese caso hay que decir que el sistema no es un modelo cross-mine todavía, sino un motor específico de monitoreo y riesgo para ese activo.

## 7. Tabla maestra recomendada

Estructura sugerida:

- `mine_id`
- `country`
- `company`
- `date_period`
- `price_copper_start_period`
- `fx_start_period`
- `planned_throughput`
- `actual_throughput`
- `planned_head_grade`
- `actual_head_grade`
- `planned_recovery`
- `actual_recovery`
- `planned_cash_cost`
- `actual_cash_cost`
- `planned_margin`
- `actual_margin`
- `downtime_hours`
- `strip_ratio`
- `ore_hardness`
- `reconciliation_grade_gap`
- `risk_target_binary`
- `risk_target_severity`

### Variables rezagadas importantes

Además incluiría:

- `lag_1` y `lag_2` de throughput
- `lag_1` y `lag_2` de recovery
- `lag_1` y `lag_2` de head grade
- volatilidad reciente del precio

Eso ayuda a capturar deterioro sin usar información futura.

## 8. Reglas anti-leakage

Esto es no negociable.

### Regla 1

Cada feature debe estar disponible al inicio del periodo que se quiere predecir.

### Regla 2

La reconciliación ex post no entra como predictor contemporáneo si aún no era conocida al momento de decisión.

### Regla 3

No usar promedios anuales cerrados para predecir dentro del mismo año.

### Regla 4

No mezclar datos planificados de largo plazo con outcomes ya realizados sin marcar fecha de disponibilidad.

## 9. Validación que sí usaría

### Para predicción

- train/test por tiempo
- backtesting rodante
- validación leave-one-mine-out si hay suficientes minas
- métricas de clasificación y calibración
- comparación con benchmarks simples

### Métricas recomendadas

- Brier score
- precision en cola de riesgo
- recall sobre incumplimientos materiales
- calibración por deciles de riesgo
- MAE o RMSE solo para la severidad continua, no como única métrica

### Para decisión

Además de métricas estadísticas:

- porcentaje de eventos adversos capturados en el decil superior de riesgo
- mejora frente a reglas heurísticas
- utilidad operativa de la alerta

## 10. Si no hay suficientes datos reales

Aquí es donde hay que bajar ambición.

### Escenario A: hay buenos datos de precio, pero poca operación

Entonces el proyecto debe presentarse como:

- modelo de downside económico bajo escenarios

No como predictor operativo.

### Escenario B: hay datos operativos de una sola mina

Entonces el proyecto debe presentarse como:

- sistema de monitoreo y alerta para un activo específico

No como modelo general de minas de cobre.

### Escenario C: hay varias minas, pero geología pobre

Entonces haría:

- modelo empírico mercado + operación
- módulo geológico como capa de escenarios o covariables parciales

No vendería una inteligencia geológica que los datos no sostienen.

## 11. Estrategia práctica de implementación

Yo lo haría en este orden.

### Fase 1: MVP con datos reales mínimos

Usar:

- precio real del cobre
- throughput real
- ley real o proxy consistente
- recuperación real
- margen o cash cost real

Objetivo:

- predecir shortfall trimestral frente a plan

### Fase 2: enriquecer con geología

Agregar:

- reconciliación
- dureza
- strip ratio
- información de planeamiento

Objetivo:

- separar deterioro de calidad del mineral vs deterioro de ejecución

### Fase 3: integrar simulación

Usar el motor tipo workbook actual para:

- estresar el sistema
- medir downside económico
- traducir probabilidad de deterioro a pérdida monetaria

## 12. Conclusión operativa

La respuesta honesta es esta:

- `sí`, usaría datos reales para la base del modelo
- `no`, no usaría datos sintéticos para entrenar o validar el riesgo final
- `sí`, usaría simulación para escenarios y VAN
- `sí`, usaría supuestos calibrados donde el horizonte excede la evidencia observada

La calidad final del proyecto dependerá de cuánta historia real tengas por mina, por periodo y por variable.

Si los datos reales son limitados, no forzaría un modelo predictivo ambicioso. Lo bajaría a un sistema híbrido de monitoreo + simulación, que en este dominio suele ser más serio que un ML sobredimensionado.
