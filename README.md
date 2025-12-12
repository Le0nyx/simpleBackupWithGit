# GitHub Backupper

An automated backup tool that organizes documents (txt, docx, pptx, md, etc.) into a folder hierarchy and uploads them to GitHub.

## Features

-  **Smart Folder Hierarchy**: Organizes backups by date → year → month → week → file type
-  **Multiple File Types**: Supports `.txt`, `.docx`, `.doc`, `.pptx`, `.ppt`, `.md`, `.pdf`, `.xlsx`, `.xls`, `.csv`, `.json`, `.xml`
-  **GitHub Integration**: Automatic upload to GitHub via SSH
-  **Size Limitation Handling**: Logs files over 25MB with detailed information
-  **Exclusion Support**: Respects path exclusion patterns from `exlude_paths.txt`
-  **Detailed Logging**: Generates exclusion logs for monitoring

## Folder Structure

```
[Backup Root]/
└── [YYYY-MM-DD] (Backup Date)
    └── YYYY (Year)
        └── MM (Month)
            └── W##(Week)
                ├── docx/
                │   └── [files]
                ├── txt/
                │   └── [files]
                ├── md/
                │   └── [files]
                └── [other extensions]/
                    └── [files]
```

## Setup Instructions

### 1. Configure Source Directory

Edit [main.py](code/main.py) and update the `source_directory`:

```python
source_directory = "C:\\Your\\Source\\Path"  # Change this
```

### 2. Configure Exclusions

Edit [exlude_paths.txt](exlude_paths.txt) to specify directories/patterns to exclude:

```
C:\Windows
C:\Program Files
C:\Users\*\node_modules
.git
__pycache__
```

**Note**: Patterns are case-insensitive and matched as substrings.

### 3. Setup GitHub Repository

1. Create a new GitHub repository for backups
2. Copy the SSH URL (e.g., `git@github.com:username/backups.git`)

### 4. Setup SSH Key

**Windows:**
```powershell
# Generate SSH key (if you don't have one)
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa"

# Add public key to GitHub
# 1. Copy contents of C:\Users\YourUsername\.ssh\id_rsa.pub
# 2. Go to GitHub Settings → SSH and GPG keys → New SSH key
# 3. Paste and save
```

**Mac/Linux:**
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
# Then add the public key to GitHub
```

### 5. Configure Backup Settings

Edit [backup_config.txt](backup_config.txt):

```
GITHUB_REPO_URL=git@github.com:your-username/your-backup-repo.git
SSH_KEY_PATH=C:\Users\YourUsername\.ssh\id_rsa
COMMIT_MESSAGE=Auto backup from GitHub Backupper - {date}
```

**Fields:**
- `GITHUB_REPO_URL`: SSH URL of your GitHub repository
- `SSH_KEY_PATH`: Full path to your SSH private key
- `COMMIT_MESSAGE`: Commit message (supports `{date}` placeholder)

## Usage

### Basic Backup (Local Only)

```bash
cd code
python main.py
```

When prompted, enter `no` to skip GitHub upload.

### Full Backup with GitHub Upload

```bash
cd code
python main.py
```

When prompted, enter `yes` to upload to GitHub.

### Direct GitHub Upload (if backups already exist)

```bash
cd code
python -c "from github_uploader import upload_backup_to_github; upload_backup_to_github('path/to/backups')"
```

## Output Files

### backup_excluded.log
Generated after each backup run, lists all files that were excluded due to size:

```
================================================================================
BACKUP EXCLUDED FILES LOG - 2025-04-20 15:30:45
================================================================================

The following files were EXCLUDED from backup due to exceeding 25MB size limit:

Total excluded files: 2

1. File: C:\Users\test1\Desktop\large_video.mp4
   Size: 150.5 MB
   Would be located: Backup folder structure would apply

2. File: C:\Users\test1\Documents\archive.zip
   Size: 35.2 MB
   Would be located: Backup folder structure would apply
```

## Size Limitations

- **Maximum file size for GitHub upload**: 25 MB (GitHub LFS required for larger files)
- Files exceeding this limit are:
  - ✅ Listed in `backup_excluded.log`
  - ✅ Not copied to backup folder
  - ✅ Show exact size in MB

### Handling Large Files

For files over 25MB, you have two options:

1. **Use Git LFS** (Recommended for GitHub):
   ```bash
   git lfs install
   git lfs track "*.mp4"  # or your large file extension
   ```

2. **Add to exclusion list** in `exlude_paths.txt`

## Module Files

### main.py
Main backup orchestrator that:
- Finds all supported files
- Creates folder hierarchy
- Handles exclusions
- Logs oversized files
- Prompts for GitHub upload

### github_uploader.py
Handles GitHub operations:
- SSH key configuration
- Git repository initialization
- Commit and push operations
- Error handling

### backup_config.txt
Configuration file with:
- GitHub repository URL
- SSH key path
- Custom commit messages

### exlude_paths.txt
List of paths/patterns to exclude from backup


## Troubleshooting

### SSH Key Not Found
- Verify the path in `backup_config.txt` is correct
- Windows path should use backslashes or forward slashes: `C:\Users\name\.ssh\id_rsa`

### Git Remote Error
- Ensure SSH key is added to GitHub account
- Test SSH connection: `ssh -i path/to/key git@github.com`

### Files Not Backing Up
- Check `exlude_paths.txt` for matching patterns
- Verify files have supported extensions
- Check permissions on source files

### GitHub Upload Fails
- Verify repository is empty or compatible
- Check network connectivity
- Review Git error messages in console

## File Type Support

| Extension | Supported |
|-----------|-----------|
| .txt      | ✅        |
| .docx     | ✅        |
| .doc      | ✅        |
| .pptx     | ✅        |
| .ppt      | ✅        |
| .md       | ✅        |
| .pdf      | ✅        |
| .xlsx     | ✅        |
| .xls      | ✅        |
| .csv      | ✅        |
| .json     | ✅        |
| .xml      | ✅        |

