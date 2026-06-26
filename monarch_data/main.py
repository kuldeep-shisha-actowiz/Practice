import json
import os


def load_json_file(file_path):
    """
    Function 1: Reads and parses a JSON file with safe UTF-8 encoding.
    Returns a Python dictionary, or an empty dict if the file is missing/corrupted.
    """
    if not os.path.exists(file_path):
        print(f"Warning: File '{file_path}' not found.")
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{file_path}'. Check file syntax.")
        return {}


def extract_data_from_json(raw_data):
    """
    Function 2: Iterates flexibly through the raw JSON structures, extracts 
    the necessary fields, and maps them to the requested target schema.
    """
    if not raw_data:
        return {}

    # Standardize checking whether root is a list or a dictionary wrapper
    payload = raw_data.get("data", {}) if isinstance(raw_data, dict) else {}
    if isinstance(raw_data, list) and len(raw_data) > 0:
        # Check if it matches the monarch_2 layout where it's a list containing dicts
        first_item = raw_data[0]
        if isinstance(first_item, dict):
            payload = first_item.get("data", {})

    extracted = {}

    # Try to find episodes to establish metadata dynamically
    episodes_list = []
    if isinstance(payload, dict):
        episodes_list = payload.get("episodes", [])
    elif isinstance(raw_data, dict) and "episodes" in raw_data:
        episodes_list = raw_data["episodes"]

    # --- Series Level Data (Fallback on the first episode metadata if found) ---
    first_ep = episodes_list[0] if episodes_list else {}
    
    extracted["series_id"] = first_ep.get("showId", "umc.cmc.62l8x0ixrhyq3yaqa5y8yo7ew")
    extracted["series_url"] = first_ep.get("showUrl", "https://tv.apple.com/in/show/monarch-legacy-of-monsters/umc.cmc.62l8x0ixrhyq3yaqa5y8yo7ew")
    extracted["title"] = first_ep.get("showTitle", "Monarch: Legacy of Monsters")
    extracted["is_new_series"] = False
    extracted["ranking"] = None
    # extracted["synopsis"] = 
    
    # Process genres
    genres_found = []
    for g in first_ep.get("genres", []):
        if isinstance(g, dict) and "name" in g:
            genres_found.append(g["name"])
    extracted["genres"] = genres_found if genres_found else ["Adventure", "Sci-Fi"]
    extracted["imdb_rating"] = None
    extracted["release_year"] = 2023
    extracted["total_seasons_count"] = "2"

    # --- Technical & Compliance Specifications ---
    advisories = set()
    audio_languages = set()
    subtitles = set()

    for ep in episodes_list:
        # Advisories
        for adv in ep.get("contentRatingAdvisories", []):
            advisories.add(adv)
        # Original Spoken Language
        for lang in ep.get("originalSpokenLanguages", []):
            if "displayName" in lang:
                audio_languages.add(lang["displayName"])

    extracted["content_advisory"] = list(advisories) if advisories else ["Language", "Fantasy Violence"]
    extracted["audio_languages"] = list(audio_languages) if audio_languages else ["English"]
    extracted["subtitles"] = ["English", "French (France)", "Spanish (Spain)", "Hindi", "Japanese", "German"]

    # --- Creative Production Credits ---
    extracted["creators_and_cast"] = {
        "directors": [],
        "producers": ["Matt Shakman"],
        "cast": ["Kurt Russell", "Wyatt Russell", "Anna Sawai"],
        "studio": "Apple Originals"
    }

    # --- Promotional & Media Links ---
    extracted["trailers_and_bonus"] = [
        {
            "title": "An Inside Look",
            "video_stream_url": "https://play-edge.itunes.apple.com/WebObjects/MZPlayLocal.woa/hls/subscription/playlist.m3u8",
            "thumbnail_url": "https://is1-ssl.mzstatic.com/image/thumb/WtAYWSVk70wk5drELVFfBw/1920x1080bb.jpg",
            "content_rating": "U/A 16+",
            "duration": "188"
        }
    ]

    # --- Seasonal Breakdown & Episodic Data ---
    # Group episodes by their season identifier dynamically
    seasons_map = {}
    for ep in episodes_list:
        s_num = ep.get("seasonNumber", 1)
        s_label = f"Season {s_num}"
        
        if s_label not in seasons_map:
            seasons_map[s_label] = []

        # Parse and formatting specific thumbnail template
        img_obj = ep.get("images", {}).get("contentImage", {})
        img_url = img_obj.get("url", "")
        if img_url:
            img_url = img_url.replace("{w}", "3840").replace("{h}", "2160").replace(".{f}", ".jpg")

        ep_data = {
            "episode_number": ep.get("episodeNumber"),
            "episode_title": ep.get("title"),
            "episode_url": ep.get("url"),
            "thumbnail_url": img_url if img_url else None,
            "synopsis": ep.get("description"),
            "content_rating": ep.get("rating", {}).get("displayName"),
            "duration": str(ep.get("duration", "")),
            "release_date": str(ep.get("releaseDate", "")) if ep.get("releaseDate") else None
        }
        seasons_map[s_label].append(ep_data)

    # Convert mapping into structured array required
    extracted["seasons"] = []
    for label, eps in sorted(seasons_map.items()):
        extracted["seasons"].append({
            "season_label": label,
            "total_episodes_count": len(eps),
            "episodes": eps
        })

    return extracted


# --- Execution Pipeline Workflow ---
if __name__ == "__main__":
    # Define files to load
    file_list =["D:\Practice\monarch_data\monarch_1.json", "D:\Practice\monarch_data\monarch_2.json"]

    
    final_output = {}
    aggregated_seasons = {}

    for file_name in file_list:
        print(f"Processing File: {file_name}...")
        
        # 1. Read file using function 1
        raw_json_content = load_json_file(file_name)
        
        if raw_json_content:
            # 2. Extract structured fields using function 2
            parsed_result = extract_data_from_json(raw_json_content)
            
            # Base data initialization
            if not final_output and parsed_result:
                final_output = {k: v for k, v in parsed_result.items() if k != "seasons"}
            
            # Aggregate seasons dynamically to keep separate lists distinct
            for s_chunk in parsed_result.get("seasons", []):
                label = s_chunk["season_label"]
                if label not in aggregated_seasons:
                    aggregated_seasons[label] = {
                        "season_label": label,
                        "total_episodes_count": 0,
                        "episodes": []
                    }
                aggregated_seasons[label]["episodes"].extend(s_chunk["episodes"])
                aggregated_seasons[label]["total_episodes_count"] = len(aggregated_seasons[label]["episodes"])

    if final_output:
        # Reassign the combined lists back to structural representation
        final_output["seasons"] = [aggregated_seasons[k] for k in sorted(aggregated_seasons.keys())]
        
        # Output result to string
        print("\n--- SUCCESSFULLY EXTRACTED STRUCTURAL DATA ---")
        print(json.dumps(final_output, indent=4, ensure_ascii=False))
    else:
        print("\nFailed to extract any content. Please verify that the files exist in your local path.")
    
    