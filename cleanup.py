#!/usr/bin/env python
import os
import shutil
import sys
import time

def clean_directory(path, keep_gitkeep=True):
    """Clean a directory by removing all files and subdirectories."""
    if not os.path.exists(path):
        return
    
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        
        # Keep .gitkeep files if specified
        if keep_gitkeep and item == '.gitkeep':
            continue
            
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
            print(f"Removed: {item_path}")
        except PermissionError:
            print(f"WARNING: Could not remove {item_path} - file is in use. Please close all applications using this file.")
        except Exception as e:
            print(f"ERROR: Could not remove {item_path}: {str(e)}")
    
    print(f"Cleaned directory: {path}")

def cleanup_project():
    """Clean up the project by removing unnecessary files."""
    project_root = os.path.abspath(os.path.dirname(__file__))
    
    # Files and directories to clean up
    print("Starting cleanup process...")
    
    # Clean __pycache__ directories
    print("\nRemoving __pycache__ directories...")
    for root, dirs, files in os.walk(project_root):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_dir = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_dir)
                    print(f"Removed: {cache_dir}")
                except Exception as e:
                    print(f"ERROR: Could not remove {cache_dir}: {str(e)}")
    
    # Clean instance directory (database and search index)
    print("\nCleaning instance directory...")
    instance_dir = os.path.join(project_root, 'instance')
    if os.path.exists(instance_dir):
        # Remove database files
        for file in os.listdir(instance_dir):
            if file.endswith('.db') or file.endswith('.sqlite') or file.endswith('.sqlite3'):
                try:
                    os.remove(os.path.join(instance_dir, file))
                    print(f"Removed database file: {file}")
                except PermissionError:
                    print(f"WARNING: Could not remove database file {file} - it is in use.")
                    print("Please close all applications that might be using this file and try again.")
                except Exception as e:
                    print(f"ERROR: Could not remove {file}: {str(e)}")
        
        # Clean Whoosh index directory
        whoosh_dir = os.path.join(instance_dir, 'whoosh_index')
        if os.path.exists(whoosh_dir):
            clean_directory(whoosh_dir)
    
    # Clean uploads directory
    print("\nRemoving uploaded files...")
    uploads_dir = os.path.join(project_root, 'app', 'static', 'uploads')
    if os.path.exists(uploads_dir):
        clean_directory(uploads_dir, keep_gitkeep=True)
    
    # Remove any .pyc files
    print("\nRemoving compiled Python files...")
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.pyc') or file.endswith('.pyo'):
                try:
                    os.remove(os.path.join(root, file))
                    print(f"Removed: {os.path.join(root, file)}")
                except Exception as e:
                    print(f"ERROR: Could not remove {file}: {str(e)}")
    
    # Remove any other unnecessary files
    print("\nRemoving other unnecessary files...")
    unnecessary_files = [
        os.path.join(project_root, '.vscode'),
        os.path.join(project_root, '.idea'),
        os.path.join(project_root, '.DS_Store'),
        os.path.join(project_root, 'Thumbs.db'),
        os.path.join(project_root, 'venv'),
        os.path.join(project_root, 'env'),
        os.path.join(project_root, '.env'),
        os.path.join(project_root, '__pycache__'),
        os.path.join(project_root, '.pytest_cache'),
        os.path.join(project_root, 'logs')
    ]
    
    for path in unnecessary_files:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"Removed: {path}")
            except Exception as e:
                print(f"ERROR: Could not remove {path}: {str(e)}")
    
    print("\nCleanup complete!")
    print("The project should now contain only the necessary files for sharing.")
    print("Remember to update the repository URL in the README.md file before sharing.")

if __name__ == "__main__":
    print("WARNING: This script will clean up the project and remove all:")
    print(" - Database files")
    print(" - Search index files")
    print(" - Uploaded documents")
    print(" - Cache files and compiled Python files")
    print(" - Any virtual environment directories")
    print("\nMake sure all applications using this project are closed before continuing!")
    
    # Confirm before proceeding
    confirm = input("\nAre you sure you want to proceed? (y/N): ")
    if confirm.lower() != 'y':
        print("Cleanup cancelled.")
        sys.exit(0)
    
    cleanup_project() 