import re
import json

# ---------------------------
# PATH PARSER
# ---------------------------
def parse_path(path):
    tokens = []
    i = 0

    while i < len(path):

        # Skip dots
        if path[i] == ".":
            i += 1
            continue

        # Normal key
        if path[i] != "[":
            j = i
            while j < len(path) and path[j] not in ".[":
                j += 1
            tokens.append(path[i:j])
            i = j
            continue

        # Inside brackets
        if path[i] == "[":
            j = path.find("]", i)
            content = path[i + 1:j].strip()

            # ['key'] or ["key"]
            if (
                (content.startswith("'") and content.endswith("'"))
                or
                (content.startswith('"') and content.endswith('"'))
            ):
                tokens.append(content[1:-1])

            elif content == "*":
                tokens.append("*")

            else:
                tokens.append(int(content))

            i = j + 1

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

js1=read_json_file(r'D:\Practice\gorgez\gorgez_6720.json')
js2=read_json_file(r'D:\Practice\gorgez\traits.json')

def get_traits(js2):
    traits = []
    attributes = extract(js2, "data.itemByIdentifier.attributes")

    for i in range(len(attributes)):
        trait = {
            "trait_type": extract(js2, f"data.itemByIdentifier.attributes[{i}].traitType"),
            "value": extract(js2, f"data.itemByIdentifier.attributes[{i}].value"),
            "count": extract(js2, f"data.itemByIdentifier.attributes[{i}].stats.itemCount"),
            "percentage": extract(js2, f"data.itemByIdentifier.attributes[{i}].stats.percent"),
            "floor_price": extract(js2, f"data.itemByIdentifier.attributes[{i}].floorPrice.usd", safe=True)
        }
        traits.append(trait)

    return traits




Data1= {
   "item_title": extract(js1, "rehydrate['-14034333087'].data.itemByIdentifier.name"),
    "collection_name": extract(js1, "rehydrate['-14034333087'].data.itemByIdentifier.collection.name"),
    "owner_username": extract(js1, "rehydrate['-14034333087'].data.itemByIdentifier.collection.owner.displayName"),
    "token_number": extract(js1, "rehydrate['-14034333087'].data.itemByIdentifier.tokenId"),

    # --- Pricing & Market Valuation ---
    "market_data": [{
        "top_offer": extract(js1,"rehydrate['-14034333087'].data.itemByIdentifier.bestOffer.pricePerItem.token.unit"),           # Highest active WETH bid placeholder amount
        "collection_floor": extract(js1,"rehydrate['-14034333087'].data.itemByIdentifier.collection.floorPrice.pricePerItem.token.unit"),    # Minimum entry floor price metric baseline
        "rarity_rank": extract(js1,"rehydrate['-14034333087'].data.itemByIdentifier.rarity.rank"),         # Numeric global rarity index ordering placement
        "last_sale_price": extract(js1,"rehydrate['-14034333087'].data.itemByIdentifier.lastSale.token.unit"),     # Final closed marketplace transaction price
        "buy_now_price_eth": None, # Current direct immediate purchase listing price in ETH
        "buy_now_price_usd": None, # Estimated fiat USD equivalent valuation index
        "listing_expiration": None   # Timeframe deadline window flag for current listing
    }],

    # --- Generative Properties & Traits ---
    "traits":get_traits(js2)  ,

    # --- Project Context & Origin ---
    "about":[ {
        "description": extract(js1,"rehydrate['-14034333087'].data.itemByIdentifier.description"),         # Textual collection baseline contextual background
        "creator_username": extract(js1,"rehydrate['-14034333087'].data.itemByIdentifier.name")     # Primary collection smart contract deployer target handle
    }],

    # --- Ledger & Blockchain Specifications ---
    "blockchain_details": [{
        "contract_address": extract(js1,"rehydrate['-14034333087'].data.itemByIdentifier.contractAddress"),    # Ethereum hexadecimal mainnet deployment address
        "token_id": extract(js1,"rehydrate['-14034333087'].data.itemByIdentifier.tokenId"),            # Specific asset identifier tag index matching network token
        "token_standard": extract(js1,"rehydrate['-14034333087'].data.itemByIdentifier.standard"),      # Network asset interface standard (e.g., 'ERC721-C')
        "chain": extract(js1,"rehydrate['-14034333087'].data.itemByIdentifier.collection.chain.name"),               # Native settlement network layer host platform name ('Ethereum')
        "metadata_status": extract(js1,"rehydrate['-14034333087'].data.itemByIdentifier.metadataStorageLabel")      # Decentralization hosting infrastructure status flag
    }]
}
print(json.dumps(Data1,indent=4))