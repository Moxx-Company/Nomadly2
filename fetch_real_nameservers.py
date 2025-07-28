#!/usr/bin/env python3
"""
Fetch real nameservers for domains using DNS queries
"""
import sys
import socket
import dns.resolver
import dns.query
import dns.message
from database import DatabaseManager


def get_nameservers_via_dns(domain):
    """Get nameservers for a domain using DNS queries"""
    try:
        # Query NS records for the domain
        result = dns.resolver.resolve(domain, "NS")
        nameservers = []

        for ns in result:
            nameservers.append(str(ns).rstrip("."))

        return nameservers
    except Exception as e:
        print(f"DNS query failed: {e}")
        return None


def get_nameservers_via_whois_servers(domain):
    """Get nameservers by querying root nameservers"""
    try:
        # Get TLD from domain
        tld = domain.split(".")[-1]

        # Query root nameservers for TLD nameservers
        root_ns = dns.resolver.resolve(f"{tld}.", "NS")

        for ns in root_ns:
            try:
                # Query TLD nameserver for domain nameservers
                ns_ip = str(dns.resolver.resolve(str(ns), "A")[0])
                query = dns.message.make_query(domain, dns.rdatatype.NS)
                response = dns.query.udp(query, ns_ip, timeout=5)

                nameservers = []
                for answer in response.answer:
                    if answer.rdtype == dns.rdatatype.NS:
                        for item in answer:
                            nameservers.append(str(item).rstrip("."))

                if nameservers:
                    return nameservers

            except Exception as e:
                print(f"Failed to query {ns}: {e}")
                continue

        return None
    except Exception as e:
        print(f"Whois server query failed: {e}")
        return None


def update_domain_nameservers_in_db(domain, nameservers):
    """Update domain nameservers in database"""
    try:
        db = DatabaseManager()

        # Convert nameservers list to JSON string format
        import json

        nameservers_json = json.dumps(nameservers)

        # Determine nameserver mode
        if any("cloudflare" in ns.lower() for ns in nameservers):
            mode = "cloudflare"
        else:
            mode = "custom"

        # Update database
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE registered_domains 
                SET nameservers = %s, nameserver_mode = %s 
                WHERE domain_name = %s
            """,
                (nameservers_json, mode, domain),
            )
            conn.commit()

        print(f"✅ Updated database with {len(nameservers)} nameservers")
        return True

    except Exception as e:
        print(f"❌ Database update failed: {e}")
        return False


def fetch_and_update_nameservers(domain):
    """Main function to fetch real nameservers and update database"""
    print(f"🔍 Fetching real nameservers for {domain}")
    print("=" * 50)

    # Try DNS query first
    nameservers = get_nameservers_via_dns(domain)

    if not nameservers:
        print("📡 Direct DNS query failed, trying TLD nameserver query...")
        nameservers = get_nameservers_via_whois_servers(domain)

    if nameservers:
        print(f"✅ Found {len(nameservers)} nameservers:")
        for i, ns in enumerate(nameservers, 1):
            print(f"  {i}. {ns}")

        # Update database
        success = update_domain_nameservers_in_db(domain, nameservers)
        return success
    else:
        print(f"❌ Could not retrieve nameservers for {domain}")
        return False


def main():
    """Main function"""
    if len(sys.argv) > 1:
        domain_name = sys.argv[1]
    else:
        domain_name = "nomadly11.sbs"

    print(f"🏴‍☠️ Real Nameserver Fetch Tool")
    print(f"Domain: {domain_name}")
    print("=" * 50)

    success = fetch_and_update_nameservers(domain_name)

    if success:
        print("\n✅ Nameserver fetch and update completed successfully")
        print("The bot will now show accurate nameserver information")
    else:
        print("\n❌ Nameserver fetch failed")
        print("Check the error messages above for details")


if __name__ == "__main__":
    main()
