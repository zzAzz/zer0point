import streamlit as st
import subprocess

st.title("Docker Command Runner")
st.write("This app runs Docker commands on the host machine via the mounted Docker socket.")

st.warning(
    "Security Warning: Executing Docker commands from a web interface can be risky. "
    "Ensure you understand the implications and restrict access as necessary."
)

# Input for the Docker command. Examples: "ps", "images", "run hello-world"
docker_command = st.text_input(
    "Enter a Docker command (e.g. 'ps', 'images', 'run hello-world')",
    "ps"
)

if st.button("Run Command"):
    try:
        # Split the input into arguments and run the docker command
        result = subprocess.run(
            ["docker"] + docker_command.split(),
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        st.subheader("Standard Output")
        st.text_area("Output", value=result.stdout or "No output", height=200)

        if result.stderr:
            st.subheader("Standard Error")
            st.text_area("Error", value=result.stderr, height=200)
    except Exception as e:
        st.error(f"Error running Docker command: {e}")

# Note: Make sure to mount /var/run/docker.sock into the container so that this app can communicate with the host Docker daemon.
