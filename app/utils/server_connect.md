### **Updated README with `tmux` and Setup Script Instructions**

I've updated the README to include **`tmux` usage** and instructions on running an **automated setup script (`engaging_node_setup.sh`)**. The script will handle loading modules, pulling the Singularity image, and setting up directories.

---

# **Running Neo4j with Singularity on the Engaging Cluster (MIT)**

This guide explains how to set up and run **Neo4j** using **Singularity** on the **Engaging Cluster** (or similar MIT clusters that do not support Docker). Since Singularity runs containerized applications differently than Docker, we need to configure writable directories for Neo4j's data, logs, and runtime files.

---

## **Quick Setup Using a Shell Script**
For convenience, you can run an **automated setup script** that performs all required steps.

### **Step 1: Download the Setup Script**
```bash
wget https://your-repo-url/engaging_node_setup.sh
chmod +x engaging_node_setup.sh
```

### **Step 2: Run the Script**
```bash
./engaging_node_setup.sh
```

This script:
- Loads the **Singularity module**  
- Pulls the **Neo4j image**  
- Creates necessary **writable directories**  
- Provides instructions for launching Neo4j  

---

## **Manual Setup (If Not Using the Script)**

### **Step 1: Load the Singularity Module**
Before using Singularity, you need to load the correct module. First, check which versions are available:

```bash
module avail singularity
```

Example output:
```
------------------------------------------------- /home/software/modulefiles --------------------------------------------------
singularity/2.3.1 singularity/2.4.2 singularity/3.0.2 singularity/3.3.0 singularity/3.5.3 singularity/3.7.0
singularity/2.3.2 singularity/2.5.2 singularity/3.2.1 singularity/3.4.2 singularity/3.6.1
```

For best compatibility, use **Singularity 3.7.0**:
```bash
module add singularity/3.7.0
```

Verify the module is loaded:
```bash
module list
```
Expected output:
```
Currently Loaded Modulefiles:
  1) firefox/93          2) singularity/3.7.0
```

---

### **Step 2: Pull the Neo4j Image**
Singularity allows you to pull images directly from **DockerHub**.

```bash
singularity pull docker://neo4j:latest
```

This will create a file called **`neo4j_latest.sif`** in your working directory.

---

### **Step 3: Set Up Writable Directories**
Since Singularity containers are **immutable**, Neo4j needs **writable directories** for storing data, logs, configurations, and runtime files.

Create the necessary directories:
```bash
mkdir -p $HOME/neo4j-data
mkdir -p $HOME/neo4j-logs
mkdir -p $HOME/neo4j-conf
mkdir -p $HOME/neo4j-run
```

---

### **Step 4: Run Neo4j with Singularity**
Now, launch Neo4j with the required **bind mounts**:

```bash
singularity exec \
  --bind $HOME/neo4j-data:/data \
  --bind $HOME/neo4j-logs:/var/lib/neo4j/logs \
  --bind $HOME/neo4j-conf:/var/lib/neo4j/conf \
  --bind $HOME/neo4j-run:/var/lib/neo4j/run \
  -e neo4j_latest.sif \
  neo4j console
```

---

## **Running Neo4j in the Background**
If you need to **keep Neo4j running after logging out**, use one of the following methods:

### **Option 1: `nohup` (Recommended for Cluster Auto-Shutdown)**
This allows the process to persist **even if you log out**:
```bash
nohup singularity exec \
  --bind $HOME/neo4j-data:/data \
  --bind $HOME/neo4j-logs:/var/lib/neo4j/logs \
  --bind $HOME/neo4j-conf:/var/lib/neo4j/conf \
  --bind $HOME/neo4j-run:/var/lib/neo4j/run \
  -e neo4j_latest.sif \
  neo4j console > neo4j.log 2>&1 &
```
Check if it's still running:
```bash
ps aux | grep neo4j
```
To **stop** Neo4j:
```bash
kill <process_id>
```

---

### **Option 2: `tmux` (For Interactive Use)**
If you want to **detach and reattach later**, use `tmux`:

#### **Start a new tmux session:**
```bash
tmux new -s neo4j_session
```

#### **Run Neo4j inside tmux:**
```bash
singularity exec \
  --bind $HOME/neo4j-data:/data \
  --bind $HOME/neo4j-logs:/var/lib/neo4j/logs \
  --bind $HOME/neo4j-conf:/var/lib/neo4j/conf \
  --bind $HOME/neo4j-run:/var/lib/neo4j/run \
  -e neo4j_latest.sif \
  neo4j console
```

#### **Detach from tmux without stopping Neo4j:**
Press **`Ctrl + B`**, then **`D`**.

#### **Reattach to tmux session:**
```bash
tmux attach -t neo4j_session
```

---

## **Troubleshooting**
### **1. Permission Errors?**
If you see errors related to **read-only filesystem access**, ensure the required directories are writable:
```bash
ls -ld $HOME/neo4j-*
```
You can also try running with **temporary write access**:
```bash
singularity exec --writable-tmpfs -e neo4j_latest.sif neo4j console
```
This allows Neo4j to write files but does not persist changes after stopping the container.

### **2. Neo4j Won’t Start?**
Check the logs:
```bash
cat $HOME/neo4j-logs/neo4j.log
```

---

## **Shell Script: `engaging_node_setup.sh`**
Save the following script as **`engaging_node_setup.sh`**:

```bash
#!/bin/bash

# Load the correct Singularity module
echo "Loading Singularity module..."
module add singularity/3.7.0

# Pull the latest Neo4j image
echo "Pulling Neo4j Singularity image..."
singularity pull docker://neo4j:latest

# Create writable directories for Neo4j
echo "Creating writable directories..."
mkdir -p $HOME/neo4j-data
mkdir -p $HOME/neo4j-logs
mkdir -p $HOME/neo4j-conf
mkdir -p $HOME/neo4j-run

echo "Neo4j setup completed. To start Neo4j, run:"
echo
echo "singularity exec \\"
echo "  --bind \$HOME/neo4j-data:/data \\"
echo "  --bind \$HOME/neo4j-logs:/var/lib/neo4j/logs \\"
echo "  --bind \$HOME/neo4j-conf:/var/lib/neo4j/conf \\"
echo "  --bind \$HOME/neo4j-run:/var/lib/neo4j/run \\"
echo "  -e neo4j_latest.sif \\"
echo "  neo4j console"
echo
echo "For persistent execution, use nohup or tmux as described in the README."
```

---

## **Next Steps**
- Modify **Neo4j configuration** inside `$HOME/neo4j-conf/`
- Persist data in `$HOME/neo4j-data/`
- Run **Neo4j in the background** using **nohup** or **tmux**

This setup ensures **Neo4j runs properly on Singularity-based clusters** while keeping data persistent and logs accessible. 🚀

---
