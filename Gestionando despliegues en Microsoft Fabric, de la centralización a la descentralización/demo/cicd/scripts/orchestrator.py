import argparse
import os
import subprocess
import logging
import json
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Orchestrate deployments across multiple workspaces.')
parser.add_argument('--ParentDirectory', type=str, required=True, help='Parent directory')
parser.add_argument('--Environment', type=str, required=True, help='Deployment environment')
args = parser.parse_args()

# Load deployment configuration from environment variable
try:
    config_data = json.loads(os.getenv('deployConfig'))
except json.JSONDecodeError as e:
    logger.error(f"Config file is not valid JSON: {str(e)}")
    sys.exit(1)

for idx, entry in enumerate(config_data, 1):
    
    folder_path = f"{args.ParentDirectory}{entry.get('folder', '').strip()}"
    # Check if folder exists
    if not os.path.isdir(folder_path):
        logger.error(f"Folder not found: {folder_path}. Aborting...")
        sys.exit(1) # Exit if any folder is missing

for idx, entry in enumerate(config_data, 1):
    folder = entry.get('folder', '').strip()
    folder_path = f"{args.ParentDirectory}{folder}"
    workspace_id = entry.get('workspace_id')
    item_types = entry.get('item_types', [])
    
    logger.info(f"Deploying folder {folder} to {workspace_id}")
    
    # Construct the command to call deploy.py
    cmd = [
        "python",
        f"{args.ParentDirectory}/cicd/scripts/deploy.py",
        "--WorkspaceId", workspace_id,
        "--Environment", args.Environment,
        "--RepositoryDirectory", str(folder_path),
        "--ItemTypeInScope", json.dumps(item_types)
    ]
    
    # Execute the deployment command using subprocess
    # Runs in a separate process to deploy the specified folder to the workspace
    # - stdout and stderr are redirected to PIPE and combined (stdout=PIPE, stderr=STDOUT)
    # - text=True ensures output is decoded as string instead of bytes
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    ) as process:
        # Stream output line by line
        for line in process.stdout:
            print(line, end="")
        
        # Wait for the process to complete and get the exit code
        process.wait()
        
        # Validate deployment success based on exit code
        if process.returncode == 0:
            logger.info(f"Successfully deployed folder {folder} to workspace {workspace_id}")
        else:
            # Exit immediately on deployment failure to prevent cascading failures
            logger.error(f"Deployment failed for folder {folder} with exit code {process.returncode}")
            sys.exit(1)

# All deployments succeeded
logger.info("All deployments completed successfully!")
sys.exit(0)