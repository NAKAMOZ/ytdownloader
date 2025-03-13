"""
Basic tests for YouTube Downloader
"""

import os
import sys
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.downloader import YouTubeDownloader

class BasicTests(unittest.TestCase):
    """Basic tests for the YouTube Downloader"""
    
    def setUp(self):
        """Set up the test case"""
        self.downloader = YouTubeDownloader()
    
    def test_initialization(self):
        """Test if downloader initializes correctly"""
        self.assertIsNotNone(self.downloader)
        self.assertIsNotNone(self.downloader.signals)
        self.assertTrue(hasattr(self.downloader, 'download_directory'))
    
    def test_clean_filename(self):
        """Test filename cleaning functionality"""
        # Test with invalid characters
        test_filename = "Video: Test? File* Name|"
        cleaned = self.downloader.clean_filename(test_filename)
        self.assertEqual(cleaned, "Video_ Test_ File_ Name_")
        
        # Test without invalid characters
        test_filename = "Normal File Name"
        cleaned = self.downloader.clean_filename(test_filename)
        self.assertEqual(cleaned, "Normal File Name")

if __name__ == '__main__':
    unittest.main() 