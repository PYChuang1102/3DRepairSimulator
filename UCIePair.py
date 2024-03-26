import time

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import find_path as fp

def create_layered_graph():
    G = nx.DiGraph()
    first_layer = ['f' + str(i) for i in range(0, 32)]
    second_layer = ['s0'] + ['i' + str(i) for i in range(0, 32)] + ['s1']
    sub_second_layer = ['sub_' + node for node in second_layer]
    third_layer = ['g' + str(i) for i in range(0, 32)]

    # Connecting first layer to second layer
    for i, node in enumerate(first_layer):
        if i == 0:
            connections = ['i0', 's0', 'i1']
        elif i == 31:
            connections = ['i31', 'i30', 's1']
        else:
            connections = ['i' + str(i), 'i' + str(i - 1), 'i' + str(i + 1)]
        for conn in connections:
            # Determine the weight based on the node names and new rule
            if conn.startswith('i'):
                if 'i' + str(i) in conn:  # Direct connection to itself
                    weight = 0
                elif conn == 'i' + str(i - 1):  # Connection to i-1
                    weight = 1 if (i + 1) <= (32 - i) else 2
                elif conn == 'i' + str(i + 1):  # Connection to i+1
                    weight = 1 if (i + 1) >= (32 - i) else 2
            else:
                weight = 1  # Default weight for connections to 's0' or 's1'

            # add edge between F and (I+S)
            G.add_edge('f' + str(i), conn, capacity=1, weight = weight)

    for node, sub_node in zip(second_layer, sub_second_layer):
        # add edge between (I+S) and sub_(I+S)
        G.add_edge(node, sub_node, capacity=1, weight=0)

    # Connecting second layer to third layer
    for i, node in enumerate(third_layer):
        if i == 0:
            connections = ['sub_i0', 'sub_s0', 'sub_i1']
        elif i == 31:
            connections = ['sub_i31', 'sub_i30', 'sub_s1']
        else:
            connections = ['sub_i' + str(i), 'sub_i' + str(i - 1), 'sub_i' + str(i + 1)]
        for conn in connections:
            # Determine the weight based on the node names and new rule
            if conn.startswith('sub_i'):
                if 'sub_i' + str(i) in conn:  # Direct connection to itself
                    weight = 0
                elif conn == 'sub_i' + str(i - 1):  # Connection to i-1
                    weight = 1 if (i + 1) <= (32 - i) else 2
                elif conn == 'sub_i' + str(i + 1):  # Connection to i+1
                    weight = 1 if (i + 1) >= (32 - i) else 2
            else:
                weight = 1  # Default weight for connections to 's0' or 's1'
            # add edge between G and sub_(I+S)
            G.add_edge(conn, 'g' + str(i), capacity=1, weight=weight)

    return G

def is_bidirectional(G, u, v):
    return G.has_edge(v, u) and G.has_edge(u, v)

def fault_injection(G, faulty_edges=None):
    for edge in faulty_edges:
        if G.has_edge(*edge):
            # Set the capacity of the edge to zero
            G[edge[0]][edge[1]]['capacity'] = 0
        else:
            print(f"Edge {edge} not found in the graph.")
    return G

def inject_faults_by_nodes(G, nodes=None):
    faulty_edges = []

    for node in nodes:
        # Get edges connected to this node (both incoming and outgoing)
        edges = list(G.in_edges(node)) + list(G.out_edges(node))
        faulty_edges.extend(edges)

    # Remove duplicates from the list, if any
    faulty_edges = list(set(faulty_edges))

    # Now, use the fault_injection function to mark these edges as faulty
    fault_injection(G, faulty_edges)

def visualize_graph(G, flow_dict):

    positions = {}
    y_offsets = {'source': 0, 'first_layer': 50, 'second_layer': 100,'sub_second_layer': 150, 'third_layer': 200, 'sink': 250}
    first_layer = ['f' + str(i) for i in range(0, 32)]
    second_layer = ['s0'] + ['i' + str(i) for i in range(0, 32)] + ['s1']
    sub_second_layer = ['sub_' + node for node in second_layer]
    third_layer = ['g' + str(i) for i in range(0, 32)]

    # Positioning the first layer
    for i, node in enumerate(first_layer):
        positions[node] = (i * 30 - 480, y_offsets['first_layer'])
    # Positioning the second layer
    for i, node in enumerate(second_layer):
        positions[node] = (i * 30 - 510, y_offsets['second_layer'])
    # Positioning the second layer
    for i, node in enumerate(sub_second_layer):
        positions[node] = (i * 30 - 510, y_offsets['sub_second_layer'])
    # Positioning the third layer
    for i, node in enumerate(third_layer):
        positions[node] = (i * 30 - 480, y_offsets['third_layer'])

    # Visualization settings
    plt.figure(figsize=(30, 15))
    # Custom colors and shapes for each layer
    colors = {'source': 'lightgray', 'first_layer': 'lightsteelblue', 'second_layer': 'khaki', 'sub_second_layer': 'khaki', 'third_layer': 'lightsteelblue',
              'sink': 'lightgray'}
    shapes = {'source': 's', 'first_layer': 'o', 'second_layer': 'o', 'sub_second_layer': 'o', 'third_layer': 'o',
              'sink': 's'}  # s-square, o-circle, ^-triangle, d-diamond

    # draw the gray rectangular for 2 dies
    fi_x, fi_y = (positions[first_layer[0]][0]-30, positions[first_layer[0]][1])
    gi_x, gi_y = (positions[third_layer[0]][0]-30, positions[third_layer[0]][1])

    fi_width = 30 * 33
    gi_width = 30 * 33
    height = 70

    rect_fi = patches.Rectangle((fi_x, fi_y - height / 2), fi_width, height, linewidth=0, edgecolor='none',
                                facecolor='lightgray', zorder=0)
    rect_gi = patches.Rectangle((gi_x, gi_y - height / 2), gi_width, height, linewidth=0, edgecolor='none',
                                facecolor='lightgray', zorder=0)
    plt.gca().add_patch(rect_fi)
    plt.gca().add_patch(rect_gi)

    # draw nodes
    for node in G.nodes:
        color = 'gray'
        shape = 'o'
        if node in ['source', 'sink']:
            color = colors[node]
            shape = shapes[node]
        elif node.startswith('f'):
            color = colors['first_layer']
            shape = shapes['first_layer']
        elif node.startswith('sub_i'):
            color = colors['sub_second_layer']
            shape = shapes['sub_second_layer']
        elif node.startswith('sub_s') :
            color = 'pink'
            shape = '^'
        elif node.startswith('i'):
            color = colors['second_layer']
            shape = shapes['second_layer']
        elif node.startswith('s') :
            color = 'pink'
            shape = '^'
        elif node.startswith('g'):
            color = colors['third_layer']
            shape = shapes['third_layer']

        if node.startswith('f') and all(flow == 0 for flow in flow_dict[node].values()):
            color = 'salmon'
        if node.startswith('g') and all(flow_dict[neighbor].get(node, 0) == 0 for neighbor in G.predecessors(node)):
            color = 'salmon'
        if node != 'source' and node != 'sink':
            nx.draw_networkx_nodes(G, positions, nodelist=[node], node_color=color, node_shape=shape, node_size=300)

    # draw edges
    for u, v, attr in G.edges(data=True):
        flow = flow_dict[u][v] if u in flow_dict and v in flow_dict[u] else 0
        color = 'springgreen' if flow == 1 else 'dimgray'
        color = 'dodgerblue' if (G[u][v]['weight'] >=1 and flow==1) else color
        color = 'red' if G[u][v]['capacity'] == 0 else color
        width = 3 if (color == 'springgreen' or color == 'dodgerblue') else 1
        width = 3 if color == 'red' else width

        # make detoured interconnect be blue
        for _, to, outgoing_attr in G.out_edges(v, data=True):
            outgoing_flow = flow_dict[v][to] if v in flow_dict and to in flow_dict[v] else 0
            if G[v][to]['weight'] >= 1 and outgoing_flow == 1:
                color = 'dodgerblue'
                width = 3
                break

        if is_bidirectional(G, u, v):
            connectionstyle = 'arc3,rad=0.2'
        else:
            connectionstyle = 'arc3,rad=0'
        nx.draw_networkx_edges(G, positions, edgelist=[(u, v)], width=width, edge_color=color, connectionstyle=connectionstyle, arrowsize=10)

    # Node labels
    nodes_to_draw = [node for node in G.nodes() if node not in ['source', 'sink']]
    node_labels = {node: node.replace('sub_', '') for node in nodes_to_draw}
    nx.draw_networkx_labels(G, positions, labels=node_labels, font_size=10)

    # Edge labels
    '''
    for (u, v), attr in nx.get_edge_attributes(G, 'capacity').items():
        x, y = (positions[u][0] + positions[v][0]) / 2, (positions[u][1] + positions[v][1]) / 2
        label = f"{flow_dict[u][v]}/{attr}, C={G[u][v]['weight']}"
        plt.text(x, y, label, size=10, ha='center', va='center')
    '''
    '''
    if faulty_interconnects:
        plt.text(0.05, 0.05, f"Defective interconnect: {faulty_interconnects}", transform=plt.gca().transAxes, fontsize=15)
        if (total_outflow==max_possible_flow):
            # Total cost text
            plt.text(0.05, 0, f"The die pair is reparable!", transform=plt.gca().transAxes, fontsize=15)
            plt.text(0.05, -0.05, f"Number of detoured signal: {total_cost}", transform=plt.gca().transAxes, fontsize=15)
        else:
            plt.text(0.05, 0, f"The die pair is irreparable!", transform=plt.gca().transAxes, fontsize=15)
    else:
        plt.text(0.05, 0.05, f"Default solution", transform=plt.gca().transAxes, fontsize=15)
    '''
    plt.axis('off')
    plt.show()

def check_repairable(G, flow_dict):
    total_outflow = sum(flow_dict['source'].values())
    max_possible_flow = sum(G['source'][neighbor]['capacity'] for neighbor in G['source'])

    return total_outflow, max_possible_flow

def main():
    # create UCIe graph
    G = create_layered_graph()

    # inject the defects
    faulty_interconnects = [25, 20]
    faulty_edges = [('i' + str(i), 'sub_i' + str(i)) for i in faulty_interconnects]
    fault_injection(G, faulty_edges)

    # finding a possible path
    start_time = time.time()
    all_paths = fp.find_all_paths(G, 32, faulty_interconnects)
    all_costs = [fp.calculate_path_cost(G, path) for path in all_paths if
                 isinstance(path, list)]  # Calculate costs for valid paths
    end_time = time.time()
    flow_dict = fp.create_flow_dict_from_paths(G, all_paths)

    print('exe time for only searching 1 solution: ', end_time-start_time)
    for path, cost in zip(all_paths[:], all_costs[:]):
        print(f"Path: {path}, Cost: {cost}")
    print('all paths:', all_paths)
    print('flow dict: ', flow_dict)

    visualize_graph(G, flow_dict)

if __name__ == "__main__":
    main()