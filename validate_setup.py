#!/usr/bin/env python3
"""
GitHub Backupper - Setup Validator

This script checks if your system is properly configured for backups.
Run this before running main.py to catch configuration issues early.
"""

import os
import sys
import subprocess


def check_python():
    """Check Python version."""
    print("[CHECK] Python Version")
    version = sys.version_info
    print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("  ✗ Python 3.6+ required")
        return False
    return True


def check_git():
    """Check if Git is installed."""
    print("\n[CHECK] Git Installation")
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        print(f"  ✓ {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("  ✗ Git not found - install from https://git-scm.com")
        return False


def check_ssh():
    """Check if SSH is available."""
    print("\n[CHECK] SSH Availability")
    try:
        result = subprocess.run(["ssh", "-V"], capture_output=True, text=True)
        print(f"  ✓ SSH available")
        return True
    except FileNotFoundError:
        print("  ✗ SSH not found - install Git with SSH support")
        return False


def check_config_file():
    """Check if backup_config.txt exists and is configured."""
    print("\n[CHECK] Configuration File")
    config_path = "backup_config.txt"
    
    if not os.path.exists(config_path):
        print(f"  ✗ {config_path} not found")
        return False
    
    print(f"  ✓ {config_path} found")
    
    with open(config_path, "r") as f:
        content = f.read()
        
    issues = []
    
    if "GITHUB_REPO_URL=" not in content:
        issues.append("GITHUB_REPO_URL not set")
    elif "git@github.com:your-username" in content:
        issues.append("GITHUB_REPO_URL still has placeholder")
    else:
        print("    ✓ GITHUB_REPO_URL configured")
    
    if "SSH_KEY_PATH=" not in content:
        issues.append("SSH_KEY_PATH not set")
    elif "your-username" in content or "your_username" in content:
        issues.append("SSH_KEY_PATH still has placeholder")
    else:
        print("    ✓ SSH_KEY_PATH configured")
    
    if issues:
        for issue in issues:
            print(f"    ✗ {issue}")
        return False
    
    return True


def check_ssh_key():
    """Check if SSH key exists and is accessible."""
    print("\n[CHECK] SSH Key File")
    
    config_path = "backup_config.txt"
    if not os.path.exists(config_path):
        print("  ! Skipping - config file not found")
        return True
    
    with open(config_path, "r") as f:
        for line in f:
            if line.startswith("SSH_KEY_PATH="):
                ssh_key_path = line.split("=", 1)[1].strip()
                break
        else:
            print("  ! SSH_KEY_PATH not configured")
            return True
    
    if not ssh_key_path or "your-username" in ssh_key_path:
        print("  ! SSH_KEY_PATH has placeholder")
        return True
    
    if not os.path.exists(ssh_key_path):
        print(f"  ✗ SSH key not found at: {ssh_key_path}")
        print("    Generate SSH key: ssh-keygen -t rsa -b 4096")
        return False
    
    print(f"  ✓ SSH key found: {ssh_key_path}")
    return True


def check_exclude_file():
    """Check if exclude file exists."""
    print("\n[CHECK] Exclusion File")
    exclude_path = "exlude_paths.txt"
    
    if not os.path.exists(exclude_path):
        print(f"  ✗ {exclude_path} not found")
        return False
    
    print(f"  ✓ {exclude_path} found")
    
    with open(exclude_path, "r") as f:
        lines = len([l for l in f if l.strip() and not l.startswith("#")])
    
    print(f"    - {lines} exclusion patterns configured")
    return True


def check_main_py():
    """Check if main.py has valid source directory."""
    print("\n[CHECK] Main Script Configuration")
    
    main_path = "code/main.py"
    if not os.path.exists(main_path):
        print(f"  ✗ {main_path} not found")
        return False
    
    print(f"  ✓ {main_path} found")
    
    with open(main_path, "r") as f:
        content = f.read()
        
    if "source_directory = " in content:
        # Extract the source directory
        for line in content.split("\n"):
            if "source_directory = " in line and not line.strip().startswith("#"):
                print(f"    - Found source_directory configuration")
                if "C:\\Users\\leonm\\Desktop" in line:
                    print("    Using default path - consider customizing")
                return True
    
    print("  ✗ source_directory not configured in main.py")
    return False


def check_github_connectivity():
    """Test SSH connection to GitHub."""
    print("\n[CHECK] GitHub SSH Connectivity")
    
    try:
        result = subprocess.run(
            ["ssh", "-T", "git@github.com"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "successfully authenticated" in result.stdout or \
           "You've successfully authenticated" in result.stderr or \
           result.returncode == 1:  # GitHub closes connection after auth
            print("  ✓ SSH connection to GitHub successful")
            return True
        else:
            print("  ✗ SSH connection to GitHub failed")
            print(f"    Message: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ✗ SSH connection timed out")
        return False
    except Exception as e:
        print(f"  ✗ Error testing SSH: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 80)
    print("GitHub Backupper - Setup Validator")
    print("=" * 80)
    
    checks = [
        ("Python Version", check_python),
        ("Git Installation", check_git),
        ("SSH Availability", check_ssh),
        ("Configuration File", check_config_file),
        ("SSH Key File", check_ssh_key),
        ("Exclusion File", check_exclude_file),
        ("Main Script", check_main_py),
        ("GitHub Connectivity", check_github_connectivity),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ Your system is ready for backup!")
        print("\nNext steps:")
        print("1. Run: python code/main.py")
        print("2. Or double-click: run_backup.bat")
    else:
        print("\n✗ Please fix the issues above before running backups")
        print("\nFor help, see README.md")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
