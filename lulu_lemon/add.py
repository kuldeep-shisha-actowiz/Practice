import json

with open(r'D:\OS_module practice\Add_file\lululemon.json','r') as f:
    data=json.load(f)

all_result=[]

for product_detail in data.get('hasVariant',[]):
    result={}

    Product_Id=product_detail.get('sku','')
    result['Product_ID']=Product_Id

    product_URL=product_detail.get("url",'')
    result["product_URL"]=product_URL

    product_name=product_detail.get("name",'')
    result["product_name"]=product_name

    Product_color=product_detail.get('color','')
    result['Product_Color']=Product_color

    Product_size=product_detail.get('size','')
    result['Product_Size']=Product_size

    Product_Image=product_detail.get('image','')
    result['Product_Image']=Product_Image

    for offer in product_detail.get('offers',[]):
        Product_price=offer.get('price',0.0)
        if Product_price:
            result['product_price']=Product_price
            break
    
    all_result.append(result)


print(json.dumps(all_result,indent=4))