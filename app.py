import streamlit as st
import pandas as pd
import networkx as nx
import os
import plotly.graph_objects as go
from datetime import datetime

try:
    from difusion_lib import GeneradorRedes
    from simulacion_webapp import ProcesadorSimulacionesWeb
except ImportError:
    st.error("Could not import libraries. Make sure app.py is in the same folder as the library package and simulacion_webapp.py.")
    st.stop()

def plot_network_plotly(G, title="Graph Visualization"):
    pos = nx.spring_layout(G, dim=3, seed=42)
    x_nodes = [pos[k][0] for k in G.nodes()]
    y_nodes = [pos[k][1] for k in G.nodes()]
    z_nodes = [pos[k][2] for k in G.nodes()]
    
    x_edges = []
    y_edges = []
    z_edges = []
    
    for edge in G.edges():
        x_edges.extend([pos[edge[0]][0], pos[edge[1]][0], None])
        y_edges.extend([pos[edge[0]][1], pos[edge[1]][1], None])
        z_edges.extend([pos[edge[0]][2], pos[edge[1]][2], None])

    trace_edges = go.Scatter3d(
        x=x_edges, y=y_edges, z=z_edges,
        mode='lines', line=dict(color='black', width=1), hoverinfo='none'
    )
    trace_nodes = go.Scatter3d(
        x=x_nodes, y=y_nodes, z=z_nodes,
        mode='markers', marker=dict(size=5, color='skyblue', line=dict(color='black', width=0.5)),
        text=[str(n) for n in G.nodes()], hoverinfo='text'
    )
    layout = go.Layout(
        title=title, showlegend=False,
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
        margin=dict(t=40, b=0, l=0, r=0)
    )
    st.plotly_chart(go.Figure(data=[trace_edges, trace_nodes], layout=layout), use_container_width=True)

st.set_page_config(page_title="Diffusion Simulation Studio", layout="wide")
st.title("🕸️ Graph Diffusion Simulator")
st.markdown("Interactive interface for `difusion_lib`. Configure graphs, add multiple strategies, and analyze diffusion dynamics.")

if 'simulation_results' not in st.session_state:
    st.session_state['simulation_results'] = None
if 'execution_queue' not in st.session_state:
    st.session_state['execution_queue'] = []

with st.sidebar:
    st.header("Global Settings")
    n_simulaciones = st.number_input("Number of Simulations (N)", min_value=1, value=5)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    default_path = f"simulaciones/WebApp_{timestamp}"
    output_folder = st.text_input("Output Folder (Optional)", value=default_path)

tab_graph, tab_algo, tab_run = st.tabs(["1. Graph Configuration", "2. Strategy Builder", "3. Execution & Results"])

with tab_graph:
    st.subheader("Generate or Define Graph Topology")
    graph_type = st.selectbox("Select Graph Type", ["malla_netlogo", "red_social_realista", "cascada_estricta", "flujo_libre_escala"])
    params = {}
    col1, col2 = st.columns(2)
    
    if graph_type == "malla_netlogo":
        with col1: params['dim'] = st.number_input("Dimensions", min_value=2, value=10)
        with col2: params['link_chance'] = st.slider("Link Probability", 0, 100, 60)
    elif graph_type == "red_social_realista":
        with col1: 
            params['n_users'] = st.number_input("Users", min_value=10, value=100)
            params['m_neighbors'] = st.number_input("Neighbors", 1, 10, 2)
        with col2:
            params['p_triangle'] = st.slider("Triangle Prob", 0.0, 1.0, 0.3)
            params['ratio_mutual'] = st.slider("Mutual Edge Ratio", 0.0, 1.0, 0.05)
    elif graph_type == "cascada_estricta":
        with col1: params['n_bloques'] = st.number_input("Blocks", min_value=1, value=10)
        with col2: params['nodos_por_bloque'] = st.number_input("Nodes per Block", min_value=1, value=4)

    if st.button("Preview Graph"):
        try:
            with st.spinner("Generating preview..."):
                if graph_type == "malla_netlogo":
                    G = GeneradorRedes.generar_malla_estocastica_netlogo(dim=params['dim'], link_chance=params['link_chance'])
                elif graph_type == "red_social_realista":
                    G = GeneradorRedes.generar_red_social_realista(**params)
                elif graph_type == "cascada_estricta":
                    G = GeneradorRedes.generar_cascada_estricta(**params)
                else:
                    G = GeneradorRedes.generar_flujo_libre_escala(n_nodos=100)
                
                st.success(f"Graph Generated: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
                plot_network_plotly(G)
                st.session_state['graph_config'] = {'tipo': graph_type, 'params': params}
        except Exception as e:
            st.error(f"Error: {e}")

with tab_algo:
    st.subheader("Strategy Builder")
    col_add, col_list = st.columns([1, 2])
    
    with col_add:
        st.markdown("#### Add Strategy")
        strat_type = st.selectbox("Type", ["Peeling (PEL)", "RIS (Influence Max)", "CELF (Greedy)"])
        
        new_strat = {}
        if strat_type == "Peeling (PEL)":
            new_strat['pel'] = {
                'num_pelados': st.number_input("Steps", 1, 500, 50),
                'iteraciones_por_pelado': st.number_input("Iter/Step", 1, 1000, 150),
                'umbral_masa': st.number_input("Mass Threshold", 0.0, 10.0, 0.001, format="%.4f"),
                'umbral_nodos_final': st.number_input("Min Nodes", 1, 100, 2),
                'tasa_difusion': st.slider("Diff Rate", 0.0, 1.0, 0.5),
                'usar_cfc': st.checkbox("Use CFC", False)
            }
        elif strat_type == "RIS (Influence Max)":
            new_strat['ris'] = {
                'p': st.number_input("Prob (p)", 0.0, 1.0, 0.05),
                'mc': st.number_input("Monte Carlo Sims", 100, 10000, 1000),
                'k': st.number_input("K Seeds (0=Auto)", 0, 100, 0)
            }
        elif strat_type == "CELF (Greedy)":
            new_strat['celf'] = {
                'p': st.number_input("Prob (p)", 0.0, 1.0, 0.1),
                'mc': st.number_input("Monte Carlo Sims", 10, 1000, 100),
                'k': st.number_input("K Seeds (0=Auto)", 0, 100, 0)
            }
        
        if st.button("Add to Queue"):
            st.session_state['execution_queue'].append(new_strat)
            st.success("Added!")

    with col_list:
        st.markdown("#### Execution Queue")
        if not st.session_state['execution_queue']:
            st.info("No strategies added yet.")
        else:
            for i, item in enumerate(st.session_state['execution_queue']):
                key = list(item.keys())[0]
                st.text(f"{i+1}. {key.upper()}: {item[key]}")
            
            if st.button("Clear Queue"):
                st.session_state['execution_queue'] = []
                st.experimental_rerun()

with tab_run:
    st.subheader("Run Simulation")
    
    run_baseline = st.checkbox("Run Baseline (Peeling + Diffusion)", value=True)
    
    if not st.session_state.get('graph_config'):
        st.warning("Please configure graph in Tab 1.")
    elif not st.session_state['execution_queue'] and not run_baseline:
        st.warning("Please add strategies or enable Baseline.")
    else:
        if st.button("Launch Simulation", type="primary"):
            progress_bar = st.progress(0)
            try:
                procesador = ProcesadorSimulacionesWeb()
                graph_configs = [st.session_state['graph_config']]
                
                df_results, figs_dict = procesador.ejecutar_bateria_masiva(
                    configuraciones_grafos=graph_configs,
                    n_simulaciones=n_simulaciones,
                    execution_plan=st.session_state['execution_queue'],
                    master_folder=None,
                    exportar_resultados=False,
                    run_baseline=run_baseline
                )
                
                st.session_state['simulation_results'] = df_results
                progress_bar.progress(100)
                st.success("Done!")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if st.session_state['simulation_results'] is not None:
        st.divider()
        st.subheader("Results")
        df = st.session_state['simulation_results']
        
        if not df.empty:
            st.dataframe(df)
            st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), "results.csv", "text/csv")
            
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            if numeric_cols:
                col_x = st.selectbox("X Axis", df.columns, index=0)
                cols_y = st.multiselect("Y Axis (Compare)", numeric_cols, default=numeric_cols[:2] if len(numeric_cols)>1 else numeric_cols)
                
                if cols_y:
                    st.line_chart(df.set_index(col_x)[cols_y])