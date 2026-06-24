import json

def read_file(filepath):
    with open(filepath,'r') as f:
        return json.load(f)
    
file_data=read_file(r'D:\Practice\Nike\NYKAA.JSON')


def extract_product_details(data):
    variant=data.get('productPage',{}).get('product',{}).get('variants',[])

    Product_rating=data.get('productPage',{}).get('product',{}).get('rating',0.0)
    Product_rating_Count=data.get('productPage',{}).get('product',{}).get('ratingCount',0)
    offer_coupan=data.get('couponReducer',{}).get('coupons',{}).get('data',[])

    All_product=[]
    for Product_detail in variant:
        products={}
        products['Product_Brand']=Product_detail.get('brandName','')
        products['Product_URL']=f"https://www.nykaaman.com/{Product_detail.get('slug')}?"
        products['Product_Id']=Product_detail.get('sku','')
        products['Product_Name']=Product_detail.get('name','')
        products['Product_Rating']=Product_rating
        products['Product_Rating_Count']=Product_rating_Count
        products['Product_Main_Image']=Product_detail.get('imageUrl','')
        products['Product_Other_Images']=[Other_Image['url'] for Other_Image in Product_detail.get('media',[])]
        products['Product_Price']=Product_detail.get('offerPrice',0.0)
        products['Product_Discount']=f"{Product_detail.get('discount',0.0)}%"
        products['Product_MRP']=Product_detail.get('mrp',0.0)
        products['Product_Offer_Coupan']=offer_coupan

        All_product.append(products)

    print(json.dumps(All_product,indent=4))


extract_product_details(file_data)     
