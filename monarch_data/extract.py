import json
import os
import re
from datetime import datetime
from collections import defaultdict

# Folder this script lives in (e.g. C:\Users\hiren.chauhan\Desktop\HirenGit\monarch_legacy_of_monsters)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_1 = os.path.join(BASE_DIR, "monarch_1.json")   # episode-detail dump (Season 1, complete)
INPUT_2 = os.path.join(BASE_DIR, "monarch_2.json")   # show-page dump (series info + partial episode window)
OUTPUT = os.path.join(BASE_DIR, "monarch_details_extract.json")


def safe_get(obj, keys, default=None):
    for key in keys:
        if isinstance(obj, dict):
            obj = obj.get(key, default)
        elif isinstance(obj, list) and isinstance(key, int):
            try:
                obj = obj[key]
            except IndexError:
                return default
        else:
            return default
        if obj is default and key != keys[-1]:
            return default
    return obj


def format_image_url(template, width=None, height=None, fmt="jpg"):
    """Fill in the {w}/{h}/{f} placeholders WITHOUT touching the rest of the
    URL (including its real ?color=XXXXXX query string)."""
    if not template:
        return None
    w = width or 3840
    h = height or 2160
    return (
        template.replace("{w}", str(w))
        .replace("{h}", str(h))
        .replace("{f}", fmt)
    )


def parse_tag_number(tag):
    """'EPISODE 6' -> 6"""
    if not tag:
        return None
    m = re.search(r"\d+", str(tag))
    return int(m.group(0)) if m else None


def seconds_to_minutes_label(seconds):
    if seconds is None:
        return None
    if seconds > 10000:  # guard against ms values
        seconds = seconds / 1000.0
    return f"{int(round(seconds / 60))} min"


def epoch_ms_to_date(epoch_ms):
    if epoch_ms is None:
        return None
    from datetime import datetime, timezone
    return datetime.fromtimestamp(epoch_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")


def parse_language_string(raw):
    """Turns 'English (CC, SDH), French (Canada) (SDH), Chinese, Traditional (SDH)'
    into ['English', 'French (Canada)', 'Chinese, Traditional'].

    Splits on top-level commas only (commas *inside* parentheses, e.g. the
    "(CC, SDH)" qualifier, are NOT split points). A few language names
    legitimately contain a comma (e.g. "Chinese, Simplified"), so those are
    protected with a placeholder before splitting, then restored."""
    if not raw:
        return []

    compounds = ["Chinese, Simplified", "Chinese, Traditional", "Cantonese, Traditional"]
    placeholder_map = {}
    protected = raw
    for i, c in enumerate(compounds):
        token = f"\x00{i}\x00"
        placeholder_map[token] = c
        protected = protected.replace(c, token)

    # Split on commas that are NOT inside parentheses
    parts = re.split(r",\s*(?![^(]*\))", protected)

    cleaned = []
    for part in parts:
        name = part.strip()
        for token, original in placeholder_map.items():
            name = name.replace(token, original)
        # Strip trailing technical-qualifier parens: (AD, ...), (CC, SDH), (SDH)
        name = re.sub(r"\s*\((?:AD|CC|SDH)[^)]*\)\s*$", "", name).strip()
        if name and name not in cleaned:
            cleaned.append(name)
    return cleaned


season2_episodes = []

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
            images=ep.get("images",{}).get("contentImage",{})
            # Map episode details to the target layout
            episode_entry = {
                "episode_number": ep.get("episodeNumber"),
                "episode_title": str(ep.get("title", "")),
                "episode_url":ep.get('url') ,
                "thumbnail_url": format_image_url(images.get("url", ""),images.get("width",''), images.get("height",'')),
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
    # final_output = {"seasons": extracted_seasons}
    return season2_episodes.append(extracted_seasons)


# --- HOW TO RUN IT ---
# Call the single function and print the result
output_data = extract_and_format_json(r"C:\Users\kuldeep.shisha\Downloads\monarch_3.json")



def main():
    with open(INPUT_1, "r", encoding="utf-8") as f:
        file1 = json.load(f)
    with open(INPUT_2, "r", encoding="utf-8") as f:
        file2 = json.load(f)

    show_intent = file2["data"][1]["data"]
    config_data = file2["data"][0]["data"]
    shelves = show_intent["shelves"]

    shelves_by_header_title = {}
    for s in shelves:
        t = safe_get(s, ["header", "title"])
        if t:
            shelves_by_header_title[t] = s

    # ---------- Series-level hero info (shelf with SuperheroLockup) ----------
    hero = shelves[0]["items"][0]
    series_id = safe_get(hero, ["buttons", 0, "action", "actionMetrics", "data", 0, "fields", "canonicalId"])
    title = hero.get("title")
    synopsis = hero.get("description")
    series_url = show_intent.get("canonicalURL")

    # ---------- About shelf (genres) ----------
    about_shelf = next((s for s in shelves if s.get("$type") == "About"), None)
    genres = []
    if about_shelf:
        genres = safe_get(about_shelf, ["items", 0, "genres"], [])

    # ---------- Info shelf (release year, rating, content advisories, languages) ----------
    info_shelf = next((s for s in shelves if s.get("$type") == "Info"), None)
    release_year = None
    content_rating = None
    content_advisory = []
    audio_languages = []
    subtitles = []
    if info_shelf:
        groups = {g.get("title"): g for g in info_shelf.get("items", [])}
        info_group = groups.get("Information", {}).get("items", [])
        for entry in info_group:
            if entry.get("id") == "information-releaseDate":
                m = re.search(r"\d{4}", entry.get("info", ""))
                if m:
                    release_year = int(m.group(0))
            elif entry.get("id") == "information-rating":
                content_rating = entry.get("info")
            elif entry.get("id") == "information-contentRatingAdvisories":
                content_advisory = [a.strip() for a in entry.get("info", "").split(",") if a.strip()]

        lang_group = groups.get("Languages", {}).get("items", [])
        for entry in lang_group:
            if entry.get("id") == "languages-subtitles":
                subtitles = parse_language_string(entry.get("info", ""))

    # Audio languages: use the per-episode playable tracks from file1 (authoritative,
    # confirmed identical across every episode) plus the original spoken language.
    playables = file1.get("data", {}).get("playables", {})
    original_lang = None
    audio_set = []
    if playables:
        first_playable = next(iter(playables.values()))
        audio_set = [t.get("displayName") for t in first_playable.get("audioTrackLocales", []) if t.get("displayName")]
    first_ep = safe_get(file1, ["data", "episodes", 0], {})
    original_langs = first_ep.get("originalSpokenLanguages", [])
    if original_langs:
        original_lang = original_langs[0].get("displayName")
    audio_languages = ([original_lang] if original_lang else []) + [l for l in audio_set if l != original_lang]

    # ---------- Cast & Crew shelf ----------
    cast_shelf = shelves_by_header_title.get("Cast & Crew")
    producers = []
    cast = []
    if cast_shelf:
        for item in cast_shelf.get("items", []):
            name = item.get("title")
            role = item.get("subtitle", "")
            if not name:
                continue
            if role == "Executive Producer":
                producers.append(name)
            else:
                cast.append(name)
                # cast.append(name if name else continue)

    # ---------- Trailers & Bonus Content shelves ----------
    trailers_and_bonus = []
    for shelf_name in ("Trailers", "Bonus Content"):
        shelf = shelves_by_header_title.get(shelf_name)
        if not shelf:
            continue
        for item in shelf.get("items", []):
            artwork = item.get("artwork", {})
            trailers_and_bonus.append({
                "title": safe_get(item, ["contextAction", "title"]) or item.get("title"),
                "video_stream_url": safe_get(item, ["contextAction", "url"]),
                "thumbnail_url": format_image_url(artwork.get("template"), artwork.get("width"), artwork.get("height")),
                "content_rating": None,
                "duration": item.get("metadata"),
            })

    # ---------- Episodes ----------
    # Season 1: complete + authoritative, comes from file1 (episode detail dump)
    season1_episodes = []
    file1_episodes = file1.get("data", {}).get("episodes", [])
    file1_titles = set()
    for ep in file1_episodes:
        images = ep.get("images", {}).get("contentImage", {})
        season1_episodes.append({
            "episode_number": ep.get("episodeNumber"),
            "episode_title": ep.get("title"),
            "episode_url": ep.get("url"),
            "thumbnail_url": format_image_url(images.get("url"), images.get("width"), images.get("height")),
            "synopsis": ep.get("description"),
            "content_rating": safe_get(ep, ["rating", "displayName"]),
            "duration": seconds_to_minutes_label(ep.get("duration")),
            "release_date": epoch_ms_to_date(ep.get("releaseDate")),
        })
        file1_titles.add(ep.get("title", "").strip().lower())

    season1_episodes.sort(key=lambda e: e["episode_number"])

    # Season 2 (partial): any episode-tagged item from file2's Episodes shelf
    # whose title ISN'T already covered by file1 (i.e. not a Season-1 re-listing)
    # season2_episodes = []
    episodes_shelf = shelves_by_header_title.get("Episodes")
    # if episodes_shelf:
    #     for item in episodes_shelf.get("items", []):
    #         if item.get("type") != "Episode":
    #             continue
    #         ep_title = item.get("title")
    #         if not ep_title or ep_title.strip().lower() in file1_titles:
    #             continue  # already have this one (and it's more complete) from file1
    #         artwork = item.get("artwork", {})
    #         season2_episodes.append({
    #             "episode_number": parse_tag_number(item.get("tag")),
    #             "episode_title": ep_title,
    #             "episode_url": safe_get(item, ["contextAction", "url"]),
    #             "thumbnail_url": format_image_url(artwork.get("template"), artwork.get("width"), artwork.get("height")),
    #             "synopsis": item.get("description"),
    #             "content_rating": None,   # not present in source data for these items
    #             "duration": item.get("metadata"),
    #             "release_date": None,     # not present in source data for these items
    #         })

    # season2_episodes.sort(key=lambda e: (e["episode_number"] is None, e["episode_number"]))

    seasons_meta = {s["seasonNumber"]: s for s in safe_get(episodes_shelf, ["header", "seasons"], [])} if episodes_shelf else {}

    seasons_output = []
    if season1_episodes:
        seasons_output.append({
            "season_label": seasons_meta.get(1, {}).get("title", "Season 1"),
            "total_episodes_count": len(season1_episodes),
            "episodes": season1_episodes,
        })
    if season2_episodes:
        # official_count = seasons_meta.get(2, {}).get("episodeCount")
        seasons_output.append({
            # "season_label": seasons_meta.get(2, {}).get("title", "Season 2"),
            # "total_episodes_count": len(season2_episodes),
            # "total_episodes_count_official": official_count,
            # "note": (
            #     f"Only {len(season2_episodes)} of {official_count} Season 2 episodes are present "
            #     "in the supplied source files; episodes 7-10 are not included in either JSON dump."
            # ) if official_count and official_count > len(season2_episodes) else None,
            "Season-2": season2_episodes,
        })

    total_seasons_count = f"{len(seasons_output)} Season" + ("" if len(seasons_output) == 1 else "s")

    result = {
        "series_id": series_id,
        "series_url": series_url,
        "title": title,
        "is_new_series": False,
        "ranking": None,
        "synopsis": synopsis,
        "genres": genres,
        "imdb_rating": None,
        "release_year": release_year,
        "total_seasons_count": total_seasons_count,
        "content_advisory": content_advisory,
        "audio_languages": audio_languages,
        "subtitles": subtitles,
        "creators_and_cast": {
            "directors": [],  # not labeled "Director" in source data; from general knowledge
            "producers": producers,
            "cast": cast,
            "studio": None,  # not present in source data; from general knowledge
        },
        "trailers_and_bonus": trailers_and_bonus,
        "seasons": seasons_output,
        # "content_rating": content_rating,
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Wrote {OUTPUT}")
    print(f"Season 1: {len(season1_episodes)} episodes | Season 2: {len(season2_episodes)} episodes")
    print(f"Trailers/Bonus: {len(trailers_and_bonus)} | Cast: {len(cast)} | Producers: {len(producers)}")
    print(f"Audio languages: {audio_languages}")


if __name__ == "__main__":
    main()