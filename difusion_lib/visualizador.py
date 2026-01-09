import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
import plotly.graph_objects as go

class VisualizadorPelado:
    @staticmethod
    def generar_figura_3d(G, titulo):
        if len(G.nodes()) == 0: return None
        pos_3d = nx.spring_layout(G, dim=3, seed=42, k=0.15)
        
        edge_x, edge_y, edge_z = [], [], []
        a_x, a_y, a_z = [], [], [] 
        a_u, a_v, a_w = [], [], [] 

        for edge in G.edges():
            x0, y0, z0 = pos_3d[edge[0]]
            x1, y1, z1 = pos_3d[edge[1]]
            
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])

            vx, vy, vz = x1 - x0, y1 - y0, z1 - z0
            length = np.sqrt(vx**2 + vy**2 + vz**2)
            
            if length > 0:
                a_x.append(x0 + 0.8 * vx)
                a_y.append(y0 + 0.8 * vy)
                a_z.append(z0 + 0.8 * vz)
                
                a_u.append(vx / length)
                a_v.append(vy / length)
                a_w.append(vz / length)

        trace_edges = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z, 
            line=dict(width=1, color='#888'), 
            hoverinfo='none', mode='lines',
            name='Aristas'
        )

        trace_arrows = go.Cone(
            x=a_x, y=a_y, z=a_z,
            u=a_u, v=a_v, w=a_w,
            sizeref=0.05,       
            anchor="tail",
            showscale=False,
            colorscale=[[0, '#666'], [1, '#666']], 
            opacity=0.6,
            name='Dirección'
        )

        masas = [G.nodes[n]['val'] for n in G.nodes()]
        trace_nodes = go.Scatter3d(
            x=[pos_3d[n][0] for n in G.nodes()],
            y=[pos_3d[n][1] for n in G.nodes()],
            z=[pos_3d[n][2] for n in G.nodes()],
            mode='markers',
            marker=dict(
                symbol='circle', 
                size=[2 + (m * 8) for m in masas], 
                color=masas, 
                colorscale='YlOrRd',
                line=dict(color='black', width=0.5),
                colorbar=dict(title='Masa', thickness=15)
            ),
            text=[f"Nodo: {n}<br>Masa: {m:.4f}" for n, m in zip(G.nodes(), masas)],
            hoverinfo='text',
            name='Nodos'
        )

        fig = go.Figure(data=[trace_edges, trace_arrows, trace_nodes])
        fig.update_layout(
            title=titulo,
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode='data' 
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            showlegend=False
        )
        return fig

    @staticmethod
    def renderizar_3d(G, titulo, ruta_base):
        fig = VisualizadorPelado.generar_figura_3d(G, titulo)
        if fig:
            ruta_3d = os.path.join(ruta_base, "renders_3d")
            os.makedirs(ruta_3d, exist_ok=True)
            titulo_archivo = titulo.replace(' ', '_')
            fig.write_html(os.path.join(ruta_3d, f"{titulo_archivo}.html"))

    @staticmethod
    def exportar_dashboard_interactivo(figuras_lista, titulos_lista, ruta_base, nombre_archivo="dashboard_interactivo.html"):
        if not figuras_lista: return

        fig_final = go.Figure()
        traces_por_fig = [len(f.data) for f in figuras_lista]
        total_traces = sum(traces_por_fig)
        
        current_trace_idx = 0
        botones = []

        for i, (fig, titulo) in enumerate(zip(figuras_lista, titulos_lista)):
            num_traces = len(fig.data)
            for trace in fig.data:
                trace.visible = (i == 0)
                fig_final.add_trace(trace)

            visibilidad = [False] * total_traces
            for j in range(current_trace_idx, current_trace_idx + num_traces):
                visibilidad[j] = True

            botones.append(dict(
                label=titulo,
                method="update",
                args=[{"visible": visibilidad},
                      {"title": f"Visualización: {titulo}"}]
            ))
            current_trace_idx += num_traces

        fig_final.update_layout(
            updatemenus=[{
                "buttons": botones,
                "direction": "down",
                "showactive": True,
                "x": 0.05, "xanchor": "left",
                "y": 1.1, "yanchor": "top"
            }],
            title=titulos_lista[0],
            scene=dict(xaxis=dict(showbackground=False),
                       yaxis=dict(showbackground=False),
                       zaxis=dict(showbackground=False))
        )

        ruta_final = os.path.join(ruta_base, nombre_archivo)
        fig_final.write_html(ruta_final)

    @staticmethod
    def renderizar(G, titulo, ruta_base, exportar_gephi=True, mostrar_grafico=False, 
                  k_layout=None, alfa_aristas=0.3, tamano_flecha=15):
        if len(G.nodes()) == 0: return
        
        ruta_imagenes = os.path.join(ruta_base, "imagenes_grafos")
        ruta_gephi = os.path.join(ruta_base, "archivos_gephi")
        os.makedirs(ruta_imagenes, exist_ok=True)
        if exportar_gephi: os.makedirs(ruta_gephi, exist_ok=True)

        plt.figure(figsize=(14, 10))
        k_val = k_layout if k_layout else 0.3 
        posicion = nx.spring_layout(G, k=k_val, seed=42)
        
        masas = [G.nodes[n]['val'] for n in G.nodes()]
        tamanos = [100 + (m * 300) for m in masas] 
        
        nodos = nx.draw_networkx_nodes(G, posicion, node_size=tamanos, node_color=masas, 
                                       cmap=plt.cm.YlOrRd, edgecolors='black', linewidths=0.8)
        
        nx.draw_networkx_edges(G, posicion, alpha=alfa_aristas, arrows=True, arrowsize=tamano_flecha,
                               arrowstyle='-|>', edge_color='gray', connectionstyle='arc3,rad=0.1')
        
        nx.draw_networkx_labels(G, posicion, font_size=8, font_family='sans-serif', font_weight='bold')
        plt.colorbar(nodos, label='Masa Acumulada')
        plt.title(titulo, fontsize=15)
        plt.axis('off')
        
        titulo_archivo = titulo.replace(' ', '_')
        plt.savefig(os.path.join(ruta_imagenes, f"{titulo_archivo}.png"), dpi=300, bbox_inches='tight')

        if exportar_gephi:
            G_export = G.copy()
            for n in G_export.nodes():
                G_export.nodes[n]['masa'] = float(G_export.nodes[n]['val'])
            nx.write_gexf(G_export, os.path.join(ruta_gephi, f"{titulo_archivo}.gexf"))

        if mostrar_grafico: plt.show()
        else: plt.close()