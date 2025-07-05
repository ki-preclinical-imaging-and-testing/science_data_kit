"""
3D Visualization Utilities for Science Data Kit

This module provides utilities for creating 3D visualizations of scientific data
using libraries like Plotly and Matplotlib. It includes functions for creating
3D scatter plots, surface plots, volume rendering, and other 3D visualizations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Union, Callable

# Import visualization libraries
try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class Visualization3DError(Exception):
    """Exception raised for errors in 3D visualization functions."""
    pass


def check_dependencies(library: str) -> bool:
    """
    Check if the required dependencies are available.
    
    Args:
        library: The library to check for ('matplotlib', 'plotly', or 'all').
        
    Returns:
        True if the dependencies are available, False otherwise.
        
    Raises:
        ValueError: If an invalid library name is provided.
    """
    if library.lower() == 'matplotlib':
        return MATPLOTLIB_AVAILABLE
    elif library.lower() == 'plotly':
        return PLOTLY_AVAILABLE
    elif library.lower() == 'all':
        return MATPLOTLIB_AVAILABLE and PLOTLY_AVAILABLE
    else:
        raise ValueError(f"Invalid library name: {library}. Expected 'matplotlib', 'plotly', or 'all'.")


def scatter_3d(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    z_column: str,
    color_column: Optional[str] = None,
    size_column: Optional[str] = None,
    title: str = '3D Scatter Plot',
    library: str = 'plotly',
    **kwargs
) -> Any:
    """
    Create a 3D scatter plot.
    
    Args:
        data: DataFrame containing the data to plot.
        x_column: Name of the column to use for the x-axis.
        y_column: Name of the column to use for the y-axis.
        z_column: Name of the column to use for the z-axis.
        color_column: Name of the column to use for coloring points.
        size_column: Name of the column to use for sizing points.
        title: Title of the plot.
        library: Visualization library to use ('matplotlib' or 'plotly').
        **kwargs: Additional keyword arguments to pass to the plotting function.
        
    Returns:
        The plot object (matplotlib.figure.Figure or plotly.graph_objects.Figure).
        
    Raises:
        Visualization3DError: If the required dependencies are not available.
    """
    if library.lower() == 'matplotlib':
        if not MATPLOTLIB_AVAILABLE:
            raise Visualization3DError("Matplotlib is not available. Please install it with 'pip install matplotlib'.")
        
        fig = plt.figure(figsize=kwargs.get('figsize', (10, 8)))
        ax = fig.add_subplot(111, projection='3d')
        
        # Extract data
        x = data[x_column]
        y = data[y_column]
        z = data[z_column]
        
        # Set up color and size
        color = data[color_column] if color_column else 'blue'
        size = data[size_column] * 10 if size_column else 50
        
        # Create scatter plot
        scatter = ax.scatter(x, y, z, c=color, s=size, alpha=kwargs.get('alpha', 0.7))
        
        # Add colorbar if color_column is provided
        if color_column:
            cbar = fig.colorbar(scatter, ax=ax, pad=0.1)
            cbar.set_label(color_column)
        
        # Set labels and title
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        ax.set_zlabel(z_column)
        ax.set_title(title)
        
        # Add grid
        ax.grid(kwargs.get('grid', True))
        
        return fig
    
    elif library.lower() == 'plotly':
        if not PLOTLY_AVAILABLE:
            raise Visualization3DError("Plotly is not available. Please install it with 'pip install plotly'.")
        
        # Create scatter plot
        if color_column and size_column:
            fig = px.scatter_3d(
                data, x=x_column, y=y_column, z=z_column,
                color=color_column, size=size_column,
                title=title,
                opacity=kwargs.get('opacity', 0.7)
            )
        elif color_column:
            fig = px.scatter_3d(
                data, x=x_column, y=y_column, z=z_column,
                color=color_column,
                title=title,
                opacity=kwargs.get('opacity', 0.7)
            )
        elif size_column:
            fig = px.scatter_3d(
                data, x=x_column, y=y_column, z=z_column,
                size=size_column,
                title=title,
                opacity=kwargs.get('opacity', 0.7)
            )
        else:
            fig = px.scatter_3d(
                data, x=x_column, y=y_column, z=z_column,
                title=title,
                opacity=kwargs.get('opacity', 0.7)
            )
        
        # Update layout
        fig.update_layout(
            scene=dict(
                xaxis_title=x_column,
                yaxis_title=y_column,
                zaxis_title=z_column
            ),
            margin=dict(l=0, r=0, b=0, t=30)
        )
        
        return fig
    
    else:
        raise ValueError(f"Invalid library: {library}. Expected 'matplotlib' or 'plotly'.")


def surface_3d(
    x: Union[np.ndarray, List],
    y: Union[np.ndarray, List],
    z: Union[np.ndarray, List, Callable],
    title: str = '3D Surface Plot',
    colormap: str = 'viridis',
    library: str = 'plotly',
    **kwargs
) -> Any:
    """
    Create a 3D surface plot.
    
    Args:
        x: 1D array of x coordinates or 2D array of x coordinates (meshgrid).
        y: 1D array of y coordinates or 2D array of y coordinates (meshgrid).
        z: 2D array of z coordinates or a function that takes x and y arrays and returns z values.
        title: Title of the plot.
        colormap: Colormap to use for the surface.
        library: Visualization library to use ('matplotlib' or 'plotly').
        **kwargs: Additional keyword arguments to pass to the plotting function.
        
    Returns:
        The plot object (matplotlib.figure.Figure or plotly.graph_objects.Figure).
        
    Raises:
        Visualization3DError: If the required dependencies are not available.
    """
    # Convert lists to numpy arrays
    x = np.array(x)
    y = np.array(y)
    
    # Create meshgrid if x and y are 1D
    if x.ndim == 1 and y.ndim == 1:
        X, Y = np.meshgrid(x, y)
    else:
        X, Y = x, y
    
    # Calculate z values if z is a function
    if callable(z):
        Z = z(X, Y)
    else:
        Z = np.array(z)
    
    if library.lower() == 'matplotlib':
        if not MATPLOTLIB_AVAILABLE:
            raise Visualization3DError("Matplotlib is not available. Please install it with 'pip install matplotlib'.")
        
        fig = plt.figure(figsize=kwargs.get('figsize', (10, 8)))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create surface plot
        surf = ax.plot_surface(
            X, Y, Z,
            cmap=colormap,
            alpha=kwargs.get('alpha', 1.0),
            linewidth=kwargs.get('linewidth', 0),
            antialiased=kwargs.get('antialiased', True)
        )
        
        # Add colorbar
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        
        # Set labels and title
        ax.set_xlabel(kwargs.get('xlabel', 'X'))
        ax.set_ylabel(kwargs.get('ylabel', 'Y'))
        ax.set_zlabel(kwargs.get('zlabel', 'Z'))
        ax.set_title(title)
        
        return fig
    
    elif library.lower() == 'plotly':
        if not PLOTLY_AVAILABLE:
            raise Visualization3DError("Plotly is not available. Please install it with 'pip install plotly'.")
        
        # Create surface plot
        fig = go.Figure(data=[
            go.Surface(
                z=Z,
                x=X,
                y=Y,
                colorscale=colormap,
                opacity=kwargs.get('opacity', 1.0)
            )
        ])
        
        # Update layout
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title=kwargs.get('xlabel', 'X'),
                yaxis_title=kwargs.get('ylabel', 'Y'),
                zaxis_title=kwargs.get('zlabel', 'Z')
            ),
            margin=dict(l=0, r=0, b=0, t=30)
        )
        
        return fig
    
    else:
        raise ValueError(f"Invalid library: {library}. Expected 'matplotlib' or 'plotly'.")


def contour_3d(
    x: Union[np.ndarray, List],
    y: Union[np.ndarray, List],
    z: Union[np.ndarray, List, Callable],
    title: str = '3D Contour Plot',
    colormap: str = 'viridis',
    library: str = 'plotly',
    **kwargs
) -> Any:
    """
    Create a 3D contour plot.
    
    Args:
        x: 1D array of x coordinates or 2D array of x coordinates (meshgrid).
        y: 1D array of y coordinates or 2D array of y coordinates (meshgrid).
        z: 2D array of z coordinates or a function that takes x and y arrays and returns z values.
        title: Title of the plot.
        colormap: Colormap to use for the contour.
        library: Visualization library to use ('matplotlib' or 'plotly').
        **kwargs: Additional keyword arguments to pass to the plotting function.
        
    Returns:
        The plot object (matplotlib.figure.Figure or plotly.graph_objects.Figure).
        
    Raises:
        Visualization3DError: If the required dependencies are not available.
    """
    # Convert lists to numpy arrays
    x = np.array(x)
    y = np.array(y)
    
    # Create meshgrid if x and y are 1D
    if x.ndim == 1 and y.ndim == 1:
        X, Y = np.meshgrid(x, y)
    else:
        X, Y = x, y
    
    # Calculate z values if z is a function
    if callable(z):
        Z = z(X, Y)
    else:
        Z = np.array(z)
    
    if library.lower() == 'matplotlib':
        if not MATPLOTLIB_AVAILABLE:
            raise Visualization3DError("Matplotlib is not available. Please install it with 'pip install matplotlib'.")
        
        fig = plt.figure(figsize=kwargs.get('figsize', (10, 8)))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create contour plot
        levels = kwargs.get('levels', 10)
        cset = ax.contour(
            X, Y, Z,
            levels=levels,
            cmap=colormap,
            alpha=kwargs.get('alpha', 1.0),
            linewidths=kwargs.get('linewidths', 1)
        )
        
        # Add colorbar
        fig.colorbar(cset, ax=ax, shrink=0.5, aspect=5)
        
        # Set labels and title
        ax.set_xlabel(kwargs.get('xlabel', 'X'))
        ax.set_ylabel(kwargs.get('ylabel', 'Y'))
        ax.set_zlabel(kwargs.get('zlabel', 'Z'))
        ax.set_title(title)
        
        return fig
    
    elif library.lower() == 'plotly':
        if not PLOTLY_AVAILABLE:
            raise Visualization3DError("Plotly is not available. Please install it with 'pip install plotly'.")
        
        # Create contour plot
        fig = go.Figure(data=[
            go.Contour(
                z=Z,
                x=x if x.ndim == 1 else X[0],
                y=y if y.ndim == 1 else Y[:, 0],
                colorscale=colormap,
                contours=dict(
                    showlabels=kwargs.get('showlabels', True),
                    labelfont=dict(
                        size=kwargs.get('labelfont_size', 12),
                        color=kwargs.get('labelfont_color', 'white')
                    )
                )
            )
        ])
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title=kwargs.get('xlabel', 'X'),
            yaxis_title=kwargs.get('ylabel', 'Y'),
            margin=dict(l=0, r=0, b=0, t=30)
        )
        
        return fig
    
    else:
        raise ValueError(f"Invalid library: {library}. Expected 'matplotlib' or 'plotly'.")


def wireframe_3d(
    x: Union[np.ndarray, List],
    y: Union[np.ndarray, List],
    z: Union[np.ndarray, List, Callable],
    title: str = '3D Wireframe Plot',
    color: str = 'blue',
    library: str = 'matplotlib',
    **kwargs
) -> Any:
    """
    Create a 3D wireframe plot.
    
    Args:
        x: 1D array of x coordinates or 2D array of x coordinates (meshgrid).
        y: 1D array of y coordinates or 2D array of y coordinates (meshgrid).
        z: 2D array of z coordinates or a function that takes x and y arrays and returns z values.
        title: Title of the plot.
        color: Color of the wireframe.
        library: Visualization library to use ('matplotlib' or 'plotly').
        **kwargs: Additional keyword arguments to pass to the plotting function.
        
    Returns:
        The plot object (matplotlib.figure.Figure or plotly.graph_objects.Figure).
        
    Raises:
        Visualization3DError: If the required dependencies are not available.
    """
    # Convert lists to numpy arrays
    x = np.array(x)
    y = np.array(y)
    
    # Create meshgrid if x and y are 1D
    if x.ndim == 1 and y.ndim == 1:
        X, Y = np.meshgrid(x, y)
    else:
        X, Y = x, y
    
    # Calculate z values if z is a function
    if callable(z):
        Z = z(X, Y)
    else:
        Z = np.array(z)
    
    if library.lower() == 'matplotlib':
        if not MATPLOTLIB_AVAILABLE:
            raise Visualization3DError("Matplotlib is not available. Please install it with 'pip install matplotlib'.")
        
        fig = plt.figure(figsize=kwargs.get('figsize', (10, 8)))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create wireframe plot
        wire = ax.plot_wireframe(
            X, Y, Z,
            color=color,
            alpha=kwargs.get('alpha', 1.0),
            linewidth=kwargs.get('linewidth', 1),
            rstride=kwargs.get('rstride', 1),
            cstride=kwargs.get('cstride', 1)
        )
        
        # Set labels and title
        ax.set_xlabel(kwargs.get('xlabel', 'X'))
        ax.set_ylabel(kwargs.get('ylabel', 'Y'))
        ax.set_zlabel(kwargs.get('zlabel', 'Z'))
        ax.set_title(title)
        
        return fig
    
    elif library.lower() == 'plotly':
        if not PLOTLY_AVAILABLE:
            raise Visualization3DError("Plotly is not available. Please install it with 'pip install plotly'.")
        
        # Create wireframe plot
        fig = go.Figure(data=[
            go.Mesh3d(
                x=X.flatten(),
                y=Y.flatten(),
                z=Z.flatten(),
                color=color,
                opacity=kwargs.get('opacity', 1.0),
                alphahull=0
            )
        ])
        
        # Update layout
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title=kwargs.get('xlabel', 'X'),
                yaxis_title=kwargs.get('ylabel', 'Y'),
                zaxis_title=kwargs.get('zlabel', 'Z')
            ),
            margin=dict(l=0, r=0, b=0, t=30)
        )
        
        return fig
    
    else:
        raise ValueError(f"Invalid library: {library}. Expected 'matplotlib' or 'plotly'.")


def volume_3d(
    x: Union[np.ndarray, List],
    y: Union[np.ndarray, List],
    z: Union[np.ndarray, List],
    values: Union[np.ndarray, List],
    title: str = '3D Volume Rendering',
    colormap: str = 'viridis',
    opacity: float = 0.1,
    **kwargs
) -> Any:
    """
    Create a 3D volume rendering.
    
    Args:
        x: 1D array of x coordinates.
        y: 1D array of y coordinates.
        z: 1D array of z coordinates.
        values: 3D array of values to render.
        title: Title of the plot.
        colormap: Colormap to use for the volume.
        opacity: Opacity of the volume.
        **kwargs: Additional keyword arguments to pass to the plotting function.
        
    Returns:
        The plot object (plotly.graph_objects.Figure).
        
    Raises:
        Visualization3DError: If the required dependencies are not available.
    """
    if not PLOTLY_AVAILABLE:
        raise Visualization3DError("Plotly is not available. Please install it with 'pip install plotly'.")
    
    # Convert lists to numpy arrays
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    values = np.array(values)
    
    # Create volume plot
    fig = go.Figure(data=[
        go.Volume(
            x=x,
            y=y,
            z=z,
            value=values,
            opacity=opacity,
            colorscale=colormap,
            surface_count=kwargs.get('surface_count', 20),
            isomin=kwargs.get('isomin', values.min()),
            isomax=kwargs.get('isomax', values.max()),
            caps=dict(
                x_show=kwargs.get('caps_x_show', False),
                y_show=kwargs.get('caps_y_show', False),
                z_show=kwargs.get('caps_z_show', False)
            )
        )
    ])
    
    # Update layout
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=kwargs.get('xlabel', 'X'),
            yaxis_title=kwargs.get('ylabel', 'Y'),
            zaxis_title=kwargs.get('zlabel', 'Z')
        ),
        margin=dict(l=0, r=0, b=0, t=30)
    )
    
    return fig


def isosurface_3d(
    x: Union[np.ndarray, List],
    y: Union[np.ndarray, List],
    z: Union[np.ndarray, List],
    values: Union[np.ndarray, List],
    isomin: Optional[float] = None,
    isomax: Optional[float] = None,
    title: str = '3D Isosurface Plot',
    colormap: str = 'viridis',
    opacity: float = 0.5,
    **kwargs
) -> Any:
    """
    Create a 3D isosurface plot.
    
    Args:
        x: 1D array of x coordinates.
        y: 1D array of y coordinates.
        z: 1D array of z coordinates.
        values: 3D array of values to render.
        isomin: Minimum value for isosurface.
        isomax: Maximum value for isosurface.
        title: Title of the plot.
        colormap: Colormap to use for the isosurface.
        opacity: Opacity of the isosurface.
        **kwargs: Additional keyword arguments to pass to the plotting function.
        
    Returns:
        The plot object (plotly.graph_objects.Figure).
        
    Raises:
        Visualization3DError: If the required dependencies are not available.
    """
    if not PLOTLY_AVAILABLE:
        raise Visualization3DError("Plotly is not available. Please install it with 'pip install plotly'.")
    
    # Convert lists to numpy arrays
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    values = np.array(values)
    
    # Set default isomin and isomax if not provided
    if isomin is None:
        isomin = values.min()
    if isomax is None:
        isomax = values.max()
    
    # Create isosurface plot
    fig = go.Figure(data=[
        go.Isosurface(
            x=x,
            y=y,
            z=z,
            value=values,
            opacity=opacity,
            colorscale=colormap,
            isomin=isomin,
            isomax=isomax,
            surface_count=kwargs.get('surface_count', 5),
            caps=dict(
                x_show=kwargs.get('caps_x_show', False),
                y_show=kwargs.get('caps_y_show', False),
                z_show=kwargs.get('caps_z_show', False)
            )
        )
    ])
    
    # Update layout
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=kwargs.get('xlabel', 'X'),
            yaxis_title=kwargs.get('ylabel', 'Y'),
            zaxis_title=kwargs.get('zlabel', 'Z')
        ),
        margin=dict(l=0, r=0, b=0, t=30)
    )
    
    return fig


def molecule_3d(
    atoms: List[Dict[str, Any]],
    bonds: Optional[List[Dict[str, Any]]] = None,
    title: str = '3D Molecule Visualization',
    **kwargs
) -> Any:
    """
    Create a 3D visualization of a molecule.
    
    Args:
        atoms: List of dictionaries with atom information (element, x, y, z).
        bonds: List of dictionaries with bond information (source, target, order).
        title: Title of the plot.
        **kwargs: Additional keyword arguments to pass to the plotting function.
        
    Returns:
        The plot object (plotly.graph_objects.Figure).
        
    Raises:
        Visualization3DError: If the required dependencies are not available.
    """
    if not PLOTLY_AVAILABLE:
        raise Visualization3DError("Plotly is not available. Please install it with 'pip install plotly'.")
    
    # Element properties (colors and radii)
    element_colors = {
        'H': '#FFFFFF',  # White
        'C': '#808080',  # Gray
        'N': '#0000FF',  # Blue
        'O': '#FF0000',  # Red
        'F': '#FFFF00',  # Yellow
        'P': '#FFA500',  # Orange
        'S': '#FFC0CB',  # Pink
        'Cl': '#00FF00', # Green
        'Br': '#A52A2A', # Brown
        'I': '#800080',  # Purple
        'default': '#000000'  # Black
    }
    
    element_radii = {
        'H': 0.3,
        'C': 0.7,
        'N': 0.65,
        'O': 0.6,
        'F': 0.5,
        'P': 1.0,
        'S': 1.0,
        'Cl': 1.0,
        'Br': 1.15,
        'I': 1.4,
        'default': 0.8
    }
    
    # Extract atom data
    elements = [atom.get('element', 'default') for atom in atoms]
    x = [atom.get('x', 0) for atom in atoms]
    y = [atom.get('y', 0) for atom in atoms]
    z = [atom.get('z', 0) for atom in atoms]
    
    # Get colors and sizes for atoms
    colors = [element_colors.get(element, element_colors['default']) for element in elements]
    sizes = [element_radii.get(element, element_radii['default']) for element in elements]
    
    # Create figure
    fig = go.Figure()
    
    # Add atoms as spheres
    fig.add_trace(go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=[s * 10 for s in sizes],  # Scale up for visibility
            color=colors,
            opacity=kwargs.get('atom_opacity', 0.9)
        ),
        text=elements,
        hoverinfo='text'
    ))
    
    # Add bonds as cylinders (lines in this simplified version)
    if bonds:
        bond_x = []
        bond_y = []
        bond_z = []
        
        for bond in bonds:
            source_idx = bond.get('source', 0)
            target_idx = bond.get('target', 0)
            
            # Skip invalid indices
            if source_idx >= len(atoms) or target_idx >= len(atoms):
                continue
            
            # Add line segments for the bond
            bond_x.extend([x[source_idx], x[target_idx], None])
            bond_y.extend([y[source_idx], y[target_idx], None])
            bond_z.extend([z[source_idx], z[target_idx], None])
        
        fig.add_trace(go.Scatter3d(
            x=bond_x,
            y=bond_y,
            z=bond_z,
            mode='lines',
            line=dict(
                color=kwargs.get('bond_color', 'gray'),
                width=kwargs.get('bond_width', 5)
            ),
            hoverinfo='none'
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=kwargs.get('xlabel', 'X (Å)'),
            yaxis_title=kwargs.get('ylabel', 'Y (Å)'),
            zaxis_title=kwargs.get('zlabel', 'Z (Å)'),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        showlegend=False
    )
    
    return fig


def example_3d_visualizations():
    """
    Example function demonstrating the 3D visualization capabilities.
    
    Returns:
        A dictionary of example plots.
    """
    examples = {}
    
    # Check if required libraries are available
    if not check_dependencies('all'):
        print("Warning: Some visualization libraries are not available.")
        print(f"Matplotlib available: {MATPLOTLIB_AVAILABLE}")
        print(f"Plotly available: {PLOTLY_AVAILABLE}")
        return examples
    
    # Example 1: 3D Scatter Plot
    np.random.seed(42)
    n_points = 100
    data = pd.DataFrame({
        'x': np.random.normal(0, 1, n_points),
        'y': np.random.normal(0, 1, n_points),
        'z': np.random.normal(0, 1, n_points),
        'color': np.random.rand(n_points),
        'size': np.random.rand(n_points) * 2 + 0.5
    })
    
    examples['scatter_3d_plotly'] = scatter_3d(
        data, 'x', 'y', 'z', 'color', 'size',
        title='3D Scatter Plot (Plotly)',
        library='plotly'
    )
    
    examples['scatter_3d_matplotlib'] = scatter_3d(
        data, 'x', 'y', 'z', 'color', 'size',
        title='3D Scatter Plot (Matplotlib)',
        library='matplotlib'
    )
    
    # Example 2: 3D Surface Plot
    x = np.linspace(-5, 5, 50)
    y = np.linspace(-5, 5, 50)
    
    def z_func(x, y):
        return np.sin(np.sqrt(x**2 + y**2))
    
    examples['surface_3d_plotly'] = surface_3d(
        x, y, z_func,
        title='3D Surface Plot (Plotly)',
        colormap='viridis',
        library='plotly'
    )
    
    examples['surface_3d_matplotlib'] = surface_3d(
        x, y, z_func,
        title='3D Surface Plot (Matplotlib)',
        colormap='viridis',
        library='matplotlib'
    )
    
    # Example 3: 3D Contour Plot
    examples['contour_3d_plotly'] = contour_3d(
        x, y, z_func,
        title='3D Contour Plot (Plotly)',
        colormap='viridis',
        library='plotly'
    )
    
    examples['contour_3d_matplotlib'] = contour_3d(
        x, y, z_func,
        title='3D Contour Plot (Matplotlib)',
        colormap='viridis',
        library='matplotlib'
    )
    
    # Example 4: 3D Wireframe Plot
    examples['wireframe_3d_matplotlib'] = wireframe_3d(
        x, y, z_func,
        title='3D Wireframe Plot (Matplotlib)',
        color='blue',
        library='matplotlib'
    )
    
    # Example 5: 3D Volume Rendering (Plotly only)
    if PLOTLY_AVAILABLE:
        # Create a 3D grid of values
        x = np.linspace(-5, 5, 20)
        y = np.linspace(-5, 5, 20)
        z = np.linspace(-5, 5, 20)
        X, Y, Z = np.meshgrid(x, y, z)
        
        # Create a 3D scalar field
        values = np.sin(np.sqrt(X**2 + Y**2 + Z**2))
        
        examples['volume_3d'] = volume_3d(
            x, y, z, values,
            title='3D Volume Rendering',
            colormap='viridis',
            opacity=0.1
        )
    
    # Example 6: 3D Isosurface Plot (Plotly only)
    if PLOTLY_AVAILABLE:
        examples['isosurface_3d'] = isosurface_3d(
            x, y, z, values,
            title='3D Isosurface Plot',
            colormap='viridis',
            opacity=0.5
        )
    
    # Example 7: 3D Molecule Visualization (Plotly only)
    if PLOTLY_AVAILABLE:
        # Define a simple water molecule
        atoms = [
            {'element': 'O', 'x': 0.0, 'y': 0.0, 'z': 0.0},
            {'element': 'H', 'x': 0.8, 'y': 0.6, 'z': 0.0},
            {'element': 'H', 'x': -0.8, 'y': 0.6, 'z': 0.0}
        ]
        
        bonds = [
            {'source': 0, 'target': 1, 'order': 1},
            {'source': 0, 'target': 2, 'order': 1}
        ]
        
        examples['molecule_3d'] = molecule_3d(
            atoms, bonds,
            title='Water Molecule (H₂O)'
        )
    
    return examples


if __name__ == "__main__":
    # Run examples
    examples = example_3d_visualizations()
    
    # Show Plotly examples in a browser
    if PLOTLY_AVAILABLE and examples:
        for name, fig in examples.items():
            if 'plotly' in name or name in ['volume_3d', 'isosurface_3d', 'molecule_3d']:
                fig.show()
    
    # Show Matplotlib examples
    if MATPLOTLIB_AVAILABLE and examples:
        for name, fig in examples.items():
            if 'matplotlib' in name:
                plt.figure(fig.number)
                plt.show()