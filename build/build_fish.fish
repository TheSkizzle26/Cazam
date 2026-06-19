source ../.venv/bin/activate.fish

# generate executable
python -m PyInstaller --paths=../src --onefile --windowed --name cazam ../src/main.py
cp -r ../src/shaders dist/shaders

# generate zip file
zip -r cazam.zip dist/cazam dist/shaders