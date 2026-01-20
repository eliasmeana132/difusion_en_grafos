import pandas as pd
import plotly.express as px
import os

def _validar_y_cargar_datos(ruta_csv, columna_x, columnas_y):
    if not os.path.exists(ruta_csv):
        print(f"Error: Archivo no encontrado en {ruta_csv}")
        return None, None
    
    df = pd.read_csv(ruta_csv)
    columnas_validas = [col for col in columnas_y if col in df.columns]
    
    if not columnas_validas:
        print(f"Error: No se encontraron las columnas métricas. Disponibles: {df.columns.tolist()}")
        return None, None
        
    return df, columnas_validas

def _preparar_ruta_salida(directorio_salida, nombre_archivo):
    if directorio_salida:
        if not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)
        return os.path.join(directorio_salida, nombre_archivo)
    return nombre_archivo

def _finalizar_grafica(fig, ruta_completa, mostrar):
    fig.write_html(ruta_completa)
    print(f"Gráfica guardada exitosamente en: {ruta_completa}")
    if mostrar:
        fig.show()

def generar_grafica_interactiva(
    ruta_csv, 
    columna_x, 
    columnas_y, 
    directorio_salida=None, 
    nombre_archivo=None, 
    mostrar_grafica=False,
    titulo_grafica=None,
    etiqueta_x=None,
    etiqueta_y=None,
    etiqueta_leyenda="Variables",
    **kwargs
):
    df, columnas_validas = _validar_y_cargar_datos(ruta_csv, columna_x, columnas_y)
    if df is None: return

    df = df.sort_values(by=columna_x)

    fig = px.line(
        df, 
        x=columna_x, 
        y=columnas_validas,
        title=titulo_grafica or f"Relación {columna_x} vs {', '.join(columnas_validas)}",
        markers=True
    )

    fig.update_layout(
        xaxis_title=etiqueta_x or columna_x,
        yaxis_title=etiqueta_y or "Valores",
        legend_title=etiqueta_leyenda,
        hovermode="x unified"
    )

    nombre_archivo = nombre_archivo or f"grafica_{columna_x}.html"
    ruta_completa = _preparar_ruta_salida(directorio_salida, nombre_archivo)
    _finalizar_grafica(fig, ruta_completa, mostrar_grafica)
    
    return ruta_completa

def generar_grafica_barras(
    ruta_csv, 
    columna_x, 
    columnas_y, 
    directorio_salida=None, 
    nombre_archivo=None,
    titulo_grafica=None,
    titulo_eje_x=None,
    titulo_eje_y="Valor", 
    titulo_leyenda="Variables",
    modo_barras='group',
    formato_texto='.2f',
    ordenar_por=None,
    mapa_colores=None,
    ancho=None,
    alto=None,
    mostrar_graficas=False
):
    df, columnas_validas = _validar_y_cargar_datos(ruta_csv, columna_x, columnas_y)
    if df is None: return

    if ordenar_por and ordenar_por in df.columns:
        df = df.sort_values(by=ordenar_por)
    elif columna_x in df.columns:
        try:
            df = df.sort_values(by=columna_x)
        except:
            pass

    fig = px.bar(
        df, 
        x=columna_x, 
        y=columnas_validas,
        barmode=modo_barras,
        title=titulo_grafica or f"Comparación: {', '.join(columnas_validas)} vs {columna_x}",
        text_auto=formato_texto,
        color_discrete_sequence=mapa_colores,
        width=ancho,
        height=alto
    )

    fig.update_layout(
        xaxis_title=titulo_eje_x or columna_x,
        yaxis_title=titulo_eje_y,
        legend_title=titulo_leyenda,
        hovermode="x unified"
    )

    nombre_archivo = nombre_archivo or f"Barras_{columna_x}_{len(columnas_validas)}_vars.html"
    ruta_completa = _preparar_ruta_salida(directorio_salida, nombre_archivo)
    _finalizar_grafica(fig, ruta_completa, mostrar_graficas)

################################################################################
# Directorio Principal
################################################################################
directorio_salida='simulacion_masiva/simulaciones/Estudio_Multigrafo_2026-01-20_03-04-17/Graficas'

################################################################################
# Estudio Netlogo Nodos Crecientes
################################################################################
Estudio_Nodos_Crec_NETLOGO = 'simulacion_masiva/simulaciones/Estudio_Multigrafo_2026-01-20_03-04-17/Estudio_suc_netlogo/Metricas_Globales_Detalladas_1768874669.404449.csv'

generar_grafica_interactiva(
    Estudio_Nodos_Crec_NETLOGO, 
    'Total_Nodos_Inicial', 
    ['Nodos_Mojados_PEL', 'Nodos_Mojados_RIS'],
    nombre_archivo='Estudio_Nodos_Crec_PEL_v_RIS_NETLOGO.html',
    directorio_salida=directorio_salida,
    titulo_grafica='Impacto de Influencia: PEL vs RIS (Entorno NetLogo)',
    etiqueta_x='Cantidad de Nodos',
    etiqueta_y='Nodos Finales Alcanzados',
    etiqueta_leyenda='Algoritmo'
)

generar_grafica_interactiva(
    Estudio_Nodos_Crec_NETLOGO, 
    'Total_Nodos_Inicial', 
    ['Tiempo_Eje_PEL', 'Tiempo_Eje_RIS'],
    nombre_archivo='Estudio_Nodos_Crec_PEL_v_RIS_NETLOGO_Tiempo.html',
    directorio_salida=directorio_salida, 
    titulo_grafica='Rendimiento Temporal: PEL vs RIS (Entorno NetLogo)',
    etiqueta_x='Cantidad de Nodos',
    etiqueta_y='Tiempo de Ejecución (s)',
    etiqueta_leyenda='Algoritmo'
)

################################################################################
# Estudio Red Social Nodos Crecientes
################################################################################
Estudio_Nodos_Crec_RED_SOCIAL = 'simulacion_masiva/simulaciones/Estudio_Multigrafo_2026-01-20_03-04-17/Estudio_usuarios_crec/Metricas_Globales_Detalladas_1768875291.145752.csv'

generar_grafica_interactiva(
    Estudio_Nodos_Crec_RED_SOCIAL, 
    'Total_Nodos_Inicial', 
    ['Nodos_Mojados_PEL', 'Nodos_Mojados_RIS'],
    nombre_archivo='Estudio_Nodos_Crec_PEL_v_RIS_RED_SOCIAL.html',
    directorio_salida=directorio_salida,
    titulo_grafica='Difusión en Redes Sociales: PEL vs RIS',
    etiqueta_x='Usuarios Totales en la Red',
    etiqueta_y='Usuarios Influenciados',
    etiqueta_leyenda='Algoritmo'
)

generar_grafica_interactiva(
    Estudio_Nodos_Crec_RED_SOCIAL, 
    'Total_Nodos_Inicial', 
    ['Tiempo_Eje_PEL', 'Tiempo_Eje_RIS'],
    nombre_archivo='Estudio_Nodos_Crec_PEL_v_RIS_RED_SOCIAL_Tiempo.html',
    directorio_salida=directorio_salida,
    titulo_grafica='Escalabilidad Temporal en Redes Sociales',
    etiqueta_x='Usuarios Totales en la Red',
    etiqueta_y='Tiempo de Ejecución (s)',
    etiqueta_leyenda='Algoritmo'
)

################################################################################
# Estudio Grafos Pequeños
################################################################################
Estudio_Grafos_PEQ = 'simulacion_masiva/simulaciones/Estudio_Multigrafo_2026-01-20_03-04-17/Estudio_Peq/Promedios_Globales_Bateria_1768882530.635916.csv'

generar_grafica_barras(
    ruta_csv=Estudio_Grafos_PEQ, 
    columna_x='Tipo_Grafo', 
    columnas_y=['Ratio_Mojados_CELF', 'Ratio_Mojados_RIS','Ratio_Mojados_PEL'],
    directorio_salida='Reportes_Visuales',
    nombre_archivo='Estudio_Grafos_PEQ.html',
    titulo_eje_x='Configuración de Grafo Pequeño',
    titulo_eje_y='Ratio de Cobertura (Nodos Infectados)',
    titulo_grafica='Comparativa de Eficiencia en Grafos Pequeños: CELF vs RIS vs PEL',
    titulo_leyenda='Estrategia',
    formato_texto='.3f',
    modo_barras='group'
)

################################################################################
# Estudio Grafos Medianos
################################################################################
Estudio_Grafos_MED = 'simulacion_masiva/simulaciones/Estudio_Multigrafo_2026-01-20_03-04-17/Estudio_Med/Promedios_Globales_Bateria_1768884392.875998.csv'

generar_grafica_barras(
    ruta_csv=Estudio_Grafos_MED, 
    columna_x='Tipo_Grafo', 
    columnas_y=['Ratio_Mojados_CELF', 'Ratio_Mojados_RIS','Ratio_Mojados_PEL'],
    directorio_salida=directorio_salida,
    nombre_archivo='Estudio_Grafos_MED.html',
    titulo_eje_x='Configuración de Grafo Mediano',
    titulo_eje_y='Ratio de Cobertura (Nodos Infectados)',
    titulo_grafica='Comparativa de Eficiencia en Grafos Medianos: CELF vs RIS vs PEL',
    titulo_leyenda='Estrategia',
    formato_texto='.3f',
    modo_barras='group'
)

################################################################################
# Estudio Grafos Grandes
################################################################################
Estudio_Grafos_GRANDES = 'simulacion_masiva/simulaciones/Estudio_Multigrafo_2026-01-20_03-04-17/Estudio_Grande/Promedios_Globales_Bateria_1768886841.6734238.csv'

generar_grafica_barras(
    ruta_csv=Estudio_Grafos_GRANDES, 
    columna_x='Tipo_Grafo', 
    columnas_y=['Ratio_Mojados_RIS','Ratio_Mojados_PEL'],
    directorio_salida=directorio_salida,
    nombre_archivo='Estudio_Grafos_GRANDES.html',
    titulo_eje_x='Configuración de Grafo Grande',
    titulo_eje_y='Ratio de Cobertura (Nodos Infectados)',
    titulo_grafica='Análisis de Cobertura en Grafos de Gran Escala: RIS vs PEL',
    titulo_leyenda='Estrategia',
    formato_texto='.3f',
    modo_barras='group'
)

################################################################################
# Estudio Grafos Masivos
################################################################################
Estudio_Grafos_MASIVOS = 'simulacion_masiva/simulaciones/Estudio_Multigrafo_2026-01-20_03-04-17/Estudio_Masivo/Promedios_Globales_Bateria_1768894376.212388.csv'

generar_grafica_barras(
    ruta_csv=Estudio_Grafos_MASIVOS, 
    columna_x='Tipo_Grafo', 
    columnas_y=['Ratio_Mojados_RIS','Ratio_Mojados_PEL'],
    directorio_salida=directorio_salida,
    nombre_archivo='Estudio_Grafos_MASIVOS.html',
    titulo_eje_x='Configuración de Grafo Masivo',
    titulo_eje_y='Ratio de Cobertura (Nodos Infectados)',
    titulo_grafica='Análisis de Cobertura en Grafos Masivos: RIS vs PEL',
    titulo_leyenda='Estrategia',
    formato_texto='.3f',
    modo_barras='group'
)

################################################################################
# Estudio Redes Sociales Crecientes
################################################################################
Estudio_Nodos_Crec_RED_SOCIAL_2 = 'simulacion_masiva/simulaciones/Estudio_Multigrafo_2026-01-20_18-00-47/Estudio_RIS_PEL_RED_SOCIAL_NODOS_CREC/Metricas_Globales_Detalladas_1768928810.956746.csv'

generar_grafica_interactiva(
    Estudio_Nodos_Crec_RED_SOCIAL_2, 
    'Total_Nodos_Inicial', 
    ['Nodos_Mojados_PEL', 'Nodos_Mojados_RIS'],
    nombre_archivo='Estudio_Nodos_Crec_RED_SOCIAL_2.html',
    directorio_salida=directorio_salida,
    titulo_grafica='Propagación Escalable en Red Social (Fase II)',
    etiqueta_x='Población Total de Usuarios',
    etiqueta_y='Impacto de Cobertura Final',
    etiqueta_leyenda='Algoritmo'
)

generar_grafica_interactiva(
    Estudio_Nodos_Crec_RED_SOCIAL_2, 
    'Total_Nodos_Inicial', 
    ['Tiempo_Eje_PEL', 'Tiempo_Eje_RIS'],
    nombre_archivo='Estudio_Nodos_Crec_RED_SOCIAL_2_Tiempo.html',
    directorio_salida=directorio_salida,
    titulo_grafica='Análisis de Tiempos de Respuesta (Fase II)',
    etiqueta_x='Población Total de Usuarios',
    etiqueta_y='Tiempo de Ejecución (s)',
    etiqueta_leyenda='Algoritmo'
)