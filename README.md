A simple Python application that can be run from a virtual environment or packaged into a standalone .exe using PyInstaller.

📁 Repository Contents

    main.py – Entry point of the application

    requirements.txt – List of required Python libraries

    myapp.spec – PyInstaller configuration file
    

🔧 Setting Up the Virtual Environment

1. Clone the repository

git clone https://github.com/your-username/myapp.git

cd myapp

2. Create a virtual environment

For Windows:

python -m venv venv

venv\Scripts\activate

For Linux/macOS:

python3 -m venv venv

source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

🚀 Running the Application

With the virtual environment activated:

python main.py

.EXE FILE

🛠️ Building an .exe File

If you'd like to create a standalone Windows executable:

1. Make sure the virtual environment is activated

venv\Scripts\activate   # On Windows

# or

source venv/bin/activate  # On Linux/macOS

2. Run PyInstaller with the spec file

pyinstaller myapp.spec