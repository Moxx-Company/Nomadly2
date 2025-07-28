#!/usr/bin/env python3
"""
Investigate checktat-atoocol.info domain management issues
Check database records, OpenProvider status, and Cloudflare integration
"""

import logging
from database import get_db_manager
from apis.production_openprovider import OpenProviderAPI
from apis.cloudflare import CloudflareAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def investigate_checktat_domain():
    """Comprehensive investigation of checktat-atoocol.info domain issues"""
    domain_name = "checktat-atoocol.info"
    logger.info(f"🔍 Investigating domain: {domain_name}")
    
    db = get_db_manager()
    
    # 1. Database Investigation
    logger.info("=" * 60)
    logger.info("1. DATABASE INVESTIGATION")
    logger.info("=" * 60)
    
    try:
        # Check registered_domains table
        domains = db.get_registered_domains()
        matching_domains = [d for d in domains if domain_name in str(d.domain_name)]
        
        if matching_domains:
            for domain in matching_domains:
                logger.info(f"✅ Domain found in database:")
                logger.info(f"   ID: {domain.id}")
                logger.info(f"   Domain: {domain.domain_name}")
                logger.info(f"   User ID: {domain.user_id}")
                logger.info(f"   OpenProvider ID: {domain.openprovider_domain_id}")
                logger.info(f"   Cloudflare Zone: {domain.cloudflare_zone_id}")
                logger.info(f"   Nameserver Mode: {domain.nameserver_mode}")
                logger.info(f"   Nameservers: {domain.nameservers}")
                logger.info(f"   Created: {domain.created_at}")
                
                # Check user information
                if domain.user_id:
                    user = db.get_user_by_id(domain.user_id)
                    if user:
                        logger.info(f"   User: {user.telegram_id} ({user.username})")
                    else:
                        logger.info(f"   User: Not found for ID {domain.user_id}")
        else:
            logger.error(f"❌ Domain {domain_name} not found in database")
            return
            
    except Exception as e:
        logger.error(f"❌ Database investigation failed: {e}")
        return
    
    # 2. OpenProvider Investigation
    logger.info("\n" + "=" * 60)
    logger.info("2. OPENPROVIDER INVESTIGATION")
    logger.info("=" * 60)
    
    domain_record = matching_domains[0]
    
    try:
        openprovider = OpenProviderAPI()
        
        if domain_record.openprovider_domain_id:
            logger.info(f"🔍 Checking OpenProvider domain ID: {domain_record.openprovider_domain_id}")
            
            # Check domain status
            domain_info = openprovider.get_domain_info(domain_record.openprovider_domain_id)
            
            if domain_info:
                logger.info(f"✅ OpenProvider domain found:")
                logger.info(f"   Status: {domain_info.get('status')}")
                logger.info(f"   Expiry: {domain_info.get('expiry_date')}")
                logger.info(f"   Nameservers: {domain_info.get('nameservers', [])}")
                logger.info(f"   Auto-renew: {domain_info.get('auto_renew')}")
            else:
                logger.error(f"❌ OpenProvider domain not found for ID {domain_record.openprovider_domain_id}")
                
        else:
            logger.error(f"❌ No OpenProvider domain ID in database record")
            
    except Exception as e:
        logger.error(f"❌ OpenProvider investigation failed: {e}")
    
    # 3. Cloudflare Investigation
    logger.info("\n" + "=" * 60)
    logger.info("3. CLOUDFLARE INVESTIGATION")
    logger.info("=" * 60)
    
    try:
        cloudflare = CloudflareAPI()
        
        if domain_record.cloudflare_zone_id:
            logger.info(f"🔍 Checking Cloudflare zone ID: {domain_record.cloudflare_zone_id}")
            
            # Check zone status
            zone_info = cloudflare.get_zone_info(domain_record.cloudflare_zone_id)
            
            if zone_info:
                logger.info(f"✅ Cloudflare zone found:")
                logger.info(f"   Name: {zone_info.get('name')}")
                logger.info(f"   Status: {zone_info.get('status')}")
                logger.info(f"   Nameservers: {zone_info.get('name_servers', [])}")
                
                # Check DNS records
                dns_records = cloudflare.get_dns_records(domain_record.cloudflare_zone_id)
                if dns_records:
                    logger.info(f"   DNS Records: {len(dns_records)} found")
                    for record in dns_records[:5]:  # Show first 5 records
                        logger.info(f"     {record.get('type')} {record.get('name')} -> {record.get('content')}")
                else:
                    logger.info(f"   DNS Records: None found")
                    
            else:
                logger.error(f"❌ Cloudflare zone not found for ID {domain_record.cloudflare_zone_id}")
                
        else:
            logger.error(f"❌ No Cloudflare zone ID in database record")
            
    except Exception as e:
        logger.error(f"❌ Cloudflare investigation failed: {e}")
    
    # 4. Potential Issues Analysis
    logger.info("\n" + "=" * 60)
    logger.info("4. POTENTIAL ISSUES ANALYSIS")
    logger.info("=" * 60)
    
    issues_found = []
    recommendations = []
    
    # Check for missing OpenProvider ID
    if not domain_record.openprovider_domain_id or domain_record.openprovider_domain_id == "already_registered":
        issues_found.append("Missing or invalid OpenProvider domain ID")
        recommendations.append("Update database with correct OpenProvider domain ID")
    
    # Check for missing Cloudflare zone
    if not domain_record.cloudflare_zone_id:
        issues_found.append("Missing Cloudflare zone ID")
        recommendations.append("Create or link Cloudflare zone for domain")
    
    # Check nameserver mode consistency
    if domain_record.nameserver_mode == "cloudflare" and not domain_record.cloudflare_zone_id:
        issues_found.append("Nameserver mode is 'cloudflare' but no zone ID present")
        recommendations.append("Either create Cloudflare zone or switch to registrar nameservers")
    
    if issues_found:
        logger.info("❌ Issues found:")
        for issue in issues_found:
            logger.info(f"   • {issue}")
            
        logger.info("\n💡 Recommendations:")
        for rec in recommendations:
            logger.info(f"   • {rec}")
    else:
        logger.info("✅ No obvious configuration issues found")
    
    # 5. Summary
    logger.info("\n" + "=" * 60)
    logger.info("5. INVESTIGATION SUMMARY")
    logger.info("=" * 60)
    
    logger.info(f"Domain: {domain_name}")
    logger.info(f"Database Record: {'✅' if matching_domains else '❌'}")
    logger.info(f"OpenProvider ID: {domain_record.openprovider_domain_id or 'Missing'}")
    logger.info(f"Cloudflare Zone: {domain_record.cloudflare_zone_id or 'Missing'}")
    logger.info(f"Nameserver Mode: {domain_record.nameserver_mode or 'Not set'}")
    logger.info(f"Issues Found: {len(issues_found)}")
    
    return {
        "domain_record": domain_record,
        "issues_found": issues_found,
        "recommendations": recommendations
    }

if __name__ == "__main__":
    investigate_checktat_domain()