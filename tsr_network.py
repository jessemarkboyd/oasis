"""Plot network of transmission rights."""
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


def plot_tsr_network(df, customer, dt=pd.Timestamp(year=2024, month=1, day=1)):
    """Find the components of the network of transmission rights owned by a customer and plot them."""
    # Create a directional network of transmission rights
    G = nx.MultiDiGraph()
    tsr_df = df[df['Customer'] == customer]
    # G['Customer'] = customer
    # G['Year'] = year
    tsr_df = tsr_df[(tsr_df['Start Time'] <= dt) & (dt <= tsr_df['Stop Time'])]
    for i, row in tsr_df.iterrows():
        G.add_edge(row['POR'], row['POD'], **row.to_dict())
    # Find the component networks
    components = nx.weakly_connected_components(G)
    # Plot each component as a subgraph
    for i, component in enumerate(components):
        subgraph = G.subgraph(component)
        # Compute the layout
        pos = nx.spring_layout(subgraph, seed=42)
        edge_widths = {}
        for u, v in subgraph.edges():
            edge_widths[(u,v)] = subgraph.edges
        edge_widths = [subgraph.edges[u][v]['MW Grant'] * 0.01 for u, v in subgraph.edges()]

        # To handle multiple edges and their widths, iterate over each edge including keys
        # Draw the graph
        nx.draw_networkx_nodes(subgraph, pos, node_color='lightblue', node_size=200)
        nx.draw_networkx_labels(subgraph, pos)
        nx.draw_networkx_edges(subgraph, pos , edgelist=subgraph.edges(), width=[w * 0.1 for w in avg_weights.values()],
        #                        arrowstyle='-|>', arrowsize=10, edge_color='gray')
        # edge_widths = [subgraph[u][v]['mw'] * 0.1 for u, v in subgraph.edges()]
        # # Draw the graph
        # nx.draw_networkx(G, pos, arrows=True, node_size=700, width=edge_widths, arrowsize=20, node_color='lightblue',
        #                  edge_color='gray')
        # nx.draw(subgraph, with_labels=True, node_color=f"C{i}")

    # def networkx_plot(self, bus_list):
    #     self.H = self.G.subgraph(bus_list)
    #     relabel_dict = dict(zip(tuple(self.H.nodes), [n.EXNAME for n in list(self.H.nodes)]))
    #     self.H = nx.relabel_nodes(self.H, relabel_dict)
    #     nx.draw_networkx(self.H, with_labels=True,
    #                      node_color=[self.H.nodes.data()[node_name]['color'] if 'color' in self.H.nodes.data()[node_name] else 'purple' for node_name in self.H.nodes])
    #
    # def networkx_get_neighboring_buses(self, bus, x: int) -> list:
    #     neighbors = [bus]
    #     new_neighbors = neighbors
    #     while len(new_neighbors) > 0:
    #         for n in neighbors:
    #             new_neighbors = [x for x in self.G.neighbors(n) if x not in neighbors]
    #         neighbors.extend(new_neighbors)
    #     return neighbors

