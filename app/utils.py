"""
Utility functions for the coaches portal application.
"""

import os
from flask import current_app


def resolve_file_path(file_record):
    """
    Resolve the actual file path for a file record.
    Tries multiple possible locations to find the file.
    
    Args:
        file_record: File model instance
        
    Returns:
        str: Resolved file path if found, None otherwise
    """
    possible_paths = [
        file_record.file_path,  # Original path from database
        os.path.join(current_app.instance_path, 'documents', file_record.original_name),
        os.path.join(current_app.instance_path, 'files', file_record.original_name),
        os.path.join(current_app.config['UPLOAD_FOLDER'], file_record.original_name),
        # Try with the stored filename if it's different from original_name
        os.path.join(current_app.instance_path, 'documents', file_record.name),
        os.path.join(current_app.instance_path, 'files', file_record.name),
        os.path.join(current_app.config['UPLOAD_FOLDER'], file_record.name),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None


def get_file_debug_info(file_record):
    """
    Get debug information about a file record.
    
    Args:
        file_record: File model instance
        
    Returns:
        dict: Debug information about the file
    """
    possible_paths = [
        file_record.file_path,
        os.path.join(current_app.instance_path, 'documents', file_record.original_name),
        os.path.join(current_app.instance_path, 'files', file_record.original_name),
        os.path.join(current_app.config['UPLOAD_FOLDER'], file_record.original_name),
    ]
    
    debug_info = {
        'file_id': file_record.id,
        'original_name': file_record.original_name,
        'stored_path': file_record.file_path,
        'instance_path': current_app.instance_path,
        'upload_folder': current_app.config['UPLOAD_FOLDER'],
        'possible_paths': []
    }
    
    for path in possible_paths:
        debug_info['possible_paths'].append({
            'path': path,
            'exists': os.path.exists(path),
            'size': os.path.getsize(path) if os.path.exists(path) else None
        })
    
    return debug_info
