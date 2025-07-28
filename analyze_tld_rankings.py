#!/usr/bin/env python3
"""
Analyze TLD rankings from domain purchase data
"""

import re
from collections import Counter

def analyze_tld_rankings():
    """Analyze the TLD rankings from the payment data"""
    
    # The domain purchase data from the URL
    domain_data = """
Bank, Domain, eazypay.sbs, $3, 5168006768, onarrival2, Sat Sep 30 2023 08:10:28 GMT+0000 (Coordinated Universal Time)
Bank, Domain, huppa.sbs, $3, 5168006768, onarrival2, Sat Sep 30 2023 08:26:33 GMT+0000 (Coordinated Universal Time)
Bank, Domain, plainote.sbs, $3, 1531772316, onarrival4, Sat Sep 30 2023 19:11:59 GMT+0000 (Coordinated Universal Time)
Bank, Domain, ch5ecure.sbs, $3, 822152954, KvnqSleemJay, Sun Oct 01 2023 13:16:39 GMT+0000 (Coordinated Universal Time)
Bank, Domain, alertfirst.sbs, $3, 5168006768, onarrival2, Sat Sep 30 2023 04:10:08 GMT+0000 (Coordinated Universal Time)
Crypto, Domain, roadsup.sbs, $6, 5168006768, onarrival2, Mon Oct 02 2023 09:00:47 GMT+0000 (Coordinated Universal Time), 0.00022 btc
Crypto, Domain, aualert.sbs, $6, 985329937, Covered77, Mon Oct 02 2023 21:44:45 GMT+0000 (Coordinated Universal Time), 0.00021584 btc
Crypto, Domain, oreguncomcu.sbs, $6, 692738899, stylesjnr, Mon Oct 02 2023 22:07:15 GMT+0000 (Coordinated Universal Time), 9 trc20_usdt
Crypto, Domain, alert-user.us, $7, 466590684, SiD_T2, Tue Oct 03 2023 13:42:24 GMT+0000 (Coordinated Universal Time), 0.10631 ltc
Crypto, Domain, oregommcu.us, $7, 692738899, stylesjnr, Tue Oct 03 2023 14:06:45 GMT+0000 (Coordinated Universal Time), 9 trc20_usdt
Crypto, Domain, s300ftp.us, $7, 5952545024, BUSHCLAN7, Tue Oct 03 2023 16:05:44 GMT+0000 (Coordinated Universal Time), 0.00029136 btc
Crypto,Domain,midqueen.com,$17,5111375913,scubajonsey,Tue Oct 17 2023 12:13:15 GMT+0000 (Coordinated Universal Time),17 trc20_usdt
Crypto,Domain,shorty2.sbs,$6,5642150983,nomadly_private,Thu Oct 19 2023 11:04:01 GMT+0000 (Coordinated Universal Time),9 trc20_usdt
Crypto,Domain,blitly.sbs,$6,5642150983,nomadly_private,Sun Oct 22 2023 16:52:33 GMT+0000 (Coordinated Universal Time),9 trc20_usdt
Crypto,Domain,shortpro.sbs,$6,5642150983,nomadly_private,Wed Oct 25 2023 14:52:29 GMT+0000 (Coordinated Universal Time),9 trc20_usdt
Crypto,Domain,shotly.sbs,$6,5642150983,nomadly_private,Sat Oct 28 2023 19:52:52 GMT+0000 (Coordinated Universal Time),9 trc20_usdt
Crypto,Domain,cold-damper.com,$17,5111375913,scubajonsey,Fri Nov 03 2023 15:47:34 GMT+0000 (Coordinated Universal Time),17 trc20_usdt
Crypto,Domain,auth04-logind.info,$6,6049824137,checkflank,Sat Nov 04 2023 11:16:00 GMT+0000 (Coordinated Universal Time),0.00017359 btc
Crypto,Domain,validateusaa.com,$16.2,1320962105,B0ss_B4by,Mon Nov 06 2023 16:26:03 GMT+0000 (Coordinated Universal Time),0.0004621 btc
Crypto,Domain,verifiedusaa.com,$16.2,1320962105,B0ss_B4by,Tue Nov 07 2023 15:11:09 GMT+0000 (Coordinated Universal Time),0.222686 ltc
Crypto,Domain,fantastic-dom.com,$19,5111375913,scubajonsey,Thu Nov 09 2023 17:42:02 GMT+0000 (Coordinated Universal Time),18 trc20_usdt
Bank, Domain, mykeeslerfcu.com, $17.100361327367605, 6972092754, Yakk000, Sat Nov 11 2023 16:16:22 GMT+0000 (Coordinated Universal Time), ₦19156
Crypto,Domain,shotpro.xyz,$6,1531772316,onarrival4,Fri Nov 17 2023 12:46:11 GMT+0000 (Coordinated Universal Time),9 trc20_usdt
Crypto,Domain,us-post-online.com,$19,1026823617,Nuck_Seller,Mon Nov 27 2023 16:27:50 GMT+0000 (Coordinated Universal Time),0.276535 ltc
Crypto,Domain,secure07b-auth.info,$6,586184142,trillionboy,Mon Dec 18 2023 16:59:31 GMT+0000 (Coordinated Universal Time),0.0862239 ltc
Crypto,Domain,mylogixhelp.com,$19,6777540321,LogsInc,Tue Dec 19 2023 23:36:43 GMT+0000 (Coordinated Universal Time),0.00044916 btc
Crypto,Domain,jpmorganchvse.info,$6,5579814771,TheresaMandosa,Sat Dec 23 2023 00:04:22 GMT+0000 (Coordinated Universal Time),0.00013631 btc
Crypto,Domain,support24u.xyz,$6,586184142,trillionboy,Thu Dec 28 2023 18:44:25 GMT+0000 (Coordinated Universal Time),0.0794222 ltc
Crypto,Domain,support15u.xyz,$6,6092166948,K_Z01,Mon Jan 08 2024 19:50:12 GMT+0000 (Coordinated Universal Time),0.00014938 btc
Crypto,Domain,securewebhuntington.com,$19,2073206501,realwil4,Fri Jan 12 2024 14:49:18 GMT+0000 (Coordinated Universal Time),0.00041858 btc
Crypto,Domain,help14b.info,$6,6092166948,K_Z01,Fri Jan 12 2024 17:41:40 GMT+0000 (Coordinated Universal Time),0.00013848 btc
Crypto,Domain,support23u.info,$6,586184142,trillionboy,Wed Jan 17 2024 19:13:22 GMT+0000 (Coordinated Universal Time),0.0866929 ltc
Bank, Domain, d0cusignonllinedocument.com, $19.810644271956825, 5811788020, hiringad, Wed Jan 17 2024 22:12:48 GMT+0000 (Coordinated Universal Time), ₦24226
Crypto,Domain,auth41a.info,$6,6092166948,K_Z01,Thu Jan 18 2024 13:07:17 GMT+0000 (Coordinated Universal Time),0.00014114 btc
Crypto,Domain,support25u.info,$6,586184142,trillionboy,Thu Jan 18 2024 17:59:00 GMT+0000 (Coordinated Universal Time),0.0864101 ltc
Crypto,Domain,support27u.info,$6,586184142,trillionboy,Fri Jan 19 2024 16:25:03 GMT+0000 (Coordinated Universal Time),0.0862644 ltc
Crypto,Domain,asisb2ha.info,$6,6092166948,K_Z01,Sat Jan 20 2024 14:58:57 GMT+0000 (Coordinated Universal Time),0.00014446 btc
Crypto,Domain,atti21b.info,$6,6092166948,K_Z01,Mon Jan 22 2024 00:25:23 GMT+0000 (Coordinated Universal Time),0.00014426 btc
Crypto,Domain,resul4b1.info,$6,6092166948,K_Z01,Mon Jan 22 2024 22:53:07 GMT+0000 (Coordinated Universal Time),0.00015099 btc
Crypto,Domain,ndbidyyudoohdklbjfgibbfjjkjjtfnjhgjghphfqdhbf.com,$19,6493402961,thisisjustpi007,Fri Jan 26 2024 19:17:31 GMT+0000 (Coordinated Universal Time),19.004 trc20_usdt
Bank, Domain, arvest27.xyz, $5.999777580071175, 2118857467, devospammer, Sat Jan 27 2024 08:37:52 GMT+0000 (Coordinated Universal Time), ₦7553
Bank, Domain, citibksecure.com, $19.064565327910525, 5952043433, murphymedic, Sat Jan 27 2024 08:54:41 GMT+0000 (Coordinated Universal Time), ₦24000
Crypto,Domain,chaseweb.live,$6,586184142,trillionboy,Sat Jan 27 2024 18:
"""
    
    print("🏆 TLD RANKINGS FROM ACTUAL PURCHASE DATA")
    print("=" * 50)
    
    # Extract domains from the data
    domain_pattern = r'Domain,\s*([^,]+),'
    domains = re.findall(domain_pattern, domain_data)
    
    # Extract TLDs
    tlds = []
    for domain in domains:
        domain = domain.strip()
        if '.' in domain:
            tld = domain.split('.')[-1].lower()
            tlds.append(tld)
    
    # Count TLD frequency
    tld_counter = Counter(tlds)
    
    print(f"📊 ANALYSIS OF {len(domains)} DOMAIN PURCHASES:")
    print("-" * 50)
    
    # Rank TLDs by purchase frequency
    ranked_tlds = tld_counter.most_common()
    
    for rank, (tld, count) in enumerate(ranked_tlds, 1):
        percentage = (count / len(tlds)) * 100
        print(f"{rank:>2}. .{tld:<8} - {count:>2} purchases ({percentage:>5.1f}%)")
    
    print(f"\n📈 TOP 3 MOST PURCHASED TLDs:")
    print("-" * 30)
    for i, (tld, count) in enumerate(ranked_tlds[:3], 1):
        percentage = (count / len(tlds)) * 100
        print(f"{i}. .{tld} - {count} purchases ({percentage:.1f}%)")
    
    print(f"\n💡 INSIGHTS:")
    print(f"• Total unique TLDs: {len(ranked_tlds)}")
    print(f"• Most popular: .{ranked_tlds[0][0]} with {ranked_tlds[0][1]} purchases")
    print(f"• Domain purchase price range: $3 - $19+")

if __name__ == "__main__":
    analyze_tld_rankings()