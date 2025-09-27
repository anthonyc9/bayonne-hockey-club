#!/usr/bin/env python3
"""
Debug script to check file paths and database consistency
Run this on production to identify the issue
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app, db
from app.models import File, Folder

def debug_files():
    app = create_app()
    
    with app.app_context():
        print("=== FILE DEBUG INFORMATION ===")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Instance path: {app.instance_path}")
        
        # Check all files in database
        files = File.query.all()
        print(f"\nTotal files in database: {len(files)}")
        
        for file in files:
            print(f"\n--- File ID: {file.id} ---")
            print(f"Original name: {file.original_name}")
            print(f"File path: {file.file_path}")
            print(f"File exists: {os.path.exists(file.file_path)}")
            print(f"File size: {file.file_size}")
            print(f"MIME type: {file.mime_type}")
            print(f"Folder ID: {file.folder_id}")
            
            if os.path.exists(file.file_path):
                actual_size = os.path.getsize(file.file_path)
                print(f"Actual file size: {actual_size}")
                print(f"Size matches: {actual_size == file.file_size}")
            else:
                print("FILE NOT FOUND ON DISK!")
                
                # Try to find the file in common locations
                filename = file.original_name
                possible_paths = [
                    os.path.join(app.instance_path, 'documents', filename),
                    os.path.join(app.instance_path, 'files', filename),
                    os.path.join(app.instance_path, 'uploads', filename),
                    os.path.join('instance', 'documents', filename),
                    os.path.join('instance', 'files', filename),
                    os.path.join('instance', 'uploads', filename),
                ]
                
                print("Searching for file in common locations:")
                for path in possible_paths:
                    if os.path.exists(path):
                        print(f"  FOUND: {path}")
                    else:
                        print(f"  Not found: {path}")
        
        # Check folders
        folders = Folder.query.all()
        print(f"\n=== FOLDERS ===")
        print(f"Total folders: {len(folders)}")
        for folder in folders:
            print(f"Folder ID: {folder.id}, Name: {folder.name}, Parent: {folder.parent_id}")

if __name__ == "__main__":
    debug_files()
