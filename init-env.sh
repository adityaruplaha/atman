echo "Creating fresh Virtual Environment... (this might take a while)"
rm -r ./env
python -m venv --clear ./env
echo "Activating Virtual Environment..."
source ./env/bin/activate
echo "Virtual Environment active."
echo "Python Path: $(which python)"
echo "PIP Path: $(which pip)"
echo "If the path doesn't look right, stop this script in the next 5 seconds."
sleep 5
echo "Execution not stopped."
echo "Installing requirements..."
pip install --use-feature=2020-resolver -r requirements.txt
echo "Done. Run 'source ./env/bin/activate' to activate Virtual Environment."
echo "Run 'python -m attendance_manager' in Virtual Environment to run program."
