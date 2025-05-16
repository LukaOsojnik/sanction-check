A simple Python application that can be run from a virtual environment or packaged into a standalone .exe using PyInstaller.

📁 Repository Contents

    main.py – Entry point of the application

    requirements.txt – List of required Python libraries

    myapp.spec – PyInstaller configuration file
    
# Run main.py

1. Clone the repository

git clone https://github.com/your-username/myapp.git

cd myapp

2. Create a virtual environment

source /path/to/venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Run main.py

python main.py

# Create an .exe with pyinstaller

1. Make sure the virtual environment is activated

source /path/to/venv/bin/activate

2. Run pyinstaller on spec

pyinstaller myapp.spec