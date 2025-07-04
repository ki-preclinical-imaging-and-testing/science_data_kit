"""
D3.js Integration for Science Data Kit

This module provides advanced integration with D3.js for creating interactive
data visualizations. It builds upon the basic functionality in visualization_utils.py
to provide more sophisticated and customizable visualizations.
"""

import json
import networkx as nx
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from pathlib import Path
import base64
import io

# Constants for D3.js versions and CDN URLs
D3_VERSION = "7.8.5"  # Latest stable version as of implementation
D3_CDN_URL = f"https://d3js.org/d3.v{D3_VERSION}.min.js"
D3_HIERARCHY_URL = f"https://d3js.org/d3-hierarchy.v{D3_VERSION}.min.js"
D3_SCALE_CHROMATIC_URL = f"https://d3js.org/d3-scale-chromatic.v1.min.js"


class D3Visualization:
    """
    Base class for D3.js visualizations.
    
    This class provides common functionality for creating D3.js visualizations,
    such as generating HTML templates, embedding data, and customizing appearance.
    """
    
    def __init__(
        self,
        width: str = "100%",
        height: str = "600px",
        title: Optional[str] = None,
        container_id: str = "visualization",
        additional_scripts: Optional[List[str]] = None,
        additional_styles: Optional[str] = None,
        responsive: bool = True
    ):
        """
        Initialize a D3 visualization.
        
        Args:
            width: Width of the visualization container.
            height: Height of the visualization container.
            title: Optional title for the visualization.
            container_id: ID for the visualization container.
            additional_scripts: Optional list of additional script URLs to include.
            additional_styles: Optional additional CSS styles.
            responsive: Whether to make the visualization responsive.
        """
        self.width = width
        self.height = height
        self.title = title
        self.container_id = container_id
        self.additional_scripts = additional_scripts or []
        self.additional_styles = additional_styles or ""
        self.responsive = responsive
        self.data = {}
        self.js_code = ""
    
    def set_data(self, data: Dict[str, Any]) -> 'D3Visualization':
        """
        Set the data for the visualization.
        
        Args:
            data: Data to visualize.
            
        Returns:
            Self for method chaining.
        """
        self.data = data
        return self
    
    def set_js_code(self, js_code: str) -> 'D3Visualization':
        """
        Set the JavaScript code for the visualization.
        
        Args:
            js_code: JavaScript code to execute.
            
        Returns:
            Self for method chaining.
        """
        self.js_code = js_code
        return self
    
    def to_html(self) -> str:
        """
        Convert the visualization to an HTML string.
        
        Returns:
            HTML string containing the visualization.
        """
        # Create script tags for additional scripts
        script_tags = f'<script src="{D3_CDN_URL}"></script>'
        for script in self.additional_scripts:
            script_tags += f'\n        <script src="{script}"></script>'
        
        # Create responsive styles if needed
        responsive_styles = ""
        if self.responsive:
            responsive_styles = """
            @media (max-width: 768px) {
                #visualization {
                    height: 400px !important;
                }
            }
            @media (max-width: 480px) {
                #visualization {
                    height: 300px !important;
                }
            }
            """
        
        # Convert data to JSON
        data_json = json.dumps(self.data)
        
        # Create the HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>{self.title or 'D3.js Visualization'}</title>
            {script_tags}
            <style>
                body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
                #{self.container_id} {{ width: {self.width}; height: {self.height}; }}
                {self.additional_styles}
                {responsive_styles}
            </style>
        </head>
        <body>
            <div id="{self.container_id}"></div>
            <script>
                // Visualization data
                const data = {data_json};
                
                // Visualization code
                {self.js_code}
            </script>
        </body>
        </html>
        """
        
        return html
    
    def save(self, file_path: Union[str, Path]) -> None:
        """
        Save the visualization to an HTML file.
        
        Args:
            file_path: Path to save the HTML file.
        """
        html = self.to_html()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)


class ForceDirectedGraph(D3Visualization):
    """
    Force-directed graph visualization using D3.js.
    
    This class provides an enhanced version of the force-directed graph
    visualization with more customization options and interactivity.
    """
    
    def __init__(
        self,
        width: str = "100%",
        height: str = "600px",
        title: Optional[str] = None,
        node_size: Union[int, Callable[[Dict[str, Any]], float]] = 10,
        node_color: Union[str, Callable[[Dict[str, Any]], str]] = "#1f78b4",
        edge_color: Union[str, Callable[[Dict[str, Any]], str]] = "#888888",
        node_label: Optional[Callable[[Dict[str, Any]], str]] = None,
        edge_width: Union[float, Callable[[Dict[str, Any]], float]] = 1.5,
        charge_strength: float = -30,
        link_distance: float = 30,
        collision_radius: Optional[float] = None,
        zoom: bool = True,
        arrow_markers: bool = True,
        tooltip: bool = True,
        highlight_neighbors: bool = True
    ):
        """
        Initialize a force-directed graph visualization.
        
        Args:
            width: Width of the visualization container.
            height: Height of the visualization container.
            title: Optional title for the visualization.
            node_size: Size of nodes or a function that returns the size based on node data.
            node_color: Color of nodes or a function that returns the color based on node data.
            edge_color: Color of edges or a function that returns the color based on edge data.
            node_label: Optional function that returns the label for a node based on node data.
            edge_width: Width of edges or a function that returns the width based on edge data.
            charge_strength: Strength of the charge force (negative for repulsion).
            link_distance: Distance between linked nodes.
            collision_radius: Optional radius for collision detection.
            zoom: Whether to enable zoom and pan.
            arrow_markers: Whether to show arrow markers for directed graphs.
            tooltip: Whether to show tooltips on hover.
            highlight_neighbors: Whether to highlight connected nodes on hover.
        """
        super().__init__(
            width=width,
            height=height,
            title=title,
            container_id="graph",
            additional_scripts=[],
            additional_styles="""
                .node { cursor: pointer; }
                .link { stroke-opacity: 0.6; }
                .node text { pointer-events: none; font: 10px sans-serif; }
                .tooltip {
                    position: absolute;
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 8px;
                    pointer-events: none;
                    font-size: 12px;
                    z-index: 1000;
                }
            """
        )
        
        self.node_size = node_size
        self.node_color = node_color
        self.edge_color = edge_color
        self.node_label = node_label
        self.edge_width = edge_width
        self.charge_strength = charge_strength
        self.link_distance = link_distance
        self.collision_radius = collision_radius
        self.zoom = zoom
        self.arrow_markers = arrow_markers
        self.tooltip = tooltip
        self.highlight_neighbors = highlight_neighbors
    
    def from_networkx(self, G: nx.Graph) -> 'ForceDirectedGraph':
        """
        Create a force-directed graph from a NetworkX graph.
        
        Args:
            G: NetworkX graph to visualize.
            
        Returns:
            Self for method chaining.
        """
        # Determine if the graph is directed
        directed = isinstance(G, nx.DiGraph)
        
        # Convert the graph to a JSON-serializable format
        nodes = []
        for node, attrs in G.nodes(data=True):
            node_data = {'id': node}
            node_data.update(attrs)
            nodes.append(node_data)
        
        edges = []
        for source, target, attrs in G.edges(data=True):
            edge_data = {'source': source, 'target': target}
            edge_data.update(attrs)
            edges.append(edge_data)
        
        # Create the graph data
        graph_data = {
            'nodes': nodes,
            'links': edges,
            'directed': directed
        }
        
        # Set the data
        self.set_data(graph_data)
        
        # Generate the JavaScript code
        js_code = self._generate_js_code()
        
        # Set the JavaScript code
        self.set_js_code(js_code)
        
        return self
    
    def _generate_js_code(self) -> str:
        """
        Generate the JavaScript code for the force-directed graph.
        
        Returns:
            JavaScript code as a string.
        """
        # Handle node size
        if callable(self.node_size):
            node_size_js = "d => nodeSize(d)"
            node_size_func = """
                const nodeSize = d => {
                    // Convert the node size function to JavaScript
                    // This is a simplified version that uses a mapping function
                    return nodeSizeFunc(d);
                };
                
                // Define the node size mapping function
                function nodeSizeFunc(d) {
                    // This would be replaced with actual logic based on the Python function
                    return 5 + (d.size || 1) * 2;
                }
            """
        else:
            node_size_js = str(self.node_size)
            node_size_func = ""
        
        # Handle node color
        if callable(self.node_color):
            node_color_js = "d => nodeColor(d)"
            node_color_func = """
                const nodeColor = d => {
                    // Convert the node color function to JavaScript
                    // This is a simplified version that uses a mapping function
                    return nodeColorFunc(d);
                };
                
                // Define the node color mapping function
                function nodeColorFunc(d) {
                    // This would be replaced with actual logic based on the Python function
                    return d.color || "#1f78b4";
                }
            """
        else:
            node_color_js = f'"{self.node_color}"'
            node_color_func = ""
        
        # Handle edge color
        if callable(self.edge_color):
            edge_color_js = "d => edgeColor(d)"
            edge_color_func = """
                const edgeColor = d => {
                    // Convert the edge color function to JavaScript
                    // This is a simplified version that uses a mapping function
                    return edgeColorFunc(d);
                };
                
                // Define the edge color mapping function
                function edgeColorFunc(d) {
                    // This would be replaced with actual logic based on the Python function
                    return d.color || "#888888";
                }
            """
        else:
            edge_color_js = f'"{self.edge_color}"'
            edge_color_func = ""
        
        # Handle edge width
        if callable(self.edge_width):
            edge_width_js = "d => edgeWidth(d)"
            edge_width_func = """
                const edgeWidth = d => {
                    // Convert the edge width function to JavaScript
                    // This is a simplified version that uses a mapping function
                    return edgeWidthFunc(d);
                };
                
                // Define the edge width mapping function
                function edgeWidthFunc(d) {
                    // This would be replaced with actual logic based on the Python function
                    return d.width || 1.5;
                }
            """
        else:
            edge_width_js = str(self.edge_width)
            edge_width_func = ""
        
        # Handle node label
        if self.node_label:
            node_label_js = "d => nodeLabel(d)"
            node_label_func = """
                const nodeLabel = d => {
                    // Convert the node label function to JavaScript
                    // This is a simplified version that uses a mapping function
                    return nodeLabelFunc(d);
                };
                
                // Define the node label mapping function
                function nodeLabelFunc(d) {
                    // This would be replaced with actual logic based on the Python function
                    return d.name || d.id;
                }
            """
        else:
            node_label_js = "d => d.id"
            node_label_func = ""
        
        # Create the JavaScript code
        js_code = f"""
            // Get the dimensions of the container
            const width = document.getElementById('graph').clientWidth;
            const height = document.getElementById('graph').clientHeight;
            
            // Create the SVG container
            const svg = d3.select('#graph')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            // Add a group for zoom transformation if zoom is enabled
            const g = {"svg.append('g')" if self.zoom else "svg"};
            
            {node_size_func}
            {node_color_func}
            {edge_color_func}
            {edge_width_func}
            {node_label_func}
            
            // Add arrow markers for directed graphs if enabled
            {"if (data.directed && " + str(self.arrow_markers).lower() + ") {" if self.arrow_markers else "if (false) {"}
                svg.append('defs').append('marker')
                    .attr('id', 'arrowhead')
                    .attr('viewBox', '0 -5 10 10')
                    .attr('refX', 15)
                    .attr('refY', 0)
                    .attr('orient', 'auto')
                    .attr('markerWidth', 6)
                    .attr('markerHeight', 6)
                    .attr('xoverflow', 'visible')
                    .append('path')
                    .attr('d', 'M 0,-5 L 10,0 L 0,5')
                    .attr('fill', {edge_color_js})
                    .style('stroke', 'none');
            }
            
            // Add tooltip if enabled
            {"const tooltip = d3.select('body').append('div')" if self.tooltip else "const tooltip = null"}
                {"" if not self.tooltip else ".attr('class', 'tooltip')"}
                {"" if not self.tooltip else ".style('opacity', 0);"}
            
            // Create the simulation
            const simulation = d3.forceSimulation()
                .force('link', d3.forceLink().id(d => d.id).distance({self.link_distance}))
                .force('charge', d3.forceManyBody().strength({self.charge_strength}))
                .force('center', d3.forceCenter(width / 2, height / 2));
            
            // Add collision force if collision radius is specified
            {"if (true) {" if self.collision_radius else "if (false) {"}
                simulation.force('collision', d3.forceCollide().radius({self.collision_radius}));
            }
            
            // Create the links
            const link = g.append('g')
                .attr('class', 'links')
                .selectAll('line')
                .data(data.links)
                .enter().append('line')
                .attr('class', 'link')
                .attr('stroke', {edge_color_js})
                .attr('stroke-width', {edge_width_js})
                {"" if not self.arrow_markers else ".attr('marker-end', data.directed ? 'url(#arrowhead)' : null)"};
            
            // Create the nodes
            const node = g.append('g')
                .attr('class', 'nodes')
                .selectAll('circle')
                .data(data.nodes)
                .enter().append('circle')
                .attr('class', 'node')
                .attr('r', {node_size_js})
                .attr('fill', {node_color_js})
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            // Add node labels if specified
            {"if (true) {" if self.node_label else "if (false) {"}
                const nodeLabels = g.append('g')
                    .attr('class', 'node-labels')
                    .selectAll('text')
                    .data(data.nodes)
                    .enter().append('text')
                    .attr('dx', 12)
                    .attr('dy', '.35em')
                    .text({node_label_js});
            }
            
            // Add tooltips if enabled
            {"if (true) {" if self.tooltip else "if (false) {"}
                node.on('mouseover', function(event, d) {{
                    tooltip.transition()
                        .duration(200)
                        .style('opacity', .9);
                    tooltip.html({node_label_js})
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 28) + 'px');
                    
                    {"if (true) {" if self.highlight_neighbors else "if (false) {"}
                        // Highlight connected nodes and links
                        const connectedNodes = new Set();
                        data.links.forEach(link => {{
                            if (link.source.id === d.id || link.source === d.id) {{
                                connectedNodes.add(typeof link.target === 'object' ? link.target.id : link.target);
                            }}
                            if (link.target.id === d.id || link.target === d.id) {{
                                connectedNodes.add(typeof link.source === 'object' ? link.source.id : link.source);
                            }}
                        }});
                        
                        node.style('opacity', node => {{
                            return node.id === d.id || connectedNodes.has(node.id) ? 1 : 0.1;
                        }});
                        
                        link.style('opacity', link => {{
                            const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                            const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                            return sourceId === d.id || targetId === d.id ? 1 : 0.1;
                        }});
                    }
                }})
                .on('mouseout', function() {{
                    tooltip.transition()
                        .duration(500)
                        .style('opacity', 0);
                    
                    {"if (true) {" if self.highlight_neighbors else "if (false) {"}
                        // Reset highlighting
                        node.style('opacity', 1);
                        link.style('opacity', 0.6);
                    }
                }});
            }
            
            // Add zoom behavior if enabled
            {"if (true) {" if self.zoom else "if (false) {"}
                const zoom = d3.zoom()
                    .scaleExtent([0.1, 10])
                    .on('zoom', zoomed);
                
                svg.call(zoom);
                
                function zoomed(event) {{
                    g.attr('transform', event.transform);
                }}
            }
            
            // Set up the simulation
            simulation
                .nodes(data.nodes)
                .on('tick', ticked);
            
            simulation.force('link')
                .links(data.links);
            
            // Update positions on each tick
            function ticked() {{
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
                
                {"if (true) {" if self.node_label else "if (false) {"}
                    nodeLabels
                        .attr('x', d => d.x)
                        .attr('y', d => d.y);
                }
            }}
            
            // Drag functions
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
        """
        
        return js_code


class HierarchicalVisualization(D3Visualization):
    """
    Base class for hierarchical visualizations using D3.js.
    
    This class provides common functionality for creating hierarchical visualizations
    such as trees, treemaps, and circle packing diagrams.
    """
    
    def __init__(
        self,
        width: str = "100%",
        height: str = "600px",
        title: Optional[str] = None,
        color_scheme: str = "schemeCategory10",
        margin: Dict[str, int] = None
    ):
        """
        Initialize a hierarchical visualization.
        
        Args:
            width: Width of the visualization container.
            height: Height of the visualization container.
            title: Optional title for the visualization.
            color_scheme: D3 color scheme to use.
            margin: Margins for the visualization.
        """
        super().__init__(
            width=width,
            height=height,
            title=title,
            container_id="hierarchy",
            additional_scripts=[D3_HIERARCHY_URL, D3_SCALE_CHROMATIC_URL],
            additional_styles="""
                .node { cursor: pointer; }
                .node:hover { stroke: #000; stroke-width: 1.5px; }
                .node--leaf { fill-opacity: 0.8; }
                .label { font: 11px sans-serif; text-anchor: middle; }
                .tooltip {
                    position: absolute;
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 8px;
                    pointer-events: none;
                    font-size: 12px;
                    z-index: 1000;
                }
            """
        )
        
        self.color_scheme = color_scheme
        self.margin = margin or {"top": 20, "right": 20, "bottom": 30, "left": 40}
    
    def from_dict(self, data: Dict[str, Any]) -> 'HierarchicalVisualization':
        """
        Create a hierarchical visualization from a dictionary.
        
        Args:
            data: Dictionary with hierarchical data.
            
        Returns:
            Self for method chaining.
        """
        self.set_data(data)
        return self
    
    def from_nested_dict(self, data: Dict[str, Any], name_key: str = "name", children_key: str = "children") -> 'HierarchicalVisualization':
        """
        Create a hierarchical visualization from a nested dictionary.
        
        Args:
            data: Nested dictionary with hierarchical data.
            name_key: Key for node names.
            children_key: Key for children nodes.
            
        Returns:
            Self for method chaining.
        """
        # Convert the nested dictionary to the expected format
        def convert_node(node):
            result = {name_key: node.get(name_key, "")}
            if children_key in node and node[children_key]:
                result[children_key] = [convert_node(child) for child in node[children_key]]
            
            # Copy other attributes
            for key, value in node.items():
                if key != name_key and key != children_key:
                    result[key] = value
            
            return result
        
        converted_data = convert_node(data)
        self.set_data(converted_data)
        return self
    
    def from_dataframe(self, df: pd.DataFrame, id_col: str, parent_id_col: str, name_col: Optional[str] = None) -> 'HierarchicalVisualization':
        """
        Create a hierarchical visualization from a DataFrame with parent-child relationships.
        
        Args:
            df: DataFrame with hierarchical data.
            id_col: Column name for node IDs.
            parent_id_col: Column name for parent node IDs.
            name_col: Optional column name for node names. If None, id_col is used.
            
        Returns:
            Self for method chaining.
        """
        # Convert the DataFrame to a hierarchical structure
        name_col = name_col or id_col
        
        # Create a dictionary of nodes
        nodes = {}
        for _, row in df.iterrows():
            node_id = row[id_col]
            node = {"name": row[name_col]}
            
            # Add other columns as attributes
            for col in df.columns:
                if col != id_col and col != parent_id_col and col != name_col:
                    node[col] = row[col]
            
            nodes[node_id] = node
        
        # Build the hierarchy
        root = None
        for _, row in df.iterrows():
            node_id = row[id_col]
            parent_id = row[parent_id_col]
            
            if parent_id and parent_id in nodes:
                # Add this node as a child of its parent
                parent = nodes[parent_id]
                if "children" not in parent:
                    parent["children"] = []
                parent["children"].append(nodes[node_id])
            elif not parent_id:
                # This is a root node
                root = nodes[node_id]
        
        if not root:
            # If no root was found, use the first node
            root = next(iter(nodes.values()))
        
        self.set_data(root)
        return self


class TreeVisualization(HierarchicalVisualization):
    """
    Tree visualization using D3.js.
    
    This class provides functionality for creating tree visualizations
    with customizable appearance and interactivity.
    """
    
    def __init__(
        self,
        width: str = "100%",
        height: str = "600px",
        title: Optional[str] = None,
        color_scheme: str = "schemeCategory10",
        margin: Dict[str, int] = None,
        orientation: str = "vertical",
        node_size: int = 10,
        node_color: Union[str, Callable[[Dict[str, Any]], str]] = "#1f78b4",
        link_color: str = "#888888",
        node_label: Optional[Callable[[Dict[str, Any]], str]] = None,
        tooltip: bool = True,
        collapsible: bool = True
    ):
        """
        Initialize a tree visualization.
        
        Args:
            width: Width of the visualization container.
            height: Height of the visualization container.
            title: Optional title for the visualization.
            color_scheme: D3 color scheme to use.
            margin: Margins for the visualization.
            orientation: Tree orientation ('vertical' or 'horizontal').
            node_size: Size of nodes.
            node_color: Color of nodes or a function that returns the color based on node data.
            link_color: Color of links.
            node_label: Optional function that returns the label for a node based on node data.
            tooltip: Whether to show tooltips on hover.
            collapsible: Whether to make the tree collapsible.
        """
        super().__init__(
            width=width,
            height=height,
            title=title,
            color_scheme=color_scheme,
            margin=margin
        )
        
        self.orientation = orientation
        self.node_size = node_size
        self.node_color = node_color
        self.link_color = link_color
        self.node_label = node_label
        self.tooltip = tooltip
        self.collapsible = collapsible
    
    def _generate_js_code(self) -> str:
        """
        Generate the JavaScript code for the tree visualization.
        
        Returns:
            JavaScript code as a string.
        """
        # Handle node color
        if callable(self.node_color):
            node_color_js = "d => nodeColor(d.data)"
            node_color_func = """
                const nodeColor = d => {
                    // Convert the node color function to JavaScript
                    // This is a simplified version that uses a mapping function
                    return nodeColorFunc(d);
                };
                
                // Define the node color mapping function
                function nodeColorFunc(d) {
                    // This would be replaced with actual logic based on the Python function
                    return d.color || "#1f78b4";
                }
            """
        else:
            node_color_js = f'"{self.node_color}"'
            node_color_func = ""
        
        # Handle node label
        if self.node_label:
            node_label_js = "d => nodeLabel(d.data)"
            node_label_func = """
                const nodeLabel = d => {
                    // Convert the node label function to JavaScript
                    // This is a simplified version that uses a mapping function
                    return nodeLabelFunc(d);
                };
                
                // Define the node label mapping function
                function nodeLabelFunc(d) {
                    // This would be replaced with actual logic based on the Python function
                    return d.name || "";
                }
            """
        else:
            node_label_js = "d => d.data.name"
            node_label_func = ""
        
        # Create the JavaScript code
        js_code = f"""
            // Get the dimensions of the container
            const width = document.getElementById('hierarchy').clientWidth;
            const height = document.getElementById('hierarchy').clientHeight;
            
            // Set up margins
            const margin = {json.dumps(self.margin)};
            const innerWidth = width - margin.left - margin.right;
            const innerHeight = height - margin.top - margin.bottom;
            
            // Create the SVG container
            const svg = d3.select('#hierarchy')
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .append('g')
                .attr('transform', `translate(${{margin.left}},${{margin.top}})`);
            
            {node_color_func}
            {node_label_func}
            
            // Add tooltip if enabled
            {"const tooltip = d3.select('body').append('div')" if self.tooltip else "const tooltip = null"}
                {"" if not self.tooltip else ".attr('class', 'tooltip')"}
                {"" if not self.tooltip else ".style('opacity', 0);"}
            
            // Create the tree layout
            const tree = d3.tree()
                .size([{'innerHeight, innerWidth' if self.orientation == 'horizontal' else 'innerWidth, innerHeight'}]);
            
            // Create the root hierarchy
            const root = d3.hierarchy(data);
            
            // Assign initial positions to nodes
            tree(root);
            
            // Create links
            const link = svg.selectAll('.link')
                .data(root.links())
                .enter().append('path')
                .attr('class', 'link')
                .attr('d', d3.linkHorizontal()
                    .x(d => {'d.y' if self.orientation == 'horizontal' else 'd.x'})
                    .y(d => {'d.x' if self.orientation == 'horizontal' else 'd.y'}))
                .attr('fill', 'none')
                .attr('stroke', '{self.link_color}')
                .attr('stroke-width', 1.5);
            
            // Create nodes
            const node = svg.selectAll('.node')
                .data(root.descendants())
                .enter().append('g')
                .attr('class', d => `node ${{d.children ? 'node--internal' : 'node--leaf'}}`)
                .attr('transform', d => `translate(${{{'d.y' if self.orientation == 'horizontal' else 'd.x'}}}, ${{{'d.x' if self.orientation == 'horizontal' else 'd.y'}}})`);
            
            // Add circles to nodes
            node.append('circle')
                .attr('r', {self.node_size})
                .attr('fill', {node_color_js})
                .attr('stroke', '#fff')
                .attr('stroke-width', 1.5);
            
            // Add labels to nodes
            node.append('text')
                .attr('dy', '.35em')
                .attr('x', d => d.children ? -{self.node_size} - 5 : {self.node_size} + 5)
                .attr('y', d => {'0' if self.orientation == 'horizontal' else '0'})
                .style('text-anchor', d => d.children ? 'end' : 'start')
                .text({node_label_js});
            
            // Add tooltips if enabled
            {"if (true) {" if self.tooltip else "if (false) {"}
                node.on('mouseover', function(event, d) {{
                    tooltip.transition()
                        .duration(200)
                        .style('opacity', .9);
                    tooltip.html({node_label_js})
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 28) + 'px');
                }})
                .on('mouseout', function() {{
                    tooltip.transition()
                        .duration(500)
                        .style('opacity', 0);
                }});
            }
            
            // Make the tree collapsible if enabled
            {"if (true) {" if self.collapsible else "if (false) {"}
                // Toggle children on click
                node.on('click', function(event, d) {{
                    if (d.children) {{
                        d._children = d.children;
                        d.children = null;
                    }} else {{
                        d.children = d._children;
                        d._children = null;
                    }}
                    update(d);
                }});
                
                // Update the tree
                function update(source) {{
                    // Compute the new tree layout
                    tree(root);
                    
                    // Update the nodes
                    const nodes = root.descendants();
                    
                    // Normalize for fixed-depth
                    nodes.forEach(d => {{
                        d.y = d.depth * 180;
                    }});
                    
                    // Update the nodes
                    const node = svg.selectAll('.node')
                        .data(nodes, d => d.id || (d.id = ++i));
                    
                    // Enter any new nodes at the parent's previous position
                    const nodeEnter = node.enter().append('g')
                        .attr('class', d => `node ${{d.children ? 'node--internal' : 'node--leaf'}}`)
                        .attr('transform', d => `translate(${{{'source.y' if self.orientation == 'horizontal' else 'source.x'}}}, ${{{'source.x' if self.orientation == 'horizontal' else 'source.y'}}})`);
                    
                    // Add circles to new nodes
                    nodeEnter.append('circle')
                        .attr('r', 1e-6)
                        .attr('fill', {node_color_js})
                        .attr('stroke', '#fff')
                        .attr('stroke-width', 1.5);
                    
                    // Add labels to new nodes
                    nodeEnter.append('text')
                        .attr('dy', '.35em')
                        .attr('x', d => d.children ? -{self.node_size} - 5 : {self.node_size} + 5)
                        .attr('y', d => {'0' if self.orientation == 'horizontal' else '0'})
                        .style('text-anchor', d => d.children ? 'end' : 'start')
                        .text({node_label_js});
                    
                    // Transition nodes to their new position
                    const nodeUpdate = nodeEnter.merge(node)
                        .transition()
                        .duration(750)
                        .attr('transform', d => `translate(${{{'d.y' if self.orientation == 'horizontal' else 'd.x'}}}, ${{{'d.x' if self.orientation == 'horizontal' else 'd.y'}}})`);
                    
                    // Update the node attributes and style
                    nodeUpdate.select('circle')
                        .attr('r', {self.node_size})
                        .attr('fill', {node_color_js});
                    
                    // Transition exiting nodes to the parent's new position
                    const nodeExit = node.exit().transition()
                        .duration(750)
                        .attr('transform', d => `translate(${{{'source.y' if self.orientation == 'horizontal' else 'source.x'}}}, ${{{'source.x' if self.orientation == 'horizontal' else 'source.y'}}})`);
                    
                    // Reduce the radius of exiting nodes
                    nodeExit.select('circle')
                        .attr('r', 1e-6);
                    
                    // Fade out exiting nodes
                    nodeExit.select('text')
                        .style('fill-opacity', 1e-6);
                    
                    // Update the links
                    const link = svg.selectAll('.link')
                        .data(root.links(), d => d.target.id);
                    
                    // Enter any new links at the parent's previous position
                    const linkEnter = link.enter().insert('path', 'g')
                        .attr('class', 'link')
                        .attr('d', d => {{
                            const o = {{x: source.x, y: source.y}};
                            return d3.linkHorizontal()
                                .x(d => {'d.y' if self.orientation == 'horizontal' else 'd.x'})
                                .y(d => {'d.x' if self.orientation == 'horizontal' else 'd.y'})
                                ({{source: o, target: o}});
                        }})
                        .attr('fill', 'none')
                        .attr('stroke', '{self.link_color}')
                        .attr('stroke-width', 1.5);
                    
                    // Transition links to their new position
                    linkEnter.merge(link).transition()
                        .duration(750)
                        .attr('d', d3.linkHorizontal()
                            .x(d => {'d.y' if self.orientation == 'horizontal' else 'd.x'})
                            .y(d => {'d.x' if self.orientation == 'horizontal' else 'd.y'}));
                    
                    // Transition exiting links to the parent's new position
                    link.exit().transition()
                        .duration(750)
                        .attr('d', d => {{
                            const o = {{x: source.x, y: source.y}};
                            return d3.linkHorizontal()
                                .x(d => {'d.y' if self.orientation == 'horizontal' else 'd.x'})
                                .y(d => {'d.x' if self.orientation == 'horizontal' else 'd.y'})
                                ({{source: o, target: o}});
                        }})
                        .remove();
                }}
            }
        """
        
        return js_code
    
    def to_html(self) -> str:
        """
        Convert the visualization to an HTML string.
        
        Returns:
            HTML string containing the visualization.
        """
        # Generate the JavaScript code
        js_code = self._generate_js_code()
        
        # Set the JavaScript code
        self.set_js_code(js_code)
        
        # Call the parent method
        return super().to_html()


class TreemapVisualization(HierarchicalVisualization):
    """
    Treemap visualization using D3.js.
    
    This class provides functionality for creating treemap visualizations
    with customizable appearance and interactivity.
    """
    
    def __init__(
        self,
        width: str = "100%",
        height: str = "600px",
        title: Optional[str] = None,
        color_scheme: str = "schemeCategory10",
        margin: Dict[str, int] = None,
        padding: int = 1,
        value_key: str = "value",
        color_by: Optional[str] = None,
        tooltip: bool = True,
        zoom: bool = True
    ):
        """
        Initialize a treemap visualization.
        
        Args:
            width: Width of the visualization container.
            height: Height of the visualization container.
            title: Optional title for the visualization.
            color_scheme: D3 color scheme to use.
            margin: Margins for the visualization.
            padding: Padding between treemap cells.
            value_key: Key for node values.
            color_by: Optional key to determine node colors.
            tooltip: Whether to show tooltips on hover.
            zoom: Whether to enable zooming into treemap cells.
        """
        super().__init__(
            width=width,
            height=height,
            title=title,
            color_scheme=color_scheme,
            margin=margin
        )
        
        self.padding = padding
        self.value_key = value_key
        self.color_by = color_by
        self.tooltip = tooltip
        self.zoom = zoom
    
    def _generate_js_code(self) -> str:
        """
        Generate the JavaScript code for the treemap visualization.
        
        Returns:
            JavaScript code as a string.
        """
        # Create the JavaScript code
        js_code = f"""
            // Get the dimensions of the container
            const width = document.getElementById('hierarchy').clientWidth;
            const height = document.getElementById('hierarchy').clientHeight;
            
            // Set up margins
            const margin = {json.dumps(self.margin)};
            const innerWidth = width - margin.left - margin.right;
            const innerHeight = height - margin.top - margin.bottom;
            
            // Create the SVG container
            const svg = d3.select('#hierarchy')
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .append('g')
                .attr('transform', `translate(${{margin.left}},${{margin.top}})`);
            
            // Add tooltip if enabled
            {"const tooltip = d3.select('body').append('div')" if self.tooltip else "const tooltip = null"}
                {"" if not self.tooltip else ".attr('class', 'tooltip')"}
                {"" if not self.tooltip else ".style('opacity', 0);"}
            
            // Create the treemap layout
            const treemap = d3.treemap()
                .size([innerWidth, innerHeight])
                .padding({self.padding});
            
            // Create the root hierarchy
            const root = d3.hierarchy(data)
                .sum(d => d.{self.value_key} || 0)
                .sort((a, b) => b.{self.value_key} - a.{self.value_key});
            
            // Compute the treemap layout
            treemap(root);
            
            // Create a color scale
            const colorScale = d3.scaleOrdinal(d3.{self.color_scheme});
            
            // Create the treemap cells
            const cell = svg.selectAll('g')
                .data(root.leaves())
                .enter().append('g')
                .attr('transform', d => `translate(${{d.x0}},${{d.y0}})`);
            
            // Add rectangles to cells
            cell.append('rect')
                .attr('width', d => d.x1 - d.x0)
                .attr('height', d => d.y1 - d.y0)
                .attr('fill', d => {f"colorScale(d.data.{self.color_by})" if self.color_by else "colorScale(d.parent.data.name)"})
                .attr('stroke', '#fff');
            
            // Add text to cells
            cell.append('text')
                .attr('x', d => (d.x1 - d.x0) / 2)
                .attr('y', d => (d.y1 - d.y0) / 2)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'middle')
                .text(d => d.data.name)
                .style('font-size', '12px')
                .style('fill', '#fff')
                .style('pointer-events', 'none');
            
            // Add tooltips if enabled
            {"if (true) {" if self.tooltip else "if (false) {"}
                cell.on('mouseover', function(event, d) {{
                    tooltip.transition()
                        .duration(200)
                        .style('opacity', .9);
                    tooltip.html(`${{d.data.name}}<br/>${{d.data.{self.value_key} || 0}}`)
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 28) + 'px');
                }})
                .on('mouseout', function() {{
                    tooltip.transition()
                        .duration(500)
                        .style('opacity', 0);
                }});
            }
            
            // Add zoom functionality if enabled
            {"if (true) {" if self.zoom else "if (false) {"}
                cell.on('click', function(event, d) {{
                    zoom(d);
                }});
                
                function zoom(d) {{
                    // Get the parent node
                    const parent = d.parent;
                    
                    // Compute the treemap layout for the parent
                    treemap.size([innerWidth, innerHeight])(root);
                    
                    // Transition to the new view
                    const t = svg.transition()
                        .duration(750);
                    
                    // Update the cells
                    cell.transition(t)
                        .attr('transform', d => `translate(${{d.x0}},${{d.y0}})`)
                        .select('rect')
                        .attr('width', d => d.x1 - d.x0)
                        .attr('height', d => d.y1 - d.y0);
                    
                    // Update the text
                    cell.select('text')
                        .transition(t)
                        .attr('x', d => (d.x1 - d.x0) / 2)
                        .attr('y', d => (d.y1 - d.y0) / 2);
                }}
            }
        """
        
        return js_code
    
    def to_html(self) -> str:
        """
        Convert the visualization to an HTML string.
        
        Returns:
            HTML string containing the visualization.
        """
        # Generate the JavaScript code
        js_code = self._generate_js_code()
        
        # Set the JavaScript code
        self.set_js_code(js_code)
        
        # Call the parent method
        return super().to_html()


def create_force_directed_graph(
    G: nx.Graph,
    width: str = "100%",
    height: str = "600px",
    title: Optional[str] = None,
    node_size: Union[int, Callable[[Dict[str, Any]], float]] = 10,
    node_color: Union[str, Callable[[Dict[str, Any]], str]] = "#1f78b4",
    edge_color: Union[str, Callable[[Dict[str, Any]], str]] = "#888888",
    node_label: Optional[Callable[[Dict[str, Any]], str]] = None,
    edge_width: Union[float, Callable[[Dict[str, Any]], float]] = 1.5,
    charge_strength: float = -30,
    link_distance: float = 30,
    collision_radius: Optional[float] = None,
    zoom: bool = True,
    arrow_markers: bool = True,
    tooltip: bool = True,
    highlight_neighbors: bool = True,
    save_path: Optional[Union[str, Path]] = None
) -> Union[str, None]:
    """
    Create a force-directed graph visualization using D3.js.
    
    Args:
        G: NetworkX graph to visualize.
        width: Width of the visualization container.
        height: Height of the visualization container.
        title: Optional title for the visualization.
        node_size: Size of nodes or a function that returns the size based on node data.
        node_color: Color of nodes or a function that returns the color based on node data.
        edge_color: Color of edges or a function that returns the color based on edge data.
        node_label: Optional function that returns the label for a node based on node data.
        edge_width: Width of edges or a function that returns the width based on edge data.
        charge_strength: Strength of the charge force (negative for repulsion).
        link_distance: Distance between linked nodes.
        collision_radius: Optional radius for collision detection.
        zoom: Whether to enable zoom and pan.
        arrow_markers: Whether to show arrow markers for directed graphs.
        tooltip: Whether to show tooltips on hover.
        highlight_neighbors: Whether to highlight connected nodes on hover.
        save_path: Optional path to save the HTML file.
        
    Returns:
        HTML string containing the visualization if save_path is None, otherwise None.
    """
    # Create the visualization
    vis = ForceDirectedGraph(
        width=width,
        height=height,
        title=title,
        node_size=node_size,
        node_color=node_color,
        edge_color=edge_color,
        node_label=node_label,
        edge_width=edge_width,
        charge_strength=charge_strength,
        link_distance=link_distance,
        collision_radius=collision_radius,
        zoom=zoom,
        arrow_markers=arrow_markers,
        tooltip=tooltip,
        highlight_neighbors=highlight_neighbors
    ).from_networkx(G)
    
    # Save or return the visualization
    if save_path:
        vis.save(save_path)
        return None
    else:
        return vis.to_html()


def create_tree_visualization(
    data: Dict[str, Any],
    width: str = "100%",
    height: str = "600px",
    title: Optional[str] = None,
    orientation: str = "vertical",
    node_size: int = 10,
    node_color: Union[str, Callable[[Dict[str, Any]], str]] = "#1f78b4",
    link_color: str = "#888888",
    node_label: Optional[Callable[[Dict[str, Any]], str]] = None,
    tooltip: bool = True,
    collapsible: bool = True,
    save_path: Optional[Union[str, Path]] = None
) -> Union[str, None]:
    """
    Create a tree visualization using D3.js.
    
    Args:
        data: Dictionary with hierarchical data.
        width: Width of the visualization container.
        height: Height of the visualization container.
        title: Optional title for the visualization.
        orientation: Tree orientation ('vertical' or 'horizontal').
        node_size: Size of nodes.
        node_color: Color of nodes or a function that returns the color based on node data.
        link_color: Color of links.
        node_label: Optional function that returns the label for a node based on node data.
        tooltip: Whether to show tooltips on hover.
        collapsible: Whether to make the tree collapsible.
        save_path: Optional path to save the HTML file.
        
    Returns:
        HTML string containing the visualization if save_path is None, otherwise None.
    """
    # Create the visualization
    vis = TreeVisualization(
        width=width,
        height=height,
        title=title,
        orientation=orientation,
        node_size=node_size,
        node_color=node_color,
        link_color=link_color,
        node_label=node_label,
        tooltip=tooltip,
        collapsible=collapsible
    ).from_dict(data)
    
    # Save or return the visualization
    if save_path:
        vis.save(save_path)
        return None
    else:
        return vis.to_html()


def create_treemap_visualization(
    data: Dict[str, Any],
    width: str = "100%",
    height: str = "600px",
    title: Optional[str] = None,
    color_scheme: str = "schemeCategory10",
    padding: int = 1,
    value_key: str = "value",
    color_by: Optional[str] = None,
    tooltip: bool = True,
    zoom: bool = True,
    save_path: Optional[Union[str, Path]] = None
) -> Union[str, None]:
    """
    Create a treemap visualization using D3.js.
    
    Args:
        data: Dictionary with hierarchical data.
        width: Width of the visualization container.
        height: Height of the visualization container.
        title: Optional title for the visualization.
        color_scheme: D3 color scheme to use.
        padding: Padding between treemap cells.
        value_key: Key for node values.
        color_by: Optional key to determine node colors.
        tooltip: Whether to show tooltips on hover.
        zoom: Whether to enable zooming into treemap cells.
        save_path: Optional path to save the HTML file.
        
    Returns:
        HTML string containing the visualization if save_path is None, otherwise None.
    """
    # Create the visualization
    vis = TreemapVisualization(
        width=width,
        height=height,
        title=title,
        color_scheme=color_scheme,
        padding=padding,
        value_key=value_key,
        color_by=color_by,
        tooltip=tooltip,
        zoom=zoom
    ).from_dict(data)
    
    # Save or return the visualization
    if save_path:
        vis.save(save_path)
        return None
    else:
        return vis.to_html()