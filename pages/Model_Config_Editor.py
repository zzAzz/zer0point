import json
import streamlit as st
import yaml
import os
import pandas as pd
from dotenv import load_dotenv
from yamllint.config import YamlLintConfig
from yamllint import linter
from code_editor import code_editor
from PIL import Image

# Uncomment to use locally
load_dotenv('.env')

MODELS_PATH = os.getenv('MODELS_PATH', default='models')
TEMPLATE_FILE = 'custom_configs/model_template.yaml'

def main():
    if not os.path.exists(MODELS_PATH):
        st.error(f"The model directory '{MODELS_PATH}' does not exist.")
        st.stop()

    model_configs = sorted([f for f in os.listdir(MODELS_PATH) if f.endswith('.yaml')])

    def load_yaml(path):
        with open(path, 'r') as file:
            return yaml.safe_load(file)

    def lint_yaml(yaml_content):
        config_str = """
        extends: default
        """
        config = YamlLintConfig(config_str)
        problems = list(linter.run(yaml_content, config))
        return problems

    st.set_page_config(layout="wide")
    
    try:
        image = Image.open("images/model-editor.jpg")
        st.image(image, width=400)
    except FileNotFoundError as e:
        st.error(f"The image file 'model-editor.jpg' was not found: {e}")
    except Exception as e:
        st.error(f"Failed to load image: {e}")
        
    st.logo("images/robotf-small.png", size="large", icon_image="images/robotf-small.png")
    
    st.sidebar.title('Model Configurations')

    # Initialize session state for selected model
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = ''

    def handle_model_change():
        st.session_state.selected_model = selected_model
        st.session_state.code_content = ""
        st.rerun()

    selected_model = st.sidebar.selectbox(
        'Select a model configuration:',
        [''] + model_configs,
        key='selected_model'
    )

    new_file_name = st.sidebar.text_input("New File Name (without .yaml)")
    if st.sidebar.button('Create New YAML File'):
        if new_file_name:
            new_file_name += ".yaml"
            new_file_path = os.path.join(MODELS_PATH, new_file_name)
            
            if os.path.exists(new_file_path):
                st.sidebar.error("File already exists. Please choose a different name.")
            else:
                with open(TEMPLATE_FILE, 'r') as template_file:
                    template_content = template_file.read()
                
                with open(new_file_path, 'w') as new_file:
                    new_file.write(template_content)
                
                st.sidebar.success(f"New model configuration '{new_file_name}' created.")
                st.rerun()  # Refresh to include the new file in the list
        else:
            st.sidebar.error("Please enter a name for the new file.")

    if selected_model and st.sidebar.button('Remove Selected YAML File'):
        file_to_remove = os.path.join(MODELS_PATH, selected_model)
        os.remove(file_to_remove)
        st.sidebar.success(f"Model configuration '{selected_model}' has been removed.")
        st.rerun()  # Refresh to update the file list

    if 'code_content' not in st.session_state:
        st.session_state.code_content = ""

    if selected_model:
        if (
            'current_model' not in st.session_state or 
            st.session_state.current_model != selected_model
        ):
            st.session_state.current_model = selected_model
            with open(os.path.join(MODELS_PATH, selected_model), 'r') as file:
                st.session_state.code_content = file.read()

        st.markdown(f"## ✏️ You are currently editing **{selected_model}**")
        st.markdown("### Common Config Changes:")
        
        # Context Size Table
        st.markdown("**Context Sizes:**")
        context_sizes = {
            "8k": 8192,
            "16k": 16384,
            "32k": 32768,
            "40k": 40960,
            "48k": 49152,
            "56k": 57344,
            "64k": 65536,
            "72k": 73728,
            "80k": 81920,
            "88k": 90112,
            "96k": 98304,
            "128k": 131072
        }
        
        df = pd.DataFrame(list(context_sizes.items()), columns=["Context Size", "Value"])
        st.table(df)
        
        # Other parameters in a condensed format
        st.markdown("""
            **Other Parameters:**
            - `gpu_layers`: Number of layers to offload to GPU(s) (e.g., '81')
            - `main_gpu`: Main GPU for tensor splitting (e.g., '0')
            - `tensor_split`: Split Tensor control between GPUs (e.g., '90,10')
            - `no_kv_offloading`: Disable key/value pair offloading (e.g., false)
            - `flash_attention`: Reduce attention matrix memory overhead (e.g., false)
            - `f16`: Use 16-bit floating-point precision (e.g., 'true')
            - `numa`: Non-uniform memory access settings (e.g., true/false)
            - `nmap`: Memory mapping for efficient I/O operations (e.g., true/false)
            - `mmlock`: Memory locking to keep data in RAM (e.g., true/false)
        """)
        
        st.markdown("Please see https://localai.io/advanced/ for more configuration values")
        
        st.markdown(f"Hit the Run button in the editor to save changes to server")

        with open('custom_configs/custom_buttons.json') as json_button_file:  # Updated path
            custom_buttons = json.load(json_button_file)

        with open('custom_configs/info_bar.json') as json_info_file:  # Updated path
            info_bar = json.load(json_info_file)

        with open('custom_configs/code_editor_css.scss') as css_file:  # Updated path
            css_text = css_file.read()

        comp_props = {"css": css_text, "globalCSS": ":root {\n  --streamlit-dark-font-family: monospace;\n}"}

        # Use a dynamic key that includes the selected model
        code_key = f"unique_key_yaml_editor_{selected_model}"
        response_dict = code_editor(
            st.session_state.code_content,
            lang='yaml',
            theme='default',
            height=(40, 32),
            buttons=custom_buttons,
            info=info_bar,
            props=comp_props,
            key=code_key
        )

        # Determine updated code from the editor
        if response_dict.get('type') == 'submit':
            code = response_dict['text']
            try:
                with open(os.path.join(MODELS_PATH, selected_model), 'w') as file:
                    file.write(code)
                st.success(f"The model configuration '{selected_model}' has been saved.")
                st.session_state.code_content = code
                st.rerun()  # Refresh the app to reload the saved content
            except Exception as e:
                st.error(f"Error saving file: {str(e)}")
        else:
            code = st.session_state.code_content

        if st.button('Lint YAML'):
            lint_problems = lint_yaml(code)
            if lint_problems:
                for problem in lint_problems:
                    st.error(f"Line {problem.line}: {problem.message} (rule: {problem.rule})")
            else:
                st.success("No linting errors found!")

    else:
        st.markdown("Please see https://localai.io/advanced/ for more configuration values")
        st.info("Please select a model configuration to edit.")
        

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