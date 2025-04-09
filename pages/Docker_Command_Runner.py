import streamlit as st
import subprocess

def main():
    st.set_page_config(layout="wide")
    st.logo("images/robotf-small.png", size="large", icon_image="images/robotf-small.png")

    st.title("Docker Command Runner")
    st.write("This app runs Docker commands on the host machine via the mounted Docker socket.")

    st.warning(
        "Security Warning: Executing Docker commands from a web interface can be risky. "
        "Ensure you understand the implications and restrict access as necessary."
    )

    docker_command = st.text_input(
        "Enter a Docker command (e.g. 'ps', 'images', 'run hello-world')",
        "ps"
    )

    if st.button("Run Command"):
        try:
            result = subprocess.run(
                ["docker"] + docker_command.split(),
                capture_output=True,
                text=True,
                check=False
            )
            st.subheader("Standard Output")
            st.text_area("Output", value=result.stdout or "No output", height=200)

            if result.stderr:
                st.subheader("Standard Error")
                st.text_area("Error", value=result.stderr, height=200)
        except Exception as e:
            st.error(f"Error running Docker command: {e}")

    if st.button("Restart LocalAI"):
        try:
            docker_command = "restart localai"
            result = subprocess.run(
                ["docker"] + docker_command.split(),
                capture_output=True,
                text=True,
                check=False
            )
            st.subheader("Standard Output")
            st.text_area("Output", value=result.stdout or "No output", height=200)

            if result.stderr:
                st.subheader("Standard Error")
                st.text_area("Error", value=result.stderr, height=200)
        except Exception as e:
            st.error(f"Error running Docker command: {e}")
            
    if st.button("LocalAI Logs"):
        try:
            # Split the input into arguments and run the docker command
            docker_command = "logs localai"
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
            
    if st.button("LocalAI Nvidia-SMI"):
        try:
            # Split the input into arguments and run the docker command
            docker_command = "exec -i localai nvidia-smi"
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