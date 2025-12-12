#!/usr/bin/env python3
"""
GitHub Backupper - Control Center UI
Simplified, robust interface for all backup operations
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime


class BackupControlCenter:
    """Simple and effective backup control center"""
    
    def __init__(self):
        # Setup paths
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.code_dir = os.path.join(self.base_dir, "code")
        self.backup_root = os.path.join(self.base_dir, "backups")
        self.config_file = os.path.join(self.base_dir, "backup_config.txt")
        self.exclude_file = os.path.join(self.base_dir, "exlude_paths.txt")
        self.log_file = os.path.join(self.base_dir, "backup_excluded.log")
        self.main_script = os.path.join(self.code_dir, "main.py")
        self.validator_script = os.path.join(self.base_dir, "validate_setup.py")
    
    def clear(self):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def header(self, title):
        """Print styled header"""
        print("\n" + "=" * 80)
        print(f"  {title.center(76)}")
        print("=" * 80 + "\n")
    
    def separator(self):
        """Print separator line"""
        print("-" * 80)
    
    def prompt(self, text):
        """Get user input"""
        try:
            return input(f"\n→ {text}: ").strip()
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return None
    
    def confirm(self, text="Continue?"):
        """Get yes/no confirmation"""
        response = self.prompt(f"{text} (yes/no)").lower()
        return response in ["y", "yes"]
    
    def main_menu(self):
        """Main menu"""
        while True:
            self.clear()
            self.header("GITHUB BACKUPPER - CONTROL CENTER")
            
            print("  What would you like to do?\n")
            print("  1. Run Backup")
            print("  2. View Backup Status")
            print("  3. View Excluded Files")
            print("  4. Upload to GitHub")
            print("  5. Settings & Configuration")
            print("  6. Validate Setup")
            print("  7. Exit\n")
            
            choice = self.prompt("Choose (1-7)")
            
            if choice == "1":
                self.run_backup()
            elif choice == "2":
                self.view_status()
            elif choice == "3":
                self.view_excluded()
            elif choice == "4":
                self.upload_github()
            elif choice == "5":
                self.settings_menu()
            elif choice == "6":
                self.validate()
            elif choice == "7":
                self.clear()
                print("Goodbye!\n")
                break
            else:
                print("\n✗ Invalid choice")
                input("Press Enter...")
    
    def run_backup(self):
        """Run backup process"""
        self.clear()
        self.header("RUN BACKUP")
        
        # Check config
        if not self.check_config():
            input("Press Enter...")
            return
        
        # Get source directory from main.py
        source_dir = self.get_source_dir()
        if not source_dir:
            print("✗ Could not find source_directory in code/main.py")
            print("  Edit code/main.py and set: source_directory = 'C:\\\\Your\\\\Path'")
            input("Press Enter...")
            return
        
        if not os.path.exists(source_dir):
            print(f"✗ Source directory not found: {source_dir}")
            input("Press Enter...")
            return
        
        print(f"Source:  {source_dir}")
        print(f"Backups: {self.backup_root}\n")
        
        if not self.confirm("Start backup"):
            print("Cancelled.")
            input("Press Enter...")
            return
        
        print("\n" + "-" * 80)
        print("Running backup...\n")
        
        try:
            # Run main.py from code directory
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd=self.code_dir,
                capture_output=False
            )
            
            if result.returncode == 0:
                print("\n" + "-" * 80)
                print("✓ Backup completed successfully!")
            else:
                print("\n✗ Backup failed. Check messages above.")
        
        except Exception as e:
            print(f"✗ Error running backup: {e}")
        
        input("\nPress Enter...")
    
    def view_status(self):
        """View backup status"""
        self.clear()
        self.header("BACKUP STATUS")
        
        if not os.path.exists(self.backup_root):
            print("No backups yet. Run a backup first.\n")
            input("Press Enter...")
            return
        
        # Count stats
        total_files = 0
        total_size = 0
        
        for root, dirs, files in os.walk(self.backup_root):
            for file in files:
                total_files += 1
                total_size += os.path.getsize(os.path.join(root, file))
        
        size_mb = total_size / (1024 * 1024)
        
        print(f"Location: {self.backup_root}\n")
        print(f"Total Files: {total_files}")
        print(f"Total Size:  {size_mb:.2f} MB\n")
        
        print("Backup Folders:\n")
        
        # Show folder structure
        try:
            items = sorted(os.listdir(self.backup_root))
            for item in items:
                item_path = os.path.join(self.backup_root, item)
                if os.path.isdir(item_path):
                    # Count files in this date folder
                    count = sum(len(f) for _, _, f in os.walk(item_path))
                    print(f"  {item}/  ({count} files)")
        except Exception as e:
            print(f"Error reading backups: {e}")
        
        print()
        input("Press Enter...")
    
    def view_excluded(self):
        """View excluded files log"""
        self.clear()
        self.header("EXCLUDED FILES (Over 25MB)")
        
        if not os.path.exists(self.log_file):
            print("No exclusion log found.\nRun a backup first to generate it.\n")
            input("Press Enter...")
            return
        
        try:
            with open(self.log_file, "r") as f:
                content = f.read()
                # Show it in chunks if too long
                lines = content.split("\n")
                for line in lines:
                    print(line)
        except Exception as e:
            print(f"Error reading log: {e}")
        
        print()
        input("Press Enter...")
    
    def upload_github(self):
        """Upload to GitHub"""
        self.clear()
        self.header("UPLOAD TO GITHUB")
        
        if not os.path.exists(self.backup_root):
            print("No backups to upload.\n")
            input("Press Enter...")
            return
        
        # Check config
        if not self.check_config():
            input("Press Enter...")
            return
        
        print(f"Backup folder: {self.backup_root}\n")
        
        if not self.confirm("Upload to GitHub"):
            print("Cancelled.")
            input("Press Enter...")
            return
        
        print("\n" + "-" * 80)
        print("Uploading...\n")
        
        try:
            # Run uploader from code directory
            result = subprocess.run(
                [sys.executable, "github_uploader.py"],
                cwd=self.code_dir,
                capture_output=False
            )
            
            if result.returncode == 0:
                print("\n✓ Upload successful!")
            else:
                print("\n✗ Upload failed")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        input("\nPress Enter...")
    
    def settings_menu(self):
        """Settings submenu"""
        while True:
            self.clear()
            self.header("SETTINGS & CONFIGURATION")
            
            print("  What would you like to configure?\n")
            print("  1. Edit GitHub Config (backup_config.txt)")
            print("  2. Edit Exclusion List (exlude_paths.txt)")
            print("  3. Change Source Directory (code/main.py)")
            print("  4. Back to Main Menu\n")
            
            choice = self.prompt("Choose (1-4)")
            
            if choice == "1":
                self.edit_file(self.config_file, "GitHub Configuration")
            elif choice == "2":
                self.edit_file(self.exclude_file, "Exclusion List")
            elif choice == "3":
                self.edit_file(self.main_script, "Main Script (find source_directory)")
            elif choice == "4":
                break
            else:
                print("✗ Invalid choice")
                input("Press Enter...")
    
    def edit_file(self, filepath, description):
        """Open file in editor"""
        self.clear()
        self.header(f"EDIT {description.upper()}")
        
        if not os.path.exists(filepath):
            print(f"✗ File not found: {filepath}\n")
            input("Press Enter...")
            return
        
        # Show preview
        print(f"File: {filepath}\n")
        print("Preview (first 20 lines):\n")
        print("-" * 80)
        
        try:
            with open(filepath, "r") as f:
                lines = f.readlines()[:20]
                for i, line in enumerate(lines, 1):
                    print(f"{i:3d}: {line.rstrip()}")
                if len(lines) == 20:
                    print("... (file continues)")
        except Exception as e:
            print(f"Error reading file: {e}")
        
        print("-" * 80)
        
        if self.confirm("Open in editor"):
            try:
                if os.name == 'nt':
                    os.startfile(filepath)
                else:
                    subprocess.run(['open', filepath])
                print("\nOpened in default editor.")
                input("Close editor when done, then press Enter here...")
            except Exception as e:
                print(f"✗ Error opening editor: {e}")
        
        input("Press Enter...")
    
    def validate(self):
        """Run validation"""
        self.clear()
        self.header("VALIDATE SETUP")
        
        if not os.path.exists(self.validator_script):
            print("✗ Validation script not found\n")
            input("Press Enter...")
            return
        
        print("Running validation checks...\n")
        print("-" * 80 + "\n")
        
        try:
            subprocess.run([sys.executable, self.validator_script], cwd=self.base_dir)
        except Exception as e:
            print(f"Error running validation: {e}")
        
        input("\nPress Enter...")
    
    def check_config(self):
        """Check if config files are set up"""
        issues = []
        
        if not os.path.exists(self.config_file):
            issues.append("backup_config.txt not found")
        else:
            with open(self.config_file) as f:
                content = f.read().lower()
                if "your-username" in content or "your_username" in content:
                    issues.append("backup_config.txt has placeholders (edit it first)")
        
        if not os.path.exists(self.exclude_file):
            issues.append("exlude_paths.txt not found")
        
        if issues:
            print("Configuration Issues:\n")
            for issue in issues:
                print(f"  ✗ {issue}")
            print()
            return False
        
        return True
    
    def get_source_dir(self):
        """Extract source directory from main.py"""
        try:
            with open(self.main_script, "r") as f:
                for line in f:
                    if 'source_directory = "' in line:
                        start = line.find('"') + 1
                        end = line.rfind('"')
                        return line[start:end]
        except:
            pass
        return None
    
    def run(self):
        """Start the UI"""
        try:
            self.main_menu()
        except KeyboardInterrupt:
            print("\n\nExiting...\n")
            sys.exit(0)


def main():
    """Entry point"""
    ui = BackupControlCenter()
    ui.run()


if __name__ == "__main__":
    main()
