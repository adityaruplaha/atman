echo "It is strongly recommended to use this software on a Linux machine."
echo "Creating fresh Virtual Environment... (this might take a while)"
rmdir ./env /s /q
python -m --clear venv ./env
echo "Activating Virtual Environment..."
./env/Scripts/activate.bat
echo "Virtual Environment active."
echo "Installing requirements..."
pip install --use-feature=2020-resolver -r requirements.txt
echo "Done. Run './env/Scripts/activate.bat' to activate Virtual Environment."
echo "Run 'python -m attendance_manager' in Virtual Environment to run program."
