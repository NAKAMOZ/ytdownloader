# YouTube Downloader

A user-friendly desktop application for downloading videos and audio from YouTube.

![YouTube Downloader Screenshot](assets/screenshot.png)

## Features

- Video and audio (MP3) download support
- Various video quality options (from 240p to 1080p)
- Different audio quality options (from 96kbps to 320kbps)
- Playlist download support
- Download progress tracking and status display
- Automatic thumbnail downloading
- Dark theme interface
- Custom download location selection

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Development Setup](#development-setup)
- [Building an Executable](#building-an-executable)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)

## Requirements

- Python 3.6 or higher
- FFmpeg
- The following Python packages:
  - PyQt6
  - yt-dlp
  - ffmpeg-python
  - pyinstaller (for building executable)

## Installation

### Quick Start

1. Download the latest release from the [Releases](https://github.com/yourusername/ytdownloader/releases) page
2. Extract the ZIP file to your preferred location
3. Run the `ytdownloader.exe` file (Windows) or `ytdownloader` executable (Linux/macOS)

### Manual Installation

#### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ytdownloader.git
cd ytdownloader
```

#### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On Linux/MacOS:

```bash
source venv/bin/activate
```

#### 3. Install the requirements

```bash
pip install -r requirements.txt
```

If you don't have a requirements.txt file, you can use:

```bash
pip install PyQt6 yt-dlp ffmpeg-python
```

#### 4. Install FFmpeg

##### Windows

1. Download FFmpeg for Windows from the [FFmpeg download page](https://ffmpeg.org/download.html)
2. Extract the ZIP file and add the files from the `bin` folder to your system path:
   - Right-click on 'This PC' or 'My Computer' and select 'Properties'
   - Click on 'Advanced system settings'
   - Click on 'Environment Variables'
   - Under System Variables, find and select 'Path', then click 'Edit'
   - Click 'New' and add the path to the FFmpeg bin folder (e.g., `C:\ffmpeg\bin`)
   - Click 'OK' to save all changes

Alternatively, you can copy the FFmpeg executable files (ffmpeg.exe, ffprobe.exe) directly into your application folder.

##### Linux

```bash
sudo apt update
sudo apt install ffmpeg
```

##### macOS

```bash
brew install ffmpeg
```

## Development Setup

If you plan to work on the YouTube Downloader source code, follow these additional steps:

1. Install development dependencies:

```bash
pip install pylint pytest black
```

2. Set up pre-commit hooks (optional):

```bash
pip install pre-commit
pre-commit install
```

3. Run tests to ensure everything is working:

```bash
pytest tests/
```

## Building an Executable

To create a standalone executable that can be run without Python installed:

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Create the executable

#### Basic command

```bash
pyinstaller --onefile --windowed --name ytdownloader src/main.py
```

#### Advanced command with icon and additional data

```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico --add-data "assets;assets" --name ytdownloader src/main.py
```

These commands will create a `dist` folder containing your executable file.

### 3. Add FFmpeg to your distribution

If you're distributing the application to users who might not have FFmpeg installed:

1. Download FFmpeg binaries for the target platform
2. Place the FFmpeg executable files in the same directory as your application executable
3. Alternatively, use the `--add-binary` option with PyInstaller to include FFmpeg:

```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico --add-data "assets;assets" --add-binary "path/to/ffmpeg.exe;." --name ytdownloader src/main.py
```

### 4. Test the executable

Make sure to test the executable on a clean system without Python or dependencies installed to verify it works correctly.

## Usage

### Running from Source

To start the application from source code:

```bash
python src/main.py
```

### Running the Executable

Simply double-click the `ytdownloader.exe` (Windows) or `ytdownloader` (Linux/macOS) executable file.

### Step-by-Step Download Process

1. Enter a YouTube video or playlist URL in the URL field
2. Select "Video" or "Audio" option
3. Choose your desired quality
   - For video: 240p, 360p, 480p, 720p, or 1080p
   - For audio: 96kbps, 128kbps, 192kbps, or 320kbps
4. Check "Download as playlist" option if needed (for playlists)
5. Change the save location if needed by clicking the "Browse" button
6. Click the "DOWNLOAD" button
7. Track the download status from the progress bar
8. Once complete, you can find your files in the selected download location

## Project Structure

```
ytdownloader/
├── src/                  # Source code
│   ├── main.py           # Main application entry
│   ├── __init__.py       # Package identifier
│   ├── core/             # Core functionality
│   │   ├── downloader.py # YouTube download operations
│   │   └── __init__.py   # Package identifier
│   └── ui/               # User interface
│       ├── main_window.py # Main window class
│       └── __init__.py    # Package identifier
├── assets/               # Images and icon files
├── dist/                 # Distribution files (created by PyInstaller)
├── build/                # Build files (created by PyInstaller)
├── tests/                # Test files
├── requirements.txt      # Project dependencies
├── LICENSE               # License information
└── README.md             # This file
```

## Technologies

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - User interface framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube download functionality
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [PyInstaller](https://www.pyinstaller.org/) - Executable creation

## Troubleshooting

### Common Issues

#### FFmpeg not found

Error: `FFmpeg not found. Please make sure FFmpeg is installed and in your PATH.`

Solution:

1. Make sure FFmpeg is installed correctly
2. Verify FFmpeg is in your system PATH by running `ffmpeg -version` in your terminal
3. If using the executable version, ensure FFmpeg binaries are in the same folder as the application

#### Download fails

Error: `Error downloading video: HTTP Error 403: Forbidden`

Solution:

1. Make sure you have a stable internet connection
2. The video might be age-restricted or private
3. Try updating yt-dlp: `pip install --upgrade yt-dlp`

#### Application crashes on startup

Solution:

1. Check if all dependencies are installed correctly
2. Ensure you're using a compatible Python version
3. Try running from the command line to see error messages: `./ytdownloader.exe` or `./ytdownloader`

### Reporting Issues

If you encounter any issues not listed here, please report them on the [Issues](https://github.com/yourusername/ytdownloader/issues) page with:

1. A detailed description of the problem
2. Steps to reproduce the issue
3. Your operating system and application version

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

### Setting Up for Development

1. Fork this repository
2. Clone your fork: `git clone https://github.com/your-username/ytdownloader.git`
3. Create a virtual environment and install dependencies (see [Development Setup](#development-setup))
4. Create a new feature branch: `git checkout -b new-feature`
5. Make your changes
6. Run tests: `pytest tests/`
7. Commit your changes: `git commit -am 'Add new feature'`
8. Push your branch: `git push origin new-feature`
9. Create a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Write unit tests for new features
- Document your code with docstrings
- Keep the UI consistent with the existing design

## Contact

For questions or suggestions, please contact [your email address] or open an issue on GitHub.
