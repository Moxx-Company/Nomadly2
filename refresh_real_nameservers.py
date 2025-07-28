#!/usr/bin/env python3
"""
Script to refresh real nameserver information from OpenProvider
and update the database with accurate nameserver data.
"""

import asyncio
import sys
from apis.production_openprovider import OpenProviderAPI
from database import get_db_manager
import json


def get_real_nameservers(domain_name):
    """Get real nameservers from OpenProvider API"""
    try:
        op_api = OpenProviderAPI()

        # Get nameservers from OpenProvider
        nameservers = op_api.get_nameservers(domain_name)

        if nameservers:
            print(f"✅ Real nameservers for {domain_name}:")
            for i, ns in enumerate(nameservers, 1):
                print(f"   NS{i}: {ns}")
            return nameservers
        else:
            print(f"❌ Could not retrieve nameservers for {domain_name}")
            return None

    except Exception as e:
        print(f"❌ Error getting nameservers for {domain_name}: {e}")
        return None


def update_database_nameservers(domain_name, real_nameservers):
    """Update database with real nameserver information"""
    try:
        db_manager = get_db_manager()

        # Convert nameservers to JSON format for database
        nameservers_json = json.dumps(real_nameservers)

        # Determine nameserver mode based on the nameservers
        if any("cloudflare.com" in ns for ns in real_nameservers):
            mode = "cloudflare"
        elif any(
            "registrar" in ns.lower() or "openprovider" in ns.lower()
            for ns in real_nameservers
        ):
            mode = "registrar"
        else:
            mode = "custom"

        # Update database
        session = db_manager.get_session()
        try:
            from models.domain_models import RegisteredDomain

            domain_record = (
                session.query(RegisteredDomain)
                .filter_by(domain_name=domain_name)
                .first()
            )

            if domain_record:
                old_nameservers = domain_record.nameservers
                old_mode = domain_record.nameserver_mode

                domain_record.nameservers = nameservers_json
                domain_record.nameserver_mode = mode
                session.commit()

                print(f"✅ Database updated for {domain_name}")
                print(f"   Old: {old_nameservers} (mode: {old_mode})")
                print(f"   New: {nameservers_json} (mode: {mode})")
                return True
            else:
                print(f"❌ Domain {domain_name} not found in database")
                return False

        except Exception as e:
            session.rollback()
            print(f"❌ Database update failed: {e}")
            return False
        finally:
            session.close()

    except Exception as e:
        print(f"❌ Error updating database for {domain_name}: {e}")
        return False


def refresh_domain_nameservers(domain_name):
    """Complete refresh of domain nameserver information"""
    print(f"🔄 Refreshing nameserver information for {domain_name}")
    print("=" * 50)

    # Get real nameservers from OpenProvider
    real_nameservers = get_real_nameservers(domain_name)

    if real_nameservers:
        # Update database with real information
        success = update_database_nameservers(domain_name, real_nameservers)

        if success:
            print(f"🎉 Successfully refreshed nameservers for {domain_name}")
            return True
        else:
            print(f"❌ Failed to update database for {domain_name}")
            return False
    else:
        print(f"❌ Could not retrieve real nameservers for {domain_name}")
        return False


def main():
    """Main function"""
    if len(sys.argv) > 1:
        domain_name = sys.argv[1]
    else:
        domain_name = "nomadly11.sbs"

    print(f"🏴‍☠️ Nameserver Refresh Tool")
    print(f"Domain: {domain_name}")
    print("=" * 50)

    success = refresh_domain_nameservers(domain_name)

    if success:
        print("\n✅ Nameserver refresh completed successfully")
        print("The bot will now show accurate nameserver information")
    else:
        print("\n❌ Nameserver refresh failed")
        print("Check the error messages above for details")


if __name__ == "__main__":
    main()
