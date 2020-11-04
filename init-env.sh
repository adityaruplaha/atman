echo "Creating Virtual Environment... (this might take a while)"
python -m venv --clear ./env
echo "Activating Virtual Environment..."
source ./env/bin/activate
echo "Installing requirements..."
pip install -r requirements.txt
echo "Done. Run 'source ./env/bin/activate' to activate Virtual Environment."
echo "Run 'python -m attendance_manager' in Virtual Environment to run program."
