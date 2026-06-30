import json
import re

# Helper function to prevent KeyError/IndexError when extracting deeply nested fields
def get_nested(data, path, default=None):
    for key in path:
        if isinstance(data, dict) and key in data:
            data = data[key]
        elif isinstance(data, list) and isinstance(key, int) and 0 <= key < len(data):
            data = data[key]
        else:
            return default
    return data

def extract_listing_data(json1_path, json2_path, json3_path):
    # Load all 3 files
    with open(r'D:\Practice\airnbn\airbnb_1.json', 'r', encoding='utf-8') as f:
        j1 = json.load(f)
    with open(r'D:\Practice\airnbn\airbnb_2.json', 'r', encoding='utf-8') as f:
        j2 = json.load(f)
    with open(r'D:\Practice\airnbn\airbnb_3.json', 'r', encoding='utf-8') as f:
        j3 = json.load(f)

    # Base references for short paths
    j3_base = get_nested(j3, ["niobeClientData", 0, 1])
    j2_pdp = get_nested(j2, ["data", "presentation", "stayProductDetailPage", "sections"])
    j1_node = get_nested(j1, ["root", 4, 1, 4, 1, "data", "node"])

    # 1. Base details
    listing_id = get_nested(j3_base, ["data", "presentation", "stayProductDetailPage", "sections", "metadata", "loggingContext", "eventDataLogging", "listingId"])
    listing_url = get_nested(j3_base, ["data", "presentation", "stayProductDetailPage", "sections", "metadata", "seoFeatures", "ogTags", "ogUrl"])

    # 2. Property
    p_sec = get_nested(j3_base, ["data", "presentation", "stayProductDetailPage", "sections", "sections"], [])
    sec_9_breadcrumbs = next((s["section"]["breadcrumbs"] for s in p_sec if s.get("section", {}).get("breadcrumbs")), None) or []
    sec_6 = next((s["section"] for s in p_sec if s.get("section", {}).get("lat")), {})

    property_data = {
        "property_name": get_nested(j3_base, ["data", "node", "pdpPresentation", "title", "content", "source"]),
        "property_type": get_nested(j3_base, ["data", "node", "pdpPresentation", "sharingConfig", "propertyType"]),
        "city": get_nested(sec_9_breadcrumbs, [3, "title"]),
        "state": get_nested(sec_9_breadcrumbs, [2, "title"]),
        "country": get_nested(sec_9_breadcrumbs, [1, "title"]),
        "address": sec_6.get("subtitle"),
        "latitude": sec_6.get("lat"),
        "longitude": sec_6.get("lng")
    }

    # 3. Property Details
    overview_items = get_nested(j2_pdp, ["sbuiData", "sectionConfiguration", "root", "sections", 1, "sectionData", "overviewItems"], [])
    property_details = {
        "guest_capacity": get_nested(overview_items, [0, "title"]),
        "bedrooms": get_nested(overview_items, [1, "title"]),
        "beds": get_nested(overview_items, [2, "title"]),
        "bathrooms": get_nested(overview_items, [3, "title"])
    }

    # 4. Ratings
    logging_ctx = get_nested(j2_pdp, ["metadata", "loggingContext", "eventDataLogging"], {})
    rating_avg = get_nested(j1_node, ["listingRatingStats", "overallRatingStats", "ratingAverage"])
    ratings = {
        "rating": rating_avg,
        "review_count": rating_avg,  # Set to map your mapping note
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

    # 5. Host Details & Lists
    sec_7_card = next((s["section"]["cardData"] for s in p_sec if s.get("section", {}).get("cardData")), {})
    sec_7_section = next((s["section"] for s in p_sec if s.get("section", {}).get("hostHighlights")), {})
    
    # Extract response rate and response time logic
    host_details_list = sec_7_section.get("hostDetails", [])
    response_rate, response_time = "", ""
    for item in host_details_list:
        if "%" in item:
            response_rate = item
        elif "hour" in item or "day" in item or "minute" in item:
            response_time = item

    # Host loops
    host_highlights = [h.get("title") for h in sec_7_section.get("hostHighlights", []) if h.get("title")]
    co_hosts = [c.get("name") for c in sec_7_section.get("cohosts", []) if c.get("name")]

    host = {
        "host_name": sec_7_card.get("name"),
        "host_type": sec_7_card.get("titleText"),
        "hosting_since": "",
        "superhost": "superhost" in str(sec_7_card.get("titleText")).lower(),
        "host_profile_url": sec_7_card.get("profilePictureUrl"),
        "host_image": "",
        "response_rate": response_rate,
        "response_time": response_time,
        "host_highlights": host_highlights,
        "co_hosts": co_hosts
    }

    # 6. Pricing & String Sanitization
    j2_sections = j2_pdp.get("sections", [])
    
    # Find original / discounted price sections
    price_sec = next((s["section"]["structuredDisplayPrice"]["primaryLine"] for s in j2_sections if s.get("section", {}).get("structuredDisplayPrice")), {})
    orig_str = price_sec.get("originalPrice")
    disc_str = price_sec.get("discountedPrice")
    qualifier = price_sec.get("qualifier", "")
    
    # Extract only digits from pricing
    original_price = int("".join(re.findall(r'\d+', orig_str)) if orig_str else None)
    discounted_price =int( "".join(re.findall(r'\d+', disc_str)) if disc_str else None)
    stay_nights = int("".join(re.findall(r'\d+', qualifier)) if qualifier else None)

    # Fees parsing
    initial_pill_title = next((s["section"]["initialPill"]["title"] for s in j2_sections if s.get("section", {}).get("initialPill")), "")
    includes_fees = "include" in initial_pill_title.lower()

    pricing = {
        "currency": get_nested(j1, ["root", "core-guest-spa", 2, 1, "serverDeterminedCurrency"]),
        "original_price": original_price,
        "discounted_price": discounted_price,
        "price_per_night": int(discounted_price/stay_nights),
        "stay_nights": stay_nights,
        "includes_fees": includes_fees
    }

    # 7. Images (De-duplicated)
    edges = get_nested(j3_base, ["data", "node", "pdpPresentation", "heroMedia", "edges"], [])
    cover_image = get_nested(edges, [0, "node", "image", "uri"])
    
    gallery_images = []
    for edge in edges:
        m_uri = get_nested(edge, ["node", "image", "moderatedUri"]) or get_nested(edge, ["node", "image", "uri"])
        if m_uri and m_uri not in gallery_images:
            gallery_images.append(m_uri)

    images = {
        "cover_image": cover_image,
        "gallery_images": gallery_images,
        "total_images": len(gallery_images)
    }

    # 8. House Rules ("No" validation)
    hr_sec = next((s["section"] for s in j2_sections if s.get("section", {}).get("houseRules")), {})
    hrs_sec = next((s["section"] for s in j2_sections if s.get("section", {}).get("houseRulesSections")), {})
    
    house_rules_list = hr_sec.get("houseRules", [])
    hr_items = get_nested(hrs_sec, ["houseRulesSections", 1, "items"], [])
    
    smoking_str = get_nested(hr_items, [5, "title"], "")
    parties_str = get_nested(hr_items, [3, "title"], "")

    house_rules = {
        "checkin_time": get_nested(house_rules_list, [0, "title"]),
        "checkout_time": get_nested(house_rules_list, [1, "title"]),
        "pets_allowed": hr_sec.get("petsAllowed", False),
        "smoking_allowed": False if "no" in smoking_str.lower() else True,
        "parties_allowed": False if "no" in parties_str.lower() else True
    }

    # 9. Amenities (Nested Groups Loop)
    amenities_groups = get_nested(j3_base, ["data", "node", "pdpPresentation", "amenities", "seeAllAmenitiesGroups"], [])
    amenities = []
    for group in amenities_groups:
        for item in group.get("amenities", []):
            if item.get("title"):
                amenities.append(item["title"])

    # 10. Description & Cancellation
    description = get_nested(j3_base, ["data", "node", "pdpPresentation", "descriptions", "shortDescriptionHtml", "content", "source"])
    cancel_policies = get_nested(j3_base, ["data", "presentation", "stayProductDetailPage", "sections", "metadata", "bookingPrefetchData", "cancellationPolicies"], [])
    cancellation_policy = get_nested(cancel_policies, [0, "book_it_module_tooltip"])

    # 11. Safety Features Loop
    preview_safety = next((s["section"]["previewSafetyAndProperties"] for s in p_sec if s.get("section", {}).get("previewSafetyAndProperties")), [])
    safety_features = [item.get("title") for item in preview_safety if item.get("title")]

    # Build Complete Output
    final_json = {
        "listing_id": listing_id,
        "listing_url": listing_url,
        "property": property_data,
        "property_details": property_details,
        "ratings": ratings,
        "host": host,
        "pricing": pricing,
        "images": images,
        "house_rules": house_rules,
        "amenities": amenities,
        "description": description,
        "cancellation_policy": cancellation_policy,
        "reviews": [],
        "nearby_places": [],
        "languages": [],
        "property_features": [],
        "safety_features": safety_features
    }

    return final_json

# Execution entry point
if __name__ == "__main__":
    result = extract_listing_data("json1.json", "json2.json", "json3.json")
    
    # Save target output structural file
    with open("extracted_data.json", "w", encoding="utf-8") as out:
        json.dump(result, out, indent=4, ensure_ascii=False)
    print("Extraction completed successfully!")