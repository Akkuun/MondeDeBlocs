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

# =================== FONCTIONS INVERSES ===================

def peut_etre_retire_de_dessus(obj_id, objects_data):
    """
    INVERSE: Returns True if the object can be removed from its current position
    (L'inverse de peut_etre_deplace - on vérifie si on peut retirer l'objet de sa position actuelle)
    
    Args:
        obj_id (int): ID of the object to check
        objects_data (list): List of object dictionaries
    
    Returns:
        bool: True if object can be removed from its current position
    """
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    # Cannot remove if it's a table (tables are always at the base)
    if obj['FORME'].strip().upper() == 'TABLE':
        return False
    
    # Cannot remove if something is on top of it
    objects_on_top = get_objects_on_top(obj_id, objects_data)
    return len(objects_on_top) == 0

def peut_etre_redresse(obj_id, objects_data):
    """
    INVERSE: Returns True if the object can be stood up (from laying down)
    (L'inverse de peut_etre_couche - on vérifie si on peut remettre debout)
    
    Args:
        obj_id (int): ID of the object to check
        objects_data (list): List of object dictionaries
    
    Returns:
        bool: True if object can be stood up
    """
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    # Cannot stand up if it's a table
    if obj['FORME'].strip().upper() == 'TABLE':
        return False
    
    # Cannot stand up if it's a cube
    if obj['FORME'].strip().upper() == 'CUBE':
        return False
    
    # Can only stand up if currently laying down
    if not obj['COUCHE']:
        return False
    
    # Cannot stand up if something is on top of it
    objects_on_top = get_objects_on_top(obj_id, objects_data)
    return len(objects_on_top) == 0

def peut_etre_couche_inverse(obj_id, objects_data):
    """
    INVERSE: Returns True if the object can be laid down (inverse action for reverse search)
    
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
    
    # Can only lay down if currently standing up
    if obj['COUCHE']:
        return False
    
    # Cannot lay down if something is on top of it
    objects_on_top = get_objects_on_top(obj_id, objects_data)
    return len(objects_on_top) == 0

def peut_liberer_sa_position(obj_id, objects_data):
    """
    INVERSE: Returns True if the object can free its position for another object
    (L'inverse de peut_recevoir_deplacement - on vérifie si l'objet peut libérer sa place)
    
    Args:
        obj_id (int): ID of the object to check
        objects_data (list): List of object dictionaries
    
    Returns:
        bool: True if object can free its position
    """
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    forme = obj['FORME'].strip().upper()
    
    # Table cannot free its position (it's the base)
    if forme == 'TABLE':
        return False
    
    # Check if something is currently on this object
    objects_on_top = get_objects_on_top(obj_id, objects_data)
    return len(objects_on_top) > 0  # Can free position only if something is on it

def retirer_de_dessus(obj_to_remove_id, objects_data):
    """
    INVERSE: Remove an object from on top of another object (move to table by default)
    (L'inverse de deplacer_au_dessus - on retire l'objet et on le place sur la table)
    
    Args:
        obj_to_remove_id (int): ID of the object to remove
        objects_data (list): List of object dictionaries (will be modified)
    
    Returns:
        tuple: (success, old_position_id) - success status and where it was before
    """
    # Check if the object can be removed
    if not peut_etre_retire_de_dessus(obj_to_remove_id, objects_data):
        return False, None
    
    # Find the object to remove
    obj_to_remove = next((o for o in objects_data if o['ID'] == obj_to_remove_id), None)
    if not obj_to_remove:
        return False, None
    
    # Find the table (default destination for removed objects)
    table = next((o for o in objects_data if o['FORME'].strip().upper() == 'TABLE'), None)
    if not table:
        return False, None
    
    # Store old position
    old_position_id = obj_to_remove['SUR_ID']
    
    # Move object to table
    obj_to_remove['SUR_ID'] = table['ID']
    
    return True, old_position_id

def redresser(obj_id, objects_data):
    """
    INVERSE: Stand up an object (set COUCHE to False)
    (L'inverse de coucher - on remet l'objet debout)
    
    Args:
        obj_id (int): ID of the object to stand up
        objects_data (list): List of object dictionaries (will be modified)
    
    Returns:
        bool: True if standing up was successful, False otherwise
    """
    # Check if the object can be stood up
    if not peut_etre_redresse(obj_id, objects_data):
        return False
    
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    # Stand up the object
    obj['COUCHE'] = False
    
    return True

def coucher_inverse(obj_id, objects_data):
    """
    INVERSE: Lay down an object (set COUCHE to True) - for reverse search
    
    Args:
        obj_id (int): ID of the object to lay down
        objects_data (list): List of object dictionaries (will be modified)
    
    Returns:
        bool: True if laying down was successful, False otherwise
    """
    # Check if the object can be laid down
    if not peut_etre_couche_inverse(obj_id, objects_data):
        return False
    
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    # Lay down the object
    obj['COUCHE'] = True
    
    return True

def get_all_possible_reverse_actions(objects_data):
    """
    INVERSE: Get all possible reverse actions from the current state
    (L'inverse de get_all_possible_actions - on cherche ce qu'on peut défaire)
    
    Args:
        objects_data (list): Current state of objects
    
    Returns:
        list: List of tuples representing possible reverse actions
              Format: ('move_to', obj_id, target_id) or ('stand_up', obj_id)
    """
    actions = []
    
    # Check all possible movements (like forward search but different validation)
    for obj in objects_data:
        obj_id = obj['ID']
        
        # Check if object can be moved
        if peut_etre_retire_de_dessus(obj_id, objects_data):
            # Try moving to each possible target position
            for target_obj in objects_data:
                target_id = target_obj['ID']
                if target_id != obj_id:
                    # In reverse search, we need different validation
                    # We can move to any position that could theoretically receive an object
                    target_forme = target_obj['FORME'].strip().upper()
                    
                    # Can move to table
                    if target_forme == 'TABLE':
                        actions.append(('move_to', obj_id, target_id))
                    # Can move to cube if nothing is on it
                    elif target_forme == 'CUBE':
                        objects_on_target = get_objects_on_top(target_id, objects_data)
                        if len(objects_on_target) == 0:
                            actions.append(('move_to', obj_id, target_id))
                    # Can move to cylinder if it's standing up
                    elif target_forme == 'CYLINDRE' and not target_obj['COUCHE']:
                        actions.append(('move_to', obj_id, target_id))
                    # Can move to donut saucisse if it's laying down
                    elif target_forme == 'DONUT_SAUCISSE' and target_obj['COUCHE']:
                        actions.append(('move_to', obj_id, target_id))
        
        # Check if object can be stood up (inverse of lay down)
        if peut_etre_redresse(obj_id, objects_data):
            actions.append(('stand_up', obj_id))
        
        # Check if object can be laid down (for reverse search completeness)
        if peut_etre_couche_inverse(obj_id, objects_data):
            actions.append(('lay_down', obj_id))
    
    return actions

def apply_reverse_action(objects_data, action):
    """
    INVERSE: Apply a reverse action to a copy of the objects data
    (L'inverse de apply_action - on applique l'action inverse)
    
    Args:
        objects_data (list): Current state of objects
        action (tuple): Reverse action to apply
    
    Returns:
        tuple: (new_objects_data, success, description)
    """
    new_state = copy.deepcopy(objects_data)
    
    if action[0] == 'move_to':
        _, obj_id, target_id = action
        
        # Check if the movement is valid
        if not peut_etre_retire_de_dessus(obj_id, new_state):
            success = False
        else:
            obj_to_move = next((o for o in new_state if o['ID'] == obj_id), None)
            if obj_to_move:
                old_position_id = obj_to_move['SUR_ID']
                obj_to_move['SUR_ID'] = target_id
                success = True
            else:
                success = False
        
        obj_name = next(o for o in new_state if o['ID'] == obj_id)['NOM']
        target_name = next(o for o in new_state if o['ID'] == target_id)['NOM']
        description = f"Déplacer {obj_name} sur {target_name}"
        
    elif action[0] == 'stand_up':
        _, obj_id = action
        
        success = redresser(obj_id, new_state)
        
        obj_name = next(o for o in new_state if o['ID'] == obj_id)['NOM']
        description = f"Redresser {obj_name}"
        
    elif action[0] == 'lay_down':
        _, obj_id = action
        
        success = coucher_inverse(obj_id, new_state)
        
        obj_name = next(o for o in new_state if o['ID'] == obj_id)['NOM']
        description = f"Coucher {obj_name}"
    
    else:
        return new_state, False, "Action inverse inconnue"
    
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

class ReverseGraphSearchJSON:
    """
    INVERSE: Class to handle backward search from goal to initial state
    (L'inverse de GraphSearchJSON - on part du but vers l'état initial)
    """
    
    def __init__(self):
        self.graph_data = []
        self.node_counter = 0
        self.visited_states = set()
    
    def create_node(self, state, parent_id=None, action=None, description="", depth=0):
        """
        Create a new node in the reverse graph
        
        Args:
            state (list): Current state of objects
            parent_id (int): ID of parent node, None for root (goal state)
            action (tuple): Reverse action that led to this state
            description (str): Human-readable description of the reverse action
            depth (int): Depth in the reverse search tree
        
        Returns:
            dict: The created node
        """
        node_id = self.node_counter
        self.node_counter += 1
        
        # Check if this state is the initial state (goal of reverse search)
        is_initial = states_equal(state, initial_state) if 'initial_state' in globals() else False
        
        node = {
            "id": node_id,
            "parent": parent_id,
            "children": [],
            "states": copy.deepcopy(state),  # Store the full state
            "is_initial": is_initial,  # Goal of reverse search is to reach initial state
            "reverse_action": action,
            "description": description,
            "depth": depth,
            "state_string": state_to_string(state)  # For quick comparison
        }
        
        self.graph_data.append(node)
        
        # Add this node as child to parent
        if parent_id is not None:
            parent_node = next(n for n in self.graph_data if n['id'] == parent_id)
            parent_node['children'].append(node_id)
        
        return node
    
    def breadth_first_reverse_search(self, goal_state, target_initial_state, max_depth=10):
        """
        INVERSE: Perform breadth-first search from goal state back to initial state
        (L'inverse de breadth_first_search - on cherche depuis le but vers le début)
        
        Args:
            goal_state (list): The goal state (our starting point in reverse search)
            target_initial_state (list): The initial state we want to reach
            max_depth (int): Maximum search depth
        
        Returns:
            tuple: (found_solution, solution_path, total_nodes)
        """
        global initial_state
        initial_state = target_initial_state
        
        # Initialize with goal state as root
        queue = [(goal_state, None, None, "", 0)]
        self.visited_states.add(state_to_string(goal_state))
        
        found_solution = False
        solution_path = []
        
        print(f"Démarrage de la recherche inverse depuis l'état but vers l'état initial...")
        print(f"Profondeur maximale: {max_depth}")
        
        while queue and not found_solution:
            current_state, parent_id, action, description, depth = queue.pop(0)
            
            # Create node for current state
            current_node = self.create_node(current_state, parent_id, action, description, depth)
            
            print(f"Nœud {current_node['id']} (profondeur {depth}): {description}")
            
            # Check if we reached the initial state
            if current_node['is_initial']:
                print(f"✅ État initial trouvé au nœud {current_node['id']} !")
                found_solution = True
                solution_path = self.get_path_to_node(current_node['id'])
                break
            
            # Don't go deeper than max_depth
            if depth >= max_depth:
                continue
            
            # Generate all possible reverse actions
            possible_actions = get_all_possible_reverse_actions(current_state)
            
            for action in possible_actions:
                new_state, success, action_description = apply_reverse_action(current_state, action)
                
                if success:
                    new_state_string = state_to_string(new_state)
                    
                    # Only add if we haven't seen this state before
                    if new_state_string not in self.visited_states:
                        self.visited_states.add(new_state_string)
                        queue.append((new_state, current_node['id'], action, action_description, depth + 1))
        
        total_nodes = len(self.graph_data)
        print(f"Recherche terminée. Total de nœuds explorés: {total_nodes}")
        
        return found_solution, solution_path, total_nodes
    
    def get_path_to_node(self, node_id):
        """
        Get the complete reverse path from goal to a specific node
        
        Args:
            node_id (int): Target node ID
        
        Returns:
            list: Path of nodes from goal to target
        """
        path = []
        current_id = node_id
        
        while current_id is not None:
            node = next(n for n in self.graph_data if n['id'] == current_id)
            path.append(node)
            current_id = node['parent']
        
        return path
    
    def save_reverse_graph(self, filename="reverse_search_graph.json"):
        """
        Save the reverse search graph to JSON file
        
        Args:
            filename (str): Output JSON filename
        """
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.graph_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Graphe de recherche inverse sauvegardé dans: {filename}")
            print(f"   📊 Nombre total de nœuds: {len(self.graph_data)}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")

def run_reverse_search_example():
    """
    Exemple d'utilisation de la recherche inverse
    """
    print("=" * 60)
    print("🔄 RECHERCHE INVERSE - Du but vers l'état initial")
    print("=" * 60)
    
    # Charger les données
    print("\n📊 Chargement des données...")
    
    # Charger l'état final (but de la recherche normale, point de départ de la recherche inverse)
    print("Chargement de l'état final (final_objet.csv)...")
    goal_state = load_objects_data('final_objet.csv')
    
    # Charger l'état initial (but de la recherche inverse)
    print("Chargement de l'état initial (start_objet.csv)...")
    initial_state = load_objects_data('start_objet.csv')
    
    if not goal_state or not initial_state:
        print("❌ Impossible de charger les états nécessaires!")
        print("📋 Fichiers CSV disponibles dans le dossier:")
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'csv')
        try:
            for file in os.listdir(csv_path):
                if file.endswith('.csv'):
                    print(f"   - {file}")
        except:
            pass
        return
    
    print(f"✅ État final chargé: {len(goal_state)} objets")
    print(f"✅ État initial chargé: {len(initial_state)} objets")
    
    # Afficher les états pour debug
    print(f"\n🎯 État FINAL (point de départ de la recherche inverse):")
    for obj in goal_state:
        if obj['FORME'].strip().upper() != 'TABLE':
            print(f"  - {obj['NOM']} sur {next(o['NOM'] for o in goal_state if o['ID'] == obj['SUR_ID'])}")
    
    print(f"\n🚀 État INITIAL (objectif de la recherche inverse):")
    for obj in initial_state:
        if obj['FORME'].strip().upper() != 'TABLE':
            print(f"  - {obj['NOM']} sur {next(o['NOM'] for o in initial_state if o['ID'] == obj['SUR_ID'])}")
    
    # Lancer la recherche inverse
    reverse_search = ReverseGraphSearchJSON()
    found, path, total_nodes = reverse_search.breadth_first_reverse_search(
        goal_state, initial_state, max_depth=20
    )
    
    if found:
        # Compter le nombre d'étapes réelles (sans compter le noeud de départ)
        actual_steps = sum(1 for node in path if node['description'])
        print(f"\n✅ Solution trouvée en {actual_steps} étapes:")
        step_num = 1
        for node in reversed(path):  # Inverser pour avoir l'ordre initial -> but
            if node['description']:
                print(f"  {step_num}. {node['description']}")
                step_num += 1
    else:
        print(f"\n❌ Aucune solution trouvée dans la limite de profondeur")
    
    # Sauvegarder le graphe
    reverse_search.save_reverse_graph()

if __name__ == "__main__":
    run_reverse_search_example()