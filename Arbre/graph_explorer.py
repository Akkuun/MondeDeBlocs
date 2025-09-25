import json
import os

def load_graph(filename="search_graph_detailed.json"):
    """
    Load the search graph from JSON file
    
    Args:
        filename (str): JSON file containing the graph
    
    Returns:
        list: List of graph nodes
    """
    filepath = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Graph file not found: {filepath}")
        return []
    except Exception as e:
        print(f"Error loading graph: {e}")
        return []

def find_node_by_id(graph, node_id):
    """Find a node by its ID"""
    return next((node for node in graph if node['id'] == node_id), None)

def get_goal_nodes(graph):
    """Get all nodes that represent goal states"""
    return [node for node in graph if node['is_goal']]

def get_nodes_by_depth(graph, depth):
    """Get all nodes at a specific depth"""
    return [node for node in graph if node['depth'] == depth]

def get_path_to_node(graph, node_id):
    """
    Get the complete path from root to a specific node
    
    Args:
        graph (list): Graph data
        node_id (int): Target node ID
    
    Returns:
        list: Path of nodes from root to target
    """
    path = []
    current_id = node_id
    
    while current_id is not None:
        node = find_node_by_id(graph, current_id)
        if node:
            path.insert(0, node)
            current_id = node['parent']
        else:
            break
    
    return path

def print_node_summary(node):
    """Print a summary of a node"""
    print(f"Node {node['id']}:")
    print(f"  Parent: {node['parent']}")
    print(f"  Children: {node['children']}")
    print(f"  Depth: {node['depth']}")
    print(f"  Is Goal: {node['is_goal']}")
    print(f"  Action: {node['action']}")
    print(f"  Description: {node['description']}")
    
    # Show object positions
    print("  Object positions:")
    for obj in node['states']:
        if obj['FORME'].strip().upper() != 'TABLE':
            couche_status = " (Couché)" if obj['COUCHE'] else " (Debout)"
            print(f"    {obj['NOM']}: sur objet {obj['SUR_ID']}{couche_status}")

def print_solution_path(graph, goal_node_id):
    """
    Print the complete solution path to a goal node
    
    Args:
        graph (list): Graph data
        goal_node_id (int): ID of goal node
    """
    path = get_path_to_node(graph, goal_node_id)
    
    print(f"=== SOLUTION PATH ({len(path)-1} steps) ===")
    for i, node in enumerate(path):
        if i == 0:
            print(f"Initial State (Node {node['id']}):")
        else:
            print(f"Step {i}: {node['description']} (Node {node['id']})")
        
        # Show state after this step
        print("  State:")
        for obj in node['states']:
            if obj['FORME'].strip().upper() != 'TABLE':
                couche_status = " (Couché)" if obj['COUCHE'] else " (Debout)"
                print(f"    {obj['NOM']}: sur objet {obj['SUR_ID']}{couche_status}")
        print()

def analyze_graph_structure(graph):
    """
    Analyze the structure of the search graph
    
    Args:
        graph (list): Graph data
    """
    print("=== GRAPH ANALYSIS ===")
    
    # Basic statistics
    total_nodes = len(graph)
    goal_nodes = [n for n in graph if n['is_goal']]
    max_depth = max(n['depth'] for n in graph) if graph else 0
    
    print(f"Total nodes: {total_nodes}")
    print(f"Goal nodes: {len(goal_nodes)}")
    print(f"Maximum depth: {max_depth}")
    
    # Depth distribution
    depth_counts = {}
    for node in graph:
        depth = node['depth']
        depth_counts[depth] = depth_counts.get(depth, 0) + 1
    
    print("\nNodes per depth level:")
    for depth in sorted(depth_counts.keys()):
        print(f"  Depth {depth}: {depth_counts[depth]} nodes")
    
    # Action type distribution
    action_types = {}
    for node in graph:
        if node['action']:
            action_type = node['action'][0]
            action_types[action_type] = action_types.get(action_type, 0) + 1
    
    print("\nAction type distribution:")
    for action_type, count in action_types.items():
        print(f"  {action_type}: {count} actions")
    
    # Find nodes with most children
    max_children = max(len(n['children']) for n in graph) if graph else 0
    nodes_with_max_children = [n for n in graph if len(n['children']) == max_children]
    
    print(f"\nMaximum branching factor: {max_children}")
    print(f"Nodes with maximum children: {len(nodes_with_max_children)}")

def main():
    """Main function to demonstrate graph exploration"""
    
    # Load the graph
    graph = load_graph()
    if not graph:
        return
    
    # Analyze graph structure
    analyze_graph_structure(graph)
    
    # Find and display goal nodes
    goal_nodes = get_goal_nodes(graph)
    print(f"\n=== GOAL NODES ({len(goal_nodes)} found) ===")
    
    for goal_node in goal_nodes:
        print(f"\nGoal Node {goal_node['id']} at depth {goal_node['depth']}:")
        print(f"  Action that led here: {goal_node['description']}")
        
        # Show the solution path
        print_solution_path(graph, goal_node['id'])
    
    # Show some example queries
    print("\n=== EXAMPLE QUERIES ===")
    
    # Root node
    root_node = find_node_by_id(graph, 0)
    print("\nRoot node:")
    print_node_summary(root_node)
    
    # Nodes at depth 2
    depth_2_nodes = get_nodes_by_depth(graph, 2)
    print(f"\nNumber of nodes at depth 2: {len(depth_2_nodes)}")
    
    # First few nodes at depth 2
    print("First 3 nodes at depth 2:")
    for i, node in enumerate(depth_2_nodes[:3]):
        print(f"  Node {node['id']}: {node['description']}")

if __name__ == "__main__":
    main()