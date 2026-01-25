import networkx as nx
import igraph as ig
import pandas as pd

class ConvertidorGrafos:

    @staticmethod
    def a_igraph(G_nx):
        if G_nx is None:
            return None

        df_edges = nx.to_pandas_edgelist(G_nx)
        if not df_edges.empty:
            df_edges['source'] = df_edges['source'].astype(str)
            df_edges['target'] = df_edges['target'].astype(str)
    
        g_ig = ig.Graph.TupleList(
            df_edges.itertuples(index=False), 
            directed=G_nx.is_directed(), 
            edge_attrs=list(df_edges.columns[2:]) 
        )

        for n in G_nx.nodes():
            node_str = str(n)
            try:
                v = g_ig.vs.find(name=node_str)
            except ValueError:
                g_ig.add_vertex(name=node_str)
                v = g_ig.vs.find(name=node_str)
            attrs = G_nx.nodes[n].copy()
            for key, value in attrs.items():
                v[key] = value
            
        return g_ig

    @staticmethod
    def a_networkx(G_ig):
        
        edges = [(G_ig.vs[e.source]['name'], G_ig.vs[e.target]['name']) 
                 for e in G_ig.es]
        
        G_nx = nx.DiGraph() if G_ig.is_directed() else nx.Graph()
        G_nx.add_edges_from(edges)
        
        for v in G_ig.vs:
            nombre = v['name']
            atributos = v.attributes()
            del atributos['name'] 
            G_nx.nodes[nombre].update(atributos)
            
        return G_nx

