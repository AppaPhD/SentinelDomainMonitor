import logging
import dns.resolver
import whois

from config.config import DOMAIN_LOGS

logger = logging.getLogger(DOMAIN_LOGS['logger'])

def resolve_dns_record(domain, record_type):
        try:
            records = dns.resolver.resolve(domain, record_type)
            return [str(record) for record in records]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.exception.DNSException) as e:
            return ["not found"]

def domain_whois(domain):
    """ enrich domains with WHOIS info """
    whois_results = {}
    whois_results['domain'] = domain
    iso8601 = '%Y-%m-%dT%H:%M:%S.%fZ'
    try:
        w = whois.whois(f'{domain}')
        if isinstance(w.creation_date, list):
            whois_results['creation_date'] = str(w.creation_date[0].strftime(iso8601))
        else:
            whois_results['creation_date'] = str(w.creation_date.strftime(iso8601))

        if isinstance(w.updated_date, list):
            whois_results['updated_date'] = str(w.updated_date[0].strftime(iso8601))
        else:
            whois_results['updated_date'] = str(w.updated_date.strftime(iso8601))

        if isinstance(w.expiration_date, list):
            whois_results['expiration_date'] = str(w.expiration_date[0].strftime(iso8601))
        else:
            whois_results['expiration_date'] = str(w.expiration_date.strftime(iso8601))

        whois_results['emails'] = str(w.emails)
        whois_results['registrar'] = str(w.registrar)

    except Exception as err:
        logger.error(f"Error getting WHOIS for domain '{domain}': {err}")

    # DNS lookups for NS, A, MX, AAAA records
    try:
        ns_records = resolve_dns_record(domain,'NS')
        a_records = resolve_dns_record(domain,'A')
        mx_records = resolve_dns_record(domain,'MX')
        aaaa_records = resolve_dns_record(domain,'AAAA')

        whois_results['ns_records'] = str([str(record) for record in ns_records])
        whois_results['a_records'] = str([str(record) for record in a_records])
        whois_results['mx_records'] = str([str(record) for record in mx_records])
        whois_results['aaaa_records'] = str([str(record) for record in aaaa_records])
    except Exception as e:
        whois_results['dns_error'] = str(e)

    return whois_results
