import os
import subprocess
import json
from pathlib import Path
from datetime import datetime


def load_config(config_file: str = "backup_config.txt") -> dict:
    """
    Load configuration from a file.
    
    Expected format (key=value pairs):
    GITHUB_REPO_URL=git@github.com:username/repo.git
    SSH_KEY_PATH=/path/to/ssh/key
    COMMIT_MESSAGE=Auto backup from {date}
    
    :param config_file: Path to the configuration file.
    :return: Dictionary with configuration values.
    """
    config = {
        "GITHUB_REPO_URL": None,
        "SSH_KEY_PATH": None,
        "COMMIT_MESSAGE": "Auto backup - {date}"
    }
    
    try:
        if not os.path.exists(config_file):
            print(f"Config file not found: {config_file}")
            return config
        
        with open(config_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        config[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error reading config file: {e}")
    
    return config


def setup_ssh_environment(ssh_key_path: str) -> bool:
    """
    Set up SSH environment to use the specified key.
    
    :param ssh_key_path: Path to the SSH private key.
    :return: True if successful, False otherwise.
    """
    try:
        # Verify SSH key exists
        if not os.path.exists(ssh_key_path):
            print(f"SSH key not found at: {ssh_key_path}")
            return False
        
        # Set permissions on SSH key (required on Unix-like systems)
        if os.name != "nt":  # Not Windows
            os.chmod(ssh_key_path, 0o600)
        
        # Set environment variable for git to use the specified SSH key
        os.environ["GIT_SSH_COMMAND"] = f'ssh -i "{ssh_key_path}"'
        print(f"SSH environment configured with key: {ssh_key_path}")
        return True
    except Exception as e:
        print(f"Error setting up SSH environment: {e}")
        return False


def initialize_git_repo(repo_path: str, repo_url: str) -> bool:
    """
    Initialize a git repository if not already initialized.
    
    :param repo_path: Path to the backup repository.
    :param repo_url: URL of the remote GitHub repository.
    :return: True if successful, False otherwise.
    """
    try:
        # Check if already a git repo
        git_dir = os.path.join(repo_path, ".git")
        if os.path.exists(git_dir):
            print(f"Repository already initialized at {repo_path}")
            return True
        
        os.makedirs(repo_path, exist_ok=True)
        
        # Initialize repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        print(f"Initialized git repository at {repo_path}")
        
        # Add remote
        subprocess.run(
            ["git", "remote", "add", "origin", repo_url],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        print(f"Added remote origin: {repo_url}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"Error initializing git repo: {e}")
        return False


def commit_and_push(repo_path: str, commit_message: str) -> bool:
    """
    Commit all changes and push to GitHub.
    
    :param repo_path: Path to the git repository.
    :param commit_message: Commit message.
    :return: True if successful, False otherwise.
    """
    try:
        # Configure git user (required for commits)
        subprocess.run(
            ["git", "config", "user.email", "backup@automated.local"],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Backup Bot"],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        
        # Add all files
        subprocess.run(
            ["git", "add", "."],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        print("Staged files for commit")
        
        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print("No changes to commit")
            return True
        
        # Commit
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        print(f"Committed with message: {commit_message}")
        
        # Push to remote
        subprocess.run(
            ["git", "push", "-u", "origin", "main"],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        print("Pushed to GitHub successfully")
        
        return True
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else "Unknown error"
        print(f"Git error during commit/push: {stderr}")
        return False
    except Exception as e:
        print(f"Error committing and pushing: {e}")
        return False


def upload_backup_to_github(
    backup_path: str,
    config_file: str = "backup_config.txt"
) -> bool:
    """
    Main function to upload backup to GitHub.
    
    :param backup_path: Path to the backup folder.
    :param config_file: Path to the configuration file.
    :return: True if successful, False otherwise.
    """
    print("\n" + "=" * 80)
    print("GITHUB UPLOAD PROCESS")
    print("=" * 80 + "\n")
    
    # Load configuration
    config = load_config(config_file)
    
    if not config["GITHUB_REPO_URL"]:
        print("ERROR: GITHUB_REPO_URL not set in config file")
        return False
    
    if not config["SSH_KEY_PATH"]:
        print("ERROR: SSH_KEY_PATH not set in config file")
        return False
    
    # Setup SSH
    if not setup_ssh_environment(config["SSH_KEY_PATH"]):
        return False
    
    # Initialize git repo
    if not initialize_git_repo(backup_path, config["GITHUB_REPO_URL"]):
        return False
    
    # Create commit message
    commit_message = config["COMMIT_MESSAGE"].format(
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # Commit and push
    if commit_and_push(backup_path, commit_message):
        print("\n" + "=" * 80)
        print("UPLOAD SUCCESSFUL")
        print("=" * 80 + "\n")
        return True
    else:
        print("\n" + "=" * 80)
        print("UPLOAD FAILED")
        print("=" * 80 + "\n")
        return False


if __name__ == "__main__":
    # Example usage
    backup_folder = "C:\\Users\\leonm\\Desktop\\github Backupper\\backups"
    upload_backup_to_github(backup_folder)
