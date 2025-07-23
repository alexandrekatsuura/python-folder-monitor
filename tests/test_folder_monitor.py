"""
Unit tests for the FolderMonitor class.

This module contains comprehensive tests for the folder monitoring functionality,
including size calculation, limit checking, and alert mechanisms.
"""

import os
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.folder_monitor import FolderMonitor


class TestFolderMonitor:
    """Test class for FolderMonitor functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.monitor = FolderMonitor()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def create_test_file(self, filename: str, size_bytes: int) -> str:
        """
        Create a test file with specified size.
        
        Args:
            filename (str): Name of the file to create
            size_bytes (int): Size of the file in bytes
            
        Returns:
            str: Full path to the created file
        """
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(b'0' * size_bytes)
        return file_path
        
    def test_init_default(self):
        """Test FolderMonitor initialization with default parameters."""
        monitor = FolderMonitor()
        assert monitor.monitoring_config == {}
        assert monitor.alerts_triggered == []
        
    def test_init_with_config(self):
        """Test FolderMonitor initialization with custom configuration."""
        config = {'/test/path': 1024}
        monitor = FolderMonitor(config)
        assert monitor.monitoring_config == config
        assert monitor.alerts_triggered == []
        
    def test_add_folder_to_monitor_success(self):
        """Test successfully adding a folder to monitor."""
        size_limit_mb = 10
        result = self.monitor.add_folder_to_monitor(self.temp_dir, size_limit_mb)
        
        assert result is True
        assert self.temp_dir in self.monitor.monitoring_config
        assert self.monitor.monitoring_config[self.temp_dir] == size_limit_mb * 1024 * 1024
        
    def test_add_folder_to_monitor_nonexistent(self):
        """Test adding a non-existent folder to monitor."""
        nonexistent_path = '/path/that/does/not/exist'
        result = self.monitor.add_folder_to_monitor(nonexistent_path, 10)
        
        assert result is False
        assert nonexistent_path not in self.monitor.monitoring_config
        
    def test_add_folder_to_monitor_not_directory(self):
        """Test adding a file (not directory) to monitor."""
        file_path = self.create_test_file('test.txt', 100)
        result = self.monitor.add_folder_to_monitor(file_path, 10)
        
        assert result is False
        assert file_path not in self.monitor.monitoring_config
        
    def test_remove_folder_from_monitor_success(self):
        """Test successfully removing a folder from monitor."""
        self.monitor.add_folder_to_monitor(self.temp_dir, 10)
        result = self.monitor.remove_folder_from_monitor(self.temp_dir)
        
        assert result is True
        assert self.temp_dir not in self.monitor.monitoring_config
        
    def test_remove_folder_from_monitor_not_monitored(self):
        """Test removing a folder that is not being monitored."""
        result = self.monitor.remove_folder_from_monitor('/some/path')
        
        assert result is False
        
    def test_get_folder_size_empty_folder(self):
        """Test getting size of an empty folder."""
        size = self.monitor.get_folder_size(self.temp_dir)
        assert size == 0
        
    def test_get_folder_size_with_files(self):
        """Test getting size of a folder with files."""
        file1_size = 1024
        file2_size = 2048
        
        self.create_test_file('file1.txt', file1_size)
        self.create_test_file('file2.txt', file2_size)
        
        total_size = self.monitor.get_folder_size(self.temp_dir)
        assert total_size == file1_size + file2_size
        
    def test_get_folder_size_with_subdirectories(self):
        """Test getting size of a folder with subdirectories."""
        # Create subdirectory
        subdir = os.path.join(self.temp_dir, 'subdir')
        os.makedirs(subdir)
        
        file1_size = 1024
        file2_size = 2048
        
        # Create files in main directory and subdirectory
        self.create_test_file('file1.txt', file1_size)
        with open(os.path.join(subdir, 'file2.txt'), 'wb') as f:
            f.write(b'0' * file2_size)
            
        total_size = self.monitor.get_folder_size(self.temp_dir)
        assert total_size == file1_size + file2_size
        
    def test_get_folder_size_nonexistent_folder(self):
        """Test getting size of a non-existent folder."""
        with pytest.raises(OSError):
            self.monitor.get_folder_size('/path/that/does/not/exist')
            
    def test_format_size_bytes(self):
        """Test formatting size in bytes."""
        assert self.monitor.format_size(512) == "512.00 B"
        
    def test_format_size_kilobytes(self):
        """Test formatting size in kilobytes."""
        assert self.monitor.format_size(1536) == "1.50 KB"
        
    def test_format_size_megabytes(self):
        """Test formatting size in megabytes."""
        assert self.monitor.format_size(1572864) == "1.50 MB"
        
    def test_format_size_gigabytes(self):
        """Test formatting size in gigabytes."""
        assert self.monitor.format_size(1610612736) == "1.50 GB"
        
    def test_check_folder_limits_no_violations(self):
        """Test checking folder limits with no violations."""
        # Create small file
        self.create_test_file('small.txt', 100)
        
        # Set large limit
        self.monitor.add_folder_to_monitor(self.temp_dir, 10)  # 10 MB
        
        violations = self.monitor.check_folder_limits()
        assert len(violations) == 0
        
    def test_check_folder_limits_with_violations(self):
        """Test checking folder limits with violations."""
        # Create large file (2 MB)
        large_file_size = 2 * 1024 * 1024
        self.create_test_file('large.txt', large_file_size)
        
        # Set small limit (1 MB)
        self.monitor.add_folder_to_monitor(self.temp_dir, 1)
        
        violations = self.monitor.check_folder_limits()
        assert len(violations) == 1
        
        violation = violations[0]
        assert violation['folder_path'] == self.temp_dir
        assert violation['current_size'] == large_file_size
        assert violation['size_limit'] == 1024 * 1024
        assert violation['excess_size'] == large_file_size - (1024 * 1024)
        
    def test_trigger_alert(self):
        """Test triggering an alert for a violation."""
        violation = {
            'folder_path': '/test/path',
            'current_size': 2048,
            'size_limit': 1024,
            'current_size_formatted': '2.00 KB',
            'size_limit_formatted': '1.00 KB',
            'excess_size': 1024,
            'excess_size_formatted': '1.00 KB'
        }
        
        with patch('builtins.print') as mock_print:
            self.monitor.trigger_alert(violation)
            
        assert len(self.monitor.alerts_triggered) == 1
        assert self.monitor.alerts_triggered[0]['violation'] == violation
        mock_print.assert_called()
        
    def test_monitor_once_no_folders(self):
        """Test monitoring once with no configured folders."""
        with patch('builtins.print') as mock_print:
            result = self.monitor.monitor_once()
            
        assert result is False
        mock_print.assert_called_with("No folders configured for monitoring.")
        
    def test_monitor_once_no_violations(self):
        """Test monitoring once with no violations."""
        self.create_test_file('small.txt', 100)
        self.monitor.add_folder_to_monitor(self.temp_dir, 10)  # 10 MB
        
        with patch('builtins.print') as mock_print:
            result = self.monitor.monitor_once()
            
        assert result is False
        mock_print.assert_called_with("All monitored folders are within their size limits.")
        
    def test_monitor_once_with_violations(self):
        """Test monitoring once with violations."""
        large_file_size = 2 * 1024 * 1024  # 2 MB
        self.create_test_file('large.txt', large_file_size)
        self.monitor.add_folder_to_monitor(self.temp_dir, 1)  # 1 MB limit
        
        with patch('builtins.print'):
            result = self.monitor.monitor_once()
            
        assert result is True
        assert len(self.monitor.alerts_triggered) == 1
        
    @patch('time.sleep')
    def test_monitor_continuously_keyboard_interrupt(self, mock_sleep):
        """Test continuous monitoring with keyboard interrupt."""
        self.monitor.add_folder_to_monitor(self.temp_dir, 10)
        
        # Simulate KeyboardInterrupt after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()
        
        with patch('builtins.print'):
            self.monitor.monitor_continuously(1)
            
        mock_sleep.assert_called_once_with(1)
        
    def test_get_monitoring_status_empty(self):
        """Test getting monitoring status with no folders."""
        status = self.monitor.get_monitoring_status()
        
        assert status['total_folders_monitored'] == 0
        assert status['folders'] == []
        assert status['total_alerts_triggered'] == 0
        
    def test_get_monitoring_status_with_folders(self):
        """Test getting monitoring status with configured folders."""
        file_size = 1024
        self.create_test_file('test.txt', file_size)
        self.monitor.add_folder_to_monitor(self.temp_dir, 10)  # 10 MB
        
        status = self.monitor.get_monitoring_status()
        
        assert status['total_folders_monitored'] == 1
        assert len(status['folders']) == 1
        
        folder_info = status['folders'][0]
        assert folder_info['path'] == self.temp_dir
        assert folder_info['current_size'] == file_size
        assert folder_info['size_limit'] == 10 * 1024 * 1024
        assert folder_info['is_over_limit'] is False
        assert 0 < folder_info['usage_percentage'] < 1
        
    def test_get_monitoring_status_with_error(self):
        """Test getting monitoring status with folder access error."""
        # Add non-existent folder to config directly
        self.monitor.monitoring_config['/nonexistent/path'] = 1024
        
        status = self.monitor.get_monitoring_status()
        
        assert status['total_folders_monitored'] == 1
        assert len(status['folders']) == 1
        assert 'error' in status['folders'][0]

