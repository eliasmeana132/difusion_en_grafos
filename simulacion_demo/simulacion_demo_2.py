from datetime import datetime
import os
from difusion_lib import ProcesadorSimulaciones,GeneradorRedes
from simulacion_demo_def import configuraciones_estudio_peq

if __name__ == "__main__":
    marca_tiempo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path_estudio = f"simulacion_demo/simulaciones/Estudio_Multigrafo_{marca_tiempo}"
    
    procesador = ProcesadorSimulaciones()
    
    G=GeneradorRedes.generar_malla_estocastica_netlogo(
        dim=20,
        link_chance=60
    )
    
    generar_visualizaciones=False
    generar_visualizaciones_pel=False
    plan_completo = [
        {
            'ris': {
                'p': 0.02,
                'mc': 2000
            }},
        {
            'pel': {
                'num_pelados': 50,
                'iteraciones_por_pelado': 200,
                'umbral_masa': 0.001,
                'umbral_nodos_final': 2,
                'tasa_difusion': 0.5,  
                'valor_inicio': 1.0,  
                'usar_cfc': False,

                'generar_visualizaciones': generar_visualizaciones,
                'mostrar_graficos': False,
                'exportar_resultados': True,
                'carpeta_exportacion': "simulaciones/debug_deep_dive",
                'nombre_resumen': "reporte_custom_pelado.csv"
            }},
        {
            'pel': {
                'num_pelados': 500,
                'iteraciones_por_pelado': 200,
                'umbral_masa': 1,
                'umbral_nodos_final': 2,
                'tasa_difusion': 0.5, 
                'valor_inicio': 1.0,  
                'usar_cfc': False,

                'generar_visualizaciones': generar_visualizaciones,
                'mostrar_graficos': False,
                'exportar_resultados': True,
                'carpeta_exportacion': "simulaciones/debug_deep_dive",
                'nombre_resumen': "reporte_custom_pelado.csv"
            }
            
        },
        {
            'pel': {
                'num_pelados': 500,
                'iteraciones_por_pelado': 200,
                'umbral_masa': 0.1,
                'umbral_nodos_final': 2,
                'tasa_difusion': 0.5, 
                'valor_inicio': 1.0,  
                'usar_cfc': False,

                'generar_visualizaciones': generar_visualizaciones,
                'mostrar_graficos': False,
                'exportar_resultados': True,
                'carpeta_exportacion': "simulaciones/debug_deep_dive",
                'nombre_resumen': "reporte_custom_pelado.csv"
            }
            
        }
    ]

    umbral_nodos=2
    n_sim=10
    procesador.ejecutar_bateria_masiva(
        # metodos=['pel'],
        configuraciones_grafos=configuraciones_estudio_peq,
        n_simulaciones=n_sim,
        execution_plan=plan_completo,
        # graph=G,
        # num_pelados=1000,
        master_folder=f"{path_estudio}/Estudio_Grafos_PEQ",
        # default_iteraciones_pelado=iteraciones_por_pelado=0,
        exportar_resultados=True,
        usar_cfc=False,
        tasa_difusion=0.4,
        generar_visualizaciones=generar_visualizaciones,
        generar_visualizaciones_pelado=generar_visualizaciones,
        iteraciones_difusion=150,
        default_umbral_nodos=umbral_nodos,
    )