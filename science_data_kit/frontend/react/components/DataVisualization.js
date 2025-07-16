/**
 * Data Visualization Component for Science Data Kit
 * 
 * This component demonstrates how to create data visualization components
 * using the React adapter layer.
 */

import React, { useState, useEffect } from 'react';
import { useKeyboardShortcut } from '../keyboard/KeyboardAdapter';
import createReactAdapter from '../adapters/ReactAdapter';

// Create adapter instances
const { dataViz } = createReactAdapter();

/**
 * Data Visualization Component
 * 
 * @param {Object} props - Component props
 * @param {Array} props.data - Data to visualize
 * @param {string} props.type - Visualization type (chart, table)
 * @param {Object} props.options - Visualization options
 */
const DataVisualization = ({ 
  data = [], 
  type = 'chart',
  options = {},
  onViewChange = () => {}
}) => {
  const [visualizationType, setVisualizationType] = useState(type);
  const [chartType, setChartType] = useState(options.chartType || 'bar');
  const [selectedDataPoint, setSelectedDataPoint] = useState(null);
  
  // Register keyboard shortcuts
  useKeyboardShortcut('Ctrl+1', 'Switch to chart view', () => {
    setVisualizationType('chart');
    onViewChange('chart');
  });
  
  useKeyboardShortcut('Ctrl+2', 'Switch to table view', () => {
    setVisualizationType('table');
    onViewChange('table');
  });
  
  useKeyboardShortcut('Ctrl+B', 'Switch to bar chart', () => {
    if (visualizationType === 'chart') {
      setChartType('bar');
      onViewChange('chart', { chartType: 'bar' });
    }
  });
  
  useKeyboardShortcut('Ctrl+L', 'Switch to line chart', () => {
    if (visualizationType === 'chart') {
      setChartType('line');
      onViewChange('chart', { chartType: 'line' });
    }
  });
  
  useKeyboardShortcut('Ctrl+P', 'Switch to pie chart', () => {
    if (visualizationType === 'chart') {
      setChartType('pie');
      onViewChange('chart', { chartType: 'pie' });
    }
  });
  
  // Prepare data for visualization
  const prepareData = () => {
    if (!data || data.length === 0) {
      return {
        chartData: [],
        tableData: [],
        columns: []
      };
    }
    
    // For table view, use data as is
    const tableData = [...data];
    
    // Extract column information from the first data item
    const firstItem = data[0];
    const columns = Object.keys(firstItem).map(key => ({
      key,
      label: key.charAt(0).toUpperCase() + key.slice(1) // Capitalize first letter
    }));
    
    // For chart view, transform data if needed
    // This is a simplified example - in a real app, you'd have more complex transformations
    const chartData = [...data];
    
    return {
      chartData,
      tableData,
      columns
    };
  };
  
  const { chartData, tableData, columns } = prepareData();
  
  // Handle data point selection
  const handleDataPointSelect = (dataPoint) => {
    setSelectedDataPoint(dataPoint);
  };
  
  return (
    <div className="data-visualization">
      <div className="visualization-header">
        <h2>Data Visualization</h2>
        <div className="visualization-controls">
          <button 
            onClick={() => setVisualizationType('chart')}
            className={visualizationType === 'chart' ? 'active' : ''}
          >
            Chart View
          </button>
          <button 
            onClick={() => setVisualizationType('table')}
            className={visualizationType === 'table' ? 'active' : ''}
          >
            Table View
          </button>
          
          {visualizationType === 'chart' && (
            <div className="chart-type-controls">
              <button 
                onClick={() => setChartType('bar')}
                className={chartType === 'bar' ? 'active' : ''}
              >
                Bar
              </button>
              <button 
                onClick={() => setChartType('line')}
                className={chartType === 'line' ? 'active' : ''}
              >
                Line
              </button>
              <button 
                onClick={() => setChartType('pie')}
                className={chartType === 'pie' ? 'active' : ''}
              >
                Pie
              </button>
            </div>
          )}
        </div>
      </div>
      
      <div className="visualization-content">
        {visualizationType === 'chart' ? (
          dataViz.renderChart({
            data: chartData,
            type: chartType,
            options: {
              ...options,
              onDataPointSelect: handleDataPointSelect
            }
          })
        ) : (
          dataViz.renderTable({
            data: tableData,
            columns: columns,
            onRowSelect: handleDataPointSelect
          })
        )}
      </div>
      
      {selectedDataPoint && (
        <div className="data-point-details">
          <h3>Selected Data Point</h3>
          <pre>{JSON.stringify(selectedDataPoint, null, 2)}</pre>
        </div>
      )}
      
      <div className="visualization-footer">
        <div className="keyboard-shortcuts-hint">
          <p>
            Keyboard shortcuts: 
            <kbd>Ctrl+1</kbd> Chart View, 
            <kbd>Ctrl+2</kbd> Table View, 
            <kbd>Ctrl+B</kbd> Bar Chart, 
            <kbd>Ctrl+L</kbd> Line Chart, 
            <kbd>Ctrl+P</kbd> Pie Chart
          </p>
        </div>
      </div>
      
      <style jsx>{`
        .data-visualization {
          border: 1px solid #ddd;
          border-radius: 4px;
          overflow: hidden;
          display: flex;
          flex-direction: column;
          height: 100%;
          min-height: 400px;
        }
        
        .visualization-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px;
          background: #f5f5f5;
          border-bottom: 1px solid #ddd;
        }
        
        .visualization-header h2 {
          margin: 0;
          font-size: 16px;
        }
        
        .visualization-controls {
          display: flex;
          gap: 5px;
        }
        
        .chart-type-controls {
          display: flex;
          gap: 5px;
          margin-left: 10px;
          padding-left: 10px;
          border-left: 1px solid #ddd;
        }
        
        .visualization-content {
          flex-grow: 1;
          padding: 10px;
          overflow: auto;
        }
        
        .data-point-details {
          padding: 10px;
          background: #f9f9f9;
          border-top: 1px solid #ddd;
        }
        
        .data-point-details h3 {
          margin-top: 0;
          font-size: 14px;
        }
        
        .data-point-details pre {
          margin: 0;
          font-size: 12px;
          white-space: pre-wrap;
        }
        
        .visualization-footer {
          padding: 8px 10px;
          background: #f5f5f5;
          border-top: 1px solid #ddd;
          font-size: 12px;
          color: #666;
        }
        
        .keyboard-shortcuts-hint {
          text-align: center;
        }
        
        button {
          padding: 5px 10px;
          background: #f0f0f0;
          color: #333;
          border: 1px solid #ddd;
          border-radius: 3px;
          cursor: pointer;
        }
        
        button:hover {
          background: #e0e0e0;
        }
        
        button.active {
          background: #2196F3;
          color: white;
          border-color: #0b7dda;
        }
        
        kbd {
          background-color: #f7f7f7;
          border: 1px solid #ccc;
          border-radius: 3px;
          box-shadow: 0 1px 0 rgba(0, 0, 0, 0.2);
          color: #333;
          display: inline-block;
          font-size: 0.85em;
          font-weight: bold;
          line-height: 1;
          padding: 2px 4px;
          white-space: nowrap;
          margin: 0 2px;
        }
      `}</style>
    </div>
  );
};

export default DataVisualization;