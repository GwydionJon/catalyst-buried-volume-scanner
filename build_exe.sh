pip install .
cd web_ui
pyinstaller launch_app.spec

cd ..
pip install -e .
./web_ui/dist/launch_app.exe
