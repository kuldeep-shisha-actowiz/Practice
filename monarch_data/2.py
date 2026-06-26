import json
import re

def get_safe(data, keys, default=None):
    """
    Safely navigates a nested list/dictionary structure.
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
            current = current[key]
        else:
            return default
    return current

def extract_episode_int(episode_tag):
    """
    Extracts the first number found in the episode tag for sorting purposes.
    e.g., "EPISODE 2" -> 2. Returns 0 if no number is found.
    """
    if not episode_tag:
        return 0
    match = re.search(r'\d+', str(episode_tag))
    return int(match.group()) if match else 0

def scrape_season_2_data(json_file_path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            root_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading file: {e}")
        return []

    scraped_seasons = []
    data_list = root_data.get("data", [])
    if not isinstance(data_list, list):
        return []

    for data_item in data_list:
        shelves = get_safe(data_item, ["data", "shelves"])
        if not shelves or not isinstance(shelves, list):
            continue
            
        for shelf in shelves:
            seasons_info = get_safe(shelf, ["header", "seasons"])
            if isinstance(seasons_info, list):
                for season in seasons_info:
                    season_label = str(season.get("title", ""))
                    
                    # Filter for Season 2 only
                    if "season 2" not in season_label.lower():
                        continue
                    
                    total_episodes = season.get("episodeCount")
                    try:
                        total_episodes_count = int(total_episodes) if total_episodes is not None else 0
                    except (ValueError, TypeError):
                        total_episodes_count = 0

                    episodes_list = []
                    items = shelf.get("items", [])
                    if isinstance(items, list):
                        for item in items:
                            episode_number = item.get("tag", "")
                            episode_title = str(item.get("title", "")).strip()
                            synopsis = str(item.get("description", "")).strip()
                            
                            # --- SKIP IF ESSENTIAL DETAILS ARE EMPTY ---
                            if not episode_title or not synopsis or not episode_number:
                                continue
                            
                            action_metrics_data = get_safe(item, ["segue", "actionMetrics", "data"])
                            episode_url = ""
                            if isinstance(action_metrics_data, list) and len(action_metrics_data) > 0:
                                episode_url = str(get_safe(action_metrics_data[0], ["fields", "actionUrl"], ""))
                            
                            thumbnail_url = get_safe(item, ["artwork", "template"], "")
                            content_rating = "U/A 16+"
                            
                            duration_meta = item.get("metadata", "")
                            duration = str(duration_meta) if isinstance(duration_meta, (str, int, float)) else ""
                            release_date = ""
                            
                            episodes_list.append({
                                "episode_number": episode_number,
                                "episode_title": episode_title,
                                "episode_url": episode_url,
                                "thumbnail_url": thumbnail_url,
                                "synopsis": synopsis,
                                "content_rating": content_rating,
                                "duration": duration,
                                "release_date": release_date
                            })
                    
                    # --- SORT EPISODES BY EPISODE NUMBER ---
                    # Uses the extract_episode_int helper to sort numerically (1, 2, 3...) instead of alphabetically
                    episodes_list.sort(key=lambda x: extract_episode_int(x["episode_number"]))
                    
                    # Only add the season if it actually contains parsed episodes
                    if episodes_list:
                        scraped_seasons.append({
                            "season_label": season_label,
                            "total_episodes_count": len(episodes_list), # Updates count to match valid scraped episodes
                            "episodes": episodes_list
                        })

    return scraped_seasons

# --- Execution ---
if __name__ == "__main__":
    file_path = "D:\Practice\monarch_data\monarch_2.json"
    result = scrape_season_2_data(file_path)
    
    final_output = {"seasons": result}
    print(json.dumps(final_output, indent=4))