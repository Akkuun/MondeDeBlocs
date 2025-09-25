#!/usr/bin/env python3
"""
Version EXHAUSTIVE pour trouver TOUS les chemins gagnants possibles
Sans limitation par états visités - explore toutes les combinaisons
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
    
    possible_files = [filename, f'export_{filename}', f'{filename}.csv']
    
    for file_to_try in possible_files:
        filepath = os.path.join(csv_path, file_to_try)
        try:
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                data = []
                for row in reader:
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
    """Check if an object can be removed from its current position"""
    objects_on_top = [o for o in objects_data if o['SUR_ID'] == obj_id]
    return len(objects_on_top) == 0

def redresser(obj_id, objects_data):
    """Stand up an object (set COUCHE to False)"""
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if obj and obj['COUCHE']:
        obj['COUCHE'] = False
        return True
    return False

def coucher_inverse(obj_id, objects_data):
    """Lay down an object (set COUCHE to True)"""
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if obj and not obj['COUCHE']:
        obj['COUCHE'] = True
        return True
    return False

def get_all_possible_reverse_actions(state):
    """Generate all possible reverse actions from current state"""
    actions = []
    
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
    """Check if placing obj_id on target_id would create a cycle"""
    current = target_id
    visited = set()
    
    while current != 0:
        if current in visited or current == obj_id:
            return True
        visited.add(current)
        
        current_obj = next((o for o in state if o['ID'] == current), None)
        if not current_obj:
            break
        current = current_obj['SUR_ID']
    
    return False

def apply_reverse_action(state, action):
    """Apply a reverse action to a state"""
    new_state = deepcopy(state)
    success = False
    description = ""
    
    if action[0] == 'move_to':
        _, obj_id, target_id = action
        
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
    """Check if two states are equal"""
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
    """Convert state to string for duplicate detection"""
    sorted_objects = sorted(state, key=lambda x: x['ID'])
    state_parts = []
    for obj in sorted_objects:
        if obj['FORME'].strip().upper() != 'TABLE':
            state_parts.append(f"{obj['ID']}-{obj['SUR_ID']}-{obj['COUCHE']}")
    return "|".join(state_parts)

def path_to_string(path_actions):
    """Convert a path (list of actions) to a string for uniqueness check"""
    return " -> ".join(path_actions)

class ExhaustivePathSearchJSON:
    """
    Class to handle EXHAUSTIVE reverse graph search that finds ALL possible winning paths
    """
    
    def __init__(self):
        self.all_solutions = []
        self.unique_paths = set()  # To track unique action sequences
        self.nodes_explored = 0
        
    def exhaustive_path_search(self, goal_state, target_initial_state, max_depth=10):
        """
        Perform EXHAUSTIVE search to find ALL possible paths from goal to initial state
        Uses DFS with path tracking instead of BFS with state visited tracking
        """
        self.all_solutions = []
        self.unique_paths = set()
        self.nodes_explored = 0
        
        print(f"🔍 RECHERCHE EXHAUSTIVE de tous les chemins possibles...")
        print(f"Profondeur maximale: {max_depth}")
        print(f"⚠️  Attention: Cette recherche peut trouver BEAUCOUP de solutions!")
        
        # Use DFS with explicit path tracking
        initial_path_actions = []
        self._dfs_search(goal_state, target_initial_state, initial_path_actions, 0, max_depth)
        
        print(f"\n✅ Recherche exhaustive terminée!")
        print(f"   📊 Nœuds explorés: {self.nodes_explored}")
        print(f"   🏆 Solutions uniques trouvées: {len(self.all_solutions)}")
        print(f"   📋 Chemins d'actions uniques: {len(self.unique_paths)}")
        
        return self.all_solutions
    
    def _dfs_search(self, current_state, target_state, path_actions, depth, max_depth):
        """
        Recursive DFS search for all paths
        """
        self.nodes_explored += 1
        
        # Progress indicator
        if self.nodes_explored % 1000 == 0:
            print(f"   Exploré {self.nodes_explored} nœuds, {len(self.all_solutions)} solutions trouvées...")
        
        # Check if we found a solution
        if states_equal(current_state, target_state):
            path_string = path_to_string(path_actions)
            
            # Only add if this exact sequence hasn't been found before
            if path_string not in self.unique_paths:
                self.unique_paths.add(path_string)
                self.all_solutions.append({
                    'depth': depth,
                    'steps_count': len(path_actions),
                    'action_sequence': path_actions.copy(),
                    'path_string': path_string
                })
                
                if len(self.all_solutions) % 10 == 1:  # Show every 10th solution found
                    print(f"🎯 Solution {len(self.all_solutions)} trouvée! ({len(path_actions)} étapes, profondeur {depth})")
            
            return  # Found solution, return from this path
        
        # Don't go deeper than max_depth
        if depth >= max_depth:
            return
        
        # Explore all possible actions
        possible_actions = get_all_possible_reverse_actions(current_state)
        
        for action in possible_actions:
            new_state, success, action_description = apply_reverse_action(current_state, action)
            
            if success:
                # Add action to path and continue searching
                new_path_actions = path_actions + [action_description]
                
                # Recursive call
                self._dfs_search(new_state, target_state, new_path_actions, depth + 1, max_depth)

def group_solutions_by_length(solutions):
    """Group solutions by their length"""
    grouped = {}
    for solution in solutions:
        length = solution['steps_count']
        if length not in grouped:
            grouped[length] = []
        grouped[length].append(solution)
    return grouped

def run_exhaustive_search():
    """
    Run exhaustive search with user input
    """
    print("=" * 80)
    print("🔍 RECHERCHE EXHAUSTIVE DE TOUS LES CHEMINS POSSIBLES")
    print("=" * 80)
    
    # Load data
    print("\n📊 Chargement des données...")
    
    goal_state = load_objects_data('final_objet.csv')
    initial_state = load_objects_data('start_objet.csv')
    
    if not goal_state or not initial_state:
        print("❌ Impossible de charger les états nécessaires!")
        return
    
    print(f"✅ États chargés: {len(goal_state)} objets")
    
    # Get configuration
    print(f"\n🔧 Configuration:")
    try:
        max_depth = int(input(f"📏 Profondeur maximale (ATTENTION: >6 peut être très long!): "))
    except:
        max_depth = 5
        print(f"Utilisation de la profondeur par défaut: {max_depth}")
    
    if max_depth > 8:
        confirm = input(f"⚠️  Profondeur {max_depth} peut générer des milliers de solutions. Continuer? (o/N): ")
        if confirm.lower() not in ['o', 'oui', 'y', 'yes']:
            print("Recherche annulée.")
            return
    
    # Run exhaustive search
    search = ExhaustivePathSearchJSON()
    solutions = search.exhaustive_path_search(goal_state, initial_state, max_depth)
    
    if solutions:
        # Group by length
        grouped = group_solutions_by_length(solutions)
        
        print(f"\n🏆 RÉSULTATS EXHAUSTIFS:")
        print("=" * 40)
        print(f"Solutions totales trouvées: {len(solutions)}")
        
        # Show distribution
        print(f"\n📊 Distribution par nombre d'étapes:")
        for length in sorted(grouped.keys()):
            count = len(grouped[length])
            percentage = (count / len(solutions)) * 100
            print(f"   {length} étapes: {count} solution(s) ({percentage:.1f}%)")
        
        # Show some examples for each length
        print(f"\n📋 EXEMPLES DE SOLUTIONS:")
        print("=" * 35)
        
        for length in sorted(grouped.keys())[:4]:  # Show first 4 lengths
            solutions_of_length = grouped[length]
            print(f"\n🔹 Solutions en {length} étapes ({len(solutions_of_length)} total):")
            
            # Show first 3 examples
            for i, solution in enumerate(solutions_of_length[:3], 1):
                print(f"\n   Exemple {i}:")
                for j, action in enumerate(solution['action_sequence'], 1):
                    print(f"     {j}. {action}")
            
            if len(solutions_of_length) > 3:
                print(f"   ... et {len(solutions_of_length) - 3} autre(s) solution(s)")
        
        # Save results
        output_file = "exhaustive_all_paths.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(solutions, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Toutes les solutions sauvegardées dans: {output_file}")
        
        # Ask if user wants to see optimal solutions in detail
        if len(solutions) > 10:
            show_optimal = input(f"\nVoir toutes les solutions optimales en détail? (o/N): ")
            if show_optimal.lower() in ['o', 'oui', 'y', 'yes']:
                min_length = min(grouped.keys())
                optimal_solutions = grouped[min_length]
                
                print(f"\n⭐ TOUTES LES SOLUTIONS OPTIMALES ({min_length} étapes):")
                print("=" * 55)
                
                for i, solution in enumerate(optimal_solutions, 1):
                    print(f"\nSolution optimale {i}:")
                    for j, action in enumerate(solution['action_sequence'], 1):
                        print(f"   {j}. {action}")
    else:
        print(f"\n❌ Aucune solution trouvée avec profondeur max {max_depth}")

if __name__ == "__main__":
    run_exhaustive_search()