import re
import json


# ---------------------------
# PATH PARSER
# ---------------------------
def parse_path(path):
    tokens = []
    parts = path.split(".")

    for part in parts:
        while part:
            # key name
            m = re.match(r"([^\[\]]+)", part)
            if m:
                tokens.append(m.group(1))
                part = part[m.end():]

            # [index] or [*]
            m = re.match(r"\[(\d+|\*)\]", part)
            if m:
                val = m.group(1)
                tokens.append("*" if val == "*" else int(val))
                part = part[m.end():]

    return tokens


# ---------------------------
# CORE EXTRACTOR
# ---------------------------
def extract(data, path, safe=False):
    tokens = parse_path(path)

    def walk(obj, remaining):
        if not remaining:
            return obj

        token = remaining[0]
        rest = remaining[1:]

        # -----------------------
        # DICT HANDLING
        # -----------------------
        if isinstance(obj, dict):

            # allow numeric token as string fallback (important fix)
            if isinstance(token, int) and str(token) in obj:
                token = str(token)

            if not isinstance(token, (str, int)):
                raise TypeError(f"Invalid dict key: {token}")

            if token not in obj:
                if safe:
                    return None
                raise KeyError(f"Key not found: {token}")

            return walk(obj[token], rest)

        # -----------------------
        # LIST HANDLING
        # -----------------------
        elif isinstance(obj, list):

            if token == "*":
                return [walk(item, rest) for item in obj]

            if isinstance(token, int):
                if token >= len(obj):
                    if safe:
                        return None
                    raise IndexError(f"Index out of range: {token}")
                return walk(obj[token], rest)

            if safe:
                return None
            raise TypeError(f"Expected list index or '*', got {token}")

        # -----------------------
        # INVALID TYPE
        # -----------------------
        if safe:
            return None
        raise TypeError(f"Cannot traverse type: {type(obj)}")

    return walk(data, tokens)


# ---------------------------
# JSON LOADER
# ---------------------------
def read_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None

data=read_json_file(r'D:\Practice\Flights\easemytrip.json')

leg=extract(data,'j[0].s[*].segKeyArr')
City=extract(data,'A')

data1={
        "total_stops": f"{len(extract(data,'j[0].s[0].segKeyArr'))-1} Stops",
        "flight_details": [
            {
                "flight_id": f"{extract(data,'dctFltDtl[0].AC')}{extract(data,'dctFltDtl[0].FN')}",
                "flight_name": extract(data,'dctFltDtl[0].FlightName'),
                "day": extract(data,'dctFltDtl[0].ADT')[:3],
                "date": extract(data,'dctFltDtl[0].ADT')[4:],
                "departure_city": City.get(f"{extract(data,'dctFltDtl[0].OG')}"),
                "departure_time": extract(data,'dctFltDtl[0].DTM'),
                "departure_terminal": extract(data,'dctFltDtl[0].DTER'),
                "arrival_city":City.get(f"{extract(data,'dctFltDtl[0].DT')}"),
                "arrival_time": extract(data,'dctFltDtl[0].ATM'),
                "arrival_terminal": extract(data,'dctFltDtl[0].ATER'),
                "time_duration": extract(data,'dctFltDtl[0].DUR'),
                "flight_class": extract(data,'dctFltDtl[0].CB')
            }
        ]}
print(data1)