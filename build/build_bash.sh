source ../.venv/bin/activate

# generate executable
python -m PyInstaller --onefile --windowed --name cazam ../main.py
cp -r ../shaders dist/

# generate zip file
cp -r dist cazam
zip -r cazam.zip cazam/cazam cazam/shaders
rm -rf cazam