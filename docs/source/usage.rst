Usage Guide
===========

This section provides a guide on how to use the Science Data Kit.

Installation
-----------

Before using the Science Data Kit, make sure it's properly installed. See the :doc:`installation` page for detailed installation instructions.

Basic Usage
----------

The Science Data Kit provides a command-line interface (CLI) and a graphical user interface (GUI) for interacting with your data.

Command-Line Interface
~~~~~~~~~~~~~~~~~~~~~

To use the CLI, open a terminal and run the following command:

.. code-block:: bash

    sdk --help

This will display the available commands and options.

Graphical User Interface
~~~~~~~~~~~~~~~~~~~~~~~

To launch the GUI, run:

.. code-block:: bash

    sdk ui

This will open the Science Data Kit UI in your default web browser.

Working with Data
----------------

The Science Data Kit provides several ways to work with your data:

1. **Indexing Data**: Index your data to make it searchable and accessible.

   .. code-block:: bash

       sdk index /path/to/your/data

2. **Exploring Data**: Explore your indexed data using the GUI or CLI.

   .. code-block:: bash

       sdk explore

3. **Analyzing Data**: Perform analysis on your data using the built-in tools.

   .. code-block:: bash

       sdk analyze --data-source=your_data_source

4. **Visualizing Data**: Create visualizations of your data.

   .. code-block:: bash

       sdk visualize --data-source=your_data_source --type=graph

Advanced Usage
-------------

For advanced usage scenarios, refer to the specific documentation sections:

- :doc:`api` - For programmatic access to the Science Data Kit
- :doc:`modules` - For information on specific modules and their functionality

Examples
--------

Here are some examples of common tasks:

Example 1: Indexing a Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    sdk index /path/to/your/data --recursive --include-metadata

Example 2: Exploring Data with Filters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    sdk explore --filter="type:csv" --sort-by="date"

Example 3: Creating a Visualization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    sdk visualize --data-source=your_data_source --type=network --output=visualization.html

Troubleshooting
--------------

If you encounter issues while using the Science Data Kit, try the following:

1. Check the logs:

   .. code-block:: bash

       sdk logs

2. Verify your configuration:

   .. code-block:: bash

       sdk config --show

3. Update to the latest version:

   .. code-block:: bash

       pip install --upgrade science-data-kit

If you continue to experience issues, please report them on our GitHub repository.