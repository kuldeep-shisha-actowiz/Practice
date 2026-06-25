import json

def read_file(path):
    with open(path,'r',encoding='utf-8')as file:
        return json.load(file)
data=read_file(r'D:\Practice\Ajio\AJIO-2.json')

# All_product=[]


product_=data.get('product',{}).get('productDetails',{})

Rating_detail=product_.get('ratingsResponse',{})

# .get('aggregateRating',{})
price_data = product_.get("price", {})
product_img = product_.get('images',[])

product= data.get('product',{}).get('productDetails',{}).get('variantOptions',[])

Details={}
Details["Brand_Name".lower()]=product_.get('brandName','')
Details['Product_ID'.lower()]=product_.get("baseProduct")
Details['sku'.lower()]=product_.get("code")
Details['Product_Name'.lower()]=product_.get("name")
Details['Product_Price'.lower()]=product_.get("price", {}).get("value")
Details['Product_MRP'.lower()]=product_.get("wasPriceData", {}).get("value")
Details['Discount'.lower()]=f'{product_.get("price", {}).get("discountValue")}%'
Details['Product_URL'.lower()]=f'https://www.ajio.com{product_.get("url")}'

Details["Different_Sizes".lower()]=[
         size.get("scDisplaySize")
         for size in product_.get("variantOptions", [])]

Details['main_img'.lower()] = product_img[0].get('url','') if product_img else ""
Details['other_img'.lower()] = [img.get("url", "") for img in product_img[1:]]
Details['Colour'.lower()]=product_.get("verticalColor")


Details['Average_rating'.lower()]=Rating_detail.get('aggregateRating',{}).get('averageRating',0.0)
Details['Rating_Count'.lower()]=Rating_detail.get('aggregateRating',{}).get('numUserRatings',0)


Details['Product_details'.lower()]= { 
        "Primary_Color".lower():product_.get("verticalColor"),
        "Fit".lower():data.get('product').get('sizeData',{}).get('fittingType',''),
        "Package_Contain".lower():data.get('product').get('productDetails').get('sectionOne').get('featureData')[2].get('featureValues')[0].get('value'),
        "Washcare".lower():data.get('product').get('productDetails').get('sectionOne').get('featureData')[3].get('featureValues')[0].get('value'),
        "Transparency".lower():data.get('product').get('productDetails').get('sectionOne').get('featureData')[4].get('featureValues')[0].get('value'),
        "Size".lower():data.get('product').get('productDetails').get('sectionOne').get('featureData')[5].get('featureValues')[0].get('value'),
        "Mood".lower():data.get('product').get('productDetails').get('sectionOne').get('featureData')[6].get('featureValues')[0].get('value'),
        "Fabric_Composition".lower():data.get('product').get('productDetails').get('sectionOne').get('featureData')[7].get('featureValues')[0].get('value'),
        "Length".lower():data.get('product').get('productDetails').get('sectionOne').get('featureData')[8].get('featureValues')[0].get('value'),
        "Sleeve".lower():data.get('product').get('productDetails').get('sectionOne').get('featureData')[9].get('featureValues')[0].get('value'),
        
        
        "Product_ID".lower(): product_.get("baseProduct"),
        f"{product_.get('variantOptions')[1].get('mandatoryInfo')[0].get('key')}".lower().replace(' ','_'):f"{product_.get('variantOptions')[1].get('mandatoryInfo')[0].get('title')}{product_.get('variantOptions')[1].get('mandatoryInfo')[0].get('subTitle')}", 
        f"{product_.get('mandatoryInfo')[0].get('key')}".lower().replace(' ','_'):product_.get('mandatoryInfo')[0].get('title'),
        f"{product_.get('mandatoryInfo')[1].get('key')}".lower().replace(' ','_'):product_.get('mandatoryInfo')[1].get('title'),
        f"{product_.get('mandatoryInfo')[2].get('key')}".lower().replace(' ','_'):product_.get('mandatoryInfo')[2].get('title'),
        f"{product_.get('mandatoryInfo')[3].get('key')}".lower().replace(' ','_'):product_.get('mandatoryInfo')[3].get('title'),
        f"{product_.get('mandatoryInfo')[4].get('key')}".lower().replace(' ','_'):product_.get('mandatoryInfo')[4].get('title'),
        f"{product_.get('mandatoryInfo')[5].get('key')}".lower().replace(' ','_'):product_.get('mandatoryInfo')[5].get('title'),
}

with open('ajio2_detail.json','w')as file:
    json.dump(Details,file,indent=4)
    