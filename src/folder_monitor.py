"""
Folder Monitor Module

This module provides functionality to monitor folder sizes and alert when they exceed defined limits.
"""

import os
import time
from typing import Dict, List, Optional


class FolderMonitor:
    """
    A class to monitor folder sizes and alert when they exceed predefined limits.
    
    This class allows users to configure multiple folders for monitoring with individual
    size limits and provides alerting mechanisms when those limits are exceeded.
    """
    
    def __init__(self, monitoring_config: Optional[Dict[str, int]] = None):
        """
        Initialize the FolderMonitor with monitoring configuration.
        
        Args:
            monitoring_config (Dict[str, int], optional): Dictionary mapping folder paths 
                                                         to size limits in bytes. 
                                                         Defaults to None.
        """
        self.monitoring_config = monitoring_config or {}
        self.alerts_triggered = []
        
    def add_folder_to_monitor(self, folder_path: str, size_limit_mb: int) -> bool:
        """
        Add a folder to the monitoring configuration.
        
        Args:
            folder_path (str): Path to the folder to monitor
            size_limit_mb (int): Size limit in megabytes
            
        Returns:
            bool: True if folder was added successfully, False otherwise
        """
        if not os.path.exists(folder_path):
            print(f"Warning: Folder '{folder_path}' does not exist.")
            return False
            
        if not os.path.isdir(folder_path):
            print(f"Warning: '{folder_path}' is not a directory.")
            return False
            
        size_limit_bytes = size_limit_mb * 1024 * 1024  # Convert MB to bytes
        self.monitoring_config[folder_path] = size_limit_bytes
        print(f"Added folder '{folder_path}' to monitoring with limit {size_limit_mb} MB")
        return True
        
    def remove_folder_from_monitor(self, folder_path: str) -> bool:
        """
        Remove a folder from the monitoring configuration.
        
        Args:
            folder_path (str): Path to the folder to remove from monitoring
            
        Returns:
            bool: True if folder was removed successfully, False otherwise
        """
        if folder_path in self.monitoring_config:
            del self.monitoring_config[folder_path]
            print(f"Removed folder '{folder_path}' from monitoring")
            return True
        else:
            print(f"Folder '{folder_path}' is not being monitored")
            return False
            
    def get_folder_size(self, folder_path: str) -> int:
        """
        Calculate the total size of a folder in bytes.
        
        Args:
            folder_path (str): Path to the folder
            
        Returns:
            int: Total size of the folder in bytes
            
        Raises:
            OSError: If there's an error accessing the folder or its contents
        """
        if not os.path.exists(folder_path):
            raise OSError(f"Folder \'{folder_path}\' does not exist.")
        if not os.path.isdir(folder_path):
            raise OSError(f"\'{folder_path}\' is not a directory.")
        
        total_size = 0
        
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                except (OSError, FileNotFoundError):
                    # Skip files that can\'t be accessed
                    continue
            
        return total_size
        
    def format_size(self, size_bytes: int) -> str:
        """
        Format size in bytes to human-readable format.
        
        Args:
            size_bytes (int): Size in bytes
            
        Returns:
            str: Formatted size string (e.g., "1.5 GB", "256 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
        
    def check_folder_limits(self) -> List[Dict[str, any]]:
        """
        Check all monitored folders against their size limits.
        
        Returns:
            List[Dict[str, any]]: List of dictionaries containing information about 
                                 folders that exceeded their limits
        """
        violations = []
        
        for folder_path, size_limit in self.monitoring_config.items():
            try:
                current_size = self.get_folder_size(folder_path)
                
                if current_size > size_limit:
                    violation = {
                        'folder_path': folder_path,
                        'current_size': current_size,
                        'size_limit': size_limit,
                        'current_size_formatted': self.format_size(current_size),
                        'size_limit_formatted': self.format_size(size_limit),
                        'excess_size': current_size - size_limit,
                        'excess_size_formatted': self.format_size(current_size - size_limit)
                    }
                    violations.append(violation)
                    
            except OSError as e:
                print(f"Error checking folder '{folder_path}': {e}")
                
        return violations
        
    def trigger_alert(self, violation: Dict[str, any]) -> None:
        """
        Trigger an alert for a folder size violation.
        
        Args:
            violation (Dict[str, any]): Dictionary containing violation information
        """
        alert_message = (
            f"🚨 FOLDER SIZE ALERT 🚨\n"
            f"Folder: {violation['folder_path']}\n"
            f"Current Size: {violation['current_size_formatted']}\n"
            f"Size Limit: {violation['size_limit_formatted']}\n"
            f"Excess: {violation['excess_size_formatted']}\n"
            f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{'-' * 50}"
        )
        
        print(alert_message)
        self.alerts_triggered.append({
            'timestamp': time.time(),
            'violation': violation,
            'message': alert_message
        })
        
    def monitor_once(self) -> bool:
        """
        Perform a single monitoring check on all configured folders.
        
        Returns:
            bool: True if any violations were found, False otherwise
        """
        if not self.monitoring_config:
            print("No folders configured for monitoring.")
            return False
            
        violations = self.check_folder_limits()
        
        if violations:
            print(f"Found {len(violations)} folder size violation(s):")
            for violation in violations:
                self.trigger_alert(violation)
            return True
        else:
            print("All monitored folders are within their size limits.")
            return False
            
    def monitor_continuously(self, check_interval: int = 60) -> None:
        """
        Monitor folders continuously at specified intervals.
        
        Args:
            check_interval (int): Time interval between checks in seconds (default: 60)
        """
        print(f"Starting continuous monitoring (checking every {check_interval} seconds)")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking folder sizes...")
                self.monitor_once()
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
            
    def get_monitoring_status(self) -> Dict[str, any]:
        """
        Get the current monitoring status and configuration.
        
        Returns:
            Dict[str, any]: Dictionary containing monitoring status information
        """
        status = {
            'total_folders_monitored': len(self.monitoring_config),
            'folders': [],
            'total_alerts_triggered': len(self.alerts_triggered)
        }
        
        for folder_path, size_limit in self.monitoring_config.items():
            try:
                current_size = self.get_folder_size(folder_path)
                folder_info = {
                    'path': folder_path,
                    'current_size': current_size,
                    'current_size_formatted': self.format_size(current_size),
                    'size_limit': size_limit,
                    'size_limit_formatted': self.format_size(size_limit),
                    'usage_percentage': (current_size / size_limit) * 100 if size_limit > 0 else 0,
                    'is_over_limit': current_size > size_limit
                }
                status['folders'].append(folder_info)
            except OSError as e:
                status['folders'].append({
                    'path': folder_path,
                    'error': str(e)
                })
                
        return status

