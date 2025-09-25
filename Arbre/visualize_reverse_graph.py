#!/usr/bin/env python3
"""
Visualisateur spécialisé pour le graphe de recherche inverse
Génère une visualisation HTML interactive du reverse_search_graph.json
"""
import json
import os
from collections import defaultdict

def load_reverse_graph(filename="reverse_search_graph.json"):
    """
    Load the reverse search graph from JSON file
    
    Args:
        filename (str): JSON file containing the reverse graph
    
    Returns:
        list: List of graph nodes
    """
    filepath = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier graphe non trouvé: {filepath}")
        return []
    except Exception as e:
        print(f"❌ Erreur de chargement: {e}")
        return []

def analyze_reverse_graph(graph):
    """
    Analyze the reverse graph structure and provide statistics
    
    Args:
        graph (list): Graph data
    
    Returns:
        dict: Analysis results
    """
    if not graph:
        return {}
    
    total_nodes = len(graph)
    depth_distribution = defaultdict(int)
    action_types = defaultdict(int)
    solution_path_length = 0
    
    # Find solution node and path
    solution_node = None
    for node in graph:
        depth_distribution[node.get('depth', 0)] += 1
        
        if node.get('is_initial', False):
            solution_node = node
            # Trace back to get path length
            current = node
            while current and current.get('parent') is not None:
                solution_path_length += 1
                parent_id = current['parent']
                current = next((n for n in graph if n['id'] == parent_id), None)
        
        # Analyze action types
        description = node.get('description', '')
        if description:
            if 'Déplacer' in description:
                action_types['move'] += 1
            elif 'Redresser' in description:
                action_types['stand_up'] += 1
            elif 'Coucher' in description:
                action_types['lay_down'] += 1
    
    max_depth = max(depth_distribution.keys()) if depth_distribution else 0
    
    return {
        'total_nodes': total_nodes,
        'max_depth': max_depth,
        'depth_distribution': dict(depth_distribution),
        'action_types': dict(action_types),
        'solution_found': solution_node is not None,
        'solution_path_length': solution_path_length,
        'solution_node_id': solution_node['id'] if solution_node else None
    }

def generate_reverse_html(graph, output_file="reverse_graph_visualization.html"):
    """
    Generate an interactive HTML visualization of the reverse search graph
    
    Args:
        graph (list): Graph data
        output_file (str): Output HTML filename
    """
    
    # Prepare nodes and links for D3.js
    nodes = []
    links = []
    
    for node in graph:
        # Extract action type from description
        description = node.get('description', '')
        action_type = 'initial'
        if 'Déplacer' in description:
            action_type = 'move'
        elif 'Redresser' in description:
            action_type = 'stand_up'
        elif 'Coucher' in description:
            action_type = 'lay_down'
        
        # Create node data
        node_data = {
            'id': node['id'],
            'depth': node.get('depth', 0),
            'is_initial': node.get('is_initial', False),
            'description': description,
            'action_type': action_type,
            'children_count': len(node.get('children', [])),
            'parent': node.get('parent')
        }
        nodes.append(node_data)
        
        # Create links to children
        for child_id in node.get('children', []):
            links.append({
                'source': node['id'],
                'target': child_id
            })
    
    # Get analysis
    analysis = analyze_reverse_graph(graph)
    
    html_content = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualisation Graphe de Recherche Inverse</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        
        .subtitle {{
            text-align: center;
            color: #666;
            font-size: 1.2em;
            margin-bottom: 30px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .stat-label {{
            color: #555;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .visualization {{
            border: 2px solid #ddd;
            border-radius: 10px;
            background: #f8f9fa;
            position: relative;
            overflow: hidden;
        }}
        
        .controls {{
            padding: 15px;
            background: #e9ecef;
            border-bottom: 1px solid #ddd;
        }}
        
        .control-group {{
            display: inline-block;
            margin-right: 20px;
        }}
        
        label {{
            font-weight: bold;
            margin-right: 10px;
        }}
        
        select, button {{
            padding: 5px 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background: white;
        }}
        
        button {{
            background: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            transition: background 0.3s;
        }}
        
        button:hover {{
            background: #0056b3;
        }}
        
        .legend {{
            position: absolute;
            top: 80px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-size: 0.9em;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }}
        
        .legend-color {{
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .tooltip {{
            position: absolute;
            text-align: center;
            width: 200px;
            padding: 10px;
            font: 12px sans-serif;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border: 0px;
            border-radius: 8px;
            pointer-events: none;
            opacity: 0;
        }}
        
        .node {{
            stroke: #fff;
            stroke-width: 2px;
            cursor: pointer;
        }}
        
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 2px;
            marker-end: url(#arrowhead);
        }}
        
        .node.initial {{
            stroke: #ff4444;
            stroke-width: 4px;
        }}
        
        .path-highlight {{
            stroke: #ff4444;
            stroke-width: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 Graphe de Recherche Inverse</h1>
        <p class="subtitle">Du but vers l'état initial - Exploration de l'espace d'états</p>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{analysis.get('total_nodes', 0)}</div>
                <div class="stat-label">Nœuds explorés</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{analysis.get('max_depth', 0)}</div>
                <div class="stat-label">Profondeur max</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{analysis.get('solution_path_length', 0)}</div>
                <div class="stat-label">Étapes solution</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{'✅' if analysis.get('solution_found', False) else '❌'}</div>
                <div class="stat-label">Solution trouvée</div>
            </div>
        </div>
        
        <div class="visualization">
            <div class="controls">
                <div class="control-group">
                    <label for="layout">Disposition:</label>
                    <select id="layout">
                        <option value="force">Force dirigée</option>
                        <option value="tree">Arbre hiérarchique</option>
                        <option value="radial">Radiale</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="depth-filter">Profondeur max:</label>
                    <select id="depth-filter">
                        <option value="all">Toutes</option>
                        {chr(10).join(f'<option value="{i}">{i}</option>' for i in range(analysis.get('max_depth', 0) + 1))}
                    </select>
                </div>
                <div class="control-group">
                    <button id="highlight-solution">Surligner solution</button>
                    <button id="reset-view">Réinitialiser vue</button>
                </div>
            </div>
            
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #4CAF50;"></div>
                    <span>État initial</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #2196F3;"></div>
                    <span>Déplacement</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #FF9800;"></div>
                    <span>Redresser</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #9C27B0;"></div>
                    <span>Coucher</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #607D8B;"></div>
                    <span>État de départ</span>
                </div>
            </div>
            
            <svg id="graph" width="100%" height="800"></svg>
        </div>
    </div>
    
    <script>
        // Graph data
        const graphData = {{
            nodes: {json.dumps(nodes, indent=12)},
            links: {json.dumps(links, indent=12)}
        }};
        
        // Color mapping for different action types
        const colorMap = {{
            'initial': '#4CAF50',    // Green for initial state
            'move': '#2196F3',       // Blue for movements
            'stand_up': '#FF9800',   // Orange for stand up
            'lay_down': '#9C27B0',   // Purple for lay down
            'goal': '#607D8B'        // Gray for goal state
        }};
        
        // Initialize visualization
        const svg = d3.select("#graph");
        const width = parseInt(svg.style("width"));
        const height = parseInt(svg.style("height"));
        
        // Create tooltip
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip");
        
        // Add arrow marker
        svg.append("defs").append("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#999");
        
        let simulation, link, node;
        
        function initializeVisualization() {{
            svg.selectAll("*").remove();
            
            // Re-add arrow marker after clearing
            svg.append("defs").append("marker")
                .attr("id", "arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 20)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#999");
            
            const layout = d3.select("#layout").property("value");
            const maxDepth = d3.select("#depth-filter").property("value");
            
            // Filter nodes and links based on depth
            let filteredNodes = graphData.nodes;
            let filteredLinks = graphData.links;
            
            if (maxDepth !== "all") {{
                const depthLimit = parseInt(maxDepth);
                filteredNodes = graphData.nodes.filter(d => d.depth <= depthLimit);
                const nodeIds = new Set(filteredNodes.map(d => d.id));
                filteredLinks = graphData.links.filter(d => nodeIds.has(d.source) && nodeIds.has(d.target));
            }}
            
            // Create links
            link = svg.append("g")
                .selectAll("line")
                .data(filteredLinks)
                .join("line")
                .attr("class", "link");
            
            // Create nodes
            node = svg.append("g")
                .selectAll("circle")
                .data(filteredNodes)
                .join("circle")
                .attr("class", d => `node ${{d.is_initial ? 'initial' : ''}}`)
                .attr("r", d => d.is_initial ? 12 : (8 + d.children_count))
                .attr("fill", d => colorMap[d.action_type] || "#999")
                .on("mouseover", function(event, d) {{
                    tooltip.transition().duration(200).style("opacity", .9);
                    tooltip.html(`
                        <strong>Nœud ${{d.id}}</strong><br/>
                        Profondeur: ${{d.depth}}<br/>
                        ${{d.description || "État de départ"}}<br/>
                        Enfants: ${{d.children_count}}
                    `)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                }})
                .on("mouseout", function() {{
                    tooltip.transition().duration(500).style("opacity", 0);
                }});
            
            // Setup simulation based on layout
            if (layout === "force") {{
                simulation = d3.forceSimulation(filteredNodes)
                    .force("link", d3.forceLink(filteredLinks).id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-300))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collision", d3.forceCollide().radius(d => d.is_initial ? 15 : 12));
                
                simulation.on("tick", () => {{
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                    
                    node
                        .attr("cx", d => Math.max(15, Math.min(width - 15, d.x)))
                        .attr("cy", d => Math.max(15, Math.min(height - 15, d.y)));
                }});
                
                // Add drag behavior
                node.call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            }} else if (layout === "tree") {{
                // Tree layout
                const root = d3.stratify()
                    .id(d => d.id)
                    .parentId(d => d.parent)
                    (filteredNodes);
                
                const treeLayout = d3.tree().size([width - 100, height - 100]);
                treeLayout(root);
                
                node
                    .attr("cx", d => d.x + 50)
                    .attr("cy", d => d.y + 50);
                
                link
                    .attr("x1", d => {{
                        const source = filteredNodes.find(n => n.id === d.source);
                        return root.descendants().find(n => n.id == source.id).x + 50;
                    }})
                    .attr("y1", d => {{
                        const source = filteredNodes.find(n => n.id === d.source);
                        return root.descendants().find(n => n.id == source.id).y + 50;
                    }})
                    .attr("x2", d => {{
                        const target = filteredNodes.find(n => n.id === d.target);
                        return root.descendants().find(n => n.id == target.id).x + 50;
                    }})
                    .attr("y2", d => {{
                        const target = filteredNodes.find(n => n.id === d.target);
                        return root.descendants().find(n => n.id == target.id).y + 50;
                    }});
            }}
        }}
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        function highlightSolution() {{
            // Find solution path
            const solutionNode = graphData.nodes.find(d => d.is_initial);
            if (!solutionNode) return;
            
            const solutionPath = [];
            let current = solutionNode;
            
            while (current && current.parent !== null) {{
                solutionPath.push(current.id);
                current = graphData.nodes.find(d => d.id === current.parent);
            }}
            if (current) solutionPath.push(current.id);
            
            // Highlight solution path
            node.classed("path-highlight", d => solutionPath.includes(d.id));
            link.classed("path-highlight", d => 
                solutionPath.includes(d.source.id || d.source) && 
                solutionPath.includes(d.target.id || d.target)
            );
        }}
        
        function resetView() {{
            node.classed("path-highlight", false);
            link.classed("path-highlight", false);
        }}
        
        // Event listeners
        d3.select("#layout").on("change", initializeVisualization);
        d3.select("#depth-filter").on("change", initializeVisualization);
        d3.select("#highlight-solution").on("click", highlightSolution);
        d3.select("#reset-view").on("click", resetView);
        
        // Initialize
        initializeVisualization();
    </script>
</body>
</html>'''
    
    output_path = os.path.join(os.path.dirname(__file__), output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path

def main():
    """
    Main function to visualize the reverse search graph
    """
    print("🔄 Visualisateur de Graphe de Recherche Inverse")
    print("=" * 50)
    
    # Load reverse graph
    print("📊 Chargement du graphe inverse...")
    graph = load_reverse_graph()
    
    if not graph:
        print("❌ Impossible de charger le graphe")
        return
    
    # Analyze graph
    analysis = analyze_reverse_graph(graph)
    print(f"✅ Graphe chargé: {analysis['total_nodes']} nœuds")
    print(f"   📏 Profondeur maximale: {analysis['max_depth']}")
    print(f"   🎯 Solution trouvée: {'Oui' if analysis['solution_found'] else 'Non'}")
    if analysis['solution_found']:
        print(f"   📋 Longueur solution: {analysis['solution_path_length']} étapes")
    
    # Generate HTML visualization
    print("\n🎨 Génération de la visualisation HTML...")
    output_file = generate_reverse_html(graph)
    print(f"✅ Visualisation créée: {os.path.basename(output_file)}")
    
    # Instructions
    print(f"\n🌐 Pour visualiser le graphe:")
    print(f"   1. Ouvrez: {os.path.basename(output_file)}")
    print(f"   2. Ou utilisez: python3 serve_visualizations.py")
    print(f"      puis allez sur http://localhost:8000/{os.path.basename(output_file)}")

if __name__ == "__main__":
    main()