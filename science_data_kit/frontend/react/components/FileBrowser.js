/**
 * File Browser Component for Science Data Kit
 * 
 * This component demonstrates the use of keyboard shortcuts in a React component.
 * It provides a simple file browser interface with keyboard navigation, file operations,
 * compression/extraction functionality, and file sharing capabilities.
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
 * @param {function} props.onCompressFiles - Callback when files are compressed
 * @param {function} props.onExtractArchive - Callback when an archive is extracted
 * @param {function} props.onListArchiveContents - Callback to list contents of an archive
 * @param {boolean} props.isArchive - Whether the selected file is an archive
 * @param {function} props.onShareFile - Callback when a file is shared
 * @param {function} props.onUnshareFile - Callback when a file is unshared
 * @param {function} props.onUpdatePermission - Callback when a file's permission is updated
 * @param {Array} props.users - List of users that files can be shared with
 * @param {string} props.currentUserId - ID of the current user
 * @param {Object} props.sharedFiles - Information about files shared with/by the current user
 */
const FileBrowser = ({ 
  files = [], 
  onFileSelect = () => {}, 
  onFileOpen = () => {}, 
  onFileDelete = () => {}, 
  onFileRename = () => {},
  onFileCreate = () => {},
  onCompressFiles = () => {},
  onExtractArchive = () => {},
  onListArchiveContents = () => {},
  isArchive = false,
  onShareFile = () => {},
  onUnshareFile = () => {},
  onUpdatePermission = () => {},
  users = [],
  currentUserId = '',
  sharedFiles = {}
}) => {
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [isRenaming, setIsRenaming] = useState(false);
  const [newName, setNewName] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [newFileName, setNewFileName] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const searchInputRef = useRef(null);

  // Compression/extraction state
  const [isCompressing, setIsCompressing] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [compressionOptions, setCompressionOptions] = useState({
    archiveType: 'zip',
    compressionLevel: 9,
    includeBaseDir: false,
    outputName: ''
  });
  const [extractionOptions, setExtractionOptions] = useState({
    outputDir: '',
    extractAll: true,
    selectedFiles: []
  });
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [multiSelectActive, setMultiSelectActive] = useState(false);

  // File sharing state
  const [isSharing, setIsSharing] = useState(false);
  const [sharingOptions, setSharingOptions] = useState({
    userIds: [],
    permission: 'view',
    userSearchQuery: ''
  });
  const [isViewingSharedUsers, setIsViewingSharedUsers] = useState(false);
  const [sharedUsers, setSharedUsers] = useState([]);

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
    if (isRenaming || isCreating || isCompressing || isExtracting || isSharing || isViewingSharedUsers) return;

    // Handle multi-select with Shift key
    if (event.shiftKey && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
      event.preventDefault();
      setMultiSelectActive(true);

      const currentIndex = selectedIndex;
      let newIndex;

      if (event.key === 'ArrowDown' && selectedIndex < filteredFiles.length - 1) {
        newIndex = selectedIndex + 1;
      } else if (event.key === 'ArrowUp' && selectedIndex > 0) {
        newIndex = selectedIndex - 1;
      } else {
        return;
      }

      setSelectedIndex(newIndex);

      // Update selected files
      const newSelectedFiles = [...selectedFiles];
      const fileToAdd = filteredFiles[newIndex];

      if (!newSelectedFiles.some(f => f.id === fileToAdd.id)) {
        newSelectedFiles.push(fileToAdd);
      }

      setSelectedFiles(newSelectedFiles);
      onFileSelect(fileToAdd);

      return;
    }

    // Handle Ctrl key for individual selection/deselection
    if (event.ctrlKey && event.key === ' ' && selectedIndex >= 0) {
      event.preventDefault();
      setMultiSelectActive(true);

      const fileToToggle = filteredFiles[selectedIndex];
      const fileIndex = selectedFiles.findIndex(f => f.id === fileToToggle.id);

      if (fileIndex === -1) {
        // Add to selection
        setSelectedFiles([...selectedFiles, fileToToggle]);
      } else {
        // Remove from selection
        const newSelectedFiles = [...selectedFiles];
        newSelectedFiles.splice(fileIndex, 1);
        setSelectedFiles(newSelectedFiles);
      }

      return;
    }

    // Regular navigation (no multi-select)
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        if (selectedIndex < filteredFiles.length - 1) {
          const newIndex = selectedIndex + 1;
          setSelectedIndex(newIndex);

          if (!multiSelectActive) {
            setSelectedFiles([filteredFiles[newIndex]]);
          }

          onFileSelect(filteredFiles[newIndex]);
        }
        break;
      case 'ArrowUp':
        event.preventDefault();
        if (selectedIndex > 0) {
          const newIndex = selectedIndex - 1;
          setSelectedIndex(newIndex);

          if (!multiSelectActive) {
            setSelectedFiles([filteredFiles[newIndex]]);
          }

          onFileSelect(filteredFiles[newIndex]);
        }
        break;
      case 'Enter':
        event.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < filteredFiles.length) {
          onFileOpen(filteredFiles[selectedIndex]);
        }
        break;
      case 'Escape':
        event.preventDefault();
        if (multiSelectActive) {
          setMultiSelectActive(false);
          if (selectedIndex >= 0) {
            setSelectedFiles([filteredFiles[selectedIndex]]);
          } else {
            setSelectedFiles([]);
          }
        }
        break;
      default:
        break;
    }
  };

  // Register keyboard shortcuts
  useKeyboardShortcut('Ctrl+N', 'Create new file', () => {
    if (!isRenaming && !isCreating && !isCompressing && !isExtracting) {
      setIsCreating(true);
      setNewFileName('');
    }
  });

  useKeyboardShortcut('F2', 'Rename selected file', () => {
    if (selectedIndex >= 0 && selectedIndex < filteredFiles.length && 
        !isRenaming && !isCreating && !isCompressing && !isExtracting) {
      setIsRenaming(true);
      setNewName(filteredFiles[selectedIndex].name);
    }
  });

  useKeyboardShortcut('Delete', 'Delete selected file', () => {
    if (selectedIndex >= 0 && selectedIndex < filteredFiles.length && 
        !isRenaming && !isCreating && !isCompressing && !isExtracting) {
      if (window.confirm(`Are you sure you want to delete "${filteredFiles[selectedIndex].name}"?`)) {
        onFileDelete(filteredFiles[selectedIndex]);
      }
    }
  });

  useKeyboardShortcut('Ctrl+F', 'Search files', () => {
    if (!isRenaming && !isCreating && !isCompressing && !isExtracting && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  });

  // Compression/extraction shortcuts
  useKeyboardShortcut('Ctrl+C', 'Compress selected files', () => {
    if (!isRenaming && !isCreating && !isCompressing && !isExtracting && !isSharing && 
        !isViewingSharedUsers && selectedFiles.length > 0) {
      setIsCompressing(true);
      setCompressionOptions({
        ...compressionOptions,
        outputName: selectedFiles.length === 1 
          ? `${selectedFiles[0].name}.zip` 
          : 'archive.zip'
      });
    }
  });

  useKeyboardShortcut('Ctrl+E', 'Extract archive', () => {
    if (!isRenaming && !isCreating && !isCompressing && !isExtracting && !isSharing && 
        !isViewingSharedUsers && selectedIndex >= 0 && isArchive) {
      setIsExtracting(true);
      setExtractionOptions({
        ...extractionOptions,
        outputDir: '',
        extractAll: true,
        selectedFiles: []
      });

      // Get archive contents
      onListArchiveContents(filteredFiles[selectedIndex]);
    }
  });

  // File sharing shortcuts
  useKeyboardShortcut('Ctrl+S', 'Share selected file', () => {
    if (!isRenaming && !isCreating && !isCompressing && !isExtracting && !isSharing && 
        !isViewingSharedUsers && selectedIndex >= 0) {
      setIsSharing(true);
      setSharingOptions({
        ...sharingOptions,
        userIds: [],
        permission: 'view',
        userSearchQuery: ''
      });
    }
  });

  // Handle file selection
  const handleFileClick = (index, event) => {
    setSelectedIndex(index);

    // Handle multi-select with Ctrl key
    if (event && event.ctrlKey) {
      setMultiSelectActive(true);

      const fileToToggle = filteredFiles[index];
      const fileIndex = selectedFiles.findIndex(f => f.id === fileToToggle.id);

      if (fileIndex === -1) {
        // Add to selection
        const newSelectedFiles = [...selectedFiles, fileToToggle];
        setSelectedFiles(newSelectedFiles);
      } else {
        // Remove from selection
        const newSelectedFiles = [...selectedFiles];
        newSelectedFiles.splice(fileIndex, 1);
        setSelectedFiles(newSelectedFiles);
      }
    }
    // Handle range select with Shift key
    else if (event && event.shiftKey && selectedIndex >= 0) {
      setMultiSelectActive(true);

      const startIdx = Math.min(selectedIndex, index);
      const endIdx = Math.max(selectedIndex, index);

      const newSelectedFiles = [...selectedFiles];

      for (let i = startIdx; i <= endIdx; i++) {
        const fileToAdd = filteredFiles[i];
        if (!newSelectedFiles.some(f => f.id === fileToAdd.id)) {
          newSelectedFiles.push(fileToAdd);
        }
      }

      setSelectedFiles(newSelectedFiles);
    }
    // Regular single selection
    else {
      if (!multiSelectActive) {
        setSelectedFiles([filteredFiles[index]]);
      }
    }

    onFileSelect(filteredFiles[index]);
  };

  // Handle file double-click
  const handleFileDoubleClick = (index) => {
    onFileOpen(filteredFiles[index]);
  };

  // Handle compression
  const handleCompressFiles = () => {
    if (selectedFiles.length === 0) return;

    onCompressFiles(
      selectedFiles.map(file => file.path), 
      compressionOptions.outputName,
      compressionOptions.archiveType,
      compressionOptions.compressionLevel,
      compressionOptions.includeBaseDir
    );

    setIsCompressing(false);
  };

  // Handle extraction
  const handleExtractArchive = () => {
    if (selectedIndex < 0 || !isArchive) return;

    onExtractArchive(
      filteredFiles[selectedIndex].path,
      extractionOptions.outputDir,
      extractionOptions.extractAll ? null : extractionOptions.selectedFiles
    );

    setIsExtracting(false);
  };

  // Handle file sharing
  const handleShareFile = () => {
    if (selectedIndex < 0) return;

    onShareFile(
      filteredFiles[selectedIndex].path,
      currentUserId,
      sharingOptions.userIds,
      sharingOptions.permission
    );

    setIsSharing(false);
  };

  // Handle viewing shared users
  const handleViewSharedUsers = () => {
    if (selectedIndex < 0) return;

    // Get users who have access to this file
    const fileUsers = sharedFiles && sharedFiles.fileUsers 
      ? sharedFiles.fileUsers[filteredFiles[selectedIndex].path] || []
      : [];

    setSharedUsers(fileUsers);
    setIsViewingSharedUsers(true);
  };

  // Handle unsharing file with a user
  const handleUnshareFile = (userId) => {
    if (selectedIndex < 0) return;

    onUnshareFile(
      filteredFiles[selectedIndex].path,
      currentUserId,
      userId
    );

    // Update the shared users list
    setSharedUsers(sharedUsers.filter(user => user.id !== userId));
  };

  // Handle updating a user's permission
  const handleUpdatePermission = (userId, permission) => {
    if (selectedIndex < 0) return;

    onUpdatePermission(
      filteredFiles[selectedIndex].path,
      currentUserId,
      userId,
      permission
    );

    // Update the shared users list
    setSharedUsers(sharedUsers.map(user => 
      user.id === userId ? { ...user, permission } : user
    ));
  };

  // Filter users based on search query
  const filteredUsers = sharingOptions.userSearchQuery.trim() === ''
    ? users
    : users.filter(user =>
        user.name.toLowerCase().includes(sharingOptions.userSearchQuery.toLowerCase()) ||
        user.id.toLowerCase().includes(sharingOptions.userSearchQuery.toLowerCase())
      );

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
          <button 
            onClick={() => {
              if (selectedFiles.length > 0) {
                setIsCompressing(true);
                setCompressionOptions({
                  ...compressionOptions,
                  outputName: selectedFiles.length === 1 
                    ? `${selectedFiles[0].name}.zip` 
                    : 'archive.zip'
                });
              }
            }} 
            title="Compress selected files (Ctrl+C)"
            disabled={selectedFiles.length === 0}
          >
            Compress
          </button>
          {isArchive && (
            <button 
              onClick={() => {
                if (selectedIndex >= 0) {
                  setIsExtracting(true);
                  setExtractionOptions({
                    ...extractionOptions,
                    outputDir: '',
                    extractAll: true,
                    selectedFiles: []
                  });
                  onListArchiveContents(filteredFiles[selectedIndex]);
                }
              }} 
              title="Extract archive (Ctrl+E)"
              disabled={selectedIndex < 0}
            >
              Extract
            </button>
          )}
          <button 
            onClick={() => {
              if (selectedIndex >= 0) {
                setIsSharing(true);
                setSharingOptions({
                  ...sharingOptions,
                  userIds: [],
                  permission: 'view',
                  userSearchQuery: ''
                });
              }
            }} 
            title="Share selected file (Ctrl+S)"
            disabled={selectedIndex < 0}
          >
            Share
          </button>
          <button 
            onClick={() => {
              if (selectedIndex >= 0) {
                handleViewSharedUsers();
              }
            }} 
            title="View shared users"
            disabled={selectedIndex < 0}
          >
            Shared With
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

      {isCompressing && (
        <div className="dialog-overlay">
          <div className="dialog">
            <h3>Compress Files</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              handleCompressFiles();
            }}>
              <div className="form-group">
                <label>Archive Name:</label>
                <input
                  type="text"
                  value={compressionOptions.outputName}
                  onChange={(e) => setCompressionOptions({
                    ...compressionOptions,
                    outputName: e.target.value
                  })}
                  placeholder="archive.zip"
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>Archive Type:</label>
                <select
                  value={compressionOptions.archiveType}
                  onChange={(e) => setCompressionOptions({
                    ...compressionOptions,
                    archiveType: e.target.value
                  })}
                >
                  <option value="zip">ZIP</option>
                  <option value="tar">TAR</option>
                  <option value="tar_gzip">TAR.GZ</option>
                  <option value="tar_bzip2">TAR.BZ2</option>
                  <option value="tar_xz">TAR.XZ</option>
                </select>
              </div>

              <div className="form-group">
                <label>Compression Level (0-9):</label>
                <input
                  type="number"
                  min="0"
                  max="9"
                  value={compressionOptions.compressionLevel}
                  onChange={(e) => setCompressionOptions({
                    ...compressionOptions,
                    compressionLevel: parseInt(e.target.value, 10)
                  })}
                />
              </div>

              <div className="form-group checkbox">
                <input
                  type="checkbox"
                  id="include-base-dir"
                  checked={compressionOptions.includeBaseDir}
                  onChange={(e) => setCompressionOptions({
                    ...compressionOptions,
                    includeBaseDir: e.target.checked
                  })}
                />
                <label htmlFor="include-base-dir">Include Base Directory</label>
              </div>

              <div className="form-group">
                <p>Selected Files: {selectedFiles.length}</p>
                <ul className="selected-files-list">
                  {selectedFiles.map((file, idx) => (
                    <li key={idx}>{file.name}</li>
                  ))}
                </ul>
              </div>

              <div className="dialog-actions">
                <button type="submit">Compress</button>
                <button type="button" onClick={() => setIsCompressing(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isExtracting && (
        <div className="dialog-overlay">
          <div className="dialog">
            <h3>Extract Archive</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              handleExtractArchive();
            }}>
              <div className="form-group">
                <label>Output Directory:</label>
                <input
                  type="text"
                  value={extractionOptions.outputDir}
                  onChange={(e) => setExtractionOptions({
                    ...extractionOptions,
                    outputDir: e.target.value
                  })}
                  placeholder="Leave empty for current directory"
                  autoFocus
                />
              </div>

              <div className="form-group checkbox">
                <input
                  type="checkbox"
                  id="extract-all"
                  checked={extractionOptions.extractAll}
                  onChange={(e) => setExtractionOptions({
                    ...extractionOptions,
                    extractAll: e.target.checked
                  })}
                />
                <label htmlFor="extract-all">Extract All Files</label>
              </div>

              {!extractionOptions.extractAll && (
                <div className="form-group">
                  <label>Select Files to Extract:</label>
                  <div className="archive-contents-list">
                    {/* This would be populated by onListArchiveContents */}
                    <p>Archive contents would be listed here</p>
                  </div>
                </div>
              )}

              <div className="dialog-actions">
                <button type="submit">Extract</button>
                <button type="button" onClick={() => setIsExtracting(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isSharing && (
        <div className="dialog-overlay">
          <div className="dialog">
            <h3>Share File</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              handleShareFile();
            }}>
              <div className="form-group">
                <label>File to Share:</label>
                <p className="file-to-share">{selectedIndex >= 0 ? filteredFiles[selectedIndex].name : ''}</p>
              </div>

              <div className="form-group">
                <label>Permission:</label>
                <select
                  value={sharingOptions.permission}
                  onChange={(e) => setSharingOptions({
                    ...sharingOptions,
                    permission: e.target.value
                  })}
                >
                  <option value="view">View</option>
                  <option value="edit">Edit</option>
                  <option value="manage">Manage</option>
                </select>
              </div>

              <div className="form-group">
                <label>Search Users:</label>
                <input
                  type="text"
                  value={sharingOptions.userSearchQuery}
                  onChange={(e) => setSharingOptions({
                    ...sharingOptions,
                    userSearchQuery: e.target.value
                  })}
                  placeholder="Search by name or ID"
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>Select Users to Share With:</label>
                <div className="user-list">
                  {filteredUsers.length === 0 ? (
                    <p className="no-results">No users found matching "{sharingOptions.userSearchQuery}"</p>
                  ) : (
                    filteredUsers.map((user) => (
                      <div key={user.id} className="user-item">
                        <input
                          type="checkbox"
                          id={`user-${user.id}`}
                          checked={sharingOptions.userIds.includes(user.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSharingOptions({
                                ...sharingOptions,
                                userIds: [...sharingOptions.userIds, user.id]
                              });
                            } else {
                              setSharingOptions({
                                ...sharingOptions,
                                userIds: sharingOptions.userIds.filter(id => id !== user.id)
                              });
                            }
                          }}
                        />
                        <label htmlFor={`user-${user.id}`}>
                          {user.name} ({user.id})
                        </label>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="form-group">
                <p>Selected Users: {sharingOptions.userIds.length}</p>
                <ul className="selected-users-list">
                  {sharingOptions.userIds.map((userId) => {
                    const user = users.find(u => u.id === userId);
                    return user ? (
                      <li key={userId}>
                        {user.name} ({user.id})
                        <button 
                          type="button" 
                          className="remove-user"
                          onClick={() => {
                            setSharingOptions({
                              ...sharingOptions,
                              userIds: sharingOptions.userIds.filter(id => id !== userId)
                            });
                          }}
                        >
                          ×
                        </button>
                      </li>
                    ) : null;
                  })}
                </ul>
              </div>

              <div className="dialog-actions">
                <button 
                  type="submit"
                  disabled={sharingOptions.userIds.length === 0}
                >
                  Share
                </button>
                <button type="button" onClick={() => setIsSharing(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isViewingSharedUsers && (
        <div className="dialog-overlay">
          <div className="dialog">
            <h3>Shared With</h3>
            <div className="form-group">
              <label>File:</label>
              <p className="file-to-share">{selectedIndex >= 0 ? filteredFiles[selectedIndex].name : ''}</p>
            </div>

            <div className="form-group">
              <label>Users with Access:</label>
              <div className="shared-users-list">
                {sharedUsers.length === 0 ? (
                  <p className="no-results">This file is not shared with anyone</p>
                ) : (
                  sharedUsers.map((user) => (
                    <div key={user.id} className="shared-user-item">
                      <div className="shared-user-info">
                        <span className="shared-user-name">{user.name} ({user.id})</span>
                        <span className="shared-user-permission">{user.permission}</span>
                      </div>
                      <div className="shared-user-actions">
                        <select
                          value={user.permission}
                          onChange={(e) => handleUpdatePermission(user.id, e.target.value)}
                        >
                          <option value="view">View</option>
                          <option value="edit">Edit</option>
                          <option value="manage">Manage</option>
                        </select>
                        <button 
                          type="button" 
                          className="unshare-button"
                          onClick={() => handleUnshareFile(user.id)}
                        >
                          Unshare
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="dialog-actions">
              <button type="button" onClick={() => setIsViewingSharedUsers(false)}>Close</button>
            </div>
          </div>
        </div>
      )}

      <ul className="file-list">
        {filteredFiles.length === 0 ? (
          <li className="no-results">No files found matching "{searchQuery}"</li>
        ) : filteredFiles.map((file, index) => (
          <li 
            key={file.id || index}
            className={`file-item ${selectedIndex === index ? 'selected' : ''} ${selectedFiles.some(f => f.id === file.id) ? 'multi-selected' : ''}`}
            onClick={(e) => handleFileClick(index, e)}
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

        .file-item.multi-selected {
          background: #bbdefb;
        }

        .file-item.selected.multi-selected {
          background: #90caf9;
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

        button:disabled {
          background: #cccccc;
          cursor: not-allowed;
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

        /* Dialog styles */
        .dialog-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }

        .dialog {
          background: white;
          border-radius: 4px;
          padding: 20px;
          width: 500px;
          max-width: 90%;
          max-height: 90vh;
          overflow-y: auto;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .dialog h3 {
          margin-top: 0;
          margin-bottom: 20px;
          font-size: 18px;
          border-bottom: 1px solid #eee;
          padding-bottom: 10px;
        }

        .form-group {
          margin-bottom: 15px;
        }

        .form-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: bold;
        }

        .form-group input[type="text"],
        .form-group input[type="number"],
        .form-group select {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .form-group.checkbox {
          display: flex;
          align-items: center;
        }

        .form-group.checkbox input {
          margin-right: 10px;
        }

        .form-group.checkbox label {
          margin-bottom: 0;
          font-weight: normal;
        }

        .selected-files-list {
          max-height: 150px;
          overflow-y: auto;
          border: 1px solid #eee;
          border-radius: 4px;
          padding: 10px;
          margin-top: 5px;
          font-size: 14px;
        }

        .selected-files-list li {
          margin-bottom: 5px;
        }

        .archive-contents-list {
          max-height: 200px;
          overflow-y: auto;
          border: 1px solid #eee;
          border-radius: 4px;
          padding: 10px;
          margin-top: 5px;
        }

        /* File sharing styles */
        .file-to-share {
          font-weight: bold;
          margin: 5px 0;
          padding: 5px;
          background-color: #f5f5f5;
          border-radius: 4px;
        }

        .user-list {
          max-height: 200px;
          overflow-y: auto;
          border: 1px solid #eee;
          border-radius: 4px;
          padding: 10px;
          margin-top: 5px;
        }

        .user-item {
          display: flex;
          align-items: center;
          margin-bottom: 5px;
          padding: 5px;
          border-radius: 4px;
        }

        .user-item:hover {
          background-color: #f9f9f9;
        }

        .user-item input {
          margin-right: 10px;
        }

        .selected-users-list {
          max-height: 150px;
          overflow-y: auto;
          border: 1px solid #eee;
          border-radius: 4px;
          padding: 10px;
          margin-top: 5px;
          font-size: 14px;
        }

        .selected-users-list li {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 5px;
          padding: 5px;
          background-color: #f5f5f5;
          border-radius: 4px;
        }

        .remove-user {
          background: none;
          border: none;
          color: #666;
          font-size: 18px;
          cursor: pointer;
          padding: 0 5px;
        }

        .remove-user:hover {
          color: #333;
          background: none;
        }

        .shared-users-list {
          max-height: 300px;
          overflow-y: auto;
          border: 1px solid #eee;
          border-radius: 4px;
          padding: 10px;
          margin-top: 5px;
        }

        .shared-user-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
          padding: 10px;
          background-color: #f5f5f5;
          border-radius: 4px;
        }

        .shared-user-info {
          display: flex;
          flex-direction: column;
        }

        .shared-user-name {
          font-weight: bold;
        }

        .shared-user-permission {
          font-size: 12px;
          color: #666;
          margin-top: 3px;
        }

        .shared-user-actions {
          display: flex;
          gap: 10px;
          align-items: center;
        }

        .unshare-button {
          background-color: #f44336;
        }

        .unshare-button:hover {
          background-color: #d32f2f;
        }

        .dialog-actions {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          margin-top: 20px;
        }
      `}</style>
    </div>
  );
};

export default FileBrowser;
