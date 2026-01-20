# ==========================================
# VARIACION: PEQUEÑA 
# Rango: Tamaño Pequeño, Prueba Inicial
# ==========================================
configuraciones_estudio_peq = [
    {
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 5,           
            'link_chance': 60    
        }
    },
    {
        'tipo': 'cascada',
        'params': {
            'n_bloques': 5,     
            'nodos_por_bloque': 10
        }
    },
    {
        'tipo': 'flujo_libre',
        'params': {
            'n_nodos': 50       
        }
    },
    {
        'tipo': 'sbm',
        'params': {
            'n_total': 40,       
            'n_grupos': 8         
        }
    },
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 51,
            'm_neighbors': 2,     
            'p_triangle': 0.3,    
            'ratio_mutual': 0.5   
        }
    }
]