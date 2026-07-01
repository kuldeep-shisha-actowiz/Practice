
import os
import json
from datetime import datetime


def read_json_file(file_path):
    """Reads and loads the JSON file."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None


def calculate_stops(seg_key_arr):
    """Calculates the number of stops based on the length of segKeyArr."""
    length = len(seg_key_arr)
    if length == 1:
        return "Non-stop"
    elif length == 2:
        return "1 stop"
    else:
        return f"{length - 1} stops"


def parse_date_and_day(date_str):
    """Parses a date string like 'Mon-01Jun2026' into Day (e.g., 'Monday')

    and Date (e.g., '01Jun2026').
    """
    try:
        # Expected format: "Mon-01Jun2026"
        dt = datetime.strptime(date_str, "%a-%d%b%Y")
        day_name = dt.strftime("%A")  # Full weekday name, e.g., Monday
        date_part = date_str.split("-")[1] if "-" in date_str else date_str
        return day_name, date_part
    except Exception:
        # Fallback if date string doesn't match expected format
        return "Unknown", date_str


def format_terminal(terminal_val):
    """Formats terminal value to 'Terminal - X'."""
    if terminal_val:
        return f"Terminal - {terminal_val}"
    return "N/A"

def extract_flight_details(seg_key_arr, dctFltDtl, city_airport_dict):
    """Matches keys in segKeyArr with LegKey in dctFltDtl and extracts details."""
    flight_details = []

    # Safe handling: If dctFltDtl is a dictionary, extract its values
    segment_pool = (
        dctFltDtl.values() if isinstance(dctFltDtl, dict) else dctFltDtl
    )

    for key in seg_key_arr:
        matched_segment = None

        # Iterate over the segments safely
        for segment in segment_pool:
            # Double check that segment is actually a dictionary before calling .get()
            if isinstance(segment, dict) and segment.get("LegKey") == key:
                matched_segment = segment
                break

        if matched_segment:
            raw_date = matched_segment.get("ADT", "")
            day_name, clean_date = parse_date_and_day(raw_date)

            dep_code = matched_segment.get("OG", "")
            arr_code = matched_segment.get("DT", "")
            dep_city = city_airport_dict.get(dep_code, dep_code)
            arr_city = city_airport_dict.get(arr_code, arr_code)

            detail = {
                "flight_id": str(matched_segment.get("AC", ""))
                + str(matched_segment.get("FN", "")),
                "flight_name": matched_segment.get("FlightName", ""),
                "day": day_name,
                "date": clean_date,
                "departure_city": dep_city,
                "departure_time": matched_segment.get("DTM", ""),
                "departure_terminal": format_terminal(
                    matched_segment.get("DTER")
                ),
                "arrival_city": arr_city,
                "arrival_time": matched_segment.get("ATM", ""),
                "arrival_terminal": format_terminal(
                    matched_segment.get("ATER")
                ),
                "time_duration": matched_segment.get("DUR", ""),
                "flight_class": matched_segment.get("CB", ""),
            }
            flight_details.append(detail)

    return flight_details


def process_flight_data(data):
    """Main function to iterate through journeys and extract structured data."""
    extracted_itineraries = []

    # Map the root level keys according to your notes
    # Assuming 'A' is the dictionary mapping city codes like {"DEL": "New Delhi"}
    city_airport_dict = data.get("A", {})
    dctFltDtl = data.get("dctFltDtl", [])
    j_list = data.get("j", [])

    for journey in j_list:
        s_list = journey.get("s", [])
        for s in s_list:
            seg_key_arr = s.get("segKeyArr", [])

            # Compile structure
            itinerary = {
                "total_stops": calculate_stops(seg_key_arr),
                "flight_details": extract_flight_details(
                    seg_key_arr, dctFltDtl, city_airport_dict
                ),
                "flight_information": {
                    "total_base_fare": s.get("AP"),
                    "tax": s.get("APT"),
                    "total": s.get("PT"),
                },
            }
            extracted_itineraries.append(itinerary)

    return extracted_itineraries


# --- Execution Example ---
data = read_json_file(r"D:\Practice\Flights\easemytrip.json")
if data:
    result = process_flight_data(data)
    # print(json.dumps(result, indent=4))

    with open(os.path.join(r'D:\Practice\Flights', 'easemytrip_outout.json'), 'w') as file:
        json.dump(result, file, indent=4)
    