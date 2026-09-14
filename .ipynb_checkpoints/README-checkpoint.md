<div align="center">
  <!-- Asegúrate de tener tu imagen 'dashboard_banner.png' dentro de la carpeta 'reports/figures/' -->
  <img src="reports/figures/dashboard_banner.png" alt="Dashboard Interactivo de Ventas" width="1000" />
  
  <h1>🛒 Dynamic Sales Prediction Engine</h1>
  <p><i>End-to-End Decision Intelligence: From Raw Data to Mathematical Optimization</i></p>

  <!-- BOTONES INTERACTIVOS -->
  <!-- IMPORTANTE: Reemplaza "TU_URL_AQUI" con el link real de Streamlit cuando lo despliegues en la nube -->
  <a href="TU_URL_AQUI">
    <img src="https://img.shields.io/badge/Streamlit-Ver_App_en_Vivo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live App" />
  </a>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3" />
</div>

El desarrollo de este ecosistema analítico sigue rigurosamente el **Método Científico** aplicado a los negocios, transformando datos crudos transaccionales en estrategias operativas óptimas.

## 🔬 1. Observación y Planteamiento (El Problema)
Las sucursales de supermercados generan grandes volúmenes de datos diariamente, pero frecuentemente fallan en traducir la información histórica en decisiones comerciales futuras.
*   **Pregunta de Investigación:** ¿Cómo podemos proyectar matemáticamente la demanda a 30 días y utilizar esa predicción para maximizar el retorno de inversión (ROI) del inventario, sujetos a restricciones físicas y financieras reales?

## 🧪 2. Hipótesis y Experimentación (Metodología)
*Hipótesis:* La integración secuencial de modelos de series de tiempo con programación lineal permitirá automatizar la toma de decisiones de inventario, superando la rentabilidad de la intuición humana tradicional. El experimento se divide en tres fases de código (`/notebooks/`):

*   **Fase 1 (Analítica Descriptiva):** Limpieza de datos (ETL) y Análisis Exploratorio (EDA). 
    *   *📌 Hallazgo Estadístico:* El análisis de distribución reveló una perfecta integridad de datos (0 nulos), pero una fuerte asimetría positiva (*Right-Skewed*) en las variables financieras, indicando transacciones atípicas de alto valor. Esta distribución no normal es la base que justifica la selección algorítmica de la siguiente fase.
*   **Fase 2 (Analítica Predictiva):** Entrenamiento de un algoritmo de Inteligencia Artificial (*Meta Prophet*) para proyectar la demanda futura. Se eligió este modelo específicamente por su robustez ante los valores atípicos y la asimetría descubierta en la Fase 1.
*   **Fase 3 (Analítica Prescriptiva):** Implementación de un motor de optimización matemática (`PuLP`) que receta la compra exacta de unidades para maximizar ganancias sin exceder el presupuesto ($) ni la capacidad física del almacén (m³).

## 📊 3. Análisis de Resultados (Deployment)
Los resultados del experimento se refutaron y validaron mediante la creación de una aplicación web interactiva bilingüe (`Streamlit`).
*   **Inferencia Dinámica:** Las predicciones de demanda se recalculan en tiempo real dependiendo de los cortes dimensionales (filtros de sucursal, género, tipo de cliente) que el usuario elija.
*   **Asignación de Recursos:** El modelo demuestra la capacidad de distribuir el capital de forma exacta, encontrando el máximo global absoluto de rentabilidad proyectada en milisegundos.

## 🚀 4. Reproducibilidad y Ejecución
Para replicar las condiciones de este experimento en un entorno local y ejecutar el código fuente:

1. Clonar este repositorio.
2. Activar tu entorno virtual y asegurar la instalación de las dependencias exactas:
   ```bash
   pip install -r requirements.txt