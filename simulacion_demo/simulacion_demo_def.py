# ==========================================
# VARIACION: PEQUEÑA 
# Rango: 100-750
# ==========================================
configuraciones_estudio_peq = [
    {
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 25,           
            'link_chance': 60    
        }
    },
    {
        'tipo': 'cascada',
        'params': {
            'n_bloques': 15,     
            'nodos_por_bloque': 50
        }
    },
    {
        'tipo': 'flujo_libre',
        'params': {
            'n_nodos': 600       
        }
    },
    {
        'tipo': 'sbm',
        'params': {
            'n_total': 654,       
            'n_grupos': 8         
        }
    },
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 500,
            'm_neighbors': 2,     
            'p_triangle': 0.3,    
            'ratio_mutual': 0.5   
        }
    }
]