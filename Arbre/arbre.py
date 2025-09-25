import csv
import os

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
        #print(f"Erreur: L'objet {obj_to_move_id} ne peut pas être déplacé")
        return False
    
    # Check if the target can receive an object
    if not peut_recevoir_deplacement(target_obj_id, objects_data):
        #print(f"Erreur: L'objet {target_obj_id} ne peut pas recevoir un objet")
        return False
    
    # Find the object to move
    obj_to_move = next((o for o in objects_data if o['ID'] == obj_to_move_id), None)
    if not obj_to_move:
        #print(f"Erreur: Objet {obj_to_move_id} non trouvé")
        return False
    
    # Find the target object
    target_obj = next((o for o in objects_data if o['ID'] == target_obj_id), None)
    if not target_obj:
        #print(f"Erreur: Objet cible {target_obj_id} non trouvé")
        return False
    
    # Perform the movement
    old_sur_id = obj_to_move['SUR_ID']
    obj_to_move['SUR_ID'] = target_obj_id
    
    #print(f"Succès: {obj_to_move['NOM']} déplacé de l'objet {old_sur_id} vers {target_obj['NOM']} ({target_obj_id})")
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
        #print(f"Erreur: L'objet {obj_id} ne peut pas être couché")
        return False
    
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        #print(f"Erreur: Objet {obj_id} non trouvé")
        return False
    
    # Check if already laying down
    if obj['COUCHE']:
        #print(f"Info: {obj['NOM']} est déjà couché")
        return True
    
    # Lay down the object
    obj['COUCHE'] = True
    
    #print(f"Succès: {obj['NOM']} a été couché")
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

def apply_action(objects_data, action, silent=False):
    """
    Apply an action to a copy of the objects data
    
    Args:
        objects_data (list): Current state of objects
        action (tuple): Action to apply
        silent (bool): If True, suppress print output
    
    Returns:
        tuple: (new_objects_data, success, description)
    """
    import copy
    new_state = copy.deepcopy(objects_data)
    
    if action[0] == 'move':
        _, obj_id, target_id = action
        
        if silent:
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
        else:
            success = deplacer_au_dessus(obj_id, target_id, new_state)
        
        obj_name = next(o for o in new_state if o['ID'] == obj_id)['NOM']
        target_name = next(o for o in new_state if o['ID'] == target_id)['NOM']
        description = f"Déplacer {obj_name} sur {target_name}"
        
    elif action[0] == 'lay_down':
        _, obj_id = action
        
        if silent:
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
        else:
            success = coucher(obj_id, new_state)
        
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

def write_path(path):
    """
    Writes the path given in a randomly named file
    """
    import random
    solution_folder = "solutions"
    if not os.path.exists(solution_folder):
        os.makedirs(solution_folder)
    number_of_moves = path.count('\n')
    filename = f"solution_{number_of_moves}_moves_{random.randint(0,99999)}.txt"
    with open(os.path.join(solution_folder, filename), 'w', encoding='utf-8') as f:
        f.write(path)

def breadth_first_search(start_state, goal_state, path = "", max_depth=5, current_depth=0):
    if current_depth >= max_depth:
        return

    if states_equal(start_state, goal_state):
        write_path(path)
        
        print("Solution found!")

    for action in get_all_possible_actions(start_state):
        new_state, success, description = apply_action(start_state, action)
        
        if success:
            detail = ""
            if action[0] == 'move':
                obj1_name = next(o for o in start_state if o['ID'] == action[1])['NOM']
                obj2_name = next(o for o in start_state if o['ID'] == action[2])['NOM']
                detail = f"#({action[1]} : {obj1_name}) -> #({action[2]} : {obj2_name})"
            elif action[0] == 'lay_down':
                obj1_name = next(o for o in start_state if o['ID'] == action[1])['NOM']
                detail = f"#({action[1]} : {obj1_name})"
            breadth_first_search(new_state, goal_state, path + f"{action} {detail}\n", max_depth, current_depth + 1)

def save_paths_to_file(paths, filename="solution_paths.txt"):
    """
    Save all successful paths to a file
    
    Args:
        paths (list): List of successful paths
        filename (str): Output filename
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Solutions trouvées: {len(paths)}\n")
        f.write("=" * 50 + "\n\n")
        
        for i, path in enumerate(paths, 1):
            f.write(f"SOLUTION {i} ({len(path)} étapes):\n")
            f.write("-" * 30 + "\n")
            
            for step, (action, description) in enumerate(path, 1):
                f.write(f"Étape {step}: {description}\n")
                if action[0] == 'move':
                    f.write(f"  Action: déplacer objet {action[1]} sur objet {action[2]}\n")
                elif action[0] == 'lay_down':
                    f.write(f"  Action: coucher objet {action[1]}\n")
            
            f.write("\n")
    
    print(f"Chemins sauvegardés dans {filename}")

# Load start and final object datasets
start_objects_data = load_objects_data('start_objet.csv')
final_objects_data = load_objects_data('final_objet.csv')
materials_data = load_materials_data()

print("\n=== START OBJECTS DATA ===")
for obj in start_objects_data:
    couche_status = "Couché" if obj['COUCHE'] else "Debout"
    print(f"Object {obj['ID']}: {obj['NOM']} ({obj['FORME'].strip()}) - {couche_status} (Material: {obj['MATERIAU_ID']}, On: {obj['SUR_ID']})")

print("\n=== FINAL OBJECTS DATA ===")
for obj in final_objects_data:
    couche_status = "Couché" if obj['COUCHE'] else "Debout"
    print(f"Object {obj['ID']}: {obj['NOM']} ({obj['FORME'].strip()}) - {couche_status} (Material: {obj['MATERIAU_ID']}, On: {obj['SUR_ID']})")

print("\n=== MATERIALS DATA ===")
for mat in materials_data:
    print(f"Material {mat['ID']}: {mat['NOM']} - {mat['COULEUR']} {mat['MATERIAU']} (Weight: {mat['POIDS']}, Opacity: {mat['OPACITE']})")

print("\n=== CHANGES BETWEEN START AND FINAL ===")
for start_obj, final_obj in zip(start_objects_data, final_objects_data):
    if start_obj['ID'] == final_obj['ID']:
        changes = []
        if start_obj['SUR_ID'] != final_obj['SUR_ID']:
            changes.append(f"SUR_ID: {start_obj['SUR_ID']} → {final_obj['SUR_ID']}")
        if start_obj['COUCHE'] != final_obj['COUCHE']:
            changes.append(f"COUCHE: {start_obj['COUCHE']} → {final_obj['COUCHE']}")
        if changes:
            print(f"Object {start_obj['ID']} ({start_obj['NOM']}): {', '.join(changes)}")
        else:
            print(f"Object {start_obj['ID']} ({start_obj['NOM']}): No changes")

print("\n=== MOVEMENT CAPABILITIES ANALYSIS ===")

def test_movement_functions(objects_data, dataset_name):
    print(f"\n--- {dataset_name} ---")
    for obj in objects_data:
        obj_id = obj['ID']
        nom = obj['NOM']
        
        peut_deplacer = peut_etre_deplace(obj_id, objects_data)
        peut_coucher = peut_etre_couche(obj_id, objects_data)
        peut_recevoir = peut_recevoir_deplacement(obj_id, objects_data)
        
        print(f"Object {obj_id} ({nom}):")
        print(f"  - Peut être déplacé: {peut_deplacer}")
        print(f"  - Peut être couché: {peut_coucher}")
        print(f"  - Peut recevoir un objet: {peut_recevoir}")
        
        # Show what's on top
        objects_on_top = get_objects_on_top(obj_id, objects_data)
        if objects_on_top:
            names_on_top = [o['NOM'] for o in objects_on_top]
            print(f"  - Objets dessus: {', '.join(names_on_top)}")
        else:
            print(f"  - Objets dessus: Aucun")

test_movement_functions(start_objects_data, "START DATASET")
test_movement_functions(final_objects_data, "FINAL DATASET")

print("\n=== TESTING MOVEMENT FUNCTIONS ===")

# Create a copy of start data to test transformations
import copy
test_objects = copy.deepcopy(start_objects_data)

print("\n--- Testing movements to recreate final state ---")

# Step 1: Move Cube gris from Cube violet to Table
print("\n1. Tentative de déplacer Cube gris (23) de Cube violet vers Table:")
success = deplacer_au_dessus(23, 25, test_objects)
if success:
    print("   État après déplacement:")
    cube_gris = next(o for o in test_objects if o['ID'] == 23)
    print(f"   Cube gris est maintenant sur l'objet {cube_gris['SUR_ID']}")

# Step 2: Lay down Donut Saucisse
print("\n2. Tentative de coucher Donut Saucisse (24):")
success = coucher(24, test_objects)
if success:
    donut = next(o for o in test_objects if o['ID'] == 24)
    print(f"   Donut Saucisse couché: {donut['COUCHE']}")

# Step 3: Move Cylindre Tungstène from Table to Donut Saucisse
print("\n3. Tentative de déplacer Cylindre Tungstène (21) de Table vers Donut Saucisse:")
success = deplacer_au_dessus(21, 24, test_objects)
if success:
    cylindre = next(o for o in test_objects if o['ID'] == 21)
    print(f"   Cylindre Tungstène est maintenant sur l'objet {cylindre['SUR_ID']}")

# Step 4: Move Cube violet to itself (this might seem odd but it's in the final data)
print("\n4. Tentative de déplacer Cube violet (22) vers lui-même:")
success = deplacer_au_dessus(22, 22, test_objects)
if success:
    cube_violet = next(o for o in test_objects if o['ID'] == 22)
    print(f"   Cube violet est maintenant sur l'objet {cube_violet['SUR_ID']}")

print("\n--- État final des objets après transformations ---")
for obj in test_objects:
    couche_status = "Couché" if obj['COUCHE'] else "Debout"
    print(f"Object {obj['ID']}: {obj['NOM']} ({obj['FORME'].strip()}) - {couche_status} (On: {obj['SUR_ID']})")

print("\n--- Comparaison avec l'état final attendu ---")
print("État actuel vs État final attendu:")
for test_obj in test_objects:
    final_obj = next(o for o in final_objects_data if o['ID'] == test_obj['ID'])
    
    sur_match = "✓" if test_obj['SUR_ID'] == final_obj['SUR_ID'] else "✗"
    couche_match = "✓" if test_obj['COUCHE'] == final_obj['COUCHE'] else "✗"
    
    print(f"Object {test_obj['ID']} ({test_obj['NOM']}):")
    print(f"  SUR_ID: {test_obj['SUR_ID']} vs {final_obj['SUR_ID']} {sur_match}")
    print(f"  COUCHE: {test_obj['COUCHE']} vs {final_obj['COUCHE']} {couche_match}")

print("\n" + "="*60)
print("=== BREADTH-FIRST SEARCH FOR SOLUTION PATHS ===")
print("="*60)


breadth_first_search(start_objects_data, final_objects_data, max_depth=6)