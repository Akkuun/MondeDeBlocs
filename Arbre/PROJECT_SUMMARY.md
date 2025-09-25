# 🔍 Complete Graph Visualization System

## Overview

A comprehensive system for visualizing breadth-first search graphs in the "Monde de Blocs" problem, featuring interactive visualizations, JSON graph storage, and multiple analysis tools.

## 🚀 Quick Start

```bash
# Run the launcher for an interactive menu
python launcher.py

# Or generate everything at once
python arbre_graph_json.py

# Then serve the visualizations
python serve_visualizations.py
```

## 📁 Project Structure

```
Arbre/
├── 🎮 launcher.py                    # Interactive launcher menu
├── 🔧 arbre_graph_json.py           # Main graph generation script  
├── 🎨 graph_visualizer.py           # Visualization generator
├── 🔍 graph_explorer.py             # Programmatic graph analysis
├── 🌐 serve_visualizations.py       # Local HTTP server
├── 📊 search_graph_detailed.json    # Generated graph data
├── 🎯 graph_visualization.html      # Interactive D3.js visualization
├── 🌲 tree_visualization.html       # Static tree view  
├── 📚 README_GRAPH.md              # Main documentation
├── 📖 VISUALIZATION_GUIDE.md       # Usage guide
└── 📄 PROJECT_SUMMARY.md           # This file
```

## 🎯 Key Features

### ✅ Graph Generation
- **Complete JSON storage** with node IDs, parent/child relationships
- **Full state tracking** at each search node
- **Goal detection** with `is_goal` boolean flags
- **Action recording** with descriptions
- **Duplicate state prevention** using state strings

### 🎨 Visualization Options

#### Interactive D3.js Graph
- **Zoom and pan** capabilities
- **Node filtering** by depth and action type
- **Solution path highlighting**
- **Hover tooltips** with detailed information
- **Goal node emphasis** with special styling
- **Real-time controls** for exploration

#### Static Tree View  
- **Organized by depth** for clear navigation
- **Solution path visualization** with step flow
- **Color-coded nodes** by action type
- **Filtering controls** for customized views
- **Statistics dashboard** with key metrics
- **Mobile-friendly design**

### 🔧 Analysis Tools
- **Programmatic access** via Python API
- **Graph statistics** calculation
- **Path reconstruction** algorithms
- **Node relationship queries**
- **Custom filtering** and searching

## 📊 Search Results

**Problem Solved**: Moving blocks from initial to goal configuration

**Results**:
- ✅ **200 nodes explored** in search space
- ✅ **1 optimal solution** found at depth 4
- ✅ **4-step solution**:
  1. Move Cube gris to Table
  2. Move Cube violet on Cube gris  
  3. Lay down Donut Saucisse
  4. Move Cylindre Tungstène on Donut Saucisse

**Performance**:
- **Maximum depth**: 6 levels
- **Branching factor**: Up to 8 children per node
- **State uniqueness**: 200 unique states discovered
- **Search efficiency**: Breadth-first guarantees optimal solution

## 🎮 Usage Options

### Option 1: Interactive Launcher
```bash
python launcher.py
```
Provides a menu-driven interface for all operations.

### Option 2: Direct Commands
```bash
# Generate graph and visualizations
python arbre_graph_json.py

# Generate visualizations only (if graph exists)
python graph_visualizer.py

# Analyze graph programmatically  
python graph_explorer.py

# Serve visualizations in browser
python serve_visualizations.py
```

### Option 3: Programmatic Access
```python
from graph_explorer import load_graph, get_goal_nodes
graph = load_graph()
goals = get_goal_nodes(graph)
```

## 🌐 Viewing Visualizations

### Method 1: Local Server (Recommended)
```bash
python serve_visualizations.py
# Opens browser to http://localhost:8000/tree_visualization.html
```

### Method 2: Direct File Opening
Open the HTML files directly in your web browser:
- `graph_visualization.html` - Interactive D3.js graph
- `tree_visualization.html` - Static tree view

## 📈 Graph Structure

### Node Format
```json
{
  "id": 132,                    // Unique identifier
  "parent": 70,                 // Parent node ID  
  "children": [],               // Child node IDs
  "states": [...],              // Complete object states
  "is_goal": true,              // Goal state flag
  "action": ["move", 21, 24],   // Action tuple
  "description": "Move X on Y",  // Human description
  "depth": 4,                   // Search depth
  "state_string": "..."         // State hash string
}
```

### Relationships
- **Parent-Child**: Bidirectional references maintained
- **Depth Levels**: Organized 0-6 with breadth-first ordering
- **Action Flow**: Each transition records the action taken
- **State Evolution**: Complete state stored at each node

## 🔍 Analysis Capabilities

### Statistics Available
- Total nodes explored: **200**
- Goal nodes found: **1**  
- Maximum depth reached: **6**
- Solution length: **4 steps**
- Action distribution: **140 moves, 59 lay-downs**

### Queries Supported
- Find nodes by depth level
- Filter by action type  
- Trace solution paths
- Analyze branching factors
- Search state properties
- Calculate graph metrics

## 🎨 Visual Design

### Color Scheme
- **Light Blue**: Initial states
- **Light Orange**: Move actions
- **Light Green**: Lay down actions  
- **Red Border**: Goal states
- **Cyan Border**: Solution path / Selected nodes

### Layout Features
- **Hierarchical organization** by search depth
- **Responsive design** for different screen sizes
- **Interactive controls** for filtering and navigation
- **Hover effects** for detailed information
- **Clear typography** and accessibility

## 🚀 Future Enhancements

### Potential Extensions
- **Cost-based search**: Add edge weights and costs
- **Heuristic functions**: A* search implementation
- **Multiple goal types**: Different success criteria
- **Animation**: Show search progression over time
- **3D visualization**: Three-dimensional graph layouts
- **Performance metrics**: Timing and memory analysis
- **Export options**: PDF, PNG, SVG output formats

### Integration Options
- **Web applications**: Embed in larger systems
- **Educational tools**: Teaching search algorithms
- **Research platforms**: Algorithm comparison
- **Game analysis**: Similar puzzle solving

## 💡 Technical Details

### Dependencies
- **Python 3.6+**: Core language
- **D3.js**: Interactive visualizations (CDN)
- **Modern Browser**: For visualization viewing
- **HTTP Server**: Built-in Python server

### File Sizes
- **JSON Graph**: ~1.5 MB (detailed state storage)
- **Interactive HTML**: ~25 KB (with embedded D3.js code)
- **Tree HTML**: ~15 KB (static layout)
- **Total Package**: ~1.6 MB

### Browser Compatibility
- ✅ **Chrome/Chromium**: Full support
- ✅ **Firefox**: Full support  
- ✅ **Safari**: Full support
- ✅ **Edge**: Full support
- ❌ **Internet Explorer**: Not supported

## 📚 Documentation

- **README_GRAPH.md**: Technical implementation details
- **VISUALIZATION_GUIDE.md**: User guide and tutorials
- **PROJECT_SUMMARY.md**: This overview document
- **Inline comments**: Comprehensive code documentation

## 🎉 Success Metrics

✅ **Complete graph representation** with JSON storage  
✅ **Interactive visualizations** with multiple views  
✅ **Solution path identification** and highlighting  
✅ **User-friendly interface** with launcher menu  
✅ **Comprehensive documentation** for all components  
✅ **Local server setup** for easy viewing  
✅ **Programmatic access** for advanced analysis  
✅ **Extensible architecture** for future enhancements  

The system successfully transforms the breadth-first search algorithm into a comprehensive, visual, and interactive exploration tool that makes the search process transparent and engaging!