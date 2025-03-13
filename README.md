# YouTube Downloader

A desktop application for downloading videos and audio from YouTube with a user-friendly interface.

![YouTube Downloader Screenshot](assets/screenshot.png)

## Features

- Download YouTube videos in various qualities (240p to 1080p)
- Download audio in MP3 format with different bitrates
- Download entire playlists
- Track download progress in real-time
- View download history
- Simple and intuitive user interface
- High-quality downloads using yt-dlp and ffmpeg

## Installation

### Requirements

- Python 3.8 or higher
- FFmpeg (automatically downloaded during installation if not present)

### Option 1: Using the Installer (Windows)

1. Download the latest installer from the [Releases](https://github.com/yourusername/ytdownloader/releases) page
2. Run the installer and follow the on-screen instructions
3. Start the application from the desktop shortcut or Start menu

### Option 2: From Source

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/ytdownloader.git
   cd ytdownloader
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Usage

1. Launch the application
2. Enter a YouTube URL in the input field
3. Select the download type (Video or Audio)
4. Choose your preferred quality
5. Click "Download" and wait for the process to complete
6. Access downloaded files through the application or in your Downloads folder

## Development

### Project Structure

```
ytdownloader/
├── assets/              # Images and resources
├── docs/                # Documentation
├── src/                 # Source code
│   ├── core/            # Core functionality
│   │   └── downloader.py  # YouTube download logic
│   ├── ui/              # User interface
│   │   └── main_window.py # Main application window
│   └── main.py          # Application entry point
├── tests/               # Test files
├── .gitignore           # Git ignore file
├── LICENSE              # License file
├── README.md            # This file
└── requirements.txt     # Python dependencies
```

### Building the Application

To build the executable and installer:

1. Install PyInstaller and NSIS:
   ```
   pip install pyinstaller
   ```
2. Download and install [NSIS](https://nsis.sourceforge.io/Download)

3. Run the build script:
   ```
   python build.py
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the powerful YouTube download engine
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework
- [FFmpeg](https://ffmpeg.org/) for media processing capabilities
