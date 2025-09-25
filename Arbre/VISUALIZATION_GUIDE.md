# Graph Visualization Usage Guide

This guide shows you how to use the graph visualization tools for the "Monde de Blocs" search problem.

## Quick Start

1. **Generate the graph and visualizations**:
   ```bash
   python arbre_graph_json.py
   ```

2. **View the visualizations**:
   ```bash
   python serve_visualizations.py
   ```
   This will open your browser to http://localhost:8000/tree_visualization.html

## Visualization Options

### Option 1: Interactive D3.js Graph (`graph_visualization.html`)

**Best for**: Exploring the search space interactively

**Features**:
- 🔍 **Zoom and Pan**: Mouse wheel to zoom, click and drag to pan
- 🎯 **Node Selection**: Click nodes to see details
- 📊 **Real-time Filtering**: 
  - Filter by maximum depth (0-6)
  - Filter by action type (move, lay_down, initial)
- 🎨 **Visual Elements**:
  - Blue nodes: Initial state
  - Orange nodes: Move actions  
  - Purple nodes: Lay down actions
  - Red border: Goal states
  - Cyan border: Selected nodes

**Controls**:
- `Max Depth` dropdown: Show nodes up to selected depth
- `Action Type` dropdown: Show only specific action types
- `Reset Zoom` button: Return to default view
- `Center on Goal` button: Focus on the goal node
- `Show Solution Path` button: Highlight the solution sequence

**Usage Tips**:
- Start with "Center on Goal" to see the solution
- Use depth filtering to explore layer by layer
- Hover over nodes for quick information
- Click nodes for detailed selection

### Option 2: Static Tree View (`tree_visualization.html`)

**Best for**: Understanding the solution path and overall structure

**Features**:
- 📋 **Organized Layout**: Nodes grouped by search depth
- 🎯 **Solution Highlighting**: Solution path nodes clearly marked
- 📊 **Statistics Dashboard**: 
  - Total nodes explored
  - Goal nodes found
  - Maximum depth reached
  - Solution step count
- 🎨 **Color Coding**:
  - Light blue: Initial states
  - Light orange: Move actions
  - Light green: Lay down actions
  - Red border: Goal states
  - Cyan border: Solution path nodes

**Controls**:
- `Show up to depth` dropdown: Display nodes up to selected depth
- `Action type` dropdown: Filter by specific action types

**Layout**:
- **Header**: Statistics and solution path visualization
- **Depth Sections**: Nodes organized by search depth (0-6)
- **Node Cards**: Individual nodes with detailed information

## Understanding the Data

### Node Information
Each node displays:
- **Node ID**: Unique identifier
- **Description**: Human-readable action description
- **Parent**: ID of the parent node (or "Root" for initial state)  
- **Children**: Number of child nodes
- **Goal Status**: Whether this is a goal state

### Solution Path
The 4-step solution is:
1. **Node 0** → **Node 4**: Move Cube gris to Table
2. **Node 4** → **Node 23**: Move Cube violet on Cube gris  
3. **Node 23** → **Node 70**: Lay down Donut Saucisse
4. **Node 70** → **Node 132**: Move Cylindre Tungstène on Donut Saucisse (🎯 GOAL)

### Search Statistics
- **200 total nodes** explored in the search space
- **1 goal node** found (optimal solution)
- **Maximum depth of 6** levels explored
- **Breadth-first search** ensures optimal solution

## Advanced Usage

### Programmatic Access
Use `graph_explorer.py` for programmatic analysis:

```python
from graph_explorer import load_graph, get_goal_nodes, get_path_to_node

# Load the graph
graph = load_graph()

# Find goal nodes
goals = get_goal_nodes(graph)

# Get solution path
path = get_path_to_node(graph, goals[0]['id'])

# Analyze specific aspects
depth_2_nodes = [n for n in graph if n['depth'] == 2]
move_actions = [n for n in graph if n['action'] and n['action'][0] == 'move']
```

### JSON Data Structure
The raw JSON data (`search_graph_detailed.json`) contains:
```json
{
  "id": 132,
  "parent": 70,
  "children": [],
  "states": [...],           // Complete object states
  "is_goal": true,
  "action": ["move", 21, 24],
  "description": "Déplacer Cylindre Tungstène sur Donut Saucisse",
  "depth": 4,
  "state_string": "21:24:False|22:23:False|23:25:False|24:25:True|25:0:False"
}
```

## Troubleshooting

### Common Issues

**Visualization not loading?**
- Ensure all files are in the same directory
- Use the local server: `python serve_visualizations.py`
- Check browser console for JavaScript errors

**Server port already in use?**
- The script automatically tries the next port (8001, 8002, etc.)
- Or specify a different port in the script

**Missing visualization files?**
- Run `python arbre_graph_json.py` first to generate all files

**Browser compatibility?**
- Modern browsers support D3.js (Chrome, Firefox, Safari, Edge)
- Internet Explorer is not supported

### Performance Notes
- The interactive graph handles 200 nodes well
- For larger graphs (1000+ nodes), consider filtering by depth
- Tree view is always responsive regardless of graph size

## File Overview

| File | Purpose |
|------|---------|
| `arbre_graph_json.py` | Main script - generates graph and visualizations |
| `graph_visualizer.py` | Standalone visualization generator |
| `graph_explorer.py` | Programmatic graph analysis tools |
| `serve_visualizations.py` | Local HTTP server for viewing |
| `search_graph_detailed.json` | Raw graph data in JSON format |
| `graph_visualization.html` | Interactive D3.js visualization |
| `tree_visualization.html` | Static tree view visualization |

## Next Steps

1. **Explore the visualizations** to understand the search process
2. **Modify search parameters** in `arbre_graph_json.py` (max_depth, etc.)
3. **Extend the visualization** by editing the HTML templates
4. **Add new analysis** using the JSON data structure
5. **Integrate with other tools** using the standardized JSON format

The visualization system provides both high-level understanding and detailed exploration of the search algorithm's behavior!