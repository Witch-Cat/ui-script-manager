## Description
This Python application allows you to drag and drop Python scripts (`.py` files) into the GUI. The scripts are then executed in the background, and you can manage them (e.g., stop or remove) through the interface.

## Installation
1. **Install Python**: Ensure you have Python 3.x installed on your system. You can download it from [python.org](https://www.python.org/).

2. **Install Required Libraries**:
   - Open a terminal or command prompt.
   - Run the following command to install `tkinterdnd2`:
     ```bash
     pip install tkinterdnd2
     ```

## Running the Application
1. **Save the Script**: Save the provided Python code into a file named `script_runner.py`.

2. **Run the Script**:
   - Open a terminal or command prompt.
   - Navigate to the directory where `script_runner.py` is saved.
   - Run the script using the following command:
     ```bash
     python script_runner.py
     ```

3. **Using the Application**:
   - Drag and drop Python files (`.py`) into the application window.
   - The scripts will be executed in the background.
   - You can stop or remove scripts using the interface.

## Notes
- The application saves the list of scripts to a file named `stored_scripts.pkl` in the same directory as the script.
- Ensure you have the necessary permissions to execute scripts and access the file system and could be restarted on startup.
