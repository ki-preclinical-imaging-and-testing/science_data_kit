/**
 * File Browser Component for Science Data Kit
 * 
 * This component demonstrates the use of keyboard shortcuts in a React component.
 * It provides a simple file browser interface with keyboard navigation.
 */

import React, { useState, useEffect } from 'react';
import { useKeyboardShortcut } from '../keyboard/KeyboardAdapter';

/**
 * File Browser Component
 * 
 * @param {Object} props - Component props
 * @param {Array} props.files - List of files to display
 * @param {function} props.onFileSelect - Callback when a file is selected
 * @param {function} props.onFileOpen - Callback when a file is opened
 * @param {function} props.onFileDelete - Callback when a file is deleted
 * @param {function} props.onFileRename - Callback when a file is renamed
 * @param {function} props.onFileCreate - Callback when a file is created
 */
const FileBrowser = ({ 
  files = [], 
  onFileSelect = () => {}, 
  onFileOpen = () => {}, 
  onFileDelete = () => {}, 
  onFileRename = () => {},
  onFileCreate = () => {} 
}) => {
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [isRenaming, setIsRenaming] = useState(false);
  const [newName, setNewName] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [newFileName, setNewFileName] = useState('');
  
  // Reset selected index when files change
  useEffect(() => {
    if (files.length > 0 && selectedIndex === -1) {
      setSelectedIndex(0);
      onFileSelect(files[0]);
    } else if (selectedIndex >= files.length) {
      setSelectedIndex(files.length - 1);
      onFileSelect(files[files.length - 1]);
    }
  }, [files, selectedIndex, onFileSelect]);
  
  // Handle keyboard navigation
  const handleKeyDown = (event) => {
    if (isRenaming || isCreating) return;
    
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        if (selectedIndex < files.length - 1) {
          const newIndex = selectedIndex + 1;
          setSelectedIndex(newIndex);
          onFileSelect(files[newIndex]);
        }
        break;
      case 'ArrowUp':
        event.preventDefault();
        if (selectedIndex > 0) {
          const newIndex = selectedIndex - 1;
          setSelectedIndex(newIndex);
          onFileSelect(files[newIndex]);
        }
        break;
      case 'Enter':
        event.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < files.length) {
          onFileOpen(files[selectedIndex]);
        }
        break;
      default:
        break;
    }
  };
  
  // Register keyboard shortcuts
  useKeyboardShortcut('Ctrl+N', 'Create new file', () => {
    if (!isRenaming && !isCreating) {
      setIsCreating(true);
      setNewFileName('');
    }
  });
  
  useKeyboardShortcut('F2', 'Rename selected file', () => {
    if (selectedIndex >= 0 && selectedIndex < files.length && !isRenaming && !isCreating) {
      setIsRenaming(true);
      setNewName(files[selectedIndex].name);
    }
  });
  
  useKeyboardShortcut('Delete', 'Delete selected file', () => {
    if (selectedIndex >= 0 && selectedIndex < files.length && !isRenaming && !isCreating) {
      if (window.confirm(`Are you sure you want to delete "${files[selectedIndex].name}"?`)) {
        onFileDelete(files[selectedIndex]);
      }
    }
  });
  
  // Handle file selection
  const handleFileClick = (index) => {
    setSelectedIndex(index);
    onFileSelect(files[index]);
  };
  
  // Handle file double-click
  const handleFileDoubleClick = (index) => {
    onFileOpen(files[index]);
  };
  
  // Handle rename submit
  const handleRenameSubmit = (event) => {
    event.preventDefault();
    if (newName.trim() && selectedIndex >= 0) {
      onFileRename(files[selectedIndex], newName.trim());
      setIsRenaming(false);
    }
  };
  
  // Handle create submit
  const handleCreateSubmit = (event) => {
    event.preventDefault();
    if (newFileName.trim()) {
      onFileCreate(newFileName.trim());
      setIsCreating(false);
    }
  };
  
  return (
    <div className="file-browser" onKeyDown={handleKeyDown} tabIndex="0">
      <div className="file-browser-header">
        <h2>Files</h2>
        <div className="file-browser-actions">
          <button onClick={() => setIsCreating(true)} title="Create new file (Ctrl+N)">
            New File
          </button>
        </div>
      </div>
      
      {isCreating && (
        <form onSubmit={handleCreateSubmit} className="file-form">
          <input
            type="text"
            value={newFileName}
            onChange={(e) => setNewFileName(e.target.value)}
            placeholder="Enter file name"
            autoFocus
          />
          <div className="file-form-actions">
            <button type="submit">Create</button>
            <button type="button" onClick={() => setIsCreating(false)}>Cancel</button>
          </div>
        </form>
      )}
      
      <ul className="file-list">
        {files.map((file, index) => (
          <li 
            key={file.id || index}
            className={`file-item ${selectedIndex === index ? 'selected' : ''}`}
            onClick={() => handleFileClick(index)}
            onDoubleClick={() => handleFileDoubleClick(index)}
          >
            {isRenaming && selectedIndex === index ? (
              <form onSubmit={handleRenameSubmit} className="file-form">
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  autoFocus
                />
                <div className="file-form-actions">
                  <button type="submit">Save</button>
                  <button type="button" onClick={() => setIsRenaming(false)}>Cancel</button>
                </div>
              </form>
            ) : (
              <>
                <span className="file-icon">
                  {file.type === 'folder' ? '📁' : '📄'}
                </span>
                <span className="file-name">{file.name}</span>
              </>
            )}
          </li>
        ))}
      </ul>
      
      <div className="file-browser-footer">
        <div className="keyboard-shortcuts-hint">
          <p>Press <kbd>?</kbd> to view keyboard shortcuts</p>
        </div>
      </div>
      
      <style jsx>{`
        .file-browser {
          border: 1px solid #ddd;
          border-radius: 4px;
          overflow: hidden;
          display: flex;
          flex-direction: column;
          height: 100%;
          min-height: 300px;
          outline: none;
        }
        
        .file-browser-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px;
          background: #f5f5f5;
          border-bottom: 1px solid #ddd;
        }
        
        .file-browser-header h2 {
          margin: 0;
          font-size: 16px;
        }
        
        .file-browser-actions {
          display: flex;
          gap: 5px;
        }
        
        .file-list {
          list-style: none;
          padding: 0;
          margin: 0;
          overflow-y: auto;
          flex-grow: 1;
        }
        
        .file-item {
          padding: 8px 10px;
          cursor: pointer;
          display: flex;
          align-items: center;
          border-bottom: 1px solid #eee;
        }
        
        .file-item:hover {
          background: #f9f9f9;
        }
        
        .file-item.selected {
          background: #e3f2fd;
        }
        
        .file-icon {
          margin-right: 8px;
        }
        
        .file-form {
          display: flex;
          flex-direction: column;
          width: 100%;
        }
        
        .file-form input {
          padding: 4px;
          margin-bottom: 5px;
        }
        
        .file-form-actions {
          display: flex;
          gap: 5px;
        }
        
        .file-browser-footer {
          padding: 8px 10px;
          background: #f5f5f5;
          border-top: 1px solid #ddd;
          font-size: 12px;
          color: #666;
        }
        
        .keyboard-shortcuts-hint {
          text-align: center;
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
        }
        
        button {
          padding: 5px 10px;
          background: #2196F3;
          color: white;
          border: none;
          border-radius: 3px;
          cursor: pointer;
        }
        
        button:hover {
          background: #0b7dda;
        }
      `}</style>
    </div>
  );
};

export default FileBrowser;