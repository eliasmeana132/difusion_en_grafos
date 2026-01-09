import networkx as nx

class AnalizadorPelado:
    @staticmethod
    def obtener_metricas_cfc(G, version_pelado, total_nodos_original):
        if G.is_directed():
            componentes = list(nx.strongly_connected_components(G))
        else:
            componentes = list(nx.connected_components(G))
        resultados = []
        for i, nodos in enumerate(componentes):
            masa = sum(G.nodes[n]['val'] for n in nodos)
            es_trivial = len(nodos) == 1 and not G.has_edge(list(nodos)[0], list(nodos)[0])
            resultados.append({
                'capa_pelado': version_pelado + 1,
                'id_componente': f"P{version_pelado+1}_C{i}",
                'nodos': sorted(list(nodos)),
                'tamano': len(nodos),
                'es_trivial': es_trivial,
                'masa_total': masa,
                'impacto_global': masa / total_nodos_original if total_nodos_original > 0 else 0
            })
        return sorted(resultados, key=lambda x: x['masa_total'], reverse=True)