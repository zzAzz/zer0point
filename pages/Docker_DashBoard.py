import streamlit as st
import json
from streamlit_autorefresh import st_autorefresh
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

def get_container_info():
    try:
        # Get running containers with JSON format
        running_containers_output = subprocess.run(
            ["docker", "ps", "--format", "{{json .}}"],
            capture_output=True,
            text=True
        ).stdout
        
        # Split the output into lines and parse each as JSON
        running_containers = []
        for line in running_containers_output.split('\n'):
            line = line.strip()
            if line:
                try:
                    container = json.loads(line)
                    running_containers.append(container)
                except json.JSONDecodeError:
                    continue
        
        # Get all containers (running and stopped)
        all_containers_output = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{json .}}"],
            capture_output=True,
            text=True
        ).stdout
        
        # Split the output into lines and parse each as JSON
        all_containers = []
        for line in all_containers_output.split('\n'):
            line = line.strip()
            if line:
                try:
                    container = json.loads(line)
                    all_containers.append(container)
                except json.JSONDecodeError:
                    continue
        
        return running_containers, all_containers
    except Exception as e:
        st.error(f"Error getting container information: {e}")
        return None, None

# Function to get container metrics
def get_container_metrics(container_id):
    try:
        # Get detailed metrics using docker stats
        metrics = subprocess.run(
            ["docker", "stats", container_id, "--no-stream"],
            capture_output=True,
            text=True
        ).stdout.split('\n')
        
        if metrics:
            return metrics[1].strip().split()
        return None
    except Exception as e:
        st.error(f"Error getting container metrics: {e}")
        return None

# Function to get container logs
def get_container_logs(container_id, tail_lines=100):
    try:
        logs = subprocess.run(
            ["docker", "logs", container_id, "--tail", str(tail_lines)],
            capture_output=True,
            text=True
        ).stdout
        return logs
    except Exception as e:
        st.error(f"Error getting logs for {container_id}: {e}")
        return None

def get_container_status(container):
    status = container.get('Status', 'Unknown')
    if 'Up' in status:
        return '🟢 Running'
    elif 'Exited' in status:
        return '🔴 Stopped'
    return '🟡 Unknown'

# Function to handle container actions
def handle_container_action(container_name, action):
    try:
        if action == "stop":
            subprocess.run(
                ["docker", "stop", container_name],
                check=True
            )
            st.success(f"Container {container_name} stopped successfully")
        elif action == "start":
            subprocess.run(
                ["docker", "start", container_name],
                check=True
            )
            st.success(f"Container {container_name} started successfully")
        elif action == "restart":
            subprocess.run(
                ["docker", "restart", container_name],
                check=True
            )
            st.success(f"Container {container_name} restarted successfully")
    except Exception as e:
        st.error(f"Error performing action on {container_name}: {e}")

# Function to delete a container
def delete_container(container_name):
    try:
        subprocess.run(
            ["docker", "rm", container_name],
            check=True
        )
        st.success(f"Container {container_name} deleted successfully")
    except Exception as e:
        st.error(f"Error deleting container {container_name}: {e}")

# Main page
def main():
    st.set_page_config(layout="wide")
    st.title("RoboTF AI Suite Status")
    
    try:
        image = Image.open("images/docker-monitor.jpg")
        st.image(image, width=200, caption="RoboTF LLM Tools")
    except FileNotFoundError as e:
        st.error(f"The image file 'docker-monitor.jpg' was not found: {e}")
    except Exception as e:
        st.error(f"Failed to load image: {e}")
        
    st.logo("images/robotf-small.png", size="large", icon_image="images/robotf-small.png")
        
    st.write("This app provides a status dashboard for Docker containers running the RoboTF AI Suite.")

    # Auto-refresh configuration
    with st.sidebar:
        st.header("Settings")
        auto_refresh_enabled = st.slider("Auto-refresh", min_value=0, max_value=1, value=1, 
                                         help="0 = Off, 1 = On")
        refresh_interval = st.select_slider("Refresh Interval (seconds)", 
                                           options=[30, 60, 120, 300], 
                                           value=60)

    # Container status dashboard
    st.header("Container Status Dashboard")
    
    # Get container information
    running_containers, all_containers = get_container_info()
    
    # Create columns for running and stopped containers
    col_running, col_stopped = st.columns(2)
    
    with col_running:
        st.subheader("Running Containers")
        if running_containers:
            container_ids = [container.get('ID') for container in running_containers]
            
            # Use ThreadPoolExecutor to gather metrics in parallel
            with ThreadPoolExecutor() as executor:
                # Submit tasks to gather metrics for all containers
                futures = {executor.submit(get_container_metrics, cid): container 
                        for container, cid in zip(running_containers, container_ids)}
                
                for future in futures:
                    container = futures[future]
                    try:
                        metrics = future.result()
                        status = get_container_status(container)
                        with st.expander(f"[{status}] {container.get('Names', 'Unnamed Container')}", expanded=False):
                            st.write(f"📸 Image: {container.get('Image', 'Unknown')}")
                            st.write(f"🔄 Status: {container.get('Status', 'Unknown')}")
                            st.write(f"📋 Ports: {container.get('Ports', 'None')}")
                            
                            if metrics and len(metrics) >= 8:
                                st.subheader("Metrics")
                                st.write(f"CPU %: {metrics[2]}")
                                st.write(f"Mem Usage: {metrics[3]}")
                                st.write(f"Net I/O: {metrics[5]}")
                                st.write(f"Block I/O: {metrics[7]}")
                            
                            # Action buttons
                            col_btn1, col_btn2, col_btn3 = st.columns(3)
                            with col_btn1:
                                if st.button(f"Stop {container.get('Names', 'Unnamed Container')}", on_click=None):
                                    handle_container_action(container.get('Names'), "stop")
                            with col_btn2:
                                if st.button(f"Restart {container.get('Names', 'Unnamed Container')}", on_click=None):
                                    handle_container_action(container.get('Names'), "restart")
                            with col_btn3:
                                if st.button(f"View Logs {container.get('Names', 'Unnamed Container')}", on_click=None):
                                    logs = get_container_logs(container.get('Names'))
                                    with st.sidebar:
                                        st.subheader("Logs")
                                        st.text_area("Logs", value=logs or "No logs available", height=400)
                    except Exception as e:
                        st.error(f"Error processing container {container.get('Names', 'Unnamed Container')}: {e}")
        else:
            st.write("No running containers found.")
    
    with col_stopped:
        st.subheader("Stopped Containers")
        if all_containers:
            stopped_containers = [container for container in all_containers 
                                if container.get('Status', '').startswith("Exited")]
            
            if stopped_containers:
                container_ids = [container.get('ID') for container in stopped_containers]
                
                # Use ThreadPoolExecutor to gather metrics in parallel
                with ThreadPoolExecutor() as executor:
                    # Submit tasks to gather metrics for all containers
                    futures = {executor.submit(get_container_metrics, cid): container 
                            for container, cid in zip(stopped_containers, container_ids)}
                    
                    for future in futures:
                        container = futures[future]
                        try:
                            metrics = future.result()
                            status = get_container_status(container)
                            with st.expander(f"[{status}] {container.get('Names', 'Unnamed Container')}", expanded=False):
                                st.write(f"📸 Image: {container.get('Image', 'Unknown')}")
                                st.write(f"🔄 Status: {container.get('Status', 'Unknown')}")
                                st.write(f"📋 Ports: {container.get('Ports', 'None')}")
                                
                                # Action buttons
                                col_btn = st.columns(3)
                                with col_btn[0]:
                                    if st.button(f"Start {container.get('Names', 'Unnamed Container')}", on_click=None):
                                        handle_container_action(container.get('Names'), "start")
                                with col_btn[1]:
                                    if st.button(f"View Logs {container.get('Names', 'Unnamed Container')}", on_click=None):
                                        logs = get_container_logs(container.get('Names'))
                                        with st.sidebar:
                                            st.subheader("Logs")
                                            st.text_area("Logs", value=logs or "No logs available", height=400)
                                with col_btn[2]:
                                    if st.button(f"Delete {container.get('Names', 'Unnamed Container')}", on_click=None):
                                        delete_container(container.get('Names'))
                        except Exception as e:
                            st.error(f"Error processing container {container.get('Names', 'Unnamed Container')}: {e}")
            st.write("Note: Containers marked as 'Exited' are stopped.")
        else:
            st.write("No containers found.")

    # Refresh button
    if st.button("Refresh Dashboard"):
        st.rerun()

    # Auto-refresh configuration
    if auto_refresh_enabled > 0:
        st_autorefresh(interval=refresh_interval * 1000)

    st.divider()

    # Social Media Icons and Links
    social_media_links = """
    [![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@RoboTFAI)
    [![Reddit](https://img.shields.io/badge/Reddit-FF4500?style=for-the-badge&logo=reddit&logoColor=white)](https://www.reddit.com/user/RoboTF-AI/)
    [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/kkacsh321)
    [![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/RoboTF)
    [![X](https://img.shields.io/badge/X-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/RoboTF_AI)
    [![Email](https://img.shields.io/badge/Email-008000?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxIDEgMTAwIj48cG9seWdvbiBwb2ludHM9IjUwLDAgMTAwLDUwIDUwLDEwMCAwLDUwIiBmaWxsPSIjMDA4MDBGIi8+PC9zdmc+&logoColor=white)](mailto:robot@robotf.ai)
    [![Website](https://img.shields.io/badge/Website-00B4D8?style=for-the-badge&logo=web&logoColor=white)](https://robotf.ai)
    """
    st.markdown(social_media_links.replace('\n', ' '), unsafe_allow_html=True)
    # Use Local CSS File
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    local_css("custom_configs/style.css")

    # Add footer with copyright information
    st.write("Copyright © 2025 RoboTF.ai. All Rights Reserved.")
    
if __name__ == "__main__":
    main()