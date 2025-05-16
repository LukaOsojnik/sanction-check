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

3. Install dependencies

pip install -r requirements.txt

python main.py

# Create an .exe with pyinstaller

1. Make sure the virtual environment is activated

pyinstaller myapp.spec