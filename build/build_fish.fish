source ../.venv/bin/activate.fish

rm -r build/* dist/*

# generate executable
python -m PyInstaller --paths=../src --onefile --windowed --name cazam ../src/main.py
cp -r ../src/shaders dist/shaders

# generate zip file
cp -r dist cazam
rm cazam.zip
zip -r cazam.zip cazam/cazam cazam/shaders
rm -r cazam