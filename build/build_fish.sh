source ../.venv/bin/activate.fish

# generate executable
python -m PyInstaller --onefile --windowed --name cazam ../src/main.py
cp -r ../src/shaders dist

# generate zip file
cp -r dist cazam
zip -r cazam.zip cazam/cazam cazam/shaders
rm -rf cazam