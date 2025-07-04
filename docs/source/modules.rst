Modules Reference
================

This section provides detailed information about the modules in the Science Data Kit.

Core Modules
-----------

The Science Data Kit is organized into several core modules, each responsible for specific functionality.

Database Module
~~~~~~~~~~~~~

The database module provides functionality for connecting to and interacting with databases.

.. automodule:: science_data_kit.core.db
   :members:
   :undoc-members:
   :show-inheritance:

Providers Module
~~~~~~~~~~~~~~

The providers module contains classes for interacting with various data sources.

.. automodule:: science_data_kit.core.providers
   :members:
   :undoc-members:
   :show-inheritance:

Storage Providers
^^^^^^^^^^^^^^^^

.. automodule:: science_data_kit.core.providers.storage
   :members:
   :undoc-members:
   :show-inheritance:

Database Providers
^^^^^^^^^^^^^^^

.. automodule:: science_data_kit.core.providers.database
   :members:
   :undoc-members:
   :show-inheritance:

API Providers
^^^^^^^^^^^

.. automodule:: science_data_kit.core.providers.api
   :members:
   :undoc-members:
   :show-inheritance:

UI Module
~~~~~~~~

The UI module provides the graphical user interface for the Science Data Kit.

.. automodule:: science_data_kit.ui
   :members:
   :undoc-members:
   :show-inheritance:

UI Pages
^^^^^^^

.. automodule:: science_data_kit.ui.pages
   :members:
   :undoc-members:
   :show-inheritance:

UI Components
^^^^^^^^^^^

.. automodule:: science_data_kit.ui.components
   :members:
   :undoc-members:
   :show-inheritance:

UI Adapters
^^^^^^^^^

.. automodule:: science_data_kit.ui.adapters
   :members:
   :undoc-members:
   :show-inheritance:

Utility Modules
--------------

The Science Data Kit includes several utility modules that provide common functionality.

Error Handling
~~~~~~~~~~~~

.. automodule:: science_data_kit.core.error_handling
   :members:
   :undoc-members:
   :show-inheritance:

Background Processing
~~~~~~~~~~~~~~~~~~

.. automodule:: science_data_kit.core.background_processing
   :members:
   :undoc-members:
   :show-inheritance:

Legacy Modules
------------

The following modules are from the legacy app structure and are in the process of being migrated to the new structure.

.. automodule:: app
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: app.utils
   :members:
   :undoc-members:
   :show-inheritance:

Module Dependency Graph
---------------------

The following diagram shows the dependencies between the main modules:

.. code-block:: text

    science_data_kit
    ├── core
    │   ├── db
    │   │   ├── db_manager.py
    │   │   ├── database_connector_base.py
    │   │   └── ...
    │   ├── providers
    │   │   ├── registry.py
    │   │   ├── abstract_providers.py
    │   │   ├── storage
    │   │   ├── database
    │   │   ├── api
    │   │   └── ...
    │   ├── error_handling.py
    │   ├── background_processing.py
    │   └── ...
    ├── ui
    │   ├── app.py
    │   ├── pages
    │   ├── components
    │   ├── adapters
    │   └── ...
    └── ...

For detailed information about specific classes and functions, refer to the API Reference section.