import csv
import os
import json
import copy

def load_csv_data(filename, data_converters=None):
    """
    Generic function to load CSV data from the csv folder
    
    Args:
        filename (str): Name of the CSV file (e.g., 'export_objet.csv')
        data_converters (dict): Optional dictionary to convert specific columns to different types
                               e.g., {'ID': int, 'POIDS': float}
    
    Returns:
        list: List of dictionaries containing the CSV data
    """
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'csv', filename)
    data = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Apply data converters if provided
                if data_converters:
                    for column, converter in data_converters.items():
                        if column in row and row[column]:
                            try:
                                row[column] = converter(row[column])
                            except ValueError as e:
                                print(f"Warning: Could not convert {column}='{row[column]}' using {converter.__name__}: {e}")
                
                data.append(row)
        
        print(f"Loaded {len(data)} records from {filename}")
        return data
    except FileNotFoundError:
        print(f"CSV file not found at: {csv_path}")
        return []
    except Exception as e:
        print(f"Error loading CSV {filename}: {e}")
        return []

def load_objects_data(filename):
    """Load objects data with appropriate type conversions"""
    converters = {
        'ID': int,
        'MATERIAU_ID': int,
        'SUR_ID': int,
        'COUCHE': lambda x: x.strip().lower() == 'true',  # Convert to boolean
        'FORME': str
    }
    return load_csv_data(filename, converters)

def load_materials_data():
    """Load materials data with appropriate type conversions"""
    converters = {
        'ID': int,
        'POIDS': float,
        'OPACITE': float
    }
    return load_csv_data('materiau.csv', converters)

def get_objects_on_top(obj_id, objects_data):
    """
    Get all objects that are directly on top of the given object
    
    Args:
        obj_id (int): ID of the object to check
        objects_data (list): List of object dictionaries
    
    Returns:
        list: List of objects that are on top of this object
    """
    return [obj for obj in objects_data if obj['SUR_ID'] == obj_id]

def peut_etre_deplace(obj_id, objects_data):
    """
    Returns True if the object can be moved
    Conditions: object is not the table AND object has nothing on top of it
    
    Args:
        obj_id (int): ID of the object to check
        objects_data (list): List of object dictionaries
    
    Returns:
        bool: True if object can be moved
    """
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    # Cannot move if it's a table
    if obj['FORME'].strip().upper() == 'TABLE':
        return False
    
    # Cannot move if something is on top of it
    objects_on_top = get_objects_on_top(obj_id, objects_data)
    return len(objects_on_top) == 0

def peut_etre_couche(obj_id, objects_data):
    """
    Returns True if the object can be laid down
    Conditions: object is not the table AND object has nothing on top of it AND object is not a cube
    
    Args:
        obj_id (int): ID of the object to check
        objects_data (list): List of object dictionaries
    
    Returns:
        bool: True if object can be laid down
    """
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    # Cannot lay down if it's a table
    if obj['FORME'].strip().upper() == 'TABLE':
        return False
    
    # Cannot lay down if it's a cube
    if obj['FORME'].strip().upper() == 'CUBE':
        return False
    
    # Cannot lay down if something is on top of it
    objects_on_top = get_objects_on_top(obj_id, objects_data)
    return len(objects_on_top) == 0

def peut_recevoir_deplacement(obj_id, objects_data):
    """
    Returns True if the object can receive another object on top of it
    Conditions: 
    - object is the table OR
    - object is a cylinder and is standing up OR  
    - object is a donut saucisse and laying down OR
    - object is a cube that has nothing on top of it
    
    Args:
        obj_id (int): ID of the object to check
        objects_data (list): List of object dictionaries
    
    Returns:
        bool: True if object can receive another object
    """
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    forme = obj['FORME'].strip().upper()
    
    # Table can always receive objects
    if forme == 'TABLE':
        return True
    
    # Cylinder can receive objects if standing up (not couché)
    if forme == 'CYLINDRE' and not obj['COUCHE']:
        return True
    
    # Donut saucisse can receive objects if laying down (couché)
    if forme == 'DONUT_SAUCISSE' and obj['COUCHE']:
        return True
    
    # Cube can receive objects if nothing is on top of it
    if forme == 'CUBE':
        objects_on_top = get_objects_on_top(obj_id, objects_data)
        return len(objects_on_top) == 0
    
    return False

def deplacer_au_dessus(obj_to_move_id, target_obj_id, objects_data):
    """
    Move one object on top of another object
    
    Args:
        obj_to_move_id (int): ID of the object to move
        target_obj_id (int): ID of the object to place it on
        objects_data (list): List of object dictionaries (will be modified)
    
    Returns:
        bool: True if movement was successful, False otherwise
    """
    # Check if the object can be moved
    if not peut_etre_deplace(obj_to_move_id, objects_data):
        return False
    
    # Check if the target can receive an object
    if not peut_recevoir_deplacement(target_obj_id, objects_data):
        return False
    
    # Find the object to move
    obj_to_move = next((o for o in objects_data if o['ID'] == obj_to_move_id), None)
    if not obj_to_move:
        return False
    
    # Find the target object
    target_obj = next((o for o in objects_data if o['ID'] == target_obj_id), None)
    if not target_obj:
        return False
    
    # Perform the movement
    old_sur_id = obj_to_move['SUR_ID']
    obj_to_move['SUR_ID'] = target_obj_id
    
    return True

def coucher(obj_id, objects_data):
    """
    Lay down an object (set COUCHE to True)
    
    Args:
        obj_id (int): ID of the object to lay down
        objects_data (list): List of object dictionaries (will be modified)
    
    Returns:
        bool: True if laying down was successful, False otherwise
    """
    # Check if the object can be laid down
    if not peut_etre_couche(obj_id, objects_data):
        return False
    
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    # Check if already laying down
    if obj['COUCHE']:
        return True
    
    # Lay down the object
    obj['COUCHE'] = True
    
    return True

def get_all_possible_actions(objects_data):
    """
    Get all possible actions from the current state
    
    Args:
        objects_data (list): Current state of objects
    
    Returns:
        list: List of tuples representing possible actions
              Format: ('move', obj_id, target_id) or ('lay_down', obj_id)
    """
    actions = []
    
    # Check all possible movements
    for obj in objects_data:
        obj_id = obj['ID']
        
        # Check if object can be moved
        if peut_etre_deplace(obj_id, objects_data):
            # Try moving to each possible target
            for target_obj in objects_data:
                target_id = target_obj['ID']
                if target_id != obj_id and peut_recevoir_deplacement(target_id, objects_data):
                    actions.append(('move', obj_id, target_id))
        
        # Check if object can be laid down
        if peut_etre_couche(obj_id, objects_data):
            actions.append(('lay_down', obj_id))
    
    return actions

def apply_action(objects_data, action):
    """
    Apply an action to a copy of the objects data
    
    Args:
        objects_data (list): Current state of objects
        action (tuple): Action to apply
    
    Returns:
        tuple: (new_objects_data, success, description)
    """
    new_state = copy.deepcopy(objects_data)
    
    if action[0] == 'move':
        _, obj_id, target_id = action
        
        # Manually check conditions without printing
        if not peut_etre_deplace(obj_id, new_state) or not peut_recevoir_deplacement(target_id, new_state):
            success = False
        else:
            obj_to_move = next((o for o in new_state if o['ID'] == obj_id), None)
            if obj_to_move:
                obj_to_move['SUR_ID'] = target_id
                success = True
            else:
                success = False
        
        obj_name = next(o for o in new_state if o['ID'] == obj_id)['NOM']
        target_name = next(o for o in new_state if o['ID'] == target_id)['NOM']
        description = f"Déplacer {obj_name} sur {target_name}"
        
    elif action[0] == 'lay_down':
        _, obj_id = action
        
        # Manually check conditions without printing
        if not peut_etre_couche(obj_id, new_state):
            success = False
        else:
            obj = next((o for o in new_state if o['ID'] == obj_id), None)
            if obj and not obj['COUCHE']:
                obj['COUCHE'] = True
                success = True
            else:
                success = True  # Already laying down is considered success
        
        obj_name = next(o for o in new_state if o['ID'] == obj_id)['NOM']
        description = f"Coucher {obj_name}"
    
    else:
        return new_state, False, "Action inconnue"
    
    return new_state, success, description

def states_equal(state1, state2):
    """
    Check if two states are equal
    
    Args:
        state1, state2 (list): States to compare
    
    Returns:
        bool: True if states are identical
    """
    if len(state1) != len(state2):
        return False
    
    for obj1 in state1:
        obj2 = next((o for o in state2 if o['ID'] == obj1['ID']), None)
        if not obj2:
            return False
        if obj1['SUR_ID'] != obj2['SUR_ID'] or obj1['COUCHE'] != obj2['COUCHE']:
            return False
    
    return True

def state_to_string(objects_data):
    """
    Convert a state to a string representation for hashing/comparison
    
    Args:
        objects_data (list): State to convert
    
    Returns:
        str: String representation of the state
    """
    sorted_objects = sorted(objects_data, key=lambda x: x['ID'])
    state_parts = []
    for obj in sorted_objects:
        state_parts.append(f"{obj['ID']}:{obj['SUR_ID']}:{obj['COUCHE']}")
    return "|".join(state_parts)

class GraphSearchJSON:
    """
    Class to handle breadth-first search with JSON graph representation
    """
    
    def __init__(self):
        self.graph_data = []
        self.node_counter = 0
        self.visited_states = set()
    
    def create_node(self, state, parent_id=None, action=None, description="", depth=0):
        """
        Create a new node in the graph
        
        Args:
            state (list): Current state of objects
            parent_id (int): ID of parent node, None for root
            action (tuple): Action that led to this state
            description (str): Human-readable description of the action
            depth (int): Depth in the search tree
        
        Returns:
            dict: The created node
        """
        node_id = self.node_counter
        self.node_counter += 1
        
        # Check if this state is a goal state
        is_goal = states_equal(state, goal_state) if 'goal_state' in globals() else False
        
        node = {
            "id": node_id,
            "parent": parent_id,
            "children": [],
            "states": copy.deepcopy(state),  # Store the full state
            "is_goal": is_goal,
            "action": action,
            "description": description,
            "depth": depth,
            "state_string": state_to_string(state)  # For quick comparison
        }
        
        self.graph_data.append(node)
        
        # If this node has a parent, add it to parent's children
        if parent_id is not None:
            parent_node = next((n for n in self.graph_data if n['id'] == parent_id), None)
            if parent_node:
                parent_node['children'].append(node_id)
        
        return node
    
    def breadth_first_search_with_graph(self, start_state, goal_state, max_depth=5):
        """
        Perform breadth-first search while building a JSON graph
        
        Args:
            start_state (list): Initial state
            goal_state (list): Target state
            max_depth (int): Maximum search depth
        
        Returns:
            list: List of solution paths found
        """
        # Initialize with root node
        root_node = self.create_node(start_state, parent_id=None, description="Initial state")
        
        # Queue for BFS: (node_id, current_state, depth)
        queue = [(root_node['id'], start_state, 0)]
        self.visited_states.add(state_to_string(start_state))
        
        solutions = []
        
        while queue:
            current_node_id, current_state, current_depth = queue.pop(0)
            
            # Check if we've reached max depth
            if current_depth >= max_depth:
                continue
            
            # Check if current state is goal
            if states_equal(current_state, goal_state):
                # Reconstruct path
                path = self.reconstruct_path(current_node_id)
                solutions.append(path)
                print(f"Solution found at depth {current_depth}!")
                continue
            
            # Generate all possible actions
            possible_actions = get_all_possible_actions(current_state)
            
            for action in possible_actions:
                # Apply action
                new_state, success, description = apply_action(current_state, action)
                
                if not success:
                    continue
                
                # Check if we've seen this state before
                state_str = state_to_string(new_state)
                if state_str in self.visited_states:
                    continue
                
                # Add to visited states
                self.visited_states.add(state_str)
                
                # Create new node
                new_node = self.create_node(
                    new_state,
                    parent_id=current_node_id,
                    action=action,
                    description=description,
                    depth=current_depth + 1
                )
                
                # Add to queue for further exploration
                queue.append((new_node['id'], new_state, current_depth + 1))
        
        return solutions
    
    def reconstruct_path(self, node_id):
        """
        Reconstruct path from root to given node
        
        Args:
            node_id (int): Target node ID
        
        Returns:
            list: List of actions leading to this node
        """
        path = []
        current_id = node_id
        
        while current_id is not None:
            node = next((n for n in self.graph_data if n['id'] == current_id), None)
            if node and node['action']:
                path.insert(0, {
                    'action': node['action'],
                    'description': node['description']
                })
            current_id = node['parent'] if node else None
        
        return path
    
    def save_graph_to_json(self, filename="search_graph.json"):
        """
        Save the complete graph to a JSON file
        
        Args:
            filename (str): Output filename
        """
        # Convert states to serializable format
        serializable_graph = []
        for node in self.graph_data:
            serializable_node = copy.deepcopy(node)
            # Ensure all data is JSON serializable
            if 'action' in serializable_node and serializable_node['action']:
                serializable_node['action'] = list(serializable_node['action'])
            serializable_graph.append(serializable_node)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_graph, f, indent=2, ensure_ascii=False)
        
        print(f"Graph saved to {filename}")
        print(f"Total nodes in graph: {len(self.graph_data)}")
        print(f"Total states visited: {len(self.visited_states)}")
    
    def get_graph_statistics(self):
        """
        Get statistics about the generated graph
        
        Returns:
            dict: Statistics about the graph
        """
        total_nodes = len(self.graph_data)
        goal_nodes = sum(1 for node in self.graph_data if node['is_goal'])
        max_depth = max(node['depth'] for node in self.graph_data) if self.graph_data else 0
        
        depth_distribution = {}
        for node in self.graph_data:
            depth = node['depth']
            depth_distribution[depth] = depth_distribution.get(depth, 0) + 1
        
        return {
            'total_nodes': total_nodes,
            'goal_nodes': goal_nodes,
            'max_depth': max_depth,
            'depth_distribution': depth_distribution,
            'total_visited_states': len(self.visited_states)
        }

def main():
    """
    Main function to run the graph-based search
    """
    # Load data
    global goal_state
    start_objects_data = load_objects_data('start_objet.csv')
    final_objects_data = load_objects_data('final_objet.csv')
    goal_state = final_objects_data
    
    print("\n=== GRAPH-BASED BREADTH-FIRST SEARCH ===")
    print("=" * 50)
    
    # Create search instance
    search = GraphSearchJSON()
    
    # Run search
    solutions = search.breadth_first_search_with_graph(
        start_objects_data, 
        final_objects_data, 
        max_depth=6
    )
    
    # Save graph to JSON
    search.save_graph_to_json("search_graph_detailed.json")
    
    # Print statistics
    stats = search.get_graph_statistics()
    print("\n=== SEARCH STATISTICS ===")
    print(f"Total nodes explored: {stats['total_nodes']}")
    print(f"Goal nodes found: {stats['goal_nodes']}")
    print(f"Maximum depth reached: {stats['max_depth']}")
    print(f"Total unique states: {stats['total_visited_states']}")
    print(f"Solutions found: {len(solutions)}")
    
    print("\nDepth distribution:")
    for depth, count in sorted(stats['depth_distribution'].items()):
        print(f"  Depth {depth}: {count} nodes")
    
    # Print first solution if found
    if solutions:
        print(f"\n=== FIRST SOLUTION ({len(solutions[0])} steps) ===")
        for i, step in enumerate(solutions[0], 1):
            print(f"Step {i}: {step['description']}")
    
    print(f"\nGraph data structure saved with {len(search.graph_data)} nodes")
    print("Each node contains: id, parent, children, states, is_goal, action, description, depth")
    
    # Generate visualizations
    print("\n=== GENERATING VISUALIZATIONS ===")
    try:
        from graph_visualizer import generate_interactive_html, generate_simple_tree_html
        generate_interactive_html(search.graph_data, "graph_visualization.html")
        generate_simple_tree_html(search.graph_data, "tree_visualization.html")
        print("✅ Visualizations generated successfully!")
        print("📊 Open graph_visualization.html for interactive D3.js visualization")
        print("🌲 Open tree_visualization.html for organized tree view")
    except ImportError as e:
        print(f"⚠️  Could not generate visualizations: {e}")
        print("Run 'python graph_visualizer.py' separately to create visualizations")

if __name__ == "__main__":
    main()