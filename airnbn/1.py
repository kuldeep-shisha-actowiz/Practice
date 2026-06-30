import json
import re

# ==========================================
# HELPER EXTRACTION FUNCTIONS
# ==========================================

def get_nested(data, path, default=None):
    """Safely traverses deeply nested dictionaries and lists."""
    for key in path:
        if isinstance(data, dict) and key in data:
            data = data[key]
        elif isinstance(data, list) and isinstance(key, int) and 0 <= key < len(data):
            data = data[key]
        else:
            return default
    return data

def extract_digits(text_string):
    """Filters out any characters except numbers from strings (for prices, night counts)."""
    if not text_string:
        return None
    digits = "".join(re.findall(r'\d+', str(text_string)))
    return int(digits) if digits else None

def extract_languages_from_text(html_text):
    """Parses a string containing list of languages and returns them as a clean Python list."""
    if not html_text:
        return []
    match = re.search(r"with\s+([^.\n]+?)\s+languages?", html_text, re.IGNORECASE)
    if not match:
        match = re.search(r"([^.\n]+?)\s+languages?", html_text, re.IGNORECASE)
        
    if match:
        languages_block = match.group(1)
        raw_langs = re.split(r',|\band\b', languages_block)
        cleaned_langs = [lang.replace("language", "").strip() for lang in raw_langs if lang.strip()]
        return [lang for lang in cleaned_langs if lang]
    return []


# ==========================================
# MODULAR PARSING FUNCTIONS
# ==========================================

def parse_property_and_base(j3_base):
    sections = get_nested(j3_base, ["data", "presentation", "stayProductDetailPage", "sections", "sections"], [])
    breadcrumbs = next((s["section"]["breadcrumbs"] for s in sections if get_nested(s, ["section", "breadcrumbs"])), [])
    location_sec = next((s["section"] for s in sections if get_nested(s, ["section", "lat"])), {})

    return {
        "listing_id": get_nested(j3_base, ["data", "presentation", "stayProductDetailPage", "sections", "metadata", "loggingContext", "eventDataLogging", "listingId"]),
        "listing_url": get_nested(j3_base, ["data", "presentation", "stayProductDetailPage", "sections", "metadata", "seoFeatures", "ogTags", "ogUrl"]),
        "property": {
            "property_name": get_nested(j3_base, ["data", "node", "pdpPresentation", "title", "content", "source"]),
            "property_type": get_nested(j3_base, ["data", "node", "pdpPresentation", "sharingConfig", "propertyType"]),
            "city": get_nested(breadcrumbs, [3, "title"]),
            "state": get_nested(breadcrumbs, [2, "title"]),
            "country": get_nested(breadcrumbs, [1, "title"]),
            "address": location_sec.get("subtitle"),
            "latitude": location_sec.get("lat"),
            "langitude": location_sec.get("lng")
        }
    }


def parse_property_details(j2_pdp):
    overview_items = get_nested(j2_pdp, ["sbuiData", "sectionConfiguration", "root", "sections", 1, "sectionData", "overviewItems"], [])
    return {
        "guest_capacity": get_nested(overview_items, [0, "title"]),
        "bedrooms": get_nested(overview_items, [1, "title"]),
        "beds": get_nested(overview_items, [2, "title"]),
        "bathrooms": get_nested(overview_items, [3, "title"])
    }


def parse_ratings(j1_node, j2_pdp):
    rating_avg = get_nested(j1_node, ["listingRatingStats", "overallRatingStats", "ratingAverage"])
    logging_ctx = get_nested(j2_pdp, ["metadata", "loggingContext", "eventDataLogging"], {})
    
    return {
        "rating": rating_avg,
        "review_count": rating_avg,
        "guest_favourite": False,
        "category_ratings": {
            "Cleanliness": logging_ctx.get("cleanlinessRating"),
            "Accuracy": logging_ctx.get("accuracyRating"),
            "Check-in": logging_ctx.get("checkinRating"),
            "Communication": logging_ctx.get("communicationRating"),
            "Location": logging_ctx.get("locationRating"),
            "Value": logging_ctx.get("valueRating")
        }
    }


def parse_host(j3_base, j2_pdp):
    sections = get_nested(j3_base, ["data", "presentation", "stayProductDetailPage", "sections", "sections"], [])
    host_sec = next((s["section"] for s in sections if get_nested(s, ["section", "cardData"])), {})
    card_data = host_sec.get("cardData", {})
    
    stats_list = card_data.get("stats", [])
    hosting_since = get_nested(stats_list, [2, "value"])

    host_id = get_nested(j2_pdp, ["sbuiData", "sectionConfiguration", "root", "sections", 2, "loggingData", "eventData", "pdpContext", "hostId"])
    host_profile_url = f"https://www.airbnb.co.in/users/show/{host_id}" if host_id else None

    host_details = host_sec.get("hostDetails", [])
    response_rate, response_time = "", ""
    
    for detail in host_details:
        detail_str = str(detail).strip()
        if "Response rate:" in detail_str:
            response_rate = detail_str.replace("Response rate:", "").strip()
        elif "Responds" in detail_str:
            response_time = detail_str.replace("Responds", "").strip()

    return {
        "host_name": card_data.get("name"),
        "host_type": card_data.get("titleText"),
        "hosting_year_since": hosting_since,
        "superhost": "superhost" in str(card_data.get("titleText")).lower(),
        "host_profile_url": host_profile_url,
        "host_image": card_data.get("profilePictureUrl"),
        "response_rate": response_rate,
        "response_time": response_time,
        "host_highlights": [h.get("title") for h in host_sec.get("hostHighlights", []) if h.get("title")],
        "co_hosts": [c.get("name") for c in host_sec.get("cohosts", []) if c.get("name")]
    }


def parse_pricing(j1, j2_pdp):
    sections = j2_pdp.get("sections", [])
    price_line = next((s["section"]["structuredDisplayPrice"]["primaryLine"] for s in sections if get_nested(s, ["section", "structuredDisplayPrice"])), {})
    pill_title = next((s["section"]["initialPill"]["title"] for s in sections if get_nested(s, ["section", "initialPill"])), "")

    discounted_price = extract_digits(price_line.get("discountedPrice"))
    stay_nights = extract_digits(price_line.get("qualifier"))

    if discounted_price is not None and stay_nights and stay_nights > 0:
        price_per_night = round(discounted_price / stay_nights)
    else:
        price_per_night = discounted_price if discounted_price else 0

    currency = None
    if isinstance(j1, dict):
        target_key = next((k for k in j1.keys() if "core-guest-spa" in k), None)
        if target_key:
            currency = get_nested(j1, [target_key, 4, 1, "serverDeterminedCurrency"])
        elif "root" in j1 and isinstance(j1["root"], dict):
            target_key = next((k for k in j1["root"].keys() if "core-guest-spa" in k), None)
            currency = get_nested(j1["root"], [target_key, 4, 1, "serverDeterminedCurrency"])

    return {
        "currency": currency,
        "original_price": extract_digits(price_line.get("originalPrice")),
        "discounted_price": discounted_price,
        "price_per_night": price_per_night,  
        "stay_nights": stay_nights,
        "includes_fees": "include" in pill_title.lower()
    }


def parse_images(j3_base):
    edges = get_nested(j3_base, ["data", "node", "pdpPresentation", "heroMedia", "edges"], [])
    cover_image = get_nested(edges, [0, "node", "image", "uri"])
    
    gallery_images = []
    for edge in edges:
        img_url = get_nested(edge, ["node", "image", "moderatedUri"]) or get_nested(edge, ["node", "image", "uri"])
        if img_url and img_url not in gallery_images:
            gallery_images.append(img_url)

    return {
        "cover_image": cover_image,
        "gallery_images": gallery_images,
        "total_images": len(gallery_images)
    }


def parse_house_rules(j2_pdp):
    sections = j2_pdp.get("sections", [])
    hr_sec = next((s["section"] for s in sections if get_nested(s, ["section", "houseRules"])), {})
    hrs_sec = next((s["section"] for s in sections if get_nested(s, ["section", "houseRulesSections"])), {})
    
    rules_list = hr_sec.get("houseRules", [])
    section_items = get_nested(hrs_sec, ["houseRulesSections", 1, "items"], [])
    
    smoking_str = get_nested(section_items, [5, "title"], "")
    parties_str = get_nested(section_items, [3, "title"], "")

    return {
        "checkin_time": get_nested(rules_list, [0, "title"]),
        "checkout_time": get_nested(rules_list, [1, "title"]),
        "pets_allowed": hr_sec.get("petsAllowed", False),
        "smoking_allowed": False if "no" in smoking_str.lower() else True,
        "parties_allowed": False if "no" in parties_str.lower() else True
    }


def parse_loops_and_lists(j3_base):
    sections = get_nested(j3_base, ["data", "presentation", "stayProductDetailPage", "sections", "sections"], [])
    
    amenities_groups = get_nested(j3_base, ["data", "node", "pdpPresentation", "amenities", "seeAllAmenitiesGroups"], [])
    amenities = [item["title"] for g in amenities_groups for item in g.get("amenities", []) if item.get("title")]

    arrange_sec = next((s["section"]["arrangementDetails"] for s in sections if get_nested(s, ["section", "arrangementDetails"])), [])
    bedroom_details = [{"room": rm.get("title"), "configuration": rm.get("subtitle")} for rm in arrange_sec]

    highlights_list = get_nested(j3_base, ["data", "node", "pdpPresentation", "highlights"], [])
    highlights = [{
        "title": hl.get("headline", {}).get("localizedContent"),
        "description": hl.get("body", {}).get("localizedContent")
    } for hl in highlights_list]

    safety_sec = next((s["section"]["previewSafetyAndProperties"] for s in sections if get_nested(s, ["section", "previewSafetyAndProperties"])), [])
    safety_features = [item.get("title") for item in safety_sec if item.get("title")]

    lang_html_text = next((get_nested(s, ["section", "items", 3, "html", "htmlText"]) for s in sections if get_nested(s, ["section", "items", 3, "html", "htmlText"])), "")
    languages = extract_languages_from_text(lang_html_text)

    # LOOP LOGIC ADDED: Scrapes all dictionary items inside reviewTags list dynamically
    review_tags_list = get_nested(j3_base, ["data", "node", "pdpPresentation", "quality", "reviewTags"], [])
    review_tags = [{
        "title": tag.get("name"),
        "count": tag.get("count")
    } for tag in review_tags_list if tag.get("name")]

    return {
        "amenities": amenities,
        "bedroom_details": bedroom_details,
        "highlights": highlights,
        "safety_features": safety_features,
        "languages": languages,
        "review_tags": review_tags
    }


# ==========================================
# MAIN ORCHESTRATION ENGINE
# ==========================================

def run_scraper(json1_path, json2_path, json3_path):
    with open(json1_path, 'r', encoding='utf-8') as f: j1 = json.load(f)
    with open(json2_path, 'r', encoding='utf-8') as f: j2 = json.load(f)
    with open(json3_path, 'r', encoding='utf-8') as f: j3 = json.load(f)

    j1_node = get_nested(j1, ["root", 4, 1, 4, 1, "data", "node"])
    j2_pdp = get_nested(j2, ["data", "presentation", "stayProductDetailPage", "sections"])
    j3_base = get_nested(j3, ["niobeClientData", 0, 1])

    base_data = parse_property_and_base(j3_base)
    loop_data = parse_loops_and_lists(j3_base)
    
    final_output = {
        "listing_id": base_data["listing_id"],
        "listing_url": base_data["listing_url"],
        "property": base_data["property"],
        "property_details": parse_property_details(j2_pdp),
        "ratings": parse_ratings(j1_node, j2_pdp),
        "host": parse_host(j3_base, j2_pdp),
        "pricing": parse_pricing(j1, j2_pdp),
        "images": parse_images(j3_base),
        "amenities": loop_data["amenities"],
        "bedroom_details": loop_data["bedroom_details"],
        "description": get_nested(j3_base, ["data", "node", "pdpPresentation", "descriptions", "shortDescriptionHtml", "content", "source"]),
        "house_rules": parse_house_rules(j2_pdp),
        "cancellation_policy": get_nested(j3_base, ["data", "presentation", "stayProductDetailPage", "sections", "metadata", "bookingPrefetchData", "cancellationPolicies", 0, "book_it_module_tooltip"]),
        "reviews": [],
        "nearby_places": [],
        "highlights": loop_data["highlights"],
        "languages": loop_data["languages"],
        "review_tags": loop_data["review_tags"],  # Output field integrated
        "property_features": [],
        "safety_features": loop_data["safety_features"],
        "availability": {
            "available": True
        }
    }
    
    return final_output

if __name__ == "__main__":
    extracted_json = run_scraper(
        r"D:\Practice\airnbn\airbnb_1.json", 
        r"D:\Practice\airnbn\airbnb_2.json", 
        r"D:\Practice\airnbn\airbnb_3.json"
    )
    
    with open("final_scraped_data.json", "w", encoding="utf-8") as out_file:
        json.dump(extracted_json, out_file, indent=4, ensure_ascii=False)
        
    print("Scraping completed! Integrated review tracking tag loops.")