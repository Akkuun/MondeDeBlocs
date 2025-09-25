#!/usr/bin/env python3
"""
Launcher script for the Graph Visualization Tools
"""
import os
import sys
import subprocess

def print_header():
    """Print the application header"""
    print("🔍" + "=" * 50 + "🔍")
    print("     GRAPH VISUALIZATION TOOLS")
    print("     Monde de Blocs Search Analysis")
    print("🔍" + "=" * 50 + "🔍")
    print()

def check_files():
    """Check if required files exist"""
    required_files = [
        "arbre_graph_json.py",
        "graph_visualizer.py", 
        "graph_explorer.py",
        "serve_visualizations.py"
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print("❌ Missing required files:")
        for f in missing:
            print(f"   - {f}")
        return False
    return True

def run_command(command, description):
    """Run a command with description"""
    print(f"🚀 {description}")
    print(f"   Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {description}: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⏹️  {description} stopped by user")
        return False

def show_menu():
    """Show the main menu"""
    print("📋 MENU OPTIONS:")
    print("   1. Generate graph and visualizations (Full process)")
    print("   2. Generate visualizations only")
    print("   3. Explore graph data programmatically")
    print("   4. Serve visualizations in browser") 
    print("   5. View documentation")
    print("   6. Check files and status")
    print("   0. Exit")
    print()

def check_status():
    """Check the status of generated files"""
    print("📁 FILE STATUS:")
    
    files_to_check = [
        ("search_graph_detailed.json", "Graph data"),
        ("graph_visualization.html", "Interactive visualization"),
        ("tree_visualization.html", "Tree visualization"),
        ("README_GRAPH.md", "Documentation"),
        ("VISUALIZATION_GUIDE.md", "Usage guide")
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            size_kb = size / 1024
            print(f"   ✅ {description}: {filename} ({size_kb:.1f} KB)")
        else:
            print(f"   ❌ {description}: {filename} (missing)")
    print()

def main():
    """Main function"""
    print_header()
    
    if not check_files():
        print("Please ensure all required files are in the current directory.")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("👉 Enter your choice (0-6): ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        
        print()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
            
        elif choice == '1':
            print("🎯 GENERATING COMPLETE GRAPH AND VISUALIZATIONS")
            print("This will:")
            print("   - Run breadth-first search")
            print("   - Generate JSON graph data")  
            print("   - Create interactive visualizations")
            print("   - Show search statistics")
            print()
            
            if run_command("python arbre_graph_json.py", "Graph generation and visualization"):
                print("\n🎉 All files generated successfully!")
                print("   You can now use option 4 to view in browser")
            
        elif choice == '2':
            if not os.path.exists("search_graph_detailed.json"):
                print("❌ Graph data not found!")
                print("   Please run option 1 first to generate the graph")
            else:
                run_command("python graph_visualizer.py", "Visualization generation")
            
        elif choice == '3':
            if not os.path.exists("search_graph_detailed.json"):
                print("❌ Graph data not found!")
                print("   Please run option 1 first to generate the graph")
            else:
                run_command("python graph_explorer.py", "Graph exploration")
            
        elif choice == '4':
            visualizations = ["graph_visualization.html", "tree_visualization.html"]
            missing_viz = [f for f in visualizations if not os.path.exists(f)]
            
            if missing_viz:
                print("❌ Visualizations not found!")
                print("   Missing files:", ", ".join(missing_viz))
                print("   Please run option 1 or 2 first")
            else:
                print("🌐 Starting local server...")
                print("   This will open your browser automatically")
                print("   Press Ctrl+C to stop the server when done")
                print()
                run_command("python serve_visualizations.py", "Visualization server")
            
        elif choice == '5':
            print("📚 DOCUMENTATION:")
            print()
            docs = [
                ("README_GRAPH.md", "Main documentation"),
                ("VISUALIZATION_GUIDE.md", "Usage guide")
            ]
            
            for doc_file, description in docs:
                if os.path.exists(doc_file):
                    print(f"   📄 {description}: {doc_file}")
                else:
                    print(f"   ❌ {description}: {doc_file} (missing)")
            
            print()
            print("💡 You can open these .md files in any text editor or markdown viewer")
            
        elif choice == '6':
            check_status()
            
        else:
            print("❌ Invalid choice. Please enter a number between 0-6.")
        
        if choice != '0':
            input("\n⏎ Press Enter to continue...")
            print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main()