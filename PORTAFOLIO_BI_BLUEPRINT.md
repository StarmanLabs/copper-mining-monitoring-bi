# Blueprint de Dashboard para Tableau o Power BI

## Objetivo

Convertir el modelo de riesgo de cobre en un producto analítico que responda preguntas de negocio, no solo en un ejercicio de simulación.

El dashboard debe permitir:

- evaluar creación o destrucción de valor
- entender drivers económicos y operativos
- visualizar downside y colas de riesgo
- monitorear el perfil anual del proyecto
- comparar benchmark Excel versus motor Python

## Estructura recomendada del dashboard

### 1. Vista Ejecutiva

KPIs principales:

- `Base NPV`
- `Expected NPV`
- `Probability of Loss`
- `VaR 5%`
- `CVaR 5%`
- `Benchmark Gap`

Visuales:

- tarjetas KPI
- velocímetro o bullet chart para probabilidad de pérdida
- comparación Python vs Excel

Fuente principal:

- `dashboard_kpis.csv`
- `simulation_summary.csv`
- `excel_benchmark_metrics.csv`

### 2. Perfil Económico del Proyecto

Preguntas:

- ¿Cómo evoluciona el flujo económico del proyecto a través del horizonte?
- ¿En qué años se concentra la generación de valor?

Visuales:

- línea de `Revenue`, `EBITDA`, `Free Cash Flow`
- barras de `Capex`
- línea de `Discounted FCF`

Fuente principal:

- `annual_profile_long.csv`

Métricas sugeridas:

- `revenue_usd`
- `opex_usd`
- `ebitda_usd`
- `taxes_usd`
- `capex_usd`
- `free_cash_flow_usd`
- `discounted_fcf_usd`

### 3. Riesgo y Distribución

Preguntas:

- ¿Qué tan asimétrica es la distribución del VAN?
- ¿Qué tan severa es la cola izquierda?

Visuales:

- histograma de `npv_usd`
- CDF del VAN
- banda de percentiles
- scatter de factores simulados versus VAN

Fuente principal:

- `simulation_distribution.csv`
- `simulation_cdf.csv`

Segmentadores útiles:

- rangos de `price_factor`
- rangos de `grade_factor`
- rangos de `recovery_factor`

### 4. Drivers y Supuestos

Preguntas:

- ¿Qué supuestos estructuran el modelo?
- ¿Qué valores operativos y financieros están imponiéndose?

Visuales:

- tabla de parámetros
- matriz de inputs anuales
- small multiples de precio, ley, recuperación y throughput

Fuente principal:

- `assumptions.csv`
- `annual_inputs.csv`
- `historical_prices.csv`
- `operational_history.csv`

### 5. Benchmark y Validación

Preguntas:

- ¿Qué tanto se parece la versión Python al workbook original?
- ¿Dónde están las principales diferencias?

Visuales:

- tabla de benchmark Python vs Excel
- línea de CDF Python vs Excel
- tarjeta de gap de NPV base

Fuente principal:

- `dashboard_kpis.csv`
- `excel_benchmark_distribution.csv`
- `simulation_cdf.csv`

## Modelo semántico sugerido

### Tabla de hechos principal

`annual_profile_long.csv`

Campos clave:

- `year`
- `metric`
- `value`

Ventaja:

permite construir gráficos dinámicos por métrica sin rehacer el modelo de datos en BI.

### Tablas auxiliares

- `dashboard_kpis.csv`
- `simulation_distribution.csv`
- `simulation_summary.csv`
- `assumptions.csv`
- `annual_inputs.csv`

## KPIs recomendados para portafolio

Los KPIs más potentes para mostrar valor analítico son:

- `Base NPV`
- `Expected NPV`
- `Downside Gap = Expected NPV - VaR`
- `Loss Probability`
- `Revenue Peak Year`
- `FCF Peak Year`
- `Average Net Price`
- `Average Head Grade`
- `Average Recovery`

## Qué hace que el dashboard se vea serio

No lo presentes como un panel genérico de BI. Preséntalo como sistema de apoyo a decisión.

La narrativa correcta es:

1. el activo parece rentable en el caso base
2. la distribución probabilística revela fragilidad
3. el downside no depende solo del precio
4. la capa Python permite trazabilidad, refresh y escalabilidad hacia monitoreo dinámico

## Siguiente evolución funcional

Para que el proyecto pase de portafolio a producto funcional:

- incorporar selector de escenarios `bull/base/bear`
- incorporar refresh automático desde CSV o base tabular
- agregar target de seguimiento trimestral si luego construyes panel histórico mina-periodo
- separar claramente `supuestos`, `resultado base`, `resultado simulado` y `benchmark`
