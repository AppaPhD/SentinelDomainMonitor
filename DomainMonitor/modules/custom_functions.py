import subprocess
import dnstwist
import dns.resolver
import logging

from config.config import DOMAIN_LOGS

logger = logging.getLogger(DOMAIN_LOGS['logger'])

def generate_permutations(domain):
    # Run dnstwist to generate domain permutations
    result = dnstwist.run(domain=domain, format='list', output="permu_domains.txt")
    return result

def read_domains_from_file(filename):
    domains = []
    try:
        with open(filename, 'r') as file:
            domains = file.read().splitlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    return domains

def run_dnstwist(domain):
    try:
        # Run dnstwist with the --format list option
        dnstwist_result = subprocess.run(['dnstwist', '--format', 'list', domain], capture_output=True, text=True)
        dnstwist_result.check_returncode()  # Ensure the subprocess ran successfully
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running dnstwist: {e}")
        return None

    return dnstwist_result.stdout.strip()

def run_dnsx(input_data):
    try:
        # Run dnsx with input data from dnstwist
        dnsx_result = subprocess.run(['dnsx'], input=input_data, capture_output=True, text=True)
        # dnsx_result = subprocess.run(['dnsx','-ns','-mx','-a','-aaaa','-j'], input=input_data, capture_output=True, text=True)
        dnsx_result.check_returncode()  # Ensure the subprocess ran successfully
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running dnsx: {e}")
        return None

    return dnsx_result.stdout.strip()

def resolve_dns_record(domain, record_type):
        try:
            records = dns.resolver.resolve(domain, record_type)
            return [str(record) for record in records]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.exception.DNSException) as e:
            return ["not found"]
