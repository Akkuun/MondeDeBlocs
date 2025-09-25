#!/usr/bin/env python3
"""
Version modifiée de arbre_graph_json_inverse pour trouver TOUS les chemins gagnants
dans une profondeur donnée, pas seulement le premier.
"""
import csv
import json
import os
from copy import deepcopy
from collections import deque

def load_objects_data(filename):
    """
    Load objects data from CSV file
    """
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'csv')
    
    # Try different possible filenames
    possible_files = [filename, f'export_{filename}', f'{filename}.csv']
    
    for file_to_try in possible_files:
        filepath = os.path.join(csv_path, file_to_try)
        try:
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                data = []
                for row in reader:
                    # Convert numeric fields
                    row['ID'] = int(row['ID'])
                    row['MATERIAU_ID'] = int(row['MATERIAU_ID'])
                    row['SUR_ID'] = int(row['SUR_ID'])
                    row['COUCHE'] = row['COUCHE'].upper() == 'TRUE'
                    data.append(row)
                print(f"Loaded {len(data)} records from {file_to_try}")
                return data
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error loading {file_to_try}: {e}")
            continue
    
    print(f"❌ Could not load {filename}")
    return None

def peut_etre_retire_de_dessus(obj_id, objects_data):
    """
    Check if an object can be removed from its current position
    (L'inverse de peut_etre_place_au_dessus)
    """
    # Find all objects that are on top of this object
    objects_on_top = [o for o in objects_data if o['SUR_ID'] == obj_id]
    
    # Object can be removed if nothing is on top of it
    return len(objects_on_top) == 0

def redresser(obj_id, objects_data):
    """
    Stand up an object (set COUCHE to False)
    (L'inverse de coucher)
    """
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if obj and obj['COUCHE']:
        obj['COUCHE'] = False
        return True
    return False

def coucher_inverse(obj_id, objects_data):
    """
    Lay down an object (set COUCHE to True)
    (L'inverse de redresser)
    """
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if obj and not obj['COUCHE']:
        obj['COUCHE'] = True
        return True
    return False

def get_all_possible_reverse_actions(state):
    """
    Generate all possible reverse actions from current state
    """
    actions = []
    
    # For each object (except table)
    for obj in state:
        if obj['FORME'].strip().upper() == 'TABLE':
            continue
            
        obj_id = obj['ID']
        
        # Reverse action 1: Move object (if it can be removed from current position)
        if peut_etre_retire_de_dessus(obj_id, state):
            # Can move to any other object (including table)
            for target in state:
                if target['ID'] != obj_id and target['ID'] != obj['SUR_ID']:
                    # Check if we can place on this target (no cycles)
                    if not would_create_cycle(obj_id, target['ID'], state):
                        actions.append(('move_to', obj_id, target['ID']))
        
        # Reverse action 2: Stand up object (if it's currently lying down)
        if obj['COUCHE']:
            actions.append(('stand_up', obj_id))
        
        # Reverse action 3: Lay down object (if it's currently standing)
        if not obj['COUCHE']:
            actions.append(('lay_down', obj_id))
    
    return actions

def would_create_cycle(obj_id, target_id, state):
    """
    Check if placing obj_id on target_id would create a cycle
    """
    current = target_id
    visited = set()
    
    while current != 0:  # 0 is typically the table/ground
        if current in visited or current == obj_id:
            return True
        visited.add(current)
        
        # Find what current is sitting on
        current_obj = next((o for o in state if o['ID'] == current), None)
        if not current_obj:
            break
        current = current_obj['SUR_ID']
    
    return False

def apply_reverse_action(state, action):
    """
    Apply a reverse action to a state
    """
    new_state = deepcopy(state)
    success = False
    description = ""
    
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
    """
    if len(state1) != len(state2):
        return False
    
    for obj1 in state1:
        obj2 = next((o for o in state2 if o['ID'] == obj1['ID']), None)
        if not obj2:
            return False
        if (obj1['SUR_ID'] != obj2['SUR_ID'] or 
            obj1['COUCHE'] != obj2['COUCHE']):
            return False
    
    return True

def state_to_string(state):
    """
    Convert state to string for duplicate detection
    """
    sorted_objects = sorted(state, key=lambda x: x['ID'])
    state_parts = []
    for obj in sorted_objects:
        if obj['FORME'].strip().upper() != 'TABLE':
            state_parts.append(f"{obj['ID']}-{obj['SUR_ID']}-{obj['COUCHE']}")
    return "|".join(state_parts)

class AllPathsReverseSearchJSON:
    """
    Class to handle reverse graph search that finds ALL winning paths
    """
    
    def __init__(self):
        self.graph_data = []
        self.visited_states = set()
        self.all_solutions = []  # Store all found solutions
        
    def create_node(self, state, parent_id, action, description, depth):
        """
        Create a new node in the graph
        """
        node_id = len(self.graph_data)
        
        node = {
            'id': node_id,
            'parent': parent_id,
            'children': [],
            'states': deepcopy(state),
            'action': action,
            'description': description,
            'depth': depth,
            'is_initial': False
        }
        
        # Add to parent's children if has parent
        if parent_id is not None:
            parent_node = self.graph_data[parent_id]
            parent_node['children'].append(node_id)
        
        self.graph_data.append(node)
        return node
    
    def breadth_first_all_paths_search(self, goal_state, target_initial_state, max_depth=15):
        """
        Perform breadth-first search to find ALL paths from goal to initial state
        """
        self.graph_data = []
        self.visited_states = set()
        self.all_solutions = []
        
        # Initialize with goal state
        root_node = self.create_node(goal_state, None, None, "", 0)
        
        queue = deque([(goal_state, None, None, "", 0)])
        initial_state_string = state_to_string(target_initial_state)
        
        print(f"🔍 Recherche de TOUS les chemins gagnants...")
        print(f"Profondeur maximale: {max_depth}")
        print(f"État initial cible: {initial_state_string}")
        
        node_count = 0
        
        while queue:
            current_state, parent_id, action, description, depth = queue.popleft()
            
            # Create node for current state
            current_node = self.create_node(current_state, parent_id, action, description, depth)
            node_count += 1
            
            if node_count % 50 == 0:
                print(f"   Nœud {current_node['id']} (profondeur {depth}): {description}")
            
            # Check if we reached the initial state
            if states_equal(current_state, target_initial_state):
                print(f"🎯 Solution trouvée au nœud {current_node['id']} (profondeur {depth})!")
                current_node['is_initial'] = True
                solution_path = self.get_path_to_node(current_node['id'])
                self.all_solutions.append({
                    'node_id': current_node['id'],
                    'depth': depth,
                    'path': solution_path
                })
                # Continue searching for more solutions - don't break!
            
            # Don't go deeper than max_depth
            if depth >= max_depth:
                continue
            
            # Generate all possible reverse actions
            possible_actions = get_all_possible_reverse_actions(current_state)
            
            for action in possible_actions:
                new_state, success, action_description = apply_reverse_action(current_state, action)
                
                if success:
                    new_state_string = state_to_string(new_state)
                    
                    # For finding all paths, we might want to revisit states at different depths
                    # But to avoid infinite loops, we'll still track visited states per depth
                    state_depth_key = f"{new_state_string}_{depth+1}"
                    
                    if state_depth_key not in self.visited_states:
                        self.visited_states.add(state_depth_key)
                        queue.append((new_state, current_node['id'], action, action_description, depth + 1))
        
        total_nodes = len(self.graph_data)
        print(f"\n✅ Recherche terminée. Total de nœuds explorés: {total_nodes}")
        print(f"🏆 Nombre de solutions trouvées: {len(self.all_solutions)}")
        
        return self.all_solutions, total_nodes
    
    def get_path_to_node(self, node_id):
        """
        Get the complete path from root to a specific node
        """
        path = []
        current_id = node_id
        
        while current_id is not None:
            node = self.graph_data[current_id]
            path.append({
                'id': node['id'],
                'description': node['description'],
                'depth': node['depth'],
                'action': node['action']
            })
            current_id = node['parent']
        
        return path  # Path from solution to root
    
    def save_all_paths_graph(self, filename="all_paths_reverse_graph.json"):
        """
        Save the complete graph with all paths to JSON file
        """
        output_path = os.path.join(os.path.dirname(__file__), filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.graph_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Graphe complet sauvegardé dans: {filename}")
        print(f"   📊 Nombre total de nœuds: {len(self.graph_data)}")
        return output_path

def analyze_all_solutions(solutions):
    """
    Analyze all found solutions to provide insights
    """
    if not solutions:
        return {}
    
    # Group solutions by depth/length
    solutions_by_depth = {}
    for solution in solutions:
        depth = solution['depth']
        if depth not in solutions_by_depth:
            solutions_by_depth[depth] = []
        solutions_by_depth[depth].append(solution)
    
    # Find shortest solutions
    min_depth = min(solutions_by_depth.keys())
    shortest_solutions = solutions_by_depth[min_depth]
    
    return {
        'total_solutions': len(solutions),
        'solutions_by_depth': solutions_by_depth,
        'shortest_depth': min_depth,
        'shortest_solutions_count': len(shortest_solutions),
        'depth_range': (min(solutions_by_depth.keys()), max(solutions_by_depth.keys()))
    }

def run_all_paths_search_example():
    """
    Exemple d'utilisation de la recherche de tous les chemins
    """
    print("=" * 70)
    print("🔍 RECHERCHE DE TOUS LES CHEMINS GAGNANTS")
    print("=" * 70)
    
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
        return
    
    print(f"✅ État final chargé: {len(goal_state)} objets")
    print(f"✅ État initial chargé: {len(initial_state)} objets")
    
    # Afficher les états pour debug
    print(f"\n🎯 État FINAL (point de départ):")
    for obj in goal_state:
        if obj['FORME'].strip().upper() != 'TABLE':
            print(f"  - {obj['NOM']} sur {next(o['NOM'] for o in goal_state if o['ID'] == obj['SUR_ID'])}")
    
    print(f"\n🚀 État INITIAL (objectif):")
    for obj in initial_state:
        if obj['FORME'].strip().upper() != 'TABLE':
            print(f"  - {obj['NOM']} sur {next(o['NOM'] for o in initial_state if o['ID'] == obj['SUR_ID'])}")
    
    # Demander la profondeur maximale
    try:
        max_depth = int(input(f"\n📏 Profondeur maximale de recherche (recommandé: 10-15): "))
    except:
        max_depth = 10
        print(f"Utilisation de la profondeur par défaut: {max_depth}")
    
    # Lancer la recherche de tous les chemins
    all_paths_search = AllPathsReverseSearchJSON()
    solutions, total_nodes = all_paths_search.breadth_first_all_paths_search(
        goal_state, initial_state, max_depth=max_depth
    )
    
    # Analyser les résultats
    analysis = analyze_all_solutions(solutions)
    
    if solutions:
        print(f"\n🏆 RÉSULTATS:")
        print(f"   Total de solutions: {analysis['total_solutions']}")
        print(f"   Profondeur minimale: {analysis['shortest_depth']} étapes")
        print(f"   Solutions optimales: {analysis['shortest_solutions_count']}")
        print(f"   Plage de profondeurs: {analysis['depth_range'][0]} à {analysis['depth_range'][1]}")
        
        print(f"\n📊 Répartition par profondeur:")
        for depth in sorted(analysis['solutions_by_depth'].keys()):
            count = len(analysis['solutions_by_depth'][depth])
            print(f"   {depth} étapes: {count} solution(s)")
        
        # Afficher quelques solutions optimales
        print(f"\n✨ Solutions optimales ({analysis['shortest_depth']} étapes):")
        optimal_solutions = analysis['solutions_by_depth'][analysis['shortest_depth']]
        for i, solution in enumerate(optimal_solutions[:3], 1):  # Show first 3
            print(f"\n   Solution {i}:")
            step_num = 1
            for node in reversed(solution['path']):
                if node['description']:
                    print(f"     {step_num}. {node['description']}")
                    step_num += 1
            if i < len(optimal_solutions):
                remaining = len(optimal_solutions) - 3
                if remaining > 0:
                    print(f"   ... et {remaining} autre(s) solution(s) optimale(s)")
                    break
        
    else:
        print(f"\n❌ Aucune solution trouvée dans la limite de profondeur {max_depth}")
    
    # Sauvegarder le graphe complet
    all_paths_search.save_all_paths_graph()

if __name__ == "__main__":
    run_all_paths_search_example()