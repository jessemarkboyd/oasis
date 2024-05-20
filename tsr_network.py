"""Plot network of transmission rights."""
import networkx as nx
import pandas as pd
from pyvis.network import Network
from tkinter import filedialog
import tkinter as tk


def plot_tsr_network(df, customer, dt=pd.Timestamp(year=2024, month=1, day=1)):
    """Find the components of the network of transmission rights owned by a customer and plot them."""
    # Create a directional network of transmission rights
    G = nx.MultiDiGraph()
    tsr_df = df[df['Customer'] == customer]
    tsr_df.to_csv('Network Data.csv')
    tsr_df = tsr_df[tsr_df['MW Grant'] > 0]
    tsr_df = tsr_df[(tsr_df['Start Time'] <= dt) & (dt <= tsr_df['Stop Time'])]
    tsr_df = tsr_df.groupby(['TP', 'POD', 'POR', 'Path']).agg({
        'MW Grant': 'sum',  # Sum the values in 'MW Grant'
        'Assign Ref': lambda x: ','.join(x.astype(str))  # Concatenate the strings in 'Assign Ref'
    }).reset_index()
    for i, row in tsr_df.iterrows():
        G.add_edge(row['POR'], row['POD'], **{'MW': row['MW Grant'], 'TP': row['TP'], 'Path': row['Path'],
                                              'Assigned Ref': row['Assign Ref']})
    # Find the component networks
    components = nx.weakly_connected_components(G)
    # Plot each component as a subgraph
    for i, component in enumerate(components):
        subgraph = G.subgraph(component)

        # Create a PyVis network from the existing MultiDiGraph
        net = Network(notebook=False, directed=True)
        # net.from_nx(subgraph)
        # # Adjust the physics layout to spread out nodes (optional)
        net.toggle_physics(False)
        net.set_options("""
        {
          "nodes": {
            "physics": false
          },
          "interaction": {
            "dragNodes": true,
            "dragView": true,
            "zoomView": true
          }
        }
        """)

        # Manually add nodes and edges to allow setting edge labels
        for node in subgraph.nodes():
            net.add_node(node)

        # Manually add edges to control widths based on 'MW Grant'
        for source, target, data in subgraph.edges(data=True):
            width = data.get('MW', 1)  # Default to 1 if 'MW Grant' not found
            tp = data.get('TP', 'Unknown')
            path = data.get('Path', 'Unknown')
            ref = data.get('Assigned Ref')
            title = f"{path} {tp}--{ref}: {width} MW"  # Tooltip title
            label = str(width) + ' MW'  # Optionally set label to 'MW Grant' value
            # Add edge with specified width, title (for tooltip), and label
            net.add_edge(source, target, title=title, width=width * 0.005, label=label)
        # Generate and save the interactive plot to an HTML file
        net.show(f'my_graph_{i}.html')


if __name__ == '__main__':
    root = tk.Tk()
    tsr_csv = filedialog.askopenfilename(title='Select the Oasis TSR csv (post-processed)',
                                         filetypes=[('Comma Delimited', '*.csv')])
    root.destroy()
    tsr_df = pd.read_excel(tsr_csv, header=None)
