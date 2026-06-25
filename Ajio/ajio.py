import json
def ajio_extract(file_path):
   with open (r"D:\Practice\Ajio\AJIO-2.json","r",encoding="UTF-8") as f:
       data=json.load(f)    
       product = data.get("product", {}).get("productDetails", {})

   Product_data = {
    "BRAND": product.get("brandName"),
    "PRODUCT_ID": product.get("baseProduct"),
    "SKU": product.get("code"),
    "NAME": product.get("name"),
    "PRICE": product.get("price", {}).get("value"),
    "MRP": product.get("wasPriceData", {}).get("value"),
    "DISCOUNT_PERCENTAGE": product.get("price", {}).get("discountValue"),
    "RATINGS": product.get("ratingsResponse", {}).get("aggregateRating", {}).get("averageRating"),
    "RATED_COUNT": int(product.get("ratingsResponse", {}).get("aggregateRating", {}).get("numUserRatings", 0)),
    "PRODUCT_URL": "https://www.ajio.com" + product.get("url", ""),
    "MAIN_IMAGE": (
        product.get("images", [{}])[0].get("url")
        if product.get("images")
        else None
    ),
    "OTHER_IMAGES": list(dict.fromkeys(
        img.get("url")
        for img in product.get("images", [])[1:]
        if img.get("url")
    )),
    "AVAILABLE_SIZES": [
        size.get("scDisplaySize")
        for size in product.get("variantOptions", [])
    ],
    "COLOR": product.get("verticalColor"),
    "STOCK_STATUS": product.get("stock", {}).get("stockLevelStatus"),
    "RETURNABLE": product.get("isReturnable"),
}
   
   Product_details = product.get("featureData", [])
      


   Details={}

   for item in Product_details:
    key = item.get("name","").upper().replace(" ", "_")
    values = item.get("featureValues", [])

    if key and values:
        Details[key] = values[0].get("value")
        Product_data["product_details"]=Details
        
   

   for item in product.get("mandatoryInfo", []):
    key = item.get("key", "").upper().replace(" ", "_")
    value = item.get("title")

    if key and value:
        Details[key] = value

   
   Details["PRODUCT_ID"] = product.get("baseProduct")

   Details["MRP"] =( product.get("variantOptions",[])[0].get("mandatoryInfo",[])[0].get("title"))
   return Product_data
data = ajio_extract(r"D:\Practice\Ajio\ajio.json")
print(json.dumps(data,indent=4))

with open("ajio2_details.json","w") as f:
    json.dump(data,f,indent=4)
print("data saved")

