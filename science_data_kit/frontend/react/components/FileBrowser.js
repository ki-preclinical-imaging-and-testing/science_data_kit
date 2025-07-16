/**
 * File Browser Component for Science Data Kit
 * 
 * This component demonstrates the use of keyboard shortcuts in a React component.
 * It provides a simple file browser interface with keyboard navigation.
 */

import React, { useState, useEffect, useRef } from 'react';
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
  const [searchQuery, setSearchQuery] = useState('');
  const searchInputRef = useRef(null);

  // Filter files based on search query
  const filteredFiles = searchQuery.trim() === '' 
    ? files 
    : files.filter(file => 
        file.name.toLowerCase().includes(searchQuery.toLowerCase())
      );

  // Reset selected index when files or search query changes
  useEffect(() => {
    if (filteredFiles.length > 0 && selectedIndex === -1) {
      setSelectedIndex(0);
      onFileSelect(filteredFiles[0]);
    } else if (selectedIndex >= filteredFiles.length) {
      setSelectedIndex(filteredFiles.length - 1);
      onFileSelect(filteredFiles[filteredFiles.length - 1]);
    } else if (filteredFiles.length === 0) {
      setSelectedIndex(-1);
    }
  }, [filteredFiles, selectedIndex, onFileSelect]);

  // Handle keyboard navigation
  const handleKeyDown = (event) => {
    if (isRenaming || isCreating) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        if (selectedIndex < filteredFiles.length - 1) {
          const newIndex = selectedIndex + 1;
          setSelectedIndex(newIndex);
          onFileSelect(filteredFiles[newIndex]);
        }
        break;
      case 'ArrowUp':
        event.preventDefault();
        if (selectedIndex > 0) {
          const newIndex = selectedIndex - 1;
          setSelectedIndex(newIndex);
          onFileSelect(filteredFiles[newIndex]);
        }
        break;
      case 'Enter':
        event.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < filteredFiles.length) {
          onFileOpen(filteredFiles[selectedIndex]);
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
    if (selectedIndex >= 0 && selectedIndex < filteredFiles.length && !isRenaming && !isCreating) {
      setIsRenaming(true);
      setNewName(filteredFiles[selectedIndex].name);
    }
  });

  useKeyboardShortcut('Delete', 'Delete selected file', () => {
    if (selectedIndex >= 0 && selectedIndex < filteredFiles.length && !isRenaming && !isCreating) {
      if (window.confirm(`Are you sure you want to delete "${filteredFiles[selectedIndex].name}"?`)) {
        onFileDelete(filteredFiles[selectedIndex]);
      }
    }
  });

  useKeyboardShortcut('Ctrl+F', 'Search files', () => {
    if (!isRenaming && !isCreating && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  });

  // Handle file selection
  const handleFileClick = (index) => {
    setSelectedIndex(index);
    onFileSelect(filteredFiles[index]);
  };

  // Handle file double-click
  const handleFileDoubleClick = (index) => {
    onFileOpen(filteredFiles[index]);
  };

  // Handle rename submit
  const handleRenameSubmit = (event) => {
    event.preventDefault();
    if (newName.trim() && selectedIndex >= 0) {
      onFileRename(filteredFiles[selectedIndex], newName.trim());
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

  // Handle search input change
  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
    // Reset selected index when search changes
    if (filteredFiles.length > 0) {
      setSelectedIndex(0);
      onFileSelect(filteredFiles[0]);
    } else {
      setSelectedIndex(-1);
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

      <div className="search-container">
        <input
          type="text"
          ref={searchInputRef}
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder="Search files... (Ctrl+F)"
          className="search-input"
        />
        {searchQuery && (
          <button 
            className="clear-search" 
            onClick={() => setSearchQuery('')}
            title="Clear search"
          >
            ×
          </button>
        )}
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
        {filteredFiles.length === 0 ? (
          <li className="no-results">No files found matching "{searchQuery}"</li>
        ) : filteredFiles.map((file, index) => (
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

        .search-container {
          display: flex;
          padding: 10px;
          background: #f9f9f9;
          border-bottom: 1px solid #ddd;
          position: relative;
        }

        .search-input {
          flex-grow: 1;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .search-input:focus {
          outline: none;
          border-color: #2196F3;
          box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
        }

        .clear-search {
          position: absolute;
          right: 15px;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          color: #666;
          font-size: 18px;
          cursor: pointer;
          padding: 0 5px;
        }

        .clear-search:hover {
          color: #333;
          background: none;
        }

        .no-results {
          padding: 20px;
          text-align: center;
          color: #666;
          font-style: italic;
        }
      `}</style>
    </div>
  );
};

export default FileBrowser;
