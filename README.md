# 📝 Folder Size Monitor and Alert

![GitHub repo size](https://img.shields.io/github/repo-size/alexandrekatsuura/python-folder-monitor?style=for-the-badge)
![GitHub language count](https://img.shields.io/github/languages/count/alexandrekatsuura/python-folder-monitor?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/alexandrekatsuura/python-folder-monitor?style=for-the-badge)
![Bitbucket open issues](https://img.shields.io/bitbucket/issues/alexandrekatsuura/python-folder-monitor?style=for-the-badge)
![Bitbucket open pull requests](https://img.shields.io/bitbucket/pr-raw/alexandrekatsuura/python-folder-monitor?style=for-the-badge)

## 📚 Academic Use Disclaimer

> ⚠️ This is an academic project created for learning purposes only.
> It is not intended for production use.

## ℹ️ About

This project is a Python application designed to monitor the size of specified folders and alert the user if their size exceeds a predefined limit. It's built to be configurable, allowing users to set monitoring paths and size thresholds. The application aims to provide a simple yet effective way to keep track of disk space usage in critical directories.

## 🚀 Features

*   **Configurable Monitoring Paths**: Easily specify which folders to monitor.
*   **Customizable Size Limits**: Set individual size thresholds for each monitored folder.
*   **Alerting Mechanism**: Notifies the user when a folder's size surpasses its limit.
*   **Command-Line Interface (CLI)**: Simple and interactive, runs in any standard terminal.
*   **Error Handling**: Robust error handling for invalid paths or configurations.
*   **Unit Tested**: Includes a suite of `pytest` tests to verify functionality.
*   **Clean Project Structure**: Organized into `src` and `tests` directories for maintainability.

## 🛠️ Technologies Used

*   **Python 3.x**
*   **`pytest`**: For creating and running unit tests.

## ⚙️ How to Run the Project

### Prerequisites

*   Python 3.x installed on your system.

### Installation

1.  Clone this repository:

    ```bash
    git clone https://github.com/alexandrekatsuura/python-folder-monitor
    cd python-folder-monitor
    ```

2.  (Recommended) Create and activate a virtual environment:

    ```bash
    python -m venv .venv
    source .venv/bin/activate      # On Linux/macOS
    # .venv\\Scripts\\activate       # On Windows
    ```

3.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Usage

To start the folder monitor, run the following command from the project root:

```bash
python src/main.py
```

The application will start monitoring the configured folders. Alerts will be displayed if any folder exceeds its defined size limit.

## ✅ Running the Tests

To run the unit tests, execute the following command from the project root directory:

```bash
pytest -v
```

This command will discover and run all tests located in the `tests/` directory.

## 📁 Project Structure

```bash
python-folder-monitor/
├── src/
│   ├── __init__.py
│   └── folder_monitor.py   # Contains the FolderMonitor class
│   └── main.py             # Contains main execution logic
├── tests/
│   ├── __init__.py
│   └── test_folder_monitor.py # Unit tests for the FolderMonitor class
├── .gitignore              # Standard Python .gitignore
├── README.md               # This documentation file
└── requirements.txt        # Project dependencies
```

## 📄 License

This project is licensed under the [MIT License](LICENSE).



