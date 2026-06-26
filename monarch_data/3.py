import json
from datetime import datetime
from collections import defaultdict

def extract_and_format_json(file_path):
    """
    Reads the nested json file, groups episodes by season, 
    converts milliseconds release dates to YYYY-MM-DD, 
    and returns the structured data.
    """
    # 1. Load the raw JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # Access the flat array under data -> episodes
    episodes_list = raw_data.get("data", {}).get("episodes", [])

    # Group episodes by their season number dynamically
    seasons_map = defaultdict(list)
    for ep in episodes_list:
        season_num = ep.get("seasonNumber", "Unknown Season")
        seasons_map[season_num].append(ep)

    extracted_seasons = []

    # 2. Iterate through each collected season group
    for season_num, s_episodes in sorted(seasons_map.items()):
        
        formatted_episodes = []
        
        # 3. Process every individual episode inside this season
        for ep in s_episodes:
            # Pull rating details safely
            rating_data = ep.get("rating", {})
            display_name = rating_data.get("displayName") if isinstance(rating_data, dict) else None
            
            # Duration conversion
            duration_val = ep.get("duration")
            duration_str = f"{int(duration_val / 60)} mins" if duration_val else ""

            # --- RELEASE DATE FORMATTING ---
            release_date_ms = ep.get("releaseDate")
            formatted_date = ""
            
            if release_date_ms:
                try:
                    # Convert milliseconds to seconds and format to YYYY-MM-DD
                    formatted_date = datetime.fromtimestamp(release_date_ms / 1000.0).strftime('%Y-%m-%d')
                except Exception:
                    # Fallback in case of an invalid timestamp format
                    formatted_date = str(release_date_ms)

            # Map episode details to the target layout
            episode_entry = {
                "episode_number": ep.get("episodeNumber"),
                "episode_title": str(ep.get("title", "")),
                "episode_url": str(ep.get("url", "")),
                "thumbnail_url": ep.get("images", {}).get("contentImage", {}).get("url", ""),
                "synopsis": str(ep.get("description", "")),
                "content_rating": display_name,
                "duration": duration_str,
                "release_date": formatted_date  # Beautifully formatted date string
            }
            formatted_episodes.append(episode_entry)

        # 4. Build the parent Season dictionary block
        season_entry = {
            "season_label": f"Season {season_num}",
            "total_episodes_count": len(formatted_episodes),
            "episodes": formatted_episodes
        }
        extracted_seasons.append(season_entry)

    # Wrap it up to meet the requested design specification
    final_output = {"seasons": extracted_seasons}
    return final_output


# --- HOW TO RUN IT ---
# Call the single function and print the result
output_data = extract_and_format_json(r"C:\Users\kuldeep.shisha\Downloads\monarch_3.json")
print(json.dumps(output_data, indent=4))