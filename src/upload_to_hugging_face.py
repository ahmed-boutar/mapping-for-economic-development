from huggingface_hub import HfApi
import os
from pathlib import Path
import sys

def upload_directory_to_hf(
    local_directory: str,
    repo_name: str,
    token: str,
    repo_type: str = "dataset",
    private: bool = False
):
    """
    Upload a directory and its subdirectories to Hugging Face Hub while preserving structure,
    and resume from where it left off by skipping already uploaded files.
    
    Args:
        local_directory: Path to local directory containing the data
        repo_name: Name for the repository (format: 'username/dataset-name')
        token: Hugging Face API token
        repo_type: Type of repository ('dataset' by default)
        private: Whether to make the repository private
    """
    # Initialize Hugging Face API
    api = HfApi()

    # Retrieve a list of all existing files in the repo
    print("Fetching existing files in the repository...")
    try:
        # The API might return a list of file paths as strings directly
        existing_files = set(api.list_repo_files(repo_id=repo_name, repo_type=repo_type, token=token))
    except Exception as e:
        print(f"Error fetching repo files: {e}")
        return
    
    print(f"Found {len(existing_files)} existing files in the repository.")

    # Function to upload all files in a directory
    def upload_directory_contents(directory_path: Path, repo_path: str = ""):
        # List all files and directories
        for item in directory_path.iterdir():
            # Create relative path for HF repo
            if repo_path:
                hf_path = f"{repo_path}/{item.name}"
            else:
                hf_path = item.name
            
            if item.is_file():
                if hf_path in existing_files:
                    print(f"Skipping already uploaded file: {hf_path}")
                    continue
                print(f"Uploading file: {hf_path}")
                try:
                    api.upload_file(
                        path_or_fileobj=str(item),
                        path_in_repo=hf_path,
                        repo_id=repo_name,
                        repo_type=repo_type,
                        token=token
                    )
                except Exception as e:
                    print(f"Error uploading {hf_path}: {e}")
            
            elif item.is_dir():
                print(f"Processing directory: {hf_path}")
                # Recursively upload contents of subdirectory
                upload_directory_contents(item, hf_path)

    # Start upload process
    print(f"Starting upload of directory: {local_directory}")
    upload_directory_contents(Path(local_directory))
    print("Upload completed!\n")

if __name__ == "__main__":
    token = "hf_xxxxxxxxxxxxxxxxxx"
    repo_name = "ahmedboutar/kenya-mapping-for-economic-development" 
    data_dir = "xxxxx" 
    
    upload_directory_to_hf(
        local_directory=data_dir,
        repo_name=repo_name,
        token=token,
        private=False 
    )
