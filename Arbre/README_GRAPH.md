# Graph-Based Breadth-First Search with JSON Storage

This implementation creates a comprehensive JSON representation of the entire search graph for the "Monde de Blocs" problem.

## Files Created

1. **`arbre_graph_json.py`** - Main implementation with graph-based BFS
2. **`graph_explorer.py`** - Utility script to analyze and explore the generated graph
3. **`search_graph_detailed.json`** - Generated JSON file containing the complete search graph

## Key Features Implemented

### JSON Node Structure
Each node in the graph contains the following fields:

```json
{
  "id": 132,                    // Unique node identifier
  "parent": 70,                 // Parent node ID (null for root)
  "children": [],               // Array of child node IDs
  "states": [...],              // Complete state of all objects at this node
  "is_goal": true,              // Boolean indicating if this is a goal state
  "action": ["move", 21, 24],   // Action that led to this state
  "description": "Déplacer Cylindre Tungstène sur Donut Saucisse",
  "depth": 4,                   // Depth in the search tree
  "state_string": "21:24:False|22:23:False|23:25:False|24:25:True|25:0:False"
}
```

### Graph Features

- **Complete State Storage**: Each node stores the full state of all objects
- **Parent-Child Relationships**: Maintains bidirectional references between nodes
- **Goal Detection**: Automatically marks goal states with `is_goal: true`
- **Action Tracking**: Records the action and description for each transition
- **Duplicate Prevention**: Uses state strings to avoid revisiting identical states

## Search Results

The search found:
- **200 total nodes** explored
- **1 goal node** found at depth 4
- **Solution in 4 steps**:
  1. Move Cube gris to Table
  2. Move Cube violet on Cube gris  
  3. Lay down Donut Saucisse
  4. Move Cylindre Tungstène on Donut Saucisse

## Usage Examples

### Load and Explore the Graph

```python
import json

# Load the graph
with open('search_graph_detailed.json', 'r') as f:
    graph = json.load(f)

# Find goal nodes
goal_nodes = [node for node in graph if node['is_goal']]

# Get path to solution
def get_path_to_node(graph, node_id):
    path = []
    current_id = node_id
    while current_id is not None:
        node = next(n for n in graph if n['id'] == current_id)
        path.insert(0, node)
        current_id = node['parent']
    return path

# Get solution path
solution_path = get_path_to_node(graph, goal_nodes[0]['id'])
```

### Query Specific Information

```python
# Get all nodes at depth 3
depth_3_nodes = [n for n in graph if n['depth'] == 3]

# Find nodes by action type
move_actions = [n for n in graph if n['action'] and n['action'][0] == 'move']
lay_down_actions = [n for n in graph if n['action'] and n['action'][0] == 'lay_down']

# Get children of a specific node
node_5_children = [n for n in graph if n['parent'] == 5]
```

## Graph Statistics

- **Depth Distribution**:
  - Depth 0: 1 node (root)
  - Depth 1: 7 nodes
  - Depth 2: 24 nodes
  - Depth 3: 53 nodes
  - Depth 4: 68 nodes
  - Depth 5: 40 nodes
  - Depth 6: 7 nodes

- **Action Distribution**:
  - Move actions: 140
  - Lay down actions: 59

- **Maximum branching factor**: 8 children per node

## Benefits of This Approach

1. **Complete Traceability**: Every state and transition is recorded
2. **Multiple Analysis Paths**: Can analyze the search process, not just the solution
3. **Reusable Data**: JSON format allows easy integration with other tools
4. **Graph Algorithms**: Can apply graph analysis algorithms (shortest path, centrality, etc.)
5. **Visualization Ready**: Data structure is ready for graph visualization tools

## Visualization Features

Two visualization options are automatically generated:

### 1. Interactive D3.js Visualization (`graph_visualization.html`)
- **Interactive graph** with zoom, pan, and drag capabilities
- **Node filtering** by depth and action type
- **Solution path highlighting** 
- **Hover tooltips** with node details
- **Goal node emphasis** with special styling
- **Real-time statistics** display

### 2. Static Tree View (`tree_visualization.html`)
- **Organized by depth levels** for easy navigation
- **Solution path highlighting** with step-by-step flow
- **Color-coded action types** (move, lay_down, initial)
- **Filtering controls** for depth and action type
- **Comprehensive statistics** dashboard
- **Mobile-friendly design**

### Visualization Features Include:
- 🎯 **Goal state identification** with special markers
- 🔍 **Search path tracing** from root to goal
- 📊 **Statistics dashboard** with real-time updates  
- 🎨 **Color-coded nodes** by action type
- 📱 **Responsive design** for different screen sizes
- ⚡ **Interactive controls** for exploration

## Future Extensions

The JSON structure supports easy extension for:
- **Cost-based search**: Add cost fields to nodes and edges
- **Heuristic search**: Add heuristic values to guide search
- **Multiple goals**: Track different types of goal states
- **Search metadata**: Add timing, memory usage, and other metrics
- **3D visualization**: Extend to three-dimensional graph layouts
- **Animation**: Add animated transitions showing search progression

## Running the Code

```bash
# Generate the graph and visualizations
python arbre_graph_json.py

# Or generate visualizations separately
python graph_visualizer.py

# Explore the results programmatically
python graph_explorer.py
```

## Opening the Visualizations

After running the code, open either HTML file in your web browser:

1. **Interactive Graph**: `graph_visualization.html`
   - Best for exploring the search space interactively
   - Use mouse to zoom, pan, and click on nodes
   - Filter by depth or action type

2. **Tree View**: `tree_visualization.html`  
   - Best for understanding the solution path
   - Organized layout by search depth
   - Clear step-by-step solution progression

The system successfully creates a comprehensive representation of the search space while finding optimal solutions to the blocks world problem.