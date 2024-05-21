# this is the first step in the DomainMonitoring process. This program fetches domains from domains.txt from the azure storage account
#!/usr/bin/env python3

import os
import json
import logging
import datetime
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

# Configurations
from config.config import BASE, AZURE_CONFIG

# Logger configuration
logger = logging.getLogger("DomainMonitorLogger")

AZURE_STORAGE_ACCOUNT = AZURE_CONFIG['AZURE_STORAGE_ACCOUNT']
AZURE_STORAGE_BLOB_NAME = AZURE_CONFIG['AZURE_STORAGE_BLOB_NAME']
AZURE_STORAGE_CONTAINER = AZURE_CONFIG['AZURE_STORAGE_CONTAINER']

def _logger():
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(os.path.join(BASE, 'domain_monitor.log'))
    fh.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s [%(process)d] - %(levelname)s - %(message)s',
                                  "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)

if __name__ == "__main__":
    start_time = datetime.datetime.now()
    _logger()
    logger.info("Starting DomainMonitor...")

    try:
        account_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url, credential=ManagedIdentityCredential())
        container_client = blob_service_client.get_container_client(container=AZURE_STORAGE_CONTAINER)
    except Exception as err:
        logger.error(f"Error connecting to Azure Storage: {err}")
        json_log = json.dumps([{'event_type': 'script_status', 'status': f'Error connecting to Azure Storage: {err}'}])
        print(json_log)
        exit(1)

    download_file_path = os.path.join(os.getcwd(), 'domains.txt')

    try:
        # Download domains list from storage account
        with open(file=download_file_path, mode="wb") as download_file:
            download_file.write(container_client.download_blob(AZURE_STORAGE_BLOB_NAME).readall())

        logger.info(f"Domains list downloaded successfully to {download_file_path}")
    except Exception as err:
        logger.error(f"Error downloading domains list: {err}")
        json_log = json.dumps([{'event_type': 'script_status', 'status': f'Error downloading domains list: {err}'}])
        print(json_log)
        exit(1)

    delta = datetime.datetime.now() - start_time
    logger.info(f"Processing took {delta.total_seconds()} seconds")
    json_log = json.dumps([{'event_type': 'script_status', 'status': f'Script completed and took {delta.total_seconds()} seconds'}])
    print(json_log)
