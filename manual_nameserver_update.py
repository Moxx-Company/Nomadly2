#!/usr/bin/env python3
"""
Manual nameserver update tool - allows manual entry of correct nameservers
"""
import sys
import json
from database import DatabaseManager


def update_nameservers_manual(domain, nameservers_input):
    """Update nameservers manually"""
    try:
        # Parse nameservers from input (comma or space separated)
        if "," in nameservers_input:
            nameservers = [ns.strip() for ns in nameservers_input.split(",")]
        else:
            nameservers = nameservers_input.split()

        # Clean nameservers (remove trailing dots)
        nameservers = [ns.rstrip(".") for ns in nameservers if ns.strip()]

        if not nameservers:
            print("❌ No valid nameservers provided")
            return False

        print(f"✅ Parsed {len(nameservers)} nameservers:")
        for i, ns in enumerate(nameservers, 1):
            print(f"  {i}. {ns}")

        # Determine nameserver mode
        if any("cloudflare" in ns.lower() for ns in nameservers):
            mode = "cloudflare"
        elif any(
            "openprovider" in ns.lower() or "nameword" in ns.lower()
            for ns in nameservers
        ):
            mode = "registrar"
        else:
            mode = "custom"

        # Update database
        db = DatabaseManager()
        nameservers_json = json.dumps(nameservers)

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

            if cursor.rowcount == 0:
                print(f"❌ Domain {domain} not found in database")
                return False

            conn.commit()

        print(f"✅ Updated database with {len(nameservers)} nameservers")
        print(f"✅ Nameserver mode set to: {mode}")
        return True

    except Exception as e:
        print(f"❌ Update failed: {e}")
        return False


def main():
    """Main function"""
    print(f"🏴‍☠️ Manual Nameserver Update Tool")
    print("=" * 50)

    if len(sys.argv) < 2:
        print("Usage: python manual_nameserver_update.py <domain> [nameservers]")
        print(
            "Example: python manual_nameserver_update.py nomadly11.sbs 'ns1.example.com, ns2.example.com'"
        )
        print("Or run interactively:")

        domain = input("Enter domain name: ").strip()
        nameservers = input("Enter nameservers (comma separated): ").strip()
    else:
        domain = sys.argv[1]
        if len(sys.argv) > 2:
            nameservers = sys.argv[2]
        else:
            nameservers = input(
                f"Enter nameservers for {domain} (comma separated): "
            ).strip()

    if not nameservers:
        print("❌ No nameservers provided")
        return

    print(f"Domain: {domain}")
    print(f"Nameservers: {nameservers}")
    print("-" * 50)

    success = update_nameservers_manual(domain, nameservers)

    if success:
        print("\n✅ Nameserver update completed successfully")
        print("Restart the bot to see updated nameserver information")
    else:
        print("\n❌ Nameserver update failed")


if __name__ == "__main__":
    main()
