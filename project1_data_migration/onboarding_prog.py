import csv
import requests

customers=[]
subscriptions=[]
usage=[]

with open("customers.csv","r") as file:
    reader=csv.DictReader(file)
    for row in reader:
        clean_data={k:v .strip() for k,v in row.items()}
        customers.append(clean_data)

with open("subscriptions.csv") as file:
    reader=csv.DictReader(file)
    for row in reader:
        clean_data={k: v.strip() for k,v in row.items()}
        subscriptions.append(row)

with open("usage.csv") as file:
    reader=csv.DictReader(file)
    for row in reader:
        clean_data={k: v.strip() for k,v in row.items()}
        usage.append(row)

# print(customers)
# print(subscriptions)
# print(usage)

subs_dict={}
usage_dict={}
for row in subscriptions:
    cust_id=row["customer_id"]
    subs_dict[cust_id]=row

for row in usage:
    cust_id=row["customer_id"]
    usage_dict[cust_id]=row

#print(subs_dict['101'])
# print(subs_dict)
# print(usage_dict)

val_data=[]
invalid_data=[]

for customer in customers:
    cid=customer["customer_id"]
    subs=subs_dict.get(cid)
    usage_=usage_dict.get(cid)

    if subs is None or usage_ is None:
        invalid_data.append({"customer_id":cid,"Reason":"Missing subscription or usage_data"})
        continue
    else:
        plan = subs["plan"].strip()
        price = subs["price"].strip()
        units = usage_["usage_units"].strip()
        email = customer["email"].strip()
        name=customer["name"].strip()

        if plan != '' and price.isdigit() and units.isdigit() and email != "":
            val_data.append({"customer_id":cid, "name":name, "email":email, "plan":plan, "price": int(price), "usage_units":int(units)})

        else:
            invalid_data.append({"customer_id":cid, "name":name, "reason":"Missing email / invalid price / invalid usage"})

for row in val_data:
    row["Total_Amount"]=row["price"] + row["usage_units"]*2

success_count=0
fail_count=0
total_amt=0

url="https://jsonplaceholder.typicode.com/posts"
for row in val_data:
    data = row["customer_id"]
    amt = row["Total_Amount"]
    try:
        response=requests.post(url,json=row)
        response.raise_for_status()

        print("Created ID: ",response.json()["id"])
        print("Status: ",response.status_code)

        success_count+=1
        total_amt+=amt
        with open("migration_log.txt","a") as file:
            file.write(f"SUCCESS : customer { data } onboarded | Amount : {amt} \n")

    except requests.exceptions.HTTPError as e:
        fail_count+=1
        with open("migration_log.txt","a") as file:
            file.write(f"FAILED : customer { data } | Reason: {e}\n")
        print(f"Failed for customer {data} -> {e}")



# print("Valid Data: ")
# print(val_data)
# print("Invalid Data: ")
# print(invalid_data)

print("\n===== SUMMARY REPORT =====")
print(f"Total processed: {len(val_data)}")
print(f"Successful: {success_count}")
print(f"Failed: {fail_count}")
print(f"Total revenue: {total_amt}")