import streamlit as st
import pandas as pd
import networkx as nx
import os
import time
import shutil
from datetime import datetime
import plotly.graph_objects as go

# Import your library
# We wrap this in try-except to handle cases where the folder structure isn't perfect
try:
    from difusion_lib import (
        ProcesadorSimulaciones, 
        GeneradorRedes, 
        VisualizadorPelado,
        ControladorPelado
    )
except ImportError:
    st.error("Could not import 'difusion_lib'. Make sure app.py is in the same folder as the library package.")
    st.stop()

# --- HELPER FUNCTIONS FOR VISUALIZATION ---
def plot_network_plotly(G, title="Graph Visualization"):
    """
    Creates an interactive 3D or 2D plot of the graph using Plotly.
    """
    # Use spring layout for 3D positioning
    pos = nx.spring_layout(G, dim=3, seed=42)
    
    # Extract node coordinates
    x_nodes = [pos[k][0] for k in G.nodes()]
    y_nodes = [pos[k][1] for k in G.nodes()]
    z_nodes = [pos[k][2] for k in G.nodes()]
    
    # Extract edge coordinates
    x_edges = []
    y_edges = []
    z_edges = []
    
    for edge in G.edges():
        x_edges.extend([pos[edge[0]][0], pos[edge[1]][0], None])
        y_edges.extend([pos[edge[0]][1], pos[edge[1]][1], None])
        z_edges.extend([pos[edge[0]][2], pos[edge[1]][2], None])

    # Trace for edges
    trace_edges = go.Scatter3d(
        x=x_edges, y=y_edges, z=z_edges,
        mode='lines',
        line=dict(color='black', width=1),
        hoverinfo='none'
    )

    # Trace for nodes
    trace_nodes = go.Scatter3d(
        x=x_nodes, y=y_nodes, z=z_nodes,
        mode='markers',
        marker=dict(size=5, color='skyblue', line=dict(color='black', width=0.5)),
        text=[str(n) for n in G.nodes()],
        hoverinfo='text'
    )

    layout = go.Layout(
        title=title,
        showlegend=False,
        scene=dict(
            xaxis=dict(showbackground=False, showticklabels=False, title=''),
            yaxis=dict(showbackground=False, showticklabels=False, title=''),
            zaxis=dict(showbackground=False, showticklabels=False, title='')
        ),
        margin=dict(t=40, b=0, l=0, r=0)
    )

    fig = go.Figure(data=[trace_edges, trace_nodes], layout=layout)
    st.plotly_chart(fig, use_container_width=True)

# --- MAIN APP UI ---

st.set_page_config(page_title="Diffusion Simulation Studio", layout="wide")
st.title("🕸️ Graph Diffusion Simulator")
st.markdown("Interactive interface for `difusion_lib`. Configure graphs, set simulation parameters, and analyze diffusion dynamics.")

# Sidebar for Global Settings
with st.sidebar:
    st.header("Global Settings")
    n_simulaciones = st.number_input("Number of Simulations (N)", min_value=1, value=5, help="How many times to repeat the experiment.")
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    default_path = f"simulaciones/WebApp_{timestamp}"
    output_folder = st.text_input("Output Folder", value=default_path)

# Tabs for workflow
tab_graph, tab_algo, tab_run = st.tabs(["1. Graph Configuration", "2. Algorithm Settings", "3. Execution & Results"])

# --- TAB 1: GRAPH CONFIGURATION ---
with tab_graph:
    st.subheader("Generate or Define Graph Topology")
    
    graph_type = st.selectbox(
        "Select Graph Type",
        ["malla_netlogo", "red_social_realista", "cascada_estricta", "flujo_libre_escala"]
    )
    
    params = {}
    
    col1, col2 = st.columns(2)
    
    if graph_type == "malla_netlogo":
        with col1:
            params['dim'] = st.number_input("Dimensions (Grid Size)", min_value=2, value=10)
        with col2:
            params['link_chance'] = st.slider("Link Probability (%)", 0, 100, 60)
            
    elif graph_type == "red_social_realista":
        with col1:
            params['n_users'] = st.number_input("Number of Users", min_value=10, value=100)
            params['m_neighbors'] = st.number_input("Neighbors per node", min_value=1, value=2)
        with col2:
            params['p_triangle'] = st.slider("Triangle Prob", 0.0, 1.0, 0.3)
            params['ratio_mutual'] = st.slider("Mutual Edge Ratio", 0.0, 1.0, 0.05)

    elif graph_type == "cascada_estricta":
        with col1:
            params['n_bloques'] = st.number_input("Number of Blocks", min_value=1, value=10)
        with col2:
            params['nodos_por_bloque'] = st.number_input("Nodes per Block", min_value=1, value=4)

    # Preview Button
    if st.button("Preview Graph Topology"):
        try:
            with st.spinner("Generating preview..."):
                # Call the specific generator from your library based on selection
                if graph_type == "malla_netlogo":
                    G_preview = GeneradorRedes.generar_malla_estocastica_netlogo(dim=params['dim'], link_chance=params['link_chance'])
                elif graph_type == "red_social_realista":
                    G_preview = GeneradorRedes.generar_red_social_realista(**params)
                elif graph_type == "cascada_estricta":
                    G_preview = GeneradorRedes.generar_cascada_estricta(**params)
                else:
                    # Fallback for scale free
                    G_preview = GeneradorRedes.generar_flujo_libre_escala(n_nodos=100)

                st.success(f"Graph Generated: {len(G_preview.nodes())} nodes, {len(G_preview.edges())} edges")
                plot_network_plotly(G_preview)
                
                # Store config for later use
                st.session_state['graph_config'] = {
                    'tipo': graph_type,
                    'params': params
                }
        except Exception as e:
            st.error(f"Error generating graph: {e}")

# --- TAB 2: ALGORITHM SETTINGS ---
with tab_algo:
    st.subheader("Define Simulation Plan")
    st.info("Configure the algorithms (strategies) you want to test on the graph.")
    
    plan_completo = []
    
    # Peeling Strategy (PEL)
    with st.expander("Strategy 1: Peeling (PEL)", expanded=True):
        enable_pel = st.checkbox("Enable Peeling Strategy", value=True)
        if enable_pel:
            c1, c2, c3 = st.columns(3)
            pel_params = {
                'num_pelados': c1.number_input("Num Pelados (Steps)", value=50),
                'iteraciones_por_pelado': c2.number_input("Iterations per Step", value=150),
                'tasa_difusion': c3.number_input("Diffusion Rate", 0.0, 1.0, 0.5),
                'umbral_masa': c1.number_input("Mass Threshold", value=0.001, format="%.4f"),
                'umbral_nodos_final': c2.number_input("Min Nodes Stop", value=2),
                'valor_inicio': 1.0,
                'usar_cfc': c3.checkbox("Use CFC (Strongly Connected)", value=False),
                'exportar_resultados': True,
                'generar_visualizaciones': False, # Keep false for speed in web app
                'mostrar_graficos': False,
                'carpeta_exportacion': output_folder,
                'nombre_resumen': "reporte_pelado.csv"
            }
            plan_completo.append({'pel': pel_params})

    # RIS Strategy
    with st.expander("Strategy 2: RIS (Influence Maximization)"):
        enable_ris = st.checkbox("Enable RIS Strategy", value=False)
        if enable_ris:
            r1, r2 = st.columns(2)
            ris_params = {
                'p': r1.number_input("Probability (p)", 0.0, 1.0, 0.1),
                'mc': r2.number_input("Monte Carlo Simulations", value=1000)
            }
            plan_completo.append({'ris': ris_params})

    # CELF Strategy
    with st.expander("Strategy 3: CELF"):
        enable_celf = st.checkbox("Enable CELF Strategy", value=False)
        if enable_celf:
            k_seeds = st.number_input("K Seeds", value=5)
            plan_completo.append({'celf': {'k': k_seeds, 'p': 0.1, 'mc': 1000}})

    st.write("### Current Execution Plan:")
    st.json(plan_completo)
    st.session_state['execution_plan'] = plan_completo

# --- TAB 3: EXECUTION ---
with tab_run:
    st.subheader("Run Simulation")
    
    if 'graph_config' not in st.session_state:
        st.warning("Please configure and preview a graph in Tab 1 first.")
    elif not st.session_state['execution_plan']:
        st.warning("Please select at least one strategy in Tab 2.")
    else:
        if st.button("🚀 Launch Simulation", type="primary"):
            
            # Prepare directory
            if os.path.exists(output_folder):
                shutil.rmtree(output_folder) # Clean previous run if same name
            os.makedirs(output_folder, exist_ok=True)
            
            # Setup Progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Initialize Processor
                procesador = ProcesadorSimulaciones()
                
                # Wrap graph config in list as expected by ejecutar_bateria_masiva
                graph_configs = [st.session_state['graph_config']]
                
                status_text.text("Running batch simulation... check terminal for detailed logs.")
                
                # EXECUTE
                # We are calling the method seen in simulacion_demo_2.py
                procesador.ejecutar_bateria_masiva(
                    configuraciones_grafos=graph_configs,
                    n_simulaciones=n_simulaciones,
                    execution_plan=st.session_state['execution_plan'],
                    master_folder=output_folder
                )
                
                progress_bar.progress(100)
                st.success("Simulation Complete!")
                
                # --- RESULTS DISPLAY ---
                st.divider()
                st.subheader("📊 Results Analysis")
                
                # Find generated CSVs
                results_found = False
                for root, dirs, files in os.walk(output_folder):
                    for file in files:
                        if file.endswith(".csv"):
                            results_found = True
                            file_path = os.path.join(root, file)
                            
                            st.write(f"**File:** `{file}`")
                            df = pd.read_csv(file_path)
                            
                            # Interactive Dataframe
                            st.dataframe(df.head())
                            
                            # Simple plotting if numeric columns exist
                            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                            if len(numeric_cols) > 0:
                                col_x = st.selectbox(f"X-Axis ({file})", df.columns, index=0, key=f"x_{file}")
                                col_y = st.selectbox(f"Y-Axis ({file})", numeric_cols, index=min(1, len(numeric_cols)-1), key=f"y_{file}")
                                st.line_chart(df.set_index(col_x)[col_y])
                            
                            # Download Button
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label=f"Download {file}",
                                    data=f,
                                    file_name=file,
                                    mime="text/csv"
                                )
                                
                if not results_found:
                    st.warning("No CSV files were found in the output folder. Check the logs or parameters.")

            except Exception as e:
                st.error(f"An error occurred during execution: {str(e)}")
                st.exception(e)