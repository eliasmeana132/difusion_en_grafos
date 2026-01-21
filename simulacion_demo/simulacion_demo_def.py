# ==========================================
# VARIACION: PEQUEÑA 
# Rango: 100-750
# ==========================================
configuraciones_estudio_peq = [
    {
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 10,           
            'link_chance': 60    
        }
    },
    {
        'tipo': 'cascada',
        'params': {
            'n_bloques': 10,     
            'nodos_por_bloque': 10
        }
    },
    {
        'tipo': 'flujo_libre',
        'params': {
            'n_nodos': 100       
        }
    },
    {
        'tipo': 'sbm',
        'params': {
            'n_total': 100,       
            'n_grupos': 4        
        }
    },
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 100,
            'm_neighbors': 2,     
            'p_triangle': 0.3,    
            'ratio_mutual': 0.5   
        }
    }
]