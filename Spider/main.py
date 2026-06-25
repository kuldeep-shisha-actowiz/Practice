import json
import re


def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    except FileNotFoundError:
        print(f"File not found: {path}")
        return None

    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}")
        return None

    except PermissionError:
        print(f"Permission denied: {path}")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None




import json

def parse_prime_video_payload(data: dict) -> dict:
    atf_state = data.get("init", {}).get("preparations", {}).get("body", {}).get("atf", {}).get("state", {})
    btf_state = data.get("init", {}).get("preparations", {}).get("body", {}).get("btf", {}).get("state", {})
    atf_strings = data.get("init", {}).get("preparations", {}).get("body", {}).get("atf", {}).get("strings", {})

    # Dynamically resolve active Series ID
    series_id = None
    if atf_state.get("self"):
        series_id = next(iter(atf_state["self"].keys()), None)
    if not series_id and atf_state.get("detail", {}).get("headerDetail"):
        series_id = next(iter(atf_state["detail"]["headerDetail"].keys()), None)
        
    if not series_id:
        raise KeyError("Could not dynamically resolve the Amazon Series GTI ID from the payload.")

    header_detail = atf_state.get("detail", {}).get("headerDetail", {}).get(series_id, {})
    action_atf = atf_state.get("action", {}).get("atf", {}).get(series_id, {})
    imdb_data = atf_state.get("imdb", {}).get(series_id, {})

    # --- WIDE NET: Content Advisory Fallbacks ---
    content_advisory = []
    # Path 1: Check standard contentAdvisories list
    raw_advisory = header_detail.get("contentAdvisories") or header_detail.get("contentAdvisory")
    
    # Path 2: Check maturityRating object text
    if not raw_advisory and "maturityRating" in header_detail:
        raw_advisory = header_detail.get("maturityRating", {}).get("advisories", [])
        
    # Path 3: Check ratingBadge
    if not raw_advisory and "ratingBadge" in header_detail:
        badge_text = header_detail.get("ratingBadge", {}).get("displayText")
        if badge_text: content_advisory.append(badge_text)

    # Process if Path 1 or Path 2 hit an array
    if isinstance(raw_advisory, list):
        for item in raw_advisory:
            if isinstance(item, dict) and item.get("text"):
                content_advisory.append(item.get("text"))
            elif isinstance(item, str):
                content_advisory.append(item)

   # --- Dynamic Regex Filtering for Spider-Noir Trailers ---
    trailers_and_bonus = []
    containers = btf_state.get("containers", {}).get(series_id, [])
    
    # Matches "Spider-Noir...Trailer" or "Spider Noir...Trailer" case-insensitively
    spider_noir_pattern = re.compile(r"spider[- ]*noir.*trailer", re.IGNORECASE)

    for container in containers:
        for entity in container.get("entities", []):
            title = entity.get("displayTitle") or entity.get("title") or ""
            
            # Extract only if the title matches our Spider-Noir trailer pattern
            if spider_noir_pattern.search(title):
                trailers_and_bonus.append({
                    "title": title,
                    "video_stream_url": f"https://www.primevideo.com/detail/{entity.get('link').get('url')}",
                    "thumbnail_url": entity.get("images", {}).get("cover") or entity.get("images", {}).get("packshot"),
                    "content_rating": entity.get("maturityRatingBadge", {}).get("displayText"),
                    "duration": entity.get("runtime")
                })

    # Standard Extractions (Genres, Audio, Crew, Episodes)
    genres = [g.get("text") for g in header_detail.get("genres", []) if isinstance(g, dict) and g.get("text")]
    audio_languages = [t.get("text") if isinstance(t, dict) else str(t) for t in header_detail.get("audioTracks", []) if t]
    subtitles = [s.get("text") if isinstance(s, dict) else str(s) for s in header_detail.get("subtitles", []) if s]
    
    contributors = header_detail.get("contributors", {})
    directors = [d.get("name") for d in contributors.get("directors", []) if isinstance(d, dict) and d.get("name")]
    producers = [p.get("name") for p in contributors.get("producers", []) if isinstance(p, dict) and p.get("name")]
    cast = [c.get("name") for c in contributors.get("cast", []) if isinstance(c, dict) and c.get("name")]

    # episodes_list = []
    # episode_details = btf_state.get("detail", {}).get("detail", {})
    # for ep_gti, ep_data in episode_details.items():
    #     if isinstance(ep_data, dict) and "episodeNumber" in ep_data:
    #         episodes_list.append({
    #             "episode_number": int(ep_data.get("episodeNumber", 0)),
    #             "episode_title": ep_data.get("title"),
    #             "episode_url": f"https://www.primevideo.com/detail/{ep_gti}",
    #             "thumbnail_url": ep_data.get("images", {}).get("packshot"),
    #             "synopsis": ep_data.get("synopsis"),
    #             "content_rating": header_detail.get("ratingBadge", {}).get("displayText"),
    #             "duration": ep_data.get("runtime"),
    #             "release_date": ep_data.get("releaseDate")
    #         })
    # episodes_list.sort(key=lambda x: x["episode_number"])



    episodes_list = []
    # 1. Grab the 'self' lookups block from the btf_state path
    btf_self_lookup = btf_state.get("self", {})
    
    episode_details = btf_state.get("detail", {}).get("detail", {})
    
    for ep_gti, ep_data in episode_details.items():
        if isinstance(ep_data, dict) and "episodeNumber" in ep_data:
            
            # 2. Dynamically extract the deep-play link path matching this episode's GTI
            # Maps to: init.preparations.body.btf.state.self[ep_gti]['link']
            ep_link_data = btf_self_lookup.get(ep_gti, {})
            dynamic_url = ep_link_data.get("link")
            
            # Fallback if the 'link' key is missing or structural paths vary slightly
            if not dynamic_url:
                dynamic_url = f"{ep_gti}"
                
            episodes_list.append({
                "episode_number": int(ep_data.get("episodeNumber", 0)),
                "episode_title": ep_data.get("title"),
                
                # --- UPDATED: Uses the exact structural path you provided ---
                "episode_url": f"https://www.primevideo.com/detail{dynamic_url}",
                
                "thumbnail_url": ep_data.get("images", {}).get("packshot",""),
                "synopsis": ep_data.get("synopsis"),
                "content_rating": header_detail.get("ratingBadge", {}).get("displayText"),
                "duration": ep_data.get("runtime"),
                "release_date": ep_data.get("releaseDate")
            })
            
    episodes_list.sort(key=lambda x: x["episode_number"])

    score = imdb_data.get("score")
    max_score = imdb_data.get("maxScore")

    return {
        "series_id": series_id,
        "series_url": f"https://www.primevideo.com/detail/{series_id}",
        "title": header_detail.get("title"),
        "is_new_series": bool(action_atf.get("messages", {}).get("titleMetadataBadge")),
        "ranking": action_atf.get("messages", {}).get("highValueMessage", {}).get("dvMessage", {}).get("string"),
        "synopsis": header_detail.get("synopsis"),
        "genres": genres,
        "imdb_rating": f"{score}/{max_score}" if score and max_score else None,
        "release_year": int(header_detail["releaseYear"]) if header_detail.get("releaseYear") else None,
        "total_seasons_count": atf_strings.get("DV_WEB_ONE_SEASON", "1 Season"),
        "content_advisory": content_advisory,
        "audio_languages": audio_languages,
        "subtitles": subtitles,
        "creators_and_cast": {
            "directors": directors,
            "producers": producers,
            "cast": cast,
            "studio": header_detail.get("studios")
        },
        "trailers_and_bonus": trailers_and_bonus,
        "seasons": [
            {
                "season_label": atf_strings.get("DV_WEB_ONE_SEASON", "Season 1"),
                "total_episodes_count": int(btf_state.get("episodeList", {}).get("totalCardSize", len(episodes_list))),
                "episodes": episodes_list
            }
        ] if episodes_list else []
    }
daa=read_file(r'D:\Practice\Spider\amazon_spider_noir.json')
output=parse_prime_video_payload(daa)

with open('spider_noir.json','w',encoding='utf-8')as file:
    json.dump(output,file,ensure_ascii=False,indent=4)