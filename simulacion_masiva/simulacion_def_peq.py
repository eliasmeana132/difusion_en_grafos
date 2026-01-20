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
            'dim': 50,           # 50x50 = 2,500 nodes
            'link_chance': 55    
        }
    },
    {
        'tipo': 'cascada',
        'params': {
            'n_bloques': 50,     
            'nodos_por_bloque': 50 # Total: 2,500 nodes
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
            'n_grupos': 15        # More groups to maintain community structure
        }
    },
    {
        'tipo': 'gaussiana',
        'params': {
            'n_nodos': 1000,      # Geometric graphs get very heavy with edges
            'radius': 0.08        # Lower radius to prevent it becoming a single blob
        }
    },
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 5000,
            'm_neighbors': 3,     # Slightly more connectivity
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
            'dim': 150,           # 150x150 = 22,500 nodes
            'link_chance': 45     # Lower chance to keep it sparse enough to run
        }
    },
    {
        'tipo': 'cascada',
        'params': {
            'n_bloques': 100,     
            'nodos_por_bloque': 100 # Total: 10,000 nodes
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
            'p_triangle': 0.1,    # Lower triangle prob to simulate loose connections
            'ratio_mutual': 0.1   
        }
    }
    # Note: Gaussiana excluded from massive because distance calc is O(N^2)
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
            'n_nodos': 500,
            # Note: You might need to edit generator to accept 'm' parameter
            # If hardcoded, this acts like normal flow
        }
    },
    {
        'tipo': 'sbm',
        'params': {
            'n_total': 400,       
            'n_grupos': 4         # Fewer groups = larger, denser communities
        }
    },
    {
        'tipo': 'red_social_realista',
        'params': {
            'n_users': 500,
            'm_neighbors': 10,    # Each new node connects to 10 existing ones (Very Dense)
            'p_triangle': 0.8,    # High clustering
            'ratio_mutual': 0.8   
        }
    }
]