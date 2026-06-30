import json

def extract_property_ids(data):
    data=data.get("data")
    # Check if citySearch and properties exist
    city_search = data.get("citySearch")
    if not city_search:
        return []
    
    properties = city_search.get("properties")
    if not properties:
        return []
    
    # Extract propertyId from each object, preserving order
    result: list = []
    for prop in properties:
        property_id = prop.get("propertyId")
        if property_id is not None:
            result.append(property_id)
    
    return result

def main():
    # Example usage
    with open(r'D:\Practice\Hotel_agoda\agoda.json','r') as file:
        h=json.load(file)
    result = extract_property_ids(h)
    print(json.dumps(result))

if __name__ == "__main__":
    main()