import streamlit as st
import os
from huggingface_hub import HfApi, hf_hub_download, snapshot_download

def get_default_output_dir():
    """Get default output directory from MODELS_PATH environment variable"""
    models_path = os.getenv("MODELS_PATH")
    if models_path:
        return models_path
    return "./models"

def search_repositories(repo_type, **kwargs):
    """Search repositories of a given type with filters"""
    api = HfApi()
    if repo_type == "model":
        return list(api.list_models(**kwargs))  # Convert generator to list
    elif repo_type == "dataset":
        return list(api.list_datasets(**kwargs))  # Convert generator to list
    elif repo_type == "space":
        return list(api.list_spaces(**kwargs))  # Convert generator to list
    else:
        raise ValueError("Invalid repository type. Must be 'model', 'dataset', or 'space'.")

def list_repository_files(repo_id):
    """List all files and directories in a given repository"""
    try:
        api = HfApi()
        files = api.list_repo_files(repo_id)
        # Convert file objects to their filenames
        file_paths = [file.filename if isinstance(file, dict) else file for file in files]
        return file_paths
    except Exception as e:
        st.error(f"Error listing files: {str(e)}")
        return []

def download_repository(repo_id, output_dir):
    """Download entire repository"""
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            st.warning(f"Output directory {output_dir} created.")
            
        repo_dir = snapshot_download(repo_id, cache_dir=output_dir, progress_bar=True)
        st.success(f"Repository downloaded to: {repo_dir}")
        return repo_dir
    except Exception as e:
        st.error(f"Error downloading repository: {str(e)}")
        return None

def download_file(repo_id, filename, output_dir):
    """Download a single file from repository"""
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            st.warning(f"Output directory {output_dir} created.")
            
        file_path = hf_hub_download(repo_id, filename, cache_dir=output_dir)
        st.success(f"File downloaded to: {file_path}")
        return file_path
    except Exception as e:
        st.error(f"Error downloading file: {str(e)}")
        return None

def get_repository_description(repo, repo_type):
    """Get the description of a repository based on its type"""
    if repo_type == "model":
        # For models, description is in modelInfo
        if hasattr(repo, 'modelInfo') and repo.modelInfo is not None:
            return repo.modelInfo.description
        return "No description available"
    else:
        # For datasets and spaces, description is directly available
        if hasattr(repo, 'description'):
            return repo.description
        return "No description available"

def display_repository_info(repo, repo_type):
    """Display repository information"""
    st.subheader(repo.modelId if repo_type == "model" else repo.id)
    if hasattr(repo, 'author'):
        st.write(f"👤 Author: {repo.author}")
    description = get_repository_description(repo, repo_type)
    st.write(f"📝 Description: {description or 'No description provided'}")
    if hasattr(repo, 'downloads'):
        st.write(f"📊 Downloads: {repo.downloads}")
    st.markdown("---")

def display_paginated_results(results, page, page_size, repo_type):
    """Display paginated search results"""
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    displayed_results = results[start_idx:end_idx]
    
    for repo in displayed_results:
        display_repository_info(repo, repo_type)

def main():
    st.title("Hugging Face Hub Search & Download")
    
    # Search filters
    st.header("Search Filters")
    repo_type = st.selectbox("Repository Type", ["model", "dataset", "space"])
    
    # Search query
    search_query = st.text_input("Search query (optional)")
    
    # Author/organization filter
    author = st.text_input("Author/Organization (optional)")
    
    # Additional filters
    st.subheader("Additional Filters")
    task = st.text_input("Task (e.g., 'image-classification')")
    library = st.text_input("Library (e.g., 'pytorch')")
    dataset = st.text_input("Trained dataset (e.g., 'imagenet')")
    
    # Search button
    if st.button("Search"):
        # Build filters
        filters = {}
        if search_query:
            filters["search"] = search_query
        if author:
            filters["author"] = author
        if task:
            filters["task"] = task
        if library:
            filters["library"] = library
        if dataset:
            filters["trained_dataset"] = dataset
        
        # Perform search
        st.header("Search Results")
        results = search_repositories(repo_type, **filters)
        
        # Pagination controls
        page_size = 20
        total_results = len(results)
        total_pages = (total_results + page_size - 1) // page_size
        page = st.number_input("Page", min_value=1, max_value=max(1, total_pages), value=1)
        
        display_paginated_results(results, page, page_size, repo_type)
    
    # Repository selection and file download
    st.header("Repository Selection & Download")
    repo_id = st.text_input("Enter repository ID (e.g., 'bert-base-uncased')")
    
    if repo_id:
        # List files in repository
        if st.button("List Files in Repository"):
            files = list_repository_files(repo_id)
            if files:
                st.subheader("Files and Directories in Repository:")
                for file in files:
                    st.write(f"📄 {file}")
            else:
                st.warning("No files found in repository.")
        
        # Download options
        st.subheader("Download Options")
        download_type = st.selectbox("Download Type", ["Entire Repository", "Specific File"])
        
        output_dir = st.text_input(
            "Output directory",
            value=get_default_output_dir()
        )
        
        if download_type == "Entire Repository":
            if st.button("Download Entire Repository"):
                download_repository(repo_id, output_dir)
        else:
            files = list_repository_files(repo_id)
            if files:
                st.subheader("Select File to Download:")
                filename = st.selectbox("Files", files)
                if st.button("Download Selected File"):
                    download_file(repo_id, filename, output_dir)
            else:
                st.warning("No files found in repository.")

if __name__ == "__main__":
    main()