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

data=read_json_file(r'D:\Practice\CArwale\carwale2.json')


Data1={ 
        'title':extract(data,'usedCarDetails.carInfo.data.makeYear')+' '+extract(data,'usedCarDetails.carInfo.data.makeName')+' '+extract(data,'usedCarDetails.carInfo.data.rootName')+' '+extract(data,'usedCarDetails.carInfo.data.versionName'),
       'kilometers':extract(data,'usedCarDetails.carInfo.data.kilometers') + "km",
       'engine':extract(data,'usedCarDetails.carInfo.data.fuelName'),
       'price':extract(data,'usedCarDetails.carInfo.data.price'),
       'mainimageurl':extract(data,'usedCarDetails.carInfo.data.mainImageUrl'),
       'other_image':extract(data,'usedCarDetails.imageList'),
       'other_image':extract(data,'usedCarDetails.imageList'),
       'feature':[{
           'sunroof':extract(data,'usedCarDetails.featuresV2[0].items[0].values[0]'),
           'spoiler':extract(data,'usedCarDetails.featuresV2[0].items[1].values[0]'),
           'roof_rails':extract(data,'usedCarDetails.featuresV2[0].items[2].values[0]'),
           "Body_coloured_Bumpers":extract(data,'usedCarDetails.featuresV2[0].items[3].values[0]'),
           'rub_strips':extract(data,'usedCarDetails.featuresV2[0].items[4].values[0]'),
           'body_kit':extract(data,'usedCarDetails.featuresV2[0].items[5].values[0]'),
           'antenna':extract(data,'usedCarDetails.featuresV2[0].items[6].values[0]'),
           'fuel_tank_capacity':extract(data,'usedCarDetails.specificationsV2[2].items[3].values[0]') + ' litres',
       }],
       'engine_&_transmission':[{
           'engine':extract(data,'usedCarDetails.specificationsV2[0].items[0].itemValue'),
           'engine_type':extract(data,'usedCarDetails.specificationsV2[0].items[1].itemValue'),
           'turbocharger/supercharger':extract(data,'usedCarDetails.specificationsV2[0].items[2].itemValue'),
           'fuel_type':extract(data,'usedCarDetails.specificationsV2[0].items[3].itemValue'),
           'max_power':extract(data,'usedCarDetails.specificationsV2[0].items[4].itemValue'),
           'max_torque':extract(data,'usedCarDetails.specificationsV2[0].items[5].itemValue'),
           'alternate_fuel':extract(data,'usedCarDetails.specificationsV2[0].items[6].itemValue'),
           'emission_standard':extract(data,'usedCarDetails.specificationsV2[0].items[7].itemValue'),
           'mileage':extract(data,'usedCarDetails.specificationsV2[0].items[8].itemValue'),
           'idle_start/stop':extract(data,'usedCarDetails.specificationsV2[0].items[9].itemValue'),
        }],
        'car_overview':[
            {
                'price':extract(data,'usedCarDetails.carInfo.data.price'),
                'kilometers':extract(data,'usedCarDetails.carInfo.data.kilometers') + " km",
                'fuel_type':extract(data,'usedCarDetails.carInfo.data.fuelName'),
                'registration_year':extract(data,'usedCarDetails.carInfo.data.formattedRegistrationDate'),
                'manufacture_year':extract(data,'usedCarDetails.carInfo.data.makeYear'),
                'no_of_owner':extract(data,'usedCarDetails.carInfo.data.noOfOwners'),
                'transmission':extract(data,'usedCarDetails.carInfo.data.transmissionType'),
                'color':extract(data,'usedCarDetails.carInfo.data.color'),
                'car_available_at':extract(data,'usedCarDetails.carInfo.data.carAvailbaleAt'),
                'insurance':extract(data,'usedCarDetails.carInfo.data.insurance'),
                'registration_type':extract(data,'usedCarDetails.carInfo.data.regType'),
                'last_updated':extract(data,'usedCarDetails.carInfo.data.lastUpdatedDate'),
            }]
       }

print(json.dumps(Data1,indent=4))