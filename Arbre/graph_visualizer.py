import json
import os
from collections import defaultdict

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

def generate_interactive_html(graph, output_file="graph_visualization.html"):
    """
    Generate an interactive HTML visualization of the search graph using D3.js
    
    Args:
        graph (list): Graph data
        output_file (str): Output HTML filename
    """
    
    # Prepare nodes and links for D3.js
    nodes = []
    links = []
    
    for node in graph:
        # Create node data
        node_data = {
            'id': node['id'],
            'depth': node['depth'],
            'is_goal': node['is_goal'],
            'description': node['description'],
            'action_type': node['action'][0] if node['action'] else 'initial',
            'children_count': len(node['children']),
            'parent': node['parent']
        }
        nodes.append(node_data)
        
        # Create links to children
        for child_id in node['children']:
            links.append({
                'source': node['id'],
                'target': child_id
            })
    
    # Calculate positions using a simple tree layout
    positions = calculate_tree_positions(graph)
    for i, node in enumerate(nodes):
        if node['id'] in positions:
            node['x'] = positions[node['id']]['x']
            node['y'] = positions[node['id']]['y']
    
    html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Graph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }}
        
        .controls {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .control-group {{
            display: inline-block;
            margin-right: 20px;
        }}
        
        label {{
            font-weight: bold;
            margin-right: 8px;
        }}
        
        select, button {{
            padding: 5px 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        
        button {{
            background-color: #007bff;
            color: white;
            cursor: pointer;
        }}
        
        button:hover {{
            background-color: #0056b3;
        }}
        
        .graph-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .node {{
            cursor: pointer;
            stroke: #333;
            stroke-width: 1px;
        }}
        
        .node.goal {{
            stroke: #ff6b6b;
            stroke-width: 3px;
        }}
        
        .node.selected {{
            stroke: #4ecdc4;
            stroke-width: 3px;
        }}
        
        .link {{
            fill: none;
            stroke: #999;
            stroke-width: 1px;
        }}
        
        .link.highlighted {{
            stroke: #ff6b6b;
            stroke-width: 2px;
        }}
        
        .node-text {{
            font-size: 10px;
            text-anchor: middle;
            pointer-events: none;
            fill: #333;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            max-width: 300px;
        }}
        
        .info-panel {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }}
        
        .stat-item {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        
        .legend {{
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .legend-circle {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 1px solid #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Search Graph Visualization</h1>
        
        <div class="controls">
            <div class="control-group">
                <label for="depthFilter">Max Depth:</label>
                <select id="depthFilter">
                    <option value="-1">All Depths</option>
                    <option value="0">0</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                    <option value="6">6</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="actionFilter">Action Type:</label>
                <select id="actionFilter">
                    <option value="all">All Actions</option>
                    <option value="initial">Initial</option>
                    <option value="move">Move</option>
                    <option value="lay_down">Lay Down</option>
                </select>
            </div>
            
            <div class="control-group">
                <button onclick="resetZoom()">Reset Zoom</button>
                <button onclick="centerOnGoal()">Center on Goal</button>
                <button onclick="showSolutionPath()">Show Solution Path</button>
            </div>
        </div>
        
        <div class="graph-container">
            <svg id="graph"></svg>
        </div>
        
        <div class="info-panel">
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value" id="totalNodes">{len(nodes)}</div>
                    <div class="stat-label">Total Nodes</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="goalNodes">{len([n for n in nodes if n['is_goal']])}</div>
                    <div class="stat-label">Goal Nodes</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="maxDepth">{max(n['depth'] for n in nodes)}</div>
                    <div class="stat-label">Max Depth</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="visibleNodes">{len(nodes)}</div>
                    <div class="stat-label">Visible Nodes</div>
                </div>
            </div>
            
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-circle" style="background-color: #e3f2fd;"></div>
                    <span>Initial State</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background-color: #fff3e0;"></div>
                    <span>Move Action</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background-color: #f3e5f5;"></div>
                    <span>Lay Down Action</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background-color: #ffebee; border: 3px solid #ff6b6b;"></div>
                    <span>Goal State</span>
                </div>
            </div>
        </div>
        
        <div class="tooltip" id="tooltip" style="display: none;"></div>
    </div>

    <script>
        // Data
        const graphData = {{
            nodes: {json.dumps(nodes, indent=12)},
            links: {json.dumps(links, indent=12)}
        }};
        
        // Set up SVG
        const width = 1200;
        const height = 800;
        const svg = d3.select("#graph")
            .attr("width", width)
            .attr("height", height);
            
        // Create zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on("zoom", function(event) {{
                g.attr("transform", event.transform);
            }});
            
        svg.call(zoom);
        
        // Create main group
        const g = svg.append("g");
        
        // Color scales
        const colorScale = d3.scaleOrdinal()
            .domain(['initial', 'move', 'lay_down'])
            .range(['#e3f2fd', '#fff3e0', '#f3e5f5']);
            
        // Current data
        let currentNodes = [...graphData.nodes];
        let currentLinks = [...graphData.links];
        let selectedNode = null;
        let solutionPath = [];
        
        // Tooltip
        const tooltip = d3.select("#tooltip");
        
        function updateVisualization() {{
            // Clear existing elements
            g.selectAll("*").remove();
            
            // Create links
            const link = g.selectAll(".link")
                .data(currentLinks)
                .enter().append("line")
                .attr("class", "link")
                .attr("x1", d => {{
                    const source = currentNodes.find(n => n.id === d.source);
                    return source ? source.x : 0;
                }})
                .attr("y1", d => {{
                    const source = currentNodes.find(n => n.id === d.source);
                    return source ? source.y : 0;
                }})
                .attr("x2", d => {{
                    const target = currentNodes.find(n => n.id === d.target);
                    return target ? target.x : 0;
                }})
                .attr("y2", d => {{
                    const target = currentNodes.find(n => n.id === d.target);
                    return target ? target.y : 0;
                }});
            
            // Create nodes
            const node = g.selectAll(".node")
                .data(currentNodes)
                .enter().append("circle")
                .attr("class", d => `node ${{d.is_goal ? 'goal' : ''}}`)
                .attr("r", d => d.is_goal ? 8 : (d.action_type === 'initial' ? 10 : 6))
                .attr("cx", d => d.x)
                .attr("cy", d => d.y)
                .attr("fill", d => d.is_goal ? '#ffebee' : colorScale(d.action_type))
                .on("click", function(event, d) {{
                    selectNode(d);
                }})
                .on("mouseover", function(event, d) {{
                    showTooltip(event, d);
                }})
                .on("mouseout", function() {{
                    hideTooltip();
                }});
            
            // Add node labels
            const nodeText = g.selectAll(".node-text")
                .data(currentNodes)
                .enter().append("text")
                .attr("class", "node-text")
                .attr("x", d => d.x)
                .attr("y", d => d.y + 3)
                .text(d => d.id);
        }}
        
        function selectNode(node) {{
            selectedNode = node;
            
            // Update visual selection
            g.selectAll(".node")
                .classed("selected", d => d.id === node.id);
                
            // Show node details in tooltip
            showNodeDetails(node);
        }}
        
        function showTooltip(event, node) {{
            const content = `
                <strong>Node ${{node.id}}</strong><br>
                Depth: ${{node.depth}}<br>
                Action: ${{node.action_type}}<br>
                ${{node.description ? 'Description: ' + node.description + '<br>' : ''}}
                Children: ${{node.children_count}}<br>
                ${{node.is_goal ? '<strong>🎯 GOAL STATE</strong>' : ''}}
            `;
            
            tooltip
                .style("display", "block")
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px")
                .html(content);
        }}
        
        function hideTooltip() {{
            tooltip.style("display", "none");
        }}
        
        function showNodeDetails(node) {{
            // This could be expanded to show more detailed information
            console.log("Selected node:", node);
        }}
        
        function applyFilters() {{
            const depthFilter = parseInt(document.getElementById("depthFilter").value);
            const actionFilter = document.getElementById("actionFilter").value;
            
            // Filter nodes
            currentNodes = graphData.nodes.filter(node => {{
                const depthMatch = depthFilter === -1 || node.depth <= depthFilter;
                const actionMatch = actionFilter === 'all' || node.action_type === actionFilter;
                return depthMatch && actionMatch;
            }});
            
            // Filter links to only include visible nodes
            const visibleNodeIds = new Set(currentNodes.map(n => n.id));
            currentLinks = graphData.links.filter(link => 
                visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target)
            );
            
            // Update stats
            document.getElementById("visibleNodes").textContent = currentNodes.length;
            
            updateVisualization();
        }}
        
        function resetZoom() {{
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
        }}
        
        function centerOnGoal() {{
            const goalNode = currentNodes.find(n => n.is_goal);
            if (goalNode) {{
                const transform = d3.zoomIdentity
                    .translate(width / 2 - goalNode.x, height / 2 - goalNode.y)
                    .scale(1.5);
                    
                svg.transition().duration(750).call(
                    zoom.transform,
                    transform
                );
                
                selectNode(goalNode);
            }}
        }}
        
        function showSolutionPath() {{
            // Find goal node and trace back to root
            const goalNode = graphData.nodes.find(n => n.is_goal);
            if (!goalNode) return;
            
            const path = [];
            let currentId = goalNode.id;
            
            while (currentId !== null) {{
                const node = graphData.nodes.find(n => n.id === currentId);
                if (node) {{
                    path.unshift(node.id);
                    currentId = node.parent;
                }} else {{
                    break;
                }}
            }}
            
            // Highlight solution path
            g.selectAll(".link")
                .classed("highlighted", d => {{
                    const sourceIndex = path.indexOf(d.source);
                    const targetIndex = path.indexOf(d.target);
                    return sourceIndex !== -1 && targetIndex !== -1 && Math.abs(sourceIndex - targetIndex) === 1;
                }});
                
            console.log("Solution path:", path);
        }}
        
        // Event listeners
        document.getElementById("depthFilter").addEventListener("change", applyFilters);
        document.getElementById("actionFilter").addEventListener("change", applyFilters);
        
        // Initial visualization
        updateVisualization();
    </script>
</body>
</html>
    '''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Interactive visualization generated: {output_file}")
    print(f"Open the file in a web browser to view the graph")

def calculate_tree_positions(graph):
    """
    Calculate positions for nodes in a tree layout
    
    Args:
        graph (list): Graph data
    
    Returns:
        dict: Dictionary mapping node_id to {x, y} positions
    """
    positions = {}
    
    # Group nodes by depth
    depth_groups = defaultdict(list)
    for node in graph:
        depth_groups[node['depth']].append(node)
    
    # Calculate positions
    y_spacing = 120
    base_y = 50
    
    for depth, nodes in depth_groups.items():
        y = base_y + depth * y_spacing
        
        # Calculate x positions to spread nodes evenly
        if len(nodes) == 1:
            x_positions = [600]  # Center single node
        else:
            x_start = 100
            x_end = 1100
            x_spacing = (x_end - x_start) / (len(nodes) - 1) if len(nodes) > 1 else 0
            x_positions = [x_start + i * x_spacing for i in range(len(nodes))]
        
        for i, node in enumerate(nodes):
            positions[node['id']] = {
                'x': x_positions[i],
                'y': y
            }
    
    return positions

def generate_simple_tree_html(graph, output_file="tree_visualization.html"):
    """
    Generate a simpler tree visualization using HTML/CSS
    
    Args:
        graph (list): Graph data
        output_file (str): Output HTML filename
    """
    
    # Find solution path
    goal_node = next((n for n in graph if n['is_goal']), None)
    solution_path = []
    if goal_node:
        current_id = goal_node['id']
        while current_id is not None:
            node = next((n for n in graph if n['id'] == current_id), None)
            if node:
                solution_path.insert(0, node['id'])
                current_id = node['parent']
            else:
                break
    
    html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Tree Visualization</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #fff;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 5px;
        }}
        
        .solution-path {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        
        .solution-path h2 {{
            color: #333;
            margin-top: 0;
            text-align: center;
        }}
        
        .path-steps {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            align-items: center;
        }}
        
        .path-step {{
            background: white;
            padding: 10px 15px;
            border-radius: 25px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            min-width: 120px;
            text-align: center;
        }}
        
        .path-step.goal {{
            background: #ff6b6b;
            color: white;
            font-weight: bold;
        }}
        
        .path-arrow {{
            font-size: 1.5em;
            color: #666;
        }}
        
        .depth-section {{
            margin-bottom: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
        }}
        
        .depth-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-weight: bold;
        }}
        
        .nodes-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }}
        
        .node-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            transition: all 0.3s ease;
        }}
        
        .node-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        .node-card.goal {{
            border-color: #ff6b6b;
            background: linear-gradient(135deg, #ffebee 0%, #fff5f5 100%);
        }}
        
        .node-card.solution-path {{
            border-color: #4ecdc4;
            background: linear-gradient(135deg, #e0f7f7 0%, #f0ffff 100%);
        }}
        
        .node-id {{
            background: #6c757d;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 10px;
        }}
        
        .node-id.goal {{
            background: #ff6b6b;
        }}
        
        .node-id.solution {{
            background: #4ecdc4;
        }}
        
        .node-description {{
            color: #495057;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        
        .node-details {{
            font-size: 0.85em;
            color: #6c757d;
        }}
        
        .action-move {{ background-color: #fff3cd; }}
        .action-lay_down {{ background-color: #d4edda; }}
        .action-initial {{ background-color: #cce7ff; }}
        
        .filters {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .filter-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        select {{
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }}
        
        label {{
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Search Tree Visualization</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(graph)}</div>
                <div class="stat-label">Total Nodes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len([n for n in graph if n['is_goal']])}</div>
                <div class="stat-label">Goal Nodes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{max(n['depth'] for n in graph) if graph else 0}</div>
                <div class="stat-label">Max Depth</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(solution_path)}</div>
                <div class="stat-label">Solution Steps</div>
            </div>
        </div>
        
        <div class="solution-path">
            <h2>🎯 Solution Path</h2>
            <div class="path-steps">
    '''
    
    # Add solution path
    if goal_node:
        path_nodes = [next(n for n in graph if n['id'] == node_id) for node_id in solution_path]
        for i, node in enumerate(path_nodes):
            if i > 0:
                html_content += '<div class="path-arrow">→</div>'
            
            css_class = "goal" if node['is_goal'] else ""
            html_content += f'''
                <div class="path-step {css_class}">
                    <div><strong>Node {node['id']}</strong></div>
                    <div style="font-size: 0.8em; margin-top: 5px;">
                        {node['description'] if node['description'] != 'Initial state' else 'Start'}
                    </div>
                </div>
            '''
    
    html_content += '''
            </div>
        </div>
        
        <div class="filters">
            <div class="filter-group">
                <label for="depthFilter">Show up to depth:</label>
                <select id="depthFilter" onchange="filterByDepth()">
    '''
    
    max_depth = max(n['depth'] for n in graph) if graph else 0
    for depth in range(max_depth + 1):
        selected = "selected" if depth == max_depth else ""
        html_content += f'<option value="{depth}" {selected}>Depth {depth}</option>'
    
    html_content += '''
                </select>
            </div>
            <div class="filter-group">
                <label for="actionFilter">Action type:</label>
                <select id="actionFilter" onchange="filterByAction()">
                    <option value="all">All Actions</option>
                    <option value="initial">Initial</option>
                    <option value="move">Move</option>
                    <option value="lay_down">Lay Down</option>
                </select>
            </div>
        </div>
        
        <div id="content">
    '''
    
    # Group nodes by depth
    depth_groups = defaultdict(list)
    for node in graph:
        depth_groups[node['depth']].append(node)
    
    # Generate depth sections
    for depth in sorted(depth_groups.keys()):
        nodes = depth_groups[depth]
        html_content += f'''
        <div class="depth-section" data-depth="{depth}">
            <div class="depth-header">
                📊 Depth {depth} - {len(nodes)} node{'s' if len(nodes) != 1 else ''}
            </div>
            <div class="nodes-grid">
        '''
        
        for node in nodes:
            # Determine CSS classes
            classes = []
            if node['is_goal']:
                classes.append('goal')
            if node['id'] in solution_path:
                classes.append('solution-path')
            
            node_class = ' '.join(classes)
            
            # Determine node ID class
            id_class = ""
            if node['is_goal']:
                id_class = "goal"
            elif node['id'] in solution_path:
                id_class = "solution"
            
            # Action type for background
            action_bg = f"action-{node.get('action', ['initial'])[0] if node.get('action') else 'initial'}"
            
            children_info = f"{len(node['children'])} child{'ren' if len(node['children']) != 1 else ''}" if node['children'] else "No children"
            
            html_content += f'''
            <div class="node-card {node_class} {action_bg}" data-action="{node.get('action', ['initial'])[0] if node.get('action') else 'initial'}">
                <div class="node-id {id_class}">Node {node['id']}</div>
                <div class="node-description">{node['description']}</div>
                <div class="node-details">
                    <div>Parent: {node['parent'] if node['parent'] is not None else 'Root'}</div>
                    <div>Children: {children_info}</div>
                    {f'<div style="color: #ff6b6b; font-weight: bold;">🎯 GOAL STATE</div>' if node['is_goal'] else ''}
                </div>
            </div>
            '''
        
        html_content += '''
            </div>
        </div>
        '''
    
    html_content += '''
        </div>
    </div>

    <script>
        function filterByDepth() {
            const maxDepth = parseInt(document.getElementById('depthFilter').value);
            const sections = document.querySelectorAll('.depth-section');
            
            sections.forEach(section => {
                const depth = parseInt(section.getAttribute('data-depth'));
                section.style.display = depth <= maxDepth ? 'block' : 'none';
            });
        }
        
        function filterByAction() {
            const actionType = document.getElementById('actionFilter').value;
            const cards = document.querySelectorAll('.node-card');
            
            cards.forEach(card => {
                const cardAction = card.getAttribute('data-action');
                card.style.display = actionType === 'all' || cardAction === actionType ? 'block' : 'none';
            });
        }
    </script>
</body>
</html>
    '''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Tree visualization generated: {output_file}")
    print(f"Open the file in a web browser to view the tree")

def main():
    """Main function to generate visualizations"""
    
    # Load the graph
    graph = load_graph()
    if not graph:
        print("No graph data found. Please run arbre_graph_json.py first.")
        return
    
    print("Generating visualizations...")
    
    # Generate interactive D3.js visualization
    generate_interactive_html(graph, "graph_visualization.html")
    
    # Generate simpler tree visualization
    generate_simple_tree_html(graph, "tree_visualization.html")
    
    print("\nTwo visualizations have been created:")
    print("1. graph_visualization.html - Interactive D3.js graph with zoom and pan")
    print("2. tree_visualization.html - Static tree view organized by depth")
    print("\nOpen either file in your web browser to explore the search graph!")

if __name__ == "__main__":
    main()