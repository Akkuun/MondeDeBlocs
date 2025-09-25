#!/usr/bin/env python3
"""
Script interactif pour trouver tous les chemins gagnants
avec configuration de profondeur personnalisable
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from find_all_winning_paths import AllPathsReverseSearchJSON, load_objects_data, analyze_all_solutions

def get_user_config():
    """
    Get user configuration for the search
    """
    print("🔧 CONFIGURATION DE LA RECHERCHE")
    print("=" * 40)
    
    # Get max depth
    while True:
        try:
            max_depth = input("📏 Profondeur maximale (recommandé: 6-10, max conseillé: 15): ")
            if max_depth.strip() == "":
                max_depth = 8
                print(f"   Utilisation de la valeur par défaut: {max_depth}")
                break
            max_depth = int(max_depth)
            if max_depth < 1:
                print("   ❌ La profondeur doit être au moins 1")
                continue
            if max_depth > 20:
                confirm = input(f"   ⚠️  Profondeur {max_depth} peut être très lente. Continuer? (o/N): ")
                if confirm.lower() not in ['o', 'oui', 'y', 'yes']:
                    continue
            break
        except ValueError:
            print("   ❌ Veuillez entrer un nombre entier")
    
    # Ask if user wants detailed output
    detailed = input("📊 Affichage détaillé pendant la recherche? (o/N): ").lower() in ['o', 'oui', 'y', 'yes']
    
    return max_depth, detailed

def run_configurable_search():
    """
    Run the search with user configuration
    """
    print("=" * 70)
    print("🎯 RECHERCHE CONFIGURABLE DE TOUS LES CHEMINS GAGNANTS")
    print("=" * 70)
    
    # Get configuration
    max_depth, detailed_output = get_user_config()
    
    # Load data
    print(f"\n📊 Chargement des données...")
    
    goal_state = load_objects_data('final_objet.csv')
    initial_state = load_objects_data('start_objet.csv')
    
    if not goal_state or not initial_state:
        print("❌ Impossible de charger les états nécessaires!")
        return
    
    print(f"✅ États chargés: {len(goal_state)} objets")
    
    # Show states
    print(f"\n🎯 État FINAL → État INITIAL:")
    print("   Transformation requise:")
    
    final_positions = {}
    initial_positions = {}
    
    for obj in goal_state:
        if obj['FORME'].strip().upper() != 'TABLE':
            support_name = next(o['NOM'] for o in goal_state if o['ID'] == obj['SUR_ID'])
            final_positions[obj['NOM']] = support_name
    
    for obj in initial_state:
        if obj['FORME'].strip().upper() != 'TABLE':
            support_name = next(o['NOM'] for o in initial_state if o['ID'] == obj['SUR_ID'])
            initial_positions[obj['NOM']] = support_name
    
    for obj_name in final_positions:
        final_pos = final_positions[obj_name]
        initial_pos = initial_positions.get(obj_name, "???")
        if final_pos != initial_pos:
            print(f"   • {obj_name}: {final_pos} → {initial_pos}")
    
    # Start search
    print(f"\n🚀 Lancement de la recherche (profondeur max: {max_depth})...")
    
    if not detailed_output:
        print("   (Mode silencieux - progress affiché tous les 100 nœuds)")
    
    # Create modified search class for optional detailed output
    class ConfigurableAllPathsSearch(AllPathsReverseSearchJSON):
        def __init__(self, show_details=True):
            super().__init__()
            self.show_details = show_details
            
        def breadth_first_all_paths_search(self, goal_state, target_initial_state, max_depth=15):
            # Copy the original method but modify output based on show_details
            from collections import deque
            from find_all_winning_paths import states_equal, state_to_string, get_all_possible_reverse_actions, apply_reverse_action
            
            self.graph_data = []
            self.visited_states = set()
            self.all_solutions = []
            
            root_node = self.create_node(goal_state, None, None, "", 0)
            queue = deque([(goal_state, None, None, "", 0)])
            initial_state_string = state_to_string(target_initial_state)
            
            if self.show_details:
                print(f"🔍 Recherche de TOUS les chemins gagnants...")
                print(f"Profondeur maximale: {max_depth}")
            
            node_count = 0
            solutions_found = 0
            
            while queue:
                current_state, parent_id, action, description, depth = queue.popleft()
                
                current_node = self.create_node(current_state, parent_id, action, description, depth)
                node_count += 1
                
                # Output control
                if self.show_details and node_count % 50 == 0:
                    print(f"   Nœud {current_node['id']} (profondeur {depth}): {description}")
                elif not self.show_details and node_count % 100 == 0:
                    print(f"   Exploré {node_count} nœuds, {solutions_found} solutions trouvées...")
                
                # Check for solution
                if states_equal(current_state, target_initial_state):
                    solutions_found += 1
                    if self.show_details:
                        print(f"🎯 Solution {solutions_found} trouvée au nœud {current_node['id']} (profondeur {depth})!")
                    else:
                        print(f"🎯 Solution {solutions_found} trouvée! (nœud {current_node['id']}, profondeur {depth})")
                    
                    current_node['is_initial'] = True
                    solution_path = self.get_path_to_node(current_node['id'])
                    self.all_solutions.append({
                        'node_id': current_node['id'],
                        'depth': depth,
                        'path': solution_path
                    })
                
                if depth >= max_depth:
                    continue
                
                possible_actions = get_all_possible_reverse_actions(current_state)
                
                for action in possible_actions:
                    new_state, success, action_description = apply_reverse_action(current_state, action)
                    
                    if success:
                        new_state_string = state_to_string(new_state)
                        state_depth_key = f"{new_state_string}_{depth+1}"
                        
                        if state_depth_key not in self.visited_states:
                            self.visited_states.add(state_depth_key)
                            queue.append((new_state, current_node['id'], action, action_description, depth + 1))
            
            total_nodes = len(self.graph_data)
            print(f"\n✅ Recherche terminée!")
            print(f"   📊 Nœuds explorés: {total_nodes}")
            print(f"   🏆 Solutions trouvées: {len(self.all_solutions)}")
            
            return self.all_solutions, total_nodes
    
    # Run search
    search = ConfigurableAllPathsSearch(show_details=detailed_output)
    solutions, total_nodes = search.breadth_first_all_paths_search(
        goal_state, initial_state, max_depth=max_depth
    )
    
    # Analyze results
    if solutions:
        analysis = analyze_all_solutions(solutions)
        
        print(f"\n🏆 RÉSULTATS DÉTAILLÉS:")
        print("=" * 35)
        print(f"   Solutions totales: {analysis['total_solutions']}")
        print(f"   Profondeur optimale: {analysis['shortest_depth']} étapes")
        print(f"   Solutions optimales: {analysis['shortest_solutions_count']}")
        
        if analysis['depth_range'][0] != analysis['depth_range'][1]:
            print(f"   Plage profondeurs: {analysis['depth_range'][0]}-{analysis['depth_range'][1]} étapes")
        
        # Show distribution
        print(f"\n📊 Distribution:")
        for depth in sorted(analysis['solutions_by_depth'].keys()):
            count = len(analysis['solutions_by_depth'][depth])
            percentage = (count / analysis['total_solutions']) * 100
            print(f"   {depth} étapes: {count} solution(s) ({percentage:.1f}%)")
        
        # Show optimal solutions
        print(f"\n⭐ Solutions optimales ({analysis['shortest_depth']} étapes):")
        optimal_solutions = analysis['solutions_by_depth'][analysis['shortest_depth']]
        
        for i, solution in enumerate(optimal_solutions[:3], 1):  # Show max 3
            print(f"\n   Solution optimale {i}:")
            step_num = 1
            for node in reversed(solution['path']):
                if node['description']:
                    print(f"     {step_num}. {node['description']}")
                    step_num += 1
        
        if len(optimal_solutions) > 3:
            print(f"   ... et {len(optimal_solutions) - 3} autre(s) solution(s) optimale(s)")
        
        # Save results
        search.save_all_paths_graph()
        
        print(f"\n💡 Pour une analyse complète, utilisez:")
        print(f"   python3 analyze_all_paths.py")
        
    else:
        print(f"\n❌ Aucune solution trouvée avec profondeur max {max_depth}")
        print(f"💡 Essayez d'augmenter la profondeur de recherche")

if __name__ == "__main__":
    run_configurable_search()