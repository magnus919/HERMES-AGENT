import subprocess
import json

# Check if the inventory file exists
result = subprocess.run(['ls', '/home/ubuntu/inventory.json'], capture_output=True, text=True)
if result.returncode != 0:
    print('ERROR: inventory.json not found at /home/ubuntu/inventory.json')
    exit(1)

# Check if the workflow script exists
result = subprocess.run(['ls', 'create_workflow.py'], capture_output=True, text=True)
if result.returncode != 0:
    print('ERROR: create_workflow.py not found in current directory')
    exit(1)

# Run the workflow creation script
result = subprocess.run(['python3', 'create_workflow.py'], capture_output=True, text=True)
if result.returncode != 0:
    print('ERROR: Failed to create workflow')
    print(result.stderr)
    exit(1)

print('SUCCESS: Workflow created successfully')