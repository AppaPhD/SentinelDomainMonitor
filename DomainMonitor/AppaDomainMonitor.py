import json
import logging
import os
import datetime
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient
from modules.get_whois import domain_whois
from config.config import DOMAIN_LIST, DOMAIN_LOGS, BASE, AZURE_CONFIG
import modules.azure_logging as LogToAzure
from modules.custom_functions import *

AZURE_STORAGE_ACCOUNT = AZURE_CONFIG['AZURE_STORAGE_ACCOUNT']
AZURE_STORAGE_BLOB_NAME = AZURE_CONFIG['AZURE_STORAGE_BLOB_NAME']
AZURE_STORAGE_CONTAINER = AZURE_CONFIG['AZURE_STORAGE_CONTAINER']

logger = logging.getLogger(DOMAIN_LOGS['logger'])

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


#start with fetching
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
        print(f"Domain List Downloaded Successfully to: {download_file_path}")
    except Exception as err:
        logger.error(f"Error downloading domains list: {err}")
        json_log = json.dumps([{'event_type': 'script_status', 'status': f'Error downloading domains list: {err}'}])
        print(json_log)
        exit(1)
    
    # read in the domains from file
    domains = read_domains_from_file("domains.txt")
    logger.info(f"Read in domains: {domains}")
    for domain in domains:
        logger.info(f"Starting workflow for original domain: {domain}")
        #run dnstwist for permutations ONLY
        dnstwist_output = run_dnstwist(domain)
        #if dnstwist succeeds, run it through dnsX to filter out unresolvable domains
        if dnstwist_output:
            dnsx_output = run_dnsx(dnstwist_output)
            if dnsx_output:
                #if successful, get whois and dns record info
                resolved_domains = dnsx_output.split('\n')
                for rd in resolved_domains:
                    whoisinfo = domain_whois(rd)
                    whoisinfo['original_domain'] = domain
                    json_results = json.dumps(whoisinfo)
                    
                    #log results to azure
                    logger.info(f"POST requesting details to Azure: {rd}..")
                    LogToAzure.post_data(json_results)
            else:
                print("Failed to run dnsx.")
                logger.info(f"Failed to run dnsx on {domain}.")
        else:
            logger.info(f"Failed to run dnstwist on {domain}.")

    logger.info(f"Appa-DomainMonitor Ran successfully!!")


