#!/usr/bin/env python3
"""
Simple HTTP server to view the graph visualizations
"""
import http.server
import socketserver
import os
import webbrowser
import threading
import time

def start_server(port=8000):
    """Start a simple HTTP server"""
    os.chdir(os.path.dirname(__file__))
    
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🚀 Starting server at http://localhost:{port}")
            print("\n📊 Available visualizations:")
            print(f"   Interactive Graph: http://localhost:{port}/graph_visualization.html")
            print(f"   Tree View:        http://localhost:{port}/tree_visualization.html")
            print(f"   Graph Explorer:   http://localhost:{port}/README_GRAPH.md")
            print(f"\n🔍 Raw data:")
            print(f"   JSON Graph:       http://localhost:{port}/search_graph_detailed.json")
            print("\n💡 Press Ctrl+C to stop the server")
            
            # Auto-open browser after a short delay
            def open_browser():
                time.sleep(1)
                try:
                    webbrowser.open(f'http://localhost:{port}/tree_visualization.html')
                except:
                    pass
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Trying port {port + 1}...")
            start_server(port + 1)
        else:
            print(f"❌ Error starting server: {e}")

def main():
    """Main function"""
    print("🔍 Graph Visualization Server")
    print("=" * 40)
    
    # Check if visualization files exist
    files_to_check = [
        "graph_visualization.html",
        "tree_visualization.html", 
        "search_graph_detailed.json"
    ]
    
    missing_files = []
    for file in files_to_check:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("⚠️  Missing visualization files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n🔧 Run the following command first:")
        print("   python arbre_graph_json.py")
        return
    
    print("✅ All visualization files found!")
    print()
    
    start_server()

if __name__ == "__main__":
    main()