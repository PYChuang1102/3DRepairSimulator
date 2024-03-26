# find all path from starting node to end node
def dfs_all_paths(G, current, end, path, visited, all_paths):
    if current == end:
        all_paths.append(list(path))
        return
    for neighbor in G[current]:
        if G[current][neighbor]['capacity'] > 0 and neighbor not in visited:
            visited.add(neighbor)
            path.append(neighbor)
            dfs_all_paths(G, neighbor, end, path, visited, all_paths)
            path.pop()
            visited.remove(neighbor)


def find_paths_for_signal(G, start, end):
    all_paths = []
    visited = set([start])
    dfs_all_paths(G, start, end, [start], visited, all_paths)
    return all_paths


def find_paths_recursive(G, signal_len, start_index, all_paths, order):
    if start_index == len(order):
        return True  # All paths found

    index = order[start_index]
    start_node = 'f' + str(index)
    end_node = 'g' + str(index)

    # search the path according to weight priority and search order
    for path in sorted(find_paths_for_signal(G, start_node, end_node), key=lambda p: path_weight(G, p)):
        if is_path_valid(path, G):
            all_paths[index] = path
            update_capacities(G, path, 0)

            if find_paths_recursive(G, signal_len, start_index + 1, all_paths, order):
                return True

            # Backtrack: reset capacities for the current path
            update_capacities(G, path, 1)
            all_paths[index] = None

    return False


def find_all_paths(G, signal_len, defect = [0]):
    G_temp = G.copy()
    search_order = list(range(defect[0], -1, -1)) + list(range(defect[0] + 1, signal_len)) # searching from defective signal
    all_paths = [None] * signal_len
    if find_paths_recursive(G_temp, signal_len, 0, all_paths, search_order):
        return all_paths
    else:
        return None


# calculate the weight of the corresponding path
def path_weight(G, path):
    return sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path) - 1))


def is_path_valid(path, G):
    # Check if all edges in the path have a capacity > 0
    for i in range(len(path) - 1):
        if G[path[i]][path[i + 1]]['capacity'] <= 0:
            return False
    return True


def update_capacities(G, path, capacity):
    # Update the capacities of edges in 'path' to the specified value
    for i in range(len(path) - 1):
        G[path[i]][path[i + 1]]['capacity'] = capacity


def calculate_path_cost(G, path):
    cost = 0
    for i in range(len(path) - 1):
        if G[path[i]][path[i + 1]]['weight'] == 0:
            pass
        else:
            cost += 1
    return cost


def create_flow_dict_from_paths(G, all_paths):
    flow_dict = {node: {} for node in G.nodes()}
    if all_paths:
        for path in all_paths:
            if path:
                for i in range(len(path) - 1):
                    start, end = path[i], path[i + 1]
                    if start in G and end in G[start]:
                        flow_dict[start][end] = 1  # Set flow to 1 for used edges
                    else:
                        flow_dict[start][end] = 0  # Set flow to 0 for unused edges
    return flow_dict
