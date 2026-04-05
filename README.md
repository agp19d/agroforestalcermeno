# Agroforestal Cermeño — Planificador Financiero de Producción de Café

Aplicación web Streamlit para productores de café que permite modelar costos de producción, volúmenes de producción, ingresos y rentabilidad bajo diferentes escenarios financieros — incluyendo análisis de riesgo con simulación Monte Carlo. Todos los valores monetarios están en **Balboas panameños (B/.)**.

## Características

- **Modelado de Producción** — estima la cosecha de cereza, rendimiento de café verde y producción final en libras para tres tipos de producto: crudo (verde), procesado (lavado/natural/honey) y tostado.
- **Control Completo de Costos** — mano de obra (permanente y temporal), insumos y materiales, procesamiento, tueste, empaque, terreno, gastos generales, impuestos y contingencia.
- **Proyecciones de Ingresos** — precio por libra para cada tipo de grano con cálculo automático de ingresos.
- **Análisis de Rentabilidad** — ganancia bruta/neta, márgenes, costo por libra, punto de equilibrio, ingresos y ganancia por hectárea, y gráfico de cascada de ingresos a ganancia neta.
- **Gestión de Escenarios** — guardar, cargar, eliminar y comparar múltiples escenarios lado a lado con tablas y gráficos de barras.
- **Simulación Monte Carlo** — modela la incertidumbre muestreando entradas clave desde distribuciones triangulares a través de miles de iteraciones. Resultados incluyen:
  - Indicador de probabilidad de pérdida
  - Histogramas con líneas de media, P5 y P95
  - Gráfico de función de distribución acumulada (CDF)
  - Tabla de estadísticas resumidas (media, desviación estándar, percentiles)

## Estructura del Proyecto

```
├── app.py              # Punto de entrada — conecta panel lateral, motor y tablero
├── config.py           # Constantes, valores predeterminados, paleta de colores
├── models.py           # Dataclass FinancialResults y motor de cálculo
├── simulation.py       # Motor de simulación Monte Carlo
├── scenarios.py        # Persistencia de escenarios en JSON
├── formatting.py       # Utilidades de formato de moneda, porcentaje y números
├── ui/
│   ├── __init__.py
│   ├── sidebar.py      # Widgets de entrada del panel lateral
│   ├── dashboard.py    # KPIs del área principal, tablas y gráficos Plotly
│   └── montecarlo.py   # Configuración y gráficos de Monte Carlo
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.10+
- Dependencias listadas en `requirements.txt`

## Primeros Pasos

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/agp19d/agroforestalcermeno.git
   cd agroforestalcermeno
   ```

2. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**

   ```bash
   streamlit run app.py
   ```

   La aplicación se abrirá en su navegador en `http://localhost:8501`.

## Uso

1. Ajuste las entradas en el **panel lateral** — tamaño de finca, estimaciones de rendimiento, asignación de producción, mano de obra, materiales, costos de procesamiento, gastos generales y precios de venta.
2. Vea los resultados en tiempo real en el **área principal** a través de seis pestañas: Producción, Ingresos, Costos, Rentabilidad, Comparar Escenarios y Monte Carlo.
3. Guarde escenarios con un nombre, luego cárguelos o compárelos después.
4. En la pestaña **Monte Carlo**, configure rangos de incertidumbre para variables clave, ejecute la simulación y revise las distribuciones de probabilidad e indicadores de riesgo.

## Categorías de Entrada

| Categoría | Ejemplos |
|---|---|
| Finca y Terreno | hectáreas totales, hectáreas productivas, costo de terreno |
| Rendimiento | rendimiento de cereza por hectárea, ratio cereza-verde, ratio verde-tostado |
| Asignación de Producción | % vendido como verde, procesado o tostado |
| Mano de Obra | trabajadores permanentes, temporales, salarios, prestaciones |
| Insumos y Materiales | fertilizante, pesticidas, plántulas, agua, herramientas, combustible |
| Procesamiento y Tueste | costo de procesamiento/lb, costo de tueste/lb, costo de empaque/lb |
| Gastos Generales y Fijos | transporte, certificaciones, administración, seguros, mantenimiento, mercadeo, préstamos, depreciación |
| Financiero | tasa de impuestos, reserva de contingencia |
| Precios de Venta | precio por libra para café verde, procesado y tostado |

## Licencia

Este proyecto es proporcionado tal cual para uso privado de Agroforestal Cermeño.
