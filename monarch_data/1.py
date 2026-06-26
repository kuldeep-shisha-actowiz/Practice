import json
from collections import defaultdict
from datetime import datetime

# Load your nested JSON data
with open('D:\Practice\monarch_data\monarch_1.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# Extract the list of episodes from the JSON structure
episodes_raw = json_data.get("data", {}).get("episodes", [])

# Use a dictionary to group episodes by season number temporary
seasons_map = defaultdict(list)

for ep in episodes_raw:
    # Safely extract all required fields based on the JSON structure
    season_num = ep.get("seasonNumber")
    episode_num = ep.get("episodeNumber")
    title = ep.get("title", "")
    episode_url = ep.get("url", "")
    
    # Get thumbnail URL if available
    images = ep.get("images", {})
    thumbnail_url = images.get("contentImage", {}).get("url", "")
    
    synopsis = ep.get("description", "")
    
    # Extract rating display name (e.g., 'U/A 13+')
    content_rating = ep.get("rating", {}).get("displayName", "")
    
    # Format duration (you can leave as integer seconds or convert to str as requested)
    duration_secs = ep.get("duration")
    duration_str = f"{duration_secs // 60}m" if duration_secs else ""
    
    # Convert epoch millisecond timestamp to a standard date string representation
    release_ms = ep.get("releaseDate")
    release_date_str = ""
    if release_ms:
        release_date_str = datetime.utcfromtimestamp(release_ms / 1000.0).strftime('%Y-%m-%d')
    
    # Construct the episode dictionary matching your target structure
    episode_data = {
        "episode_number": int(episode_num) if episode_num is not None else None,
        "episode_title": str(title),
        "episode_url": str(episode_url),
        "thumbnail_url": str(thumbnail_url),
        "synopsis": str(synopsis),
        "content_rating": str(content_rating),
        "duration": str(duration_str),
        "release_date": str(release_date_str)
    }
    
    if season_num is not None:
        seasons_map[season_num].append(episode_data)

# Build the final list format sorted chronologically by season and episode number
seasons_list = []
for season_num in sorted(seasons_map.keys()):
    # Sort episodes inside this season chronologically by episode_number
    sorted_episodes = sorted(seasons_map[season_num], key=lambda x: x["episode_number"] or 0)
    
    season_entry = {
        "season_label": f"Season {season_num}",
        "total_episodes_count": len(sorted_episodes),
        "episodes": sorted_episodes
    }
    seasons_list.append(season_entry)

# Wrap inside the final dictionary structure
output_data = {
    "seasons": seasons_list
}

# Print or save the structured result
print(json.dumps(output_data, indent=4))