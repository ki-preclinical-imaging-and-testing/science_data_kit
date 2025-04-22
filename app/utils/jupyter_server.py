import docker
import socket
import streamlit as st
import os

client = docker.from_env()

def initialize_jupyter_session():
    if "jupyter_container_name" not in st.session_state:
        st.session_state["jupyter_container_name"] = "dsk-jupyter-instance"
    if "jupyter_port" not in st.session_state:
        st.session_state["jupyter_port"] = 8888
    if "jupyter_token" not in st.session_state:
        st.session_state["jupyter_token"] = "letmein"

initialize_jupyter_session()

def find_free_port(start_port):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port
        port += 1

# # # # # def start_jupyter_container():
# # # # #     initialize_jupyter_session()
# # # # #     name = st.session_state["jupyter_container_name"]
# # # # #     st.session_state["jupyter_port"] = find_free_port(st.session_state["jupyter_port"])

# # # # #     existing = client.containers.list(all=True, filters={"name": name})
# # # # #     for container in existing:
# # # # #         st.write(container.name)
# # # # #         if container.name == name:
# # # # #             if container.status != "running":
# # # # #                 container.start()
# # # # #             return

# # # # #     client.containers.run(
# # # # #         "jupyter/base-notebook",
# # # # #         name=name,
# # # # #         ports={"8888/tcp": st.session_state["jupyter_port"]},
# # # # #         environment={"JUPYTER_TOKEN": st.session_state["jupyter_token"]},
# # # # #         # volumes={
# # # # #         #     "/path/to/notebooks": {"bind": "/home/jovyan/work", "mode": "rw"}  # optional
# # # # #         # },
# # # # #         detach=True,
# # # # #         tty=True,
# # # # #     )

# # # # def start_jupyter_container():
# # # #     initialize_jupyter_session()
# # # #     name = st.session_state["jupyter_container_name"]
# # # #     token = st.session_state["jupyter_token"]

# # # #     # Start from preferred port
# # # #     port = st.session_state.get("jupyter_port", 8888)

# # # #     while True:
# # # #         # Check if this port is already in use
# # # #         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
# # # #             in_use = s.connect_ex(("localhost", port)) == 0

# # # #         # Check if there's a container with the desired name
# # # #         matching = client.containers.list(all=True, filters={"name": name})
# # # #         matching = [c for c in matching if c.name == name]

# # # #         if in_use:
# # # #             if matching:
# # # #                 # Container exists with this name
# # # #                 container = matching[0]
# # # #                 try:
# # # #                     # Check which port it's actually bound to
# # # #                     bound_port = int(container.attrs["HostConfig"]["PortBindings"]["8888/tcp"][0]["HostPort"])
# # # #                     if bound_port == port:
# # # #                         # Port matches container → success
# # # #                         if container.status != "running":
# # # #                             container.start()
# # # #                         st.session_state["jupyter_port"] = port
# # # #                         st.success(f"✅ Reconnected to Jupyter container on port {port}")
# # # #                         return
# # # #                     else:
# # # #                         st.warning(f"Port {port} is bound, but not by {name}. Trying next port...")
# # # #                         port += 1
# # # #                 except Exception as e:
# # # #                     st.error(f"Error inspecting existing container: {e}")
# # # #                     return
# # # #             else:
# # # #                 # Port is taken, but not by the expected container → skip to next
# # # #                 port += 1
# # # #         else:
# # # #             # Port is free → start fresh container with our desired name
# # # #             st.session_state["jupyter_port"] = port
# # # #             client.containers.run(
# # # #                 "jupyter/base-notebook",
# # # #                 name=name,
# # # #                 ports={"8888/tcp": port},
# # # #                 environment={"JUPYTER_TOKEN": token},
# # # #                 detach=True,
# # # #                 tty=True,
# # # #             )
# # # #             st.success(f"🚀 Started new Jupyter container on port {port}")
# # # #             return

# # # def start_jupyter_container():
# # #     initialize_jupyter_session()
# # #     name = st.session_state["jupyter_container_name"]
# # #     token = st.session_state["jupyter_token"]

# # #     port = st.session_state.get("jupyter_port", 8888)

# # #     while True:
# # #         # Is this port in use already?
# # #         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
# # #             port_in_use = s.connect_ex(("localhost", port)) == 0

# # #         # Check for container with our expected name
# # #         existing = client.containers.list(all=True, filters={"name": name})
# # #         matching = [c for c in existing if c.name == name]

# # #         if matching:
# # #             container = matching[0]
# # #             try:
# # #                 bindings = container.attrs["HostConfig"]["PortBindings"]
# # #                 bound_port = int(bindings["8888/tcp"][0]["HostPort"])
# # #             except Exception:
# # #                 st.error("⚠️ Could not determine port bindings for existing container.")
# # #                 return

# # #             if bound_port == port:
# # #                 # Our container is bound to this port → perfect
# # #                 if container.status != "running":
# # #                     container.start()
# # #                     st.success(f"✅ Started existing container on port {port}")
# # #                 else:
# # #                     st.success(f"🔁 Reconnected to running container on port {port}")
# # #                 st.session_state["jupyter_port"] = port
# # #                 return
# # #             else:
# # #                 # Name matches, but port doesn't match current check → reconnect on that other port
# # #                 st.success(f"🔁 Reconnected to existing container on port {bound_port}")
# # #                 if container.status != "running":
# # #                     container.start()
# # #                     st.info("Started container that was previously stopped.")
# # #                 st.session_state["jupyter_port"] = bound_port
# # #                 return

# # #         if port_in_use:
# # #             # Port is in use, but not by our named container → skip it
# # #             port += 1
# # #             continue

# # #         # If we reach here, no container by that name exists yet, and this port is free
# # #         st.session_state["jupyter_port"] = port
# # #         client.containers.run(
# # #             "jupyter/base-notebook",
# # #             name=name,
# # #             ports={"8888/tcp": port},
# # #             environment={"JUPYTER_TOKEN": token},
# # #             detach=True,
# # #             tty=True,
# # #         )
# # #         st.success(f"🚀 Started new Jupyter container on port {port}")
# # #         return


# # def start_jupyter_container():
# #     initialize_jupyter_session()
# #     name = st.session_state["jupyter_container_name"]
# #     token = st.session_state["jupyter_token"]
# #     port = st.session_state.get("jupyter_port", 8889)

# #     # Check if port is in use
# #     def is_port_in_use(p):
# #         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
# #             return s.connect_ex(("localhost", p)) == 0

# #     # Find matching container
# #     existing = client.containers.list(all=True, filters={"name": name})
# #     matching = [c for c in existing if c.name == name]

# #     if matching:
# #         container = matching[0]
# #         try:
# #             bindings = container.attrs["HostConfig"]["PortBindings"]
# #             bound_port = int(bindings["8888/tcp"][0]["HostPort"]) if "8888/tcp" in bindings else None

# #             if bound_port and is_port_in_use(bound_port):
# #                 if container.status != "running":
# #                     container.start()
# #                     st.success(f"🔁 Started existing container '{name}' on port {bound_port}")
# #                 else:
# #                     st.info(f"✅ Container '{name}' already running on port {bound_port}")
# #                 st.session_state["jupyter_port"] = bound_port
# #                 return
# #             elif not bound_port:
# #                 st.error(f"⚠️ Container '{name}' exists but has no port binding.")
# #                 return
# #             else:
# #                 st.warning(f"⚠️ Container '{name}' exists, and port {bound_port} is bound")
# #                 return

# #         except Exception as e:
# #             st.error(f"Error inspecting or starting container: {e}")
# #             return

# #     # If no matching container — find a free port and launch
# #     while is_port_in_use(port):
# #         port += 1

# #     st.session_state["jupyter_port"] = port

# #     client.containers.run(
# #         "jupyter/base-notebook",
# #         name=name,
# #         ports={"8888/tcp": port},
# #         environment={"JUPYTER_TOKEN": token},
# #         detach=True,
# #         tty=True,
# #     )
# #     st.success(f"🚀 Started new Jupyter container '{name}' on port {port}")

# import time

# def start_jupyter_container():
#     initialize_jupyter_session()
#     name = st.session_state["jupyter_container_name"]
#     token = st.session_state["jupyter_token"]
#     port = st.session_state.get("jupyter_port", 8888)

#     def is_port_in_use(p):
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             return s.connect_ex(("localhost", p)) == 0

#     def get_container_url(port, token):
#         return f"http://localhost:{port}/?token={token}"

#     # Step 1: Look for container with matching name
#     existing = client.containers.list(all=True, filters={"name": name})
#     matching = [c for c in existing if c.name == name]

#     if matching:
#         container = matching[0]
#         try:
#             bindings = container.attrs["HostConfig"]["PortBindings"]
#             bound_port = int(bindings["8888/tcp"][0]["HostPort"]) if "8888/tcp" in bindings else None

#             if not bound_port:
#                 st.error(f"⚠️ Container '{name}' exists but has no port binding.")
#                 return None

#             if is_port_in_use(bound_port):
#                 if container.status != "running":
#                     container.start()
#                     st.info("🔄 Starting container...")
#                     time.sleep(3)  # give it a sec to be ready
#                 else:
#                     st.info(f"Container '{name}' already running on port {port_binding}")

#                 st.session_state["jupyter_port"] = bound_port
#                 url = get_container_url(bound_port, token)
#                 st.success(f"✅ Reconnected to container '{name}'")
#                 st.markdown(f"🔗 [Open JupyterLab]({url})")
#                 st.code(f"{url}")
#                 return url
#             else:
#                 st.warning(f"⚠️ Port {bound_port} is bound but not connectable. Trying next available port...")
#                 port += 1  # try new port
#         except Exception as e:
#             st.error(f"❌ Error handling existing container: {e}")
#             return None

#     # Step 2: Find a truly free port for new container
#     while is_port_in_use(port):
#         port += 1

#     st.session_state["jupyter_port"] = port

#     try:
#         container = client.containers.run(
#             "jupyter/base-notebook",
#             name=name,
#             ports={"8888/tcp": port},
#             environment={"JUPYTER_TOKEN": token},
#             detach=True,
#             tty=True,
#         )
#         st.info("🚀 Launching new Jupyter container...")
#         time.sleep(2)
#         url = get_container_url(port, token)
#         st.success(f"✅ New container started at port {port}")
#         st.markdown(f"🔗 [Open JupyterLab]({url})")
#         st.code(f"{url}")
#         return url

#     except Exception as e:
#         st.error(f"❌ Failed to start Jupyter container: {e}")
#         return None

import time
import socket
import docker
import streamlit as st
from docker.errors import NotFound

client = docker.from_env()

def is_port_in_use(port, host='localhost'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def is_port_available(port, host="0.0.0.0"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False

def find_free_port(start=8888):
    port = start
    # while is_port_in_use(port):
    while not is_port_available(port):
        port += 1
    return port

def get_container_port_binding(container, internal_port="8888/tcp"):
    try:
        return int(container.attrs["HostConfig"]["PortBindings"][internal_port][0]["HostPort"])
    except (KeyError, IndexError, TypeError):
        return None

def start_jupyter_container():
    """
    Start a Jupyter Lab container or connect to an existing one.

    This function will:
    1. Check if a container with the configured name already exists
    2. If it exists, start it if it's not running and return the URL
    3. If it doesn't exist, create a new container and return the URL

    Returns:
        str: The URL to access Jupyter Lab, or None if there was an error
    """
    initialize_jupyter_session()
    name = st.session_state["jupyter_container_name"]
    token = st.session_state["jupyter_token"]

    def get_container_ip(container):
        """Get the IP address of a container, defaulting to localhost if not available"""
        st.session_state['jupyter_host_ip'] = container.attrs["NetworkSettings"]["IPAddress"] or "localhost"
        return st.session_state['jupyter_host_ip']

    try:
        # Try to get an existing container
        container = client.containers.get(name)
        port = find_free_port(8888)
        jupyter_host_ip = get_container_ip(container)
        bound_port = get_container_port_binding(container)

        if not bound_port:
            st.error(f"⚠️ Container '{name}' exists but has no bound port.")
            return None

        st.session_state["jupyter_port"] = bound_port

        # Start the container if it's not running
        if container.status != "running":
            container.start()
            st.info(f"🔄 Started container '{name}'...")
            time.sleep(2)

        # Generate and display the URL
        url = f"http://{jupyter_host_ip}:{bound_port}/?token={token}"
        st.success(f"✅ Jupyter Lab started!")
        st.markdown(f"🔗 [Open Jupyter Lab]({url})")
        st.code(url)

        return url

    except NotFound:
        # Container does not exist yet — create a new one
        port = find_free_port(8888)
        st.session_state["jupyter_port"] = port
        st.session_state['jupyter_host_mountpoint'] = os.path.abspath('../')

        # Create and start the container
        container = client.containers.run(
            "jupyter/base-notebook",
            name=name,
            ports={"8888/tcp": port},
            environment={"JUPYTER_TOKEN": token},
            volumes={
                st.session_state['jupyter_host_mountpoint']: {
                    "bind": "/home/jovyan/work",
                    "mode": "rw"
                }
            },
            detach=True,
            tty=True,
        )

        jupyter_host_ip = get_container_ip(container)
        st.info(f"🚀 Starting new Jupyter container on port {port}...")
        time.sleep(2)

        # Generate and display the URL
        url = f"http://{jupyter_host_ip}:{port}/?token={token}"
        st.success(f"✅ Jupyter Lab Started")
        st.markdown(f"🔗 [Open Jupyter Lab]({url})")
        st.code(url)

        return url

    except Exception as e:
        st.error(f"❌ Failed to start Jupyter container: {e}")
        return None


def stop_jupyter_container():
    initialize_jupyter_session()
    name = st.session_state["jupyter_container_name"]
    existing = client.containers.list(all=True, filters={"name": name})
    for container in existing:
        if container.name == name and container.status == "running":
            container.stop()
