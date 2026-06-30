# import json

# # --- Extraction Helper Functions ---

# def get_basic_info(property_data):
#     """Extracts basic property info: ID, name, rating, and type."""
#     summary = property_data.get("content", {}).get("informationSummary", {})
#     return {
#         "propertyId": property_data.get("propertyId"),
#         "name": summary.get("displayName"),
#         "starRating": summary.get("rating"),
#         "propertyType": summary.get("propertyType"),
#     }

# def get_address(property_data):
#     """Extracts address details with proper safety fallbacks."""
#     summary = property_data.get("content", {}).get("informationSummary", {})
#     address_data = summary.get("address", {})
    
#     return {
#         "area": address_data.get("area", {}).get("name"),
#         "city": address_data.get("city", {}).get("name"),
#         "distanceFromCityCenter_km": None  # Set default placeholder or numeric type if available
#     }

# def get_reviews(property_data):
#     """Extracts review scores and counts from the first review element."""
#     reviews_list = property_data.get("content", {}).get("reviews", {}).get("contentReview", [])
#     if reviews_list and isinstance(reviews_list, list):
#         cumulative = reviews_list[0].get("cumulative", {})
#         return {
#             "score": cumulative.get("score"),
#             "count": cumulative.get("reviewCount")
#         }
#     return {"score": None, "count": None}

# def get_all_images(property_data):
#     """Extracts ALL image URLs for this hotel into a single flat list."""
#     images_list = property_data.get("content", {}).get("images", {}).get("hotelImages", [])
#     all_urls = []
    
#     if isinstance(images_list, list):
#         for img in images_list:
#             urls = img.get("urls", [])
#             if urls and isinstance(urls, list):
#                 # Grabs the first resolution URL structure provided for each image item
#                 url_val = urls[0].get("value")
#                 if url_val:
#                     all_urls.append(url_val)
                    
#     return all_urls

# def get_pricing_and_cancellation(property_data):
#     """Extracts room pricing matrices and cancellation policy types."""
#     offers = property_data.get("pricing", {}).get("offers", [])
    
#     pricing_info = {
#         "currency": None, 
#         "crossedOutPrice": None, 
#         "displayPrice": None, 
#         "discountPercent": None
#     }
#     cancellation_type = None
    
#     if offers and isinstance(offers, list):
#         room_offers = offers[0].get("roomOffers", [])
#         if room_offers and isinstance(room_offers, list):
#             room = room_offers[0].get("room", {})
            
#             # Extract cancellation
#             cancellation_type = room.get("payment", {}).get("cancellation", {}).get("cancellationType")
            
#             # Extract pricing details
#             pricing_list = room.get("pricing", [])
#             if pricing_list and isinstance(pricing_list, list):
#                 pricing = pricing_list[0]
#                 exc_price = pricing.get("price", {}).get("perRoomPerNight", {}).get("exclusive", {})
                
#                 pricing_info = {
#                     "currency": pricing.get("currency"),
#                     "crossedOutPrice": exc_price.get("crossedOutPrice"),
#                     "displayPrice": exc_price.get("display"),
#                     "discountPercent": pricing.get("price", {}).get("totalDiscount")
#                 }
                
#     return pricing_info, cancellation_type

# def get_property_url(property_data):
#     """Safely builds the absolute canonical Agoda property URL."""
#     base_url = "https://www.agoda.com/en-in/"
#     summary = property_data.get("content", {}).get("informationSummary", {})
#     page_path = summary.get("propertyLinks", {}).get("propertyPage", "")
    
#     if page_path:
#         return base_url + str(page_path).lstrip('/')
#     return base_url


# # --- Main Orchestrator Function ---

# def transform_hotel_data(json_file_path):
#     """Reads Agoda JSON source file and formats it to match your custom target schema."""
#     try:
#         with open(json_file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#     except FileNotFoundError:
#         print(f"Error: The file at path '{json_file_path}' was not found.")
#         return []
#     except json.JSONDecodeError:
#         print("Error: Failed to parse file. Make sure it contains valid JSON.")
#         return []
        
#     # Fixed Path: Unwraps the root GraphQL object using data.get("data")
#     properties = data.get("data", {}).get("citySearch", {}).get("properties", [])
    
#     if not properties:
#         print("Warning: No properties found under path 'data.citySearch.properties'.")
#         return []
    
#     extracted_properties = []
    
#     for prop in properties:
#         basic = get_basic_info(prop)
#         address = get_address(prop)
#         reviews = get_reviews(prop)
#         images = get_all_images(prop)
#         pricing, cancellation = get_pricing_and_cancellation(prop)
#         property_url = get_property_url(prop)
        
#         # Structure the payload exactly according to your requested schema
#         extracted_hotel = {
#             "propertyId": basic["propertyId"],
#             "name": basic["name"],
#             "starRating": basic["starRating"],
#             "propertyType": basic["propertyType"],
#             "address": address,
#             "review": reviews,
#             "images": images,  # All extracted image URLs combined into a single flat list
#             "price": pricing,
#             "coupon": {
#                 "code": None,
#                 "amountOff": None
#             },
#             "badges": [],
#             "soldOut": None,
#             "onlyXLeft": None,
#             "bookingActivity": {
#                 "count": None,
#                 "timeFrame": None
#             },
#             "freeCancellation": cancellation,
#             "propertyPage": property_url
#         }
#         extracted_properties.append(extracted_hotel)
        
#     return extracted_properties


# # --- Execution Block ---
# if __name__ == "__main__":
#     # Point this to your local source JSON file path
#     file_path = r"D:\Practice\Hotel_agoda\agoda.json"
    
#     final_data = transform_hotel_data(file_path)
    
#     if final_data:
#         # Prints out your newly formatted hotel schema data
#         print(json.dumps(final_data, indent=2))
#     else:
#         print("The returned dataset is empty. Check your input JSON file schema structure.")






import json
import re
import os


# --- Extraction Helper Functions ---

def get_basic_info(property_data):
    """Extracts basic property info: ID, name, rating, and type."""
    summary = (property_data.get("content") or {}).get("informationSummary") or {}
    return {
        "propertyId": property_data.get("propertyId"),
        "name": summary.get("displayName"),
        "starRating": summary.get("rating"),
        "propertyType": summary.get("propertyType"),
    }

def get_address(property_data):
    """Extracts address details with proper safety fallbacks."""
    summary = (property_data.get("content") or {}).get("informationSummary") or {}
    address_data = summary.get("address") or {}
    
    return {
        "area": (address_data.get("area") or {}).get("name"),
        "city": (address_data.get("city") or {}).get("name")
    }

def get_reviews(property_data):
    """Extracts review scores and counts from the contentReview collection."""
    cumulative = (property_data.get("content") or {}).get("reviews") or {}
    reviews_list = cumulative.get("contentReview", [])
    if reviews_list and isinstance(reviews_list, list):
        cum_data = reviews_list[0].get("cumulative") or {}
        return {
            "score": cum_data.get("score"),
            "count": cum_data.get("reviewCount")
        }
    return {"score": None, "count": None}

def get_all_images(property_data):
    """Extracts ALL image URLs for this hotel into a single flat list."""
    images_list = (property_data.get("content") or {}).get("images") or {}
    hotel_images = images_list.get("hotelImages", [])
    all_urls = []
    
    if isinstance(hotel_images, list):
        for img in hotel_images:
            urls = img.get("urls", [])
            if urls and isinstance(urls, list):
                url_val = urls[0].get("value")
                if url_val.startswith("//"):
                    all_urls.append("https:" + url_val)
                if url_val.startswith("http://") or url_val.startswith("https://"):
                    all_urls.append(url_val)
                    
    return all_urls

def get_pricing_and_offers(property_data):
    """
    Extracts pricing metrics, cancellation rules, coupon flags, 
    and targets your exact path configuration for room availability.
    """
    offers = (property_data.get("pricing") or {}).get("offers", [])
    
    pricing_info = {
        "currency": None, 
        "crossedOutPrice": None, 
        "displayPrice": None, 
        "discountPercent": None
    }
    cancellation_type = None
    coupon_data = {"code": None, "amountOff": None}
    sold_out = None
    only_x_left = None
    
    if offers and isinstance(offers, list):
        room_offers = offers[0].get("roomOffers", [])
        if room_offers and isinstance(room_offers, list):
            room_node = room_offers[0].get("room") or {}
            
            # 1. Cancellation Extract
            cancellation_type = (room_node.get("payment") or {}).get("cancellation") or {}
            if isinstance(cancellation_type, dict):
                cancellation_type = cancellation_type.get("cancellationType")
            
            # 2. YOUR TARGET CONFIGURATION: availableRooms Parsing
            avail_rooms = room_node.get("availableRooms")
            if avail_rooms is not None:
                # If available rooms is 0, then it's sold out
                sold_out = True if avail_rooms == 0 else False
                # If there's a limited number of rooms left, populate onlyXLeft
                only_x_left = avail_rooms
            
            # 3. Dynamic Coupon Text Scraper
            msg_formatted = (room_node.get("pricingMessages") or {}).get("formatted", [])
            if msg_formatted and isinstance(msg_formatted, list):
                for msg in msg_formatted:
                    texts = msg.get("texts", [])
                    if texts and isinstance(texts, list):
                        raw_text = texts[0].get("text", "")
                        if "Coupon Code" in raw_text:
                            code_match = re.search(r"<b>(.*?)</b>", raw_text)
                            amt_match = re.search(r"Rs\.\s*([\d,]+)", raw_text)
                            
                            coupon_data["code"] = code_match.group(1) if code_match else None
                            if amt_match:
                                coupon_data["amountOff"] = float(amt_match.group(1).replace(",", ""))

            # 4. Exclusive Price Metrics Matrix
            pricing_list = room_node.get("pricing", [])
            if pricing_list and isinstance(pricing_list, list):
                pricing = pricing_list[0] or {}
                exc_price = ((pricing.get("price") or {}).get("perRoomPerNight") or {}).get("exclusive") or {}
                
                pricing_info = {
                    "currency": pricing.get("currency"),
                    "crossedOutPrice": exc_price.get("crossedOutPrice"),
                    "displayPrice": exc_price.get("display"),
                    "discountPercent": str((pricing.get("price") or {}).get("totalDiscount"))+'%'
                }
                
    return pricing_info, cancellation_type, coupon_data, sold_out, only_x_left

def get_enrichment_data(property_data):
    """Safely extracts badges and history elements from the enrichment tracking node."""
    enrichment = property_data.get("enrichment") or {}
    
    # Extract structural badges array
    badges = (enrichment.get("pricingBadges") or {}).get("badges", [])
    if not isinstance(badges, list):
        badges = []
        
    # Extract real-time booking history metrics 
    booking_history = (enrichment.get("bookingHistory") or {}).get("bookingCount") or {}
    booking_activity = {
        "count": booking_history.get("count"),
        "timeFrame": booking_history.get("timeFrame")
    }
    
    return badges, booking_activity

def get_property_url(property_data):
    """Safely builds the absolute canonical Agoda property URL."""
    base_url = "https://www.agoda.com/en-in/"
    summary = (property_data.get("content") or {}).get("informationSummary") or {}
    page_path = summary.get("propertyLinks") or {}
    if isinstance(page_path, dict):
        page_path = page_path.get("propertyPage", "")
    
    if page_path:
        return base_url + str(page_path).lstrip('/')
    return base_url


# --- Main Orchestrator Function ---

def transform_hotel_data(json_file_path):
    """Reads Agoda JSON source file and formats it into the complete schema target layout."""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file at path '{json_file_path}' was not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Failed to parse file. Make sure it contains valid JSON.")
        return []
        
    # Target property list path unwrap
    properties = data.get("data", {}).get("citySearch", {}).get("properties", [])
    
    if not properties:
        print("Warning: No properties found under path 'data.citySearch.properties'.")
        return []
    
    extracted_properties = []
    
    for prop in properties:
        basic = get_basic_info(prop)
        address = get_address(prop)
        reviews = get_reviews(prop)
        images = get_all_images(prop)
        pricing, cancellation, coupon, sold_out, only_x_left = get_pricing_and_offers(prop)
        badges, booking_activity = get_enrichment_data(prop)
        property_url = get_property_url(prop)
        
        # Maps variables dynamically into your custom response configuration 
        extracted_hotel = {
            "propertyId": basic["propertyId"],
            "name": basic["name"],
            "starRating": basic["starRating"],
            "propertyType": basic["propertyType"],
            "address": address,
            "review": reviews,
            "images": images,  
            "price": pricing,
            "coupon": coupon,                 
            "badges": badges,                 
            "soldOut": sold_out,             
            "onlyXLeft": only_x_left,         
            "bookingActivity": booking_activity, 
            "freeCancellation": cancellation,
            "propertyPage": property_url
        }
        extracted_properties.append(extracted_hotel)
        
    return extracted_properties

# --- Execution Block ---
if __name__ == "__main__":
    file_path = r"D:\Practice\Hotel_agoda\agoda.json"
    
    final_data = transform_hotel_data(file_path)
    print(len(final_data))
    
    if final_data:
        with open(os.path.join('D:\Practice\Hotel_agoda','Agoda_data_extract.json'),'w',encoding='utf-8') as file:
            json.dump(final_data,file, indent=2)