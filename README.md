# Difusión en Grafos (v1.0.2)

Una librería robusta de Python para la **simulación, análisis y visualización de procesos de difusión** en redes complejas. Este kit de herramientas permite estudiar la propagación de información o masa, aplicar algoritmos de maximización de influencia y realizar una descomposición estructural avanzada mediante el método de "Pelado" (Peeling).

## Características Principales

* **Motor de Difusión (Sparse):** Implementación eficiente basada en matrices dispersas de `scipy.sparse` para simular la propagación de valores entre nodos.
* **Algoritmos de Influencia:** * **CELF (Cost-Effective Lazy Forwarding):** Optimización para modelos de cascada independiente.
    * **RIS (Reverse Influence Sampling):** Muestreo eficiente para redes de gran escala.
* **Estudio de Pelado (Peeling):** Algoritmo propio para identificar nodos críticos mediante la eliminación sucesiva de componentes basados en su acumulación de masa.
* **Generador de Redes:** Creación de diversos modelos como Redes de Flujo Libre de Escala, Cascadas Estrictas, Mallas Estocásticas y Redes Sociales Realistas.
* **Visualización 3D Interactiva:** Generación de dashboards en Plotly que permiten explorar la topología de la red y los resultados de difusión en un entorno tridimensional.

## 🛠️ Instalación

Puedes clonar este repositorio y asegurarte de tener instaladas las dependencias necesarias:

```bash
pip install networkx numpy scipy pandas plotly python-igraph
