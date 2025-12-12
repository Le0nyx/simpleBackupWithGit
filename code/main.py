import os
import shutil
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path to import github_uploader
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from github_uploader import upload_backup_to_github


# Define supported file extensions for backup
SUPPORTED_EXTENSIONS = {
    ".txt", ".docx", ".doc", ".pptx", ".ppt", ".md", 
    ".pdf", ".xlsx", ".xls", ".csv", ".json", ".xml"
}

SIZE_LIMIT = 25 * 1024 * 1024  # 25 MB


def load_exclude_paths(exclude_file: str = "exlude_paths.txt") -> set:
    """
    Load excluded paths from the exclude file.

    :param exclude_file: Path to the exclusion file.
    :return: Set of excluded paths.
    """
    excluded = set()
    try:
        if os.path.exists(exclude_file):
            with open(exclude_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        excluded.add(line.lower())
    except Exception as e:
        print(f"Error reading exclude file: {e}")
    return excluded


def is_path_excluded(file_path: str, excluded_paths: set) -> bool:
    """
    Check if a file path matches any excluded pattern.

    :param file_path: Path to check.
    :param excluded_paths: Set of excluded path patterns.
    :return: True if path should be excluded, False otherwise.
    """
    file_path_lower = file_path.lower()
    for excluded in excluded_paths:
        if excluded in file_path_lower:
            return True
    return False


def get_file_size(file_path: str) -> int:
    """
    Returns the size of the file in bytes.

    :param file_path: The path of the file.
    :return: Size of the file in bytes.
    """
    try:
        size = os.path.getsize(file_path)
        return size
    except Exception as e:
        print(f"An error occurred: {e}")
        return -1


def get_file_extension(file_path: str) -> str:
    """
    Get the file extension in lowercase.

    :param file_path: Path to the file.
    :return: File extension including the dot.
    """
    return os.path.splitext(file_path)[1].lower()


def is_supported_file(file_path: str) -> bool:
    """
    Check if file has a supported extension for backup.

    :param file_path: Path to the file.
    :return: True if supported, False otherwise.
    """
    return get_file_extension(file_path) in SUPPORTED_EXTENSIONS


def find_all_files(directory: str, excluded_paths: set) -> list:
    """
    Recursively find all supported files in directory tree.

    :param directory: Root directory to search.
    :param excluded_paths: Set of paths to exclude.
    :return: List of file paths.
    """
    files = []
    try:
        for root, dirs, filenames in os.walk(directory):
            # Remove excluded directories from dirs in-place to prevent os.walk from traversing them
            dirs[:] = [d for d in dirs if not is_path_excluded(os.path.join(root, d), excluded_paths)]
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if not is_path_excluded(file_path, excluded_paths) and is_supported_file(file_path):
                    files.append(file_path)
    except Exception as e:
        print(f"Error finding files: {e}")
    
    return files


def get_week_number(date: datetime) -> int:
    """
    Get the ISO week number for a given date.

    :param date: Datetime object.
    :return: Week number (1-53).
    """
    return date.isocalendar()[1]


def create_backup_hierarchy(backup_root: str, file_path: str, excluded_size_files: list) -> str:
    """
    Create folder hierarchy: year -> month -> week -> [file type] -> file
    Uses the file's creation date to organize into this structure.

    :param backup_root: Root backup directory.
    :param file_path: Source file path.
    :param excluded_size_files: List to track excluded files.
    :return: Destination path for the file, or None if excluded.
    """
    try:
        file_size = get_file_size(file_path)
        
        if file_size > SIZE_LIMIT:
            excluded_size_files.append({
                "file": file_path,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "destination": "Would be placed in year/month/week hierarchy"
            })
            return None
        
        # Get file's creation date (or modification date on Unix-like systems)
        file_timestamp = os.path.getctime(file_path)
        file_date = datetime.fromtimestamp(file_timestamp)
        
        # Create hierarchy: backups/YYYY/MM/W##/filetype/file
        year_folder = file_date.strftime("%Y")
        month_folder = file_date.strftime("%m")
        week_folder = f"W{get_week_number(file_date):02d}"
        file_extension = get_file_extension(file_path).lstrip(".")
        
        dest_dir = os.path.join(
            backup_root,
            year_folder,
            month_folder,
            week_folder,
            file_extension
        )
        
        os.makedirs(dest_dir, exist_ok=True)
        
        dest_path = os.path.join(dest_dir, os.path.basename(file_path))
        return dest_path
    except Exception as e:
        print(f"Error creating backup hierarchy for {file_path}: {e}")
        return None




def log_excluded_files(excluded_files: list, log_file: str = "backup_excluded.log"):
    """
    Log files that were excluded (too large) during backup.

    :param excluded_files: List of excluded file information.
    :param log_file: Path to the log file.
    """
    try:
        with open(log_file, "w") as f:
            f.write("=" * 80 + "\n")
            f.write(f"BACKUP EXCLUDED FILES LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write("The following files were EXCLUDED from backup due to exceeding 25MB size limit:\n\n")
            
            if not excluded_files:
                f.write("No files were excluded.\n")
            else:
                f.write(f"Total excluded files: {len(excluded_files)}\n\n")
                for idx, file_info in enumerate(excluded_files, 1):
                    f.write(f"{idx}. File: {file_info['file']}\n")
                    f.write(f"   Size: {file_info['size_mb']} MB\n")
                    f.write(f"   Would be located: Backup folder structure would apply\n")
                    f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("To fix this, consider using git-lfs (Large File Storage) or exclude these files in config.\n")
        
        print(f"Exclusion log written to {log_file}")
    except Exception as e:
        print(f"Error writing log file: {e}")


def main():
    source_directory = "C:\\Users\\leonm\\Desktop"  # Change to your source directory
    backup_root = "C:\\Users\\leonm\\Desktop\\github Backupper\\backups"
    log_file = "C:\\Users\\leonm\\Desktop\\github Backupper\\backup_excluded.log"
    config_file = "C:\\Users\\leonm\\Desktop\\github Backupper\\backup_config.txt"
    
    print("=" * 80)
    print("GITHUB BACKUPPER - LOCAL BACKUP")
    print("=" * 80 + "\n")
    print("Starting backup process...")
    print(f"Source directory: {source_directory}")
    print(f"Backup root: {backup_root}\n")
    
    # Load excluded paths
    excluded_paths = load_exclude_paths("exlude_paths.txt")
    print(f"Loaded {len(excluded_paths)} excluded path patterns")
    
    # Find all files to backup
    files_to_backup = find_all_files(source_directory, excluded_paths)
    print(f"Found {len(files_to_backup)} files to backup\n")
    
    # Backup files and track excluded ones
    excluded_size_files = []
    backed_up_count = 0
    
    for file_path in files_to_backup:
        dest_path = create_backup_hierarchy(backup_root, file_path, excluded_size_files)
        
        if dest_path:
            try:
                shutil.copy2(file_path, dest_path)
                backed_up_count += 1
                print(f"Backed up: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error backing up {file_path}: {e}")
    
    # Log excluded files
    log_excluded_files(excluded_size_files, log_file)
    
    print(f"\n" + "=" * 80)
    print(f"LOCAL BACKUP COMPLETE")
    print(f"=" * 80)
    print(f"Files backed up: {backed_up_count}")
    print(f"Files excluded (size): {len(excluded_size_files)}")
    print(f"Backup location: {backup_root}")
    print(f"Exclusion log: {log_file}\n")
    
    # Ask user if they want to upload to GitHub
    user_input = input("Would you like to upload this backup to GitHub? (yes/no): ").strip().lower()
    
    if user_input in ["yes", "y"]:
        print()
        if upload_backup_to_github(backup_root, config_file):
            print("Backup successfully uploaded to GitHub!")
        else:
            print("Failed to upload backup to GitHub. Check your configuration.")
    else:
        print("Skipping GitHub upload.")
    
    









if __name__ == "__main__":
    main()

