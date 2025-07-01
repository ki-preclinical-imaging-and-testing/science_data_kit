Installation
===========

This guide will help you install the Science Data Toolkit and its dependencies.

Prerequisites
------------

Before installing the Science Data Toolkit, ensure you have the following prerequisites:

* Python 3.8 or higher
* pip (Python package installer)
* Docker (for running Neo4j and other services)

Installation Steps
----------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/your-username/science-data-toolkit.git
      cd science-data-toolkit

2. Install the required Python packages:

   .. code-block:: bash

      pip install -r requirements.txt

3. Set up the Neo4j database:

   The Science Data Toolkit uses Neo4j as its graph database. You can either:

   * Use the built-in Neo4j container management in the application
   * Set up your own Neo4j instance and connect to it

Running the Application
---------------------

To start the Science Data Toolkit:

.. code-block:: bash

   cd app
   ./start.sh

This will launch the Streamlit application, which you can access in your web browser at http://localhost:8501.

Troubleshooting
-------------

If you encounter any issues during installation:

* Ensure all prerequisites are installed correctly
* Check that Docker is running if you're using the built-in Neo4j container management
* Verify that the required ports (7474, 7687 for Neo4j, 8501 for Streamlit) are available