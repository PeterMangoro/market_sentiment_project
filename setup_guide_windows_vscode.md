# Market Sentiment Analysis Project - Windows & VS Code Setup Guide

This guide will help you set up the Market Sentiment Analysis project on your Windows computer using Visual Studio Code (VS Code).

## Prerequisites

1.  **Python:** Ensure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/). During installation, make sure to check the box that says "Add Python to PATH". We used Python 3.11 in this project.
2.  **VS Code:** Download and install VS Code from [code.visualstudio.com](https://code.visualstudio.com/).
3.  **Git (Recommended):** While not strictly necessary for running the provided files, Git is useful for version control if you plan to expand the project. Download it from [git-scm.com](https://git-scm.com/).

## Setup Steps

1.  **Download and Extract Project Files:**
    *   You will receive a `market_sentiment_project.zip` file.
    *   Create a new folder on your computer where you want to store the project (e.g., `C:\Users\YourUser\Documents\DataProjects`).
    *   Extract the contents of `market_sentiment_project.zip` into this new folder. You should now have a `market_sentiment_project` subfolder containing all project files (data, scripts, notebooks, etc.).

2.  **Open Project in VS Code:**
    *   Open VS Code.
    *   Go to `File > Open Folder...` and select the `market_sentiment_project` folder you just extracted.

3.  **Set Up a Virtual Environment (Highly Recommended):**
    *   Open the terminal in VS Code (`View > Terminal` or `Ctrl+\`).
    *   Navigate to your project directory if you are not already there (e.g., `cd C:\Users\YourUser\Documents\DataProjects\market_sentiment_project`).
    *   Create a virtual environment: `python -m venv .venv`
    *   Activate the virtual environment:
        *   On Windows (PowerShell): `.venv\Scripts\Activate.ps1`
        *   On Windows (Command Prompt): `.venv\Scripts\activate.bat`
    *   VS Code might prompt you to select this environment as the interpreter for the workspace. If so, agree. Otherwise, you can select it manually by clicking on the Python version in the bottom-left corner of VS Code and choosing your `.venv` interpreter.

4.  **Install Required Python Libraries:**
    *   Ensure your virtual environment is activated (you should see `(.venv)` at the beginning of your terminal prompt).
    *   Install the libraries listed in `requirements.txt`:
        `pip install -r requirements.txt`

5.  **Configure API Key:**
    *   In the `market_sentiment_project` folder, you will find a file named `api_keys.py`.
    *   Open this file in VS Code.
    *   Replace the placeholder API token for Marketaux with your actual API key:
        `MARKETAUX_API_KEY = "YOUR_MARKETAUX_API_KEY_HERE"`
    *   Save the file.

6.  **Verify NLTK Data (VADER Lexicon):**
    *   The sentiment analysis script (`scripts/perform_sentiment_analysis.py`) attempts to download the NLTK VADER lexicon if it's not found. When you run it for the first time, it might take a moment to download this.

7.  **Running the Scripts:**
    *   You can now run the Python scripts step-by-step as we did previously. It is generally recommended to run them from the project root directory (`market_sentiment_project`) or ensure your VS Code terminal is in that directory.
    *   **Example: Running the news fetching script:**
        *   Open a new terminal in VS Code (ensure the virtual environment is active).
        *   Navigate to the `scripts` directory: `cd scripts`
        *   Run the script: `python fetch_marketaux_news.py`
        *   Similarly, you can run `fetch_twitter_data.py` (note: this script uses an internal API that was available in our sandbox; it might not work directly on your local machine without adjustments or access to a similar Twitter API service), `fetch_stock_data.py`, `perform_sentiment_analysis.py`, etc.

8.  **Database Setup (SQLite):**
    *   The script `create_db.py` (located in the project root after extraction) will create a SQLite database file named `market_sentiment.db` in the same directory when executed.
    *   Run it from the project root: `python create_db.py`
    *   To interact with the SQLite database, you can use Python scripts (as we will do for populating it) or a SQLite browser tool (e.g., "DB Browser for SQLite").

9.  **Populating the Database and Further Steps:**
    *   Follow the project plan to populate the database, perform EDA, modeling, and create visualizations using Tableau.
    *   The `advanced_modeling.py` script will train models and save some output plots.

## Troubleshooting Tips

*   **Python not found:** Ensure Python is added to your system PATH during installation, or you are using the full path to the python executable.
*   **ModuleNotFoundError:** Make sure your virtual environment is activated and you have installed all packages from `requirements.txt`.
*   **API Key Issues:** Double-check that your Marketaux API key is correctly placed in `api_keys.py` and is active.
*   **File Paths:** Windows uses backslashes (`\`) for paths, while Python scripts often use forward slashes (`/`). Python usually handles this well, but be mindful if you modify paths manually.
*   **VS Code Python Interpreter:** Ensure VS Code is using the Python interpreter from your virtual environment. You can select it by clicking the Python version in the status bar (bottom left) or using the `Python: Select Interpreter` command from the Command Palette (`Ctrl+Shift+P`).

Let me know if you have any questions or run into any issues!

