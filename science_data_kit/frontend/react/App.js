/**
 * Example React App for Science Data Kit
 * 
 * This example demonstrates how to use the keyboard shortcut system in a React application.
 */

import React, { useState } from 'react';
import KeyboardProvider, { useKeyboardShortcut } from './keyboard/KeyboardAdapter';
import FileBrowser from './components/FileBrowser';

/**
 * Example file data
 */
const exampleFiles = [
  { id: 1, name: 'Document.txt', type: 'file' },
  { id: 2, name: 'Spreadsheet.xlsx', type: 'file' },
  { id: 3, name: 'Presentation.pptx', type: 'file' },
  { id: 4, name: 'Images', type: 'folder' },
  { id: 5, name: 'Videos', type: 'folder' },
  { id: 6, name: 'Project Files', type: 'folder' },
];

/**
 * Main App Component
 */
const App = () => {
  const [files, setFiles] = useState(exampleFiles);
  const [selectedFile, setSelectedFile] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  
  // Add a notification
  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 3000);
  };
  
  // Handle file operations
  const handleFileSelect = (file) => {
    setSelectedFile(file);
  };
  
  const handleFileOpen = (file) => {
    addNotification(`Opening ${file.name}`, 'success');
  };
  
  const handleFileDelete = (file) => {
    setFiles(prev => prev.filter(f => f.id !== file.id));
    addNotification(`Deleted ${file.name}`, 'success');
  };
  
  const handleFileRename = (file, newName) => {
    setFiles(prev => prev.map(f => 
      f.id === file.id ? { ...f, name: newName } : f
    ));
    addNotification(`Renamed ${file.name} to ${newName}`, 'success');
  };
  
  const handleFileCreate = (fileName) => {
    const newFile = {
      id: Math.max(...files.map(f => f.id)) + 1,
      name: fileName,
      type: fileName.includes('.') ? 'file' : 'folder'
    };
    setFiles(prev => [...prev, newFile]);
    addNotification(`Created ${fileName}`, 'success');
  };
  
  // Register global keyboard shortcuts
  useKeyboardShortcut('Ctrl+D', 'Toggle dark mode', () => {
    setDarkMode(prev => !prev);
    addNotification(`Dark mode ${darkMode ? 'disabled' : 'enabled'}`, 'info');
  });
  
  useKeyboardShortcut('Ctrl+H', 'Show help', () => {
    addNotification('Help: Press ? to view keyboard shortcuts', 'info');
  });
  
  return (
    <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
      <header className="app-header">
        <h1>Science Data Kit - React Example</h1>
        <div className="app-actions">
          <button onClick={() => setDarkMode(prev => !prev)}>
            {darkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>
      </header>
      
      <main className="app-content">
        <div className="file-browser-container">
          <FileBrowser 
            files={files}
            onFileSelect={handleFileSelect}
            onFileOpen={handleFileOpen}
            onFileDelete={handleFileDelete}
            onFileRename={handleFileRename}
            onFileCreate={handleFileCreate}
          />
        </div>
        
        <div className="file-details">
          <h2>File Details</h2>
          {selectedFile ? (
            <div className="file-info">
              <p><strong>Name:</strong> {selectedFile.name}</p>
              <p><strong>Type:</strong> {selectedFile.type}</p>
              <p><strong>ID:</strong> {selectedFile.id}</p>
            </div>
          ) : (
            <p>No file selected</p>
          )}
        </div>
      </main>
      
      <div className="notifications">
        {notifications.map(notification => (
          <div key={notification.id} className={`notification ${notification.type}`}>
            {notification.message}
          </div>
        ))}
      </div>
      
      <footer className="app-footer">
        <p>Science Data Kit - Framework-Agnostic Architecture Example</p>
        <p>Press <kbd>?</kbd> to view keyboard shortcuts</p>
      </footer>
      
      <style jsx>{`
        .app {
          display: flex;
          flex-direction: column;
          min-height: 100vh;
          background-color: #f9f9f9;
          color: #333;
          transition: background-color 0.3s, color 0.3s;
        }
        
        .app.dark-mode {
          background-color: #222;
          color: #eee;
        }
        
        .app-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background-color: #2196F3;
          color: white;
        }
        
        .app-header h1 {
          margin: 0;
          font-size: 1.5rem;
        }
        
        .app-content {
          display: flex;
          flex: 1;
          padding: 1rem;
          gap: 1rem;
        }
        
        .file-browser-container {
          flex: 1;
          min-width: 300px;
        }
        
        .file-details {
          flex: 1;
          padding: 1rem;
          background-color: white;
          border-radius: 4px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .dark-mode .file-details {
          background-color: #333;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
        }
        
        .notifications {
          position: fixed;
          bottom: 1rem;
          right: 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          max-width: 300px;
        }
        
        .notification {
          padding: 0.75rem 1rem;
          border-radius: 4px;
          background-color: #f8f9fa;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          animation: slideIn 0.3s ease-out;
        }
        
        .notification.info {
          background-color: #e3f2fd;
          border-left: 4px solid #2196F3;
        }
        
        .notification.success {
          background-color: #e8f5e9;
          border-left: 4px solid #4caf50;
        }
        
        .notification.warning {
          background-color: #fff8e1;
          border-left: 4px solid #ff9800;
        }
        
        .notification.error {
          background-color: #ffebee;
          border-left: 4px solid #f44336;
        }
        
        .dark-mode .notification {
          background-color: #333;
          color: #eee;
        }
        
        .dark-mode .notification.info {
          background-color: #0d47a1;
          border-left: 4px solid #2196F3;
        }
        
        .dark-mode .notification.success {
          background-color: #1b5e20;
          border-left: 4px solid #4caf50;
        }
        
        .dark-mode .notification.warning {
          background-color: #e65100;
          border-left: 4px solid #ff9800;
        }
        
        .dark-mode .notification.error {
          background-color: #b71c1c;
          border-left: 4px solid #f44336;
        }
        
        .app-footer {
          padding: 1rem;
          background-color: #f5f5f5;
          text-align: center;
          font-size: 0.875rem;
          color: #666;
        }
        
        .dark-mode .app-footer {
          background-color: #333;
          color: #aaa;
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
        
        .dark-mode kbd {
          background-color: #444;
          border-color: #666;
          color: #eee;
        }
        
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

/**
 * App with KeyboardProvider
 */
const AppWithKeyboard = () => (
  <KeyboardProvider>
    <App />
  </KeyboardProvider>
);

export default AppWithKeyboard;