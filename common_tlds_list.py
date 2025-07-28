#!/usr/bin/env python3
"""
Common Top-Level Domains List
"""

def display_tld_categories():
    """Display categorized list of common TLDs"""
    
    print("🌐 COMPREHENSIVE TOP-LEVEL DOMAINS LIST")
    print("=" * 50)
    
    # Generic TLDs (gTLDs)
    generic_tlds = [
        "com", "net", "org", "info", "biz", "name", "pro", "mobi", 
        "travel", "museum", "aero", "coop", "int", "edu", "gov", "mil"
    ]
    
    # Country Code TLDs (ccTLDs) - Popular ones
    country_tlds = [
        "us", "uk", "ca", "au", "de", "fr", "it", "es", "nl", "be",
        "ch", "at", "dk", "se", "no", "fi", "ie", "pt", "gr", "pl",
        "ru", "ua", "cz", "sk", "hu", "ro", "bg", "hr", "si", "lt",
        "lv", "ee", "is", "mt", "cy", "lu", "li", "mc", "sm", "va",
        "jp", "cn", "kr", "in", "th", "sg", "my", "ph", "id", "vn",
        "tw", "hk", "mo", "mn", "kz", "uz", "kg", "tj", "tm", "af",
        "pk", "bd", "lk", "np", "bt", "mv", "mm", "la", "kh", "bn",
        "mx", "br", "ar", "cl", "pe", "co", "ve", "ec", "bo", "py",
        "uy", "gf", "sr", "gy", "fk", "gs", "za", "eg", "ma", "dz",
        "tn", "ly", "sd", "et", "ke", "tz", "ug", "rw", "bi", "mg",
        "mu", "mz", "zw", "bw", "na", "sz", "ls", "mw", "zm", "ao"
    ]
    
    # New Generic TLDs (New gTLDs)
    new_gtlds = [
        "app", "dev", "tech", "online", "store", "shop", "buy", "sale",
        "website", "site", "web", "blog", "news", "media", "tv", "video",
        "photo", "pics", "gallery", "art", "design", "studio", "agency",
        "company", "business", "work", "career", "jobs", "team", "group",
        "community", "social", "network", "chat", "email", "cloud", "host",
        "server", "domains", "zone", "link", "click", "download", "file",
        "data", "digital", "cyber", "software", "codes", "systems", "solutions",
        "services", "support", "help", "center", "guide", "tips", "how",
        "wiki", "review", "feedback", "survey", "vote", "poll", "forum",
        "club", "group", "team", "family", "kids", "baby", "love", "dating",
        "wedding", "party", "fun", "game", "play", "toy", "sport", "fit",
        "health", "medical", "doctor", "hospital", "clinic", "pharmacy", "care",
        "food", "restaurant", "cafe", "bar", "kitchen", "recipe", "cooking",
        "travel", "hotel", "holiday", "vacation", "tour", "trip", "flight",
        "car", "auto", "bike", "boat", "house", "home", "garden", "land",
        "city", "town", "country", "world", "global", "international", "local",
        "money", "finance", "bank", "credit", "loan", "insurance", "tax",
        "law", "legal", "attorney", "lawyer", "court", "justice", "government",
        "education", "school", "university", "college", "course", "training",
        "book", "library", "music", "movie", "film", "theater", "show"
    ]
    
    # Premium/Specialty TLDs
    premium_tlds = [
        "ai", "io", "co", "me", "tv", "fm", "am", "ly", "gl", "gg",
        "crypto", "nft", "blockchain", "bitcoin", "eth", "dao", "defi",
        "luxury", "vip", "diamond", "gold", "silver", "rich", "wealth",
        "xxx", "sex", "adult", "porn", "casino", "bet", "poker", "game"
    ]
    
    # Geographic TLDs
    geographic_tlds = [
        "london", "nyc", "tokyo", "paris", "berlin", "madrid", "rome",
        "sydney", "melbourne", "toronto", "vancouver", "miami", "vegas",
        "asia", "africa", "eu", "cat", "gal", "scot", "wales", "irish"
    ]
    
    categories = [
        ("🏛️ GENERIC TLDs (gTLDs)", generic_tlds),
        ("🌍 COUNTRY CODE TLDs (ccTLDs)", country_tlds[:40]),  # Show first 40
        ("🚀 NEW GENERIC TLDs", new_gtlds[:60]),  # Show first 60
        ("💎 PREMIUM/SPECIALTY TLDs", premium_tlds),
        ("📍 GEOGRAPHIC TLDs", geographic_tlds)
    ]
    
    for category_name, tld_list in categories:
        print(f"\n{category_name} ({len(tld_list)} shown):")
        print("-" * 50)
        
        # Display in columns
        for i, tld in enumerate(tld_list):
            if i % 8 == 0 and i > 0:
                print()  # New line every 8 TLDs
            print(f".{tld:<8}", end=" ")
        print("\n")
    
    print(f"📊 TOTAL SHOWN: {sum(len(cat[1]) for cat in categories)} TLDs")
    print(f"📝 NOTE: There are 1000+ TLDs available globally")
    print(f"💰 Pricing varies significantly by TLD and registrar")

if __name__ == "__main__":
    display_tld_categories()