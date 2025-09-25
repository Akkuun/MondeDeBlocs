#!/usr/bin/env python3
"""
Analyseur détaillé de tous les chemins gagnants
Affiche toutes les solutions trouvées avec leurs détails
"""
import json
import os

def load_all_paths_graph(filename="all_paths_reverse_graph.json"):
    """
    Load the complete graph with all paths
    """
    filepath = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {filepath}")
        return []
    except Exception as e:
        print(f"❌ Erreur de chargement: {e}")
        return []

def find_all_solution_nodes(graph):
    """
    Find all nodes that represent solutions (initial states)
    """
    solution_nodes = []
    for node in graph:
        if node.get('is_initial', False):
            solution_nodes.append(node)
    return solution_nodes

def trace_path_to_root(graph, node_id):
    """
    Trace path from a solution node back to the root
    """
    path = []
    current_id = node_id
    
    while current_id is not None:
        node = next((n for n in graph if n['id'] == current_id), None)
        if node:
            path.append({
                'id': node['id'],
                'description': node['description'],
                'depth': node['depth'],
                'action': node.get('action', None)
            })
            current_id = node['parent']
        else:
            break
    
    return path

def analyze_solution_differences(solutions):
    """
    Analyze differences between solutions
    """
    if len(solutions) < 2:
        return {}
    
    # Group by length
    by_length = {}
    for sol in solutions:
        length = sol['steps_count']
        if length not in by_length:
            by_length[length] = []
        by_length[length].append(sol)
    
    # Find unique action sequences
    unique_sequences = set()
    for sol in solutions:
        sequence = tuple(sol['action_sequence'])
        unique_sequences.add(sequence)
    
    return {
        'by_length': by_length,
        'unique_sequences': len(unique_sequences),
        'total_solutions': len(solutions)
    }

def extract_action_sequence(path):
    """
    Extract the sequence of actions from a path
    """
    actions = []
    for node in reversed(path):  # Reverse to get correct order
        if node['description']:
            actions.append(node['description'])
    return actions

def analyze_action_patterns(all_solutions):
    """
    Analyze common patterns in the solutions
    """
    all_actions = []
    action_frequency = {}
    
    for solution in all_solutions:
        for action in solution['action_sequence']:
            all_actions.append(action)
            action_frequency[action] = action_frequency.get(action, 0) + 1
    
    # Find most common actions
    sorted_actions = sorted(action_frequency.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'total_actions': len(all_actions),
        'unique_actions': len(action_frequency),
        'most_common': sorted_actions[:5],
        'action_frequency': action_frequency
    }

def main():
    """
    Main analysis function
    """
    print("=" * 80)
    print("🔍 ANALYSE DÉTAILLÉE DE TOUS LES CHEMINS GAGNANTS")
    print("=" * 80)
    
    # Load the graph
    print("\n📊 Chargement du graphe complet...")
    graph = load_all_paths_graph()
    
    if not graph:
        print("❌ Impossible de charger le graphe")
        return
    
    print(f"✅ Graphe chargé: {len(graph)} nœuds au total")
    
    # Find all solution nodes
    solution_nodes = find_all_solution_nodes(graph)
    print(f"🎯 Solutions trouvées: {len(solution_nodes)}")
    
    if not solution_nodes:
        print("❌ Aucune solution trouvée dans le graphe")
        return
    
    # Analyze each solution
    all_solutions = []
    
    print(f"\n📋 DÉTAIL DE TOUTES LES SOLUTIONS:")
    print("=" * 60)
    
    for i, sol_node in enumerate(solution_nodes, 1):
        print(f"\n🏆 SOLUTION {i} (Nœud {sol_node['id']}, Profondeur {sol_node['depth']}):")
        
        # Trace path
        path = trace_path_to_root(graph, sol_node['id'])
        action_sequence = extract_action_sequence(path)
        
        # Display steps
        for j, action in enumerate(action_sequence, 1):
            print(f"   {j}. {action}")
        
        # Store solution data
        all_solutions.append({
            'node_id': sol_node['id'],
            'depth': sol_node['depth'],
            'steps_count': len(action_sequence),
            'path': path,
            'action_sequence': action_sequence
        })
    
    # Comparative analysis
    print(f"\n🔬 ANALYSE COMPARATIVE:")
    print("=" * 40)
    
    analysis = analyze_solution_differences(all_solutions)
    
    print(f"📊 Répartition par nombre d'étapes:")
    for length in sorted(analysis['by_length'].keys()):
        count = len(analysis['by_length'][length])
        print(f"   {length} étapes: {count} solution(s)")
    
    print(f"\n📈 Statistiques générales:")
    print(f"   Nombre total de solutions: {analysis['total_solutions']}")
    print(f"   Séquences d'actions uniques: {analysis['unique_sequences']}")
    
    # Optimal solutions analysis
    min_steps = min(sol['steps_count'] for sol in all_solutions)
    optimal_solutions = [sol for sol in all_solutions if sol['steps_count'] == min_steps]
    
    print(f"\n⭐ SOLUTIONS OPTIMALES ({min_steps} étapes):")
    print("=" * 50)
    
    for i, sol in enumerate(optimal_solutions, 1):
        print(f"\nSolution optimale {i}:")
        for j, action in enumerate(sol['action_sequence'], 1):
            print(f"   {j}. {action}")
    
    # Action pattern analysis
    patterns = analyze_action_patterns(all_solutions)
    
    print(f"\n🎯 ANALYSE DES PATTERNS D'ACTIONS:")
    print("=" * 45)
    print(f"Actions totales exécutées: {patterns['total_actions']}")
    print(f"Types d'actions uniques: {patterns['unique_actions']}")
    
    print(f"\nActions les plus fréquentes:")
    for action, count in patterns['most_common']:
        percentage = (count / patterns['total_actions']) * 100
        print(f"   {action}: {count} fois ({percentage:.1f}%)")
    
    # Efficiency analysis
    print(f"\n⚡ ANALYSE D'EFFICACITÉ:")
    print("=" * 35)
    
    depths = [sol['depth'] for sol in all_solutions]
    steps = [sol['steps_count'] for sol in all_solutions]
    
    print(f"Profondeur minimum trouvée: {min(depths)}")
    print(f"Profondeur maximum trouvée: {max(depths)}")
    print(f"Nombre d'étapes minimum: {min(steps)}")
    print(f"Nombre d'étapes maximum: {max(steps)}")
    print(f"Moyenne d'étapes par solution: {sum(steps)/len(steps):.1f}")
    
    # Find completely different solutions
    print(f"\n🔄 SOLUTIONS COMPLÈTEMENT DIFFÉRENTES:")
    print("=" * 45)
    
    unique_solutions = {}
    for sol in all_solutions:
        sequence_key = tuple(sol['action_sequence'])
        if sequence_key not in unique_solutions:
            unique_solutions[sequence_key] = sol
    
    if len(unique_solutions) > 1:
        for i, (sequence, sol) in enumerate(unique_solutions.items(), 1):
            print(f"\nApproche {i} ({sol['steps_count']} étapes):")
            for j, action in enumerate(sequence, 1):
                print(f"   {j}. {action}")
    else:
        print("Toutes les solutions suivent la même séquence d'actions.")
    
    print(f"\n✅ Analyse terminée!")
    print(f"💾 Données complètes disponibles dans: all_paths_reverse_graph.json")

if __name__ == "__main__":
    main()