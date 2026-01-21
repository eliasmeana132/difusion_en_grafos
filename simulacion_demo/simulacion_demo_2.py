from datetime import datetime
import os
from difusion_lib import ProcesadorSimulaciones
from simulacion_demo_def import configuraciones_estudio_peq

if __name__ == "__main__":
    marca_tiempo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path_estudio = f"simulacion_demo/simulaciones/Estudio_Multigrafo_{marca_tiempo}"
    
    procesador = ProcesadorSimulaciones()
    
    procesador.ejecutar_bateria_masiva(
        metodos=['pel', 'celf','ris'],
        configuraciones_grafos=configuraciones_estudio_peq,
        n_simulaciones=1,
        master_folder=f"{path_estudio}/Estudio_Grafos_PEQ",
        iteraciones_por_pelado=10,
        tasa_difusion=0.4,
        generar_visualizaciones=True,
        generar_visualizaciones_pelado=False,
        iteraciones_difusion=150,
        umbral_nodos_final=2,
        params_metodos={
            'celf': {
                'p': 0.05,
                'mc': 300
            },
            'ris': {
                'p': 0.02,
                'mc': 2000
            }
        }
    )
