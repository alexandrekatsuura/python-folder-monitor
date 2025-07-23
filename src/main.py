"""
Main Module

This module contains the main execution logic for the Folder Monitor application.
"""

import sys
import os
from typing import Optional

from folder_monitor import FolderMonitor


class Main:
    """
    Main class that handles the application's entry point and user interaction.
    
    This class provides a command-line interface for the folder monitoring application,
    allowing users to configure folders, set limits, and start monitoring.
    """
    
    def __init__(self):
        """Initialize the Main class with a FolderMonitor instance."""
        self.monitor = FolderMonitor()
        
    def display_menu(self) -> None:
        """Display the main menu options to the user."""
        print("\n" + "=" * 50)
        print("📁 FOLDER SIZE MONITOR")
        print("=" * 50)
        print("1. Add folder to monitor")
        print("2. Remove folder from monitor")
        print("3. Check folder sizes once")
        print("4. Start continuous monitoring")
        print("5. View monitoring status")
        print("6. Exit")
        print("-" * 50)
        
    def get_user_input(self, prompt: str) -> str:
        """
        Get user input with error handling.
        
        Args:
            prompt (str): The prompt to display to the user
            
        Returns:
            str: User input string
        """
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return ""
        except EOFError:
            print("\nEnd of input reached.")
            return ""
            
    def add_folder_interactive(self) -> None:
        """Interactive method to add a folder to monitoring."""
        print("\n📂 Add Folder to Monitor")
        print("-" * 30)
        
        folder_path = self.get_user_input("Enter folder path: ")
        if not folder_path:
            return
            
        # Expand user path (e.g., ~/Documents)
        folder_path = os.path.expanduser(folder_path)
        
        try:
            size_limit_str = self.get_user_input("Enter size limit in MB: ")
            if not size_limit_str:
                return
                
            size_limit_mb = int(size_limit_str)
            if size_limit_mb <= 0:
                print("Error: Size limit must be a positive number.")
                return
                
        except ValueError:
            print("Error: Please enter a valid number for size limit.")
            return
            
        success = self.monitor.add_folder_to_monitor(folder_path, size_limit_mb)
        if success:
            print("✅ Folder added successfully!")
        else:
            print("❌ Failed to add folder.")
            
    def remove_folder_interactive(self) -> None:
        """Interactive method to remove a folder from monitoring."""
        print("\n🗑️ Remove Folder from Monitor")
        print("-" * 35)
        
        if not self.monitor.monitoring_config:
            print("No folders are currently being monitored.")
            return
            
        print("Currently monitored folders:")
        for i, folder_path in enumerate(self.monitor.monitoring_config.keys(), 1):
            print(f"{i}. {folder_path}")
            
        choice = self.get_user_input("Enter folder number to remove (or path): ")
        if not choice:
            return
            
        try:
            # Try to parse as number first
            folder_index = int(choice) - 1
            folder_paths = list(self.monitor.monitoring_config.keys())
            if 0 <= folder_index < len(folder_paths):
                folder_path = folder_paths[folder_index]
            else:
                print("Error: Invalid folder number.")
                return
        except ValueError:
            # Treat as folder path
            folder_path = os.path.expanduser(choice)
            
        success = self.monitor.remove_folder_from_monitor(folder_path)
        if success:
            print("✅ Folder removed successfully!")
        else:
            print("❌ Failed to remove folder.")
            
    def check_once_interactive(self) -> None:
        """Interactive method to perform a single monitoring check."""
        print("\n🔍 Checking Folder Sizes...")
        print("-" * 30)
        
        violations_found = self.monitor.monitor_once()
        
        if not violations_found:
            print("✅ All folders are within their limits!")
            
    def start_continuous_monitoring_interactive(self) -> None:
        """Interactive method to start continuous monitoring."""
        print("\n⏰ Continuous Monitoring Setup")
        print("-" * 35)
        
        if not self.monitor.monitoring_config:
            print("No folders configured for monitoring.")
            print("Please add folders first.")
            return
            
        try:
            interval_str = self.get_user_input("Enter check interval in seconds (default: 60): ")
            if not interval_str:
                interval = 60
            else:
                interval = int(interval_str)
                if interval <= 0:
                    print("Error: Interval must be a positive number.")
                    return
        except ValueError:
            print("Error: Please enter a valid number for interval.")
            return
            
        print(f"\n🚀 Starting continuous monitoring...")
        self.monitor.monitor_continuously(interval)
        
    def view_status_interactive(self) -> None:
        """Interactive method to view monitoring status."""
        print("\n📊 Monitoring Status")
        print("-" * 25)
        
        status = self.monitor.get_monitoring_status()
        
        print(f"Total folders monitored: {status['total_folders_monitored']}")
        print(f"Total alerts triggered: {status['total_alerts_triggered']}")
        
        if status['folders']:
            print("\nFolder Details:")
            print("-" * 80)
            for folder in status['folders']:
                if 'error' in folder:
                    print(f"❌ {folder['path']}: {folder['error']}")
                else:
                    status_icon = "🔴" if folder['is_over_limit'] else "🟢"
                    print(f"{status_icon} {folder['path']}")
                    print(f"   Current: {folder['current_size_formatted']}")
                    print(f"   Limit: {folder['size_limit_formatted']}")
                    print(f"   Usage: {folder['usage_percentage']:.1f}%")
                    print()
        else:
            print("No folders configured for monitoring.")
            
    def run(self) -> None:
        """
        Main application loop.
        
        This method displays the menu and handles user choices until the user exits.
        """
        print("Welcome to Folder Size Monitor!")
        
        while True:
            self.display_menu()
            choice = self.get_user_input("Enter your choice (1-6): ")
            
            if choice == "1":
                self.add_folder_interactive()
            elif choice == "2":
                self.remove_folder_interactive()
            elif choice == "3":
                self.check_once_interactive()
            elif choice == "4":
                self.start_continuous_monitoring_interactive()
            elif choice == "5":
                self.view_status_interactive()
            elif choice == "6":
                print("\n👋 Thank you for using Folder Size Monitor!")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1 and 6.")
                
            # Pause before showing menu again
            if choice in ["1", "2", "3", "5"]:
                input("\nPress Enter to continue...")


def main() -> None:
    """
    Entry point of the application.
    
    This function creates a Main instance and starts the application.
    """
    try:
        app = Main()
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

