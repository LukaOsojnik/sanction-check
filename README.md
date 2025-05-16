Python app for comparing names in bulk size against EU list of sanctioned people.

Techniques for comparison - normalization, tokenization, rapid fuzz (library for string matching).

📁 Repository Contents

    clients.csv - Example of what .csv file should look like

    main.py – Entry point of the application

    requirements.txt – List of required Python libraries

    myapp.spec – PyInstaller configuration file

# CSV file explaination

 - app takes coulmn "IME" and seperates it into "name" and "surname" parameters saving the last string as name and the rest as surname
    
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