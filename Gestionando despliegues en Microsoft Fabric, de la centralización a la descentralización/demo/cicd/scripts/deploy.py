# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import os
from azure.identity import ClientSecretCredential
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items
import argparse

parser = argparse.ArgumentParser(description='Process some variables.')
parser.add_argument('--WorkspaceId', type=str)
parser.add_argument('--Environment', type=str)
parser.add_argument('--RepositoryDirectory', type=str)
parser.add_argument('--ItemTypeInScope', type=str)
args = parser.parse_args()

# Use Azure CLI credential to authenticate
client_id =  os.getenv('clientId')
client_secret = os.getenv('clientSecret')
tenant_id = os.getenv('tenantId')
token_credential = ClientSecretCredential(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)

# Initialize the FabricWorkspace object with the required parameters
target_workspace = FabricWorkspace(
    workspace_id= args.WorkspaceId,
    environment=args.Environment,
    repository_directory=args.RepositoryDirectory,
    item_type_in_scope=json.loads(args.ItemTypeInScope),
    token_credential=token_credential
)

# Publish all items defined in item_type_in_scope
publish_all_items(target_workspace)

# Unpublish all items defined in item_type_in_scope not found in repository
unpublish_all_orphan_items(target_workspace)