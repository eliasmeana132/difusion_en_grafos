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
# ==========================================
# VARIACION: Mediana 
# Rango: Tamaño Mediano
# ==========================================
configuraciones_estudio_med = [
    {
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 20,           
            'link_chance': 60    
        }
    },
    {
        'tipo': 'cascada',
        'params': {
            'n_bloques': 15,     
            'nodos_por_bloque': 70
        }
    },
    {
        'tipo': 'flujo_libre',
        'params': {
            'n_nodos': 500       
        }
    },
    {
        'tipo': 'sbm',
        'params': {
            'n_total': 400,       
            'n_grupos': 8         
        }
    },
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 1001,
            'm_neighbors': 2,     
            'p_triangle': 0.3,    
            'ratio_mutual': 0.5   
        }
    }
]

# ==========================================
# NIVEL 3: GRANDE 
# Rango: 2,500 - 5,000 Nodos
# ==========================================
configuraciones_estudio_grande = [
    {
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 50,           
            'link_chance': 55    
        }
    },
    {
        'tipo': 'cascada',
        'params': {
            'n_bloques': 50,     
            'nodos_por_bloque':5
        }
    },
    {
        'tipo': 'flujo_libre',
        'params': {
            'n_nodos': 3000       
        }
    },
    {
        'tipo': 'sbm',
        'params': {
            'n_total': 3000,       
            'n_grupos': 15        
        }
    },
    {
        'tipo': 'gaussiana',
        'params': {
            'n_nodos': 1000,      
            'radius': 0.08        
        }
    },
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 5000,
            'm_neighbors': 3,     
            'p_triangle': 0.25,    
            'ratio_mutual': 0.3   
        }
    }
]

# ==========================================
# NIVEL 4: MASIVO 
# Rango: 10,000 - 25,000 Nodos
# CELF BASICAMENTE NO VA
# ==========================================
configuraciones_estudio_masivo = [
    {
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 150,          
            'link_chance': 60     
        }
    },
    {
        'tipo': 'cascada',
        'params': {
            'n_bloques': 100,     
            'nodos_por_bloque': 100 
        }
    },
    {
        'tipo': 'flujo_libre',
        'params': {
            'n_nodos': 15000       
        }
    },
    {
        'tipo': 'sbm',
        'params': {
            'n_total': 10000,       
            'n_grupos': 50        # Many small communities
        }
    },
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 20000,
            'm_neighbors': 2,     
            'p_triangle': 0.1,    
            'ratio_mutual': 0.1   
        }
    }
]

# ==========================================
# VARIACION: ALTA DENSIDAD (Topology Test)
# Rango: Tamaño Medio, pero muchas aristas
# ==========================================
configuraciones_estudio_denso = [
    {
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 20,           
            'link_chance': 95    # Almost fully connected grid
        }
    },
    {
        'tipo': 'flujo_libre',
        'params': {
            'n_nodos': 500
        }
    },
    {
        'tipo': 'sbm',
        'params': {
            'n_total': 400,       
            'n_grupos': 4         
        }
    },
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 500,
            'm_neighbors': 10,   
            'p_triangle': 0.8,   
            'ratio_mutual': 0.8   
        }
    }
]


# ==========================================
# VARIACION: Grafo Creciente NETLOGO
# Rango: Tamaño PEQ-MED
# ==========================================
configuraciones_estudio_suc_netlogo = [
    {
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 5,           
            'link_chance': 60    
        }
    },{
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 10,           
            'link_chance': 60    
        }
    },{
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 15,           
            'link_chance': 60    
        }
    },{
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 20,           
            'link_chance': 60    
        }
    },{
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 25,           
            'link_chance': 60    
        }
    },{
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 30,           
            'link_chance': 60    
        }
    },{
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 35,           
            'link_chance': 60    
        }
    },{
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 40,           
            'link_chance': 60    
        }
    },{
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 45,           
            'link_chance': 60    
        }
    },{
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 50,           
            'link_chance': 60    
        }
    },{
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 55,           
            'link_chance': 60    
        }
    },
]

# ==========================================
# VARIACION: Usuarios Crecientes RED SOCIAL
# Rango: Tamaño PEQ-MED
# ==========================================
configuraciones_estudio_red_usuarios_crec = [
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': n,
            'm_neighbors': 2,
            'p_triangle': 0.8,
            'ratio_mutual': 0.8
        }
    } for n in range(50, 10000, 50)
] 

# ==========================================
# VARIACION: Conecciones Crecientes RED SOCIAL
# Rango: Tamaño PEQ-MED
# ==========================================
configuraciones_estudio_red_con_crec=[
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 5000,
            'm_neighbors': m,
            'p_triangle': 0.8,
            'ratio_mutual': 0.8
        }
    } for m in range(25, 1025, 100)
]

configuraciones_estudio_RIS_umbral_min_250k = [
        {
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 500,           
            'link_chance': 60    
        }
    },
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 250000,
            'm_neighbors': 2,
            'p_triangle': 0.8,
            'ratio_mutual': 0.8
        }
    }
    
]

configuraciones_estudio_RIS_umbral_min_1000k = [
    {
        'tipo': 'malla_netlogo',
        'params': {
            'dim': 1000,           
            'link_chance': 60    
        }
    },
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 1000000,
            'm_neighbors': 2,
            'p_triangle': 0.8,
            'ratio_mutual': 0.8
        }
    }
    
]