import csv
import requests

usage_data=[]
with open("usage_data.csv", "r") as file:
    reader=csv.DictReader(file)
    for row in reader:
        clean_data={k: v.strip() for k,v in row.items()}
        usage_data.append(clean_data)

# print(usage_data)
valid_rows=[]
invalid_rows=[]

for row in usage_data:
    units=row['units'].strip()
    price_per_unit=row['price_per_unit'].strip()
    usage_type=row['usage_type'].strip()

    if units.isdigit() and price_per_unit.replace('.','',1).isdigit() and usage_type !='':
        valid_rows.append({
            "customer_id":row["customer_id"],
            "usage_type":usage_type,
            "units":int(units),
            "price_per_unit":float(price_per_unit)
        })
    else:
        invalid_rows.append({
            "customer_id":row["customer_id"],
             "Reason":"Missing data"})

# print("Valid data: ",valid_rows)
# print("Invalid Data: ",invalid_rows)

grouped_data={}
for row in valid_rows:
    cid=row['customer_id']
    if cid not in grouped_data:
        grouped_data[cid]=[]

    grouped_data[cid].append(row)

#print(grouped_data)
billing_data=[]
for cid, records in grouped_data.items():
    total_amount=0
    breakdown={}
    for row in records:
        usg_type=row["usage_type"]
        amount=row["units"]*row["price_per_unit"]
        total_amount+=amount
        breakdown[usg_type]=amount

    billing_data.append({
        "customer_id":cid,
        "total_amount":total_amount,
        "breakdown":breakdown
    })
# print("Billing data: ")
# print(billing_data)

url="https://jsonplaceholder.typicode.com/posts"
success_count=0
fail_count=0
total_revenue=0

for customer in billing_data:
    cid=customer["customer_id"]
    amt=customer["total_amount"]

    try:
        response=requests.post(url,json=customer)
        response.raise_for_status()

        print(f"Customer with {cid} is successfully billed | Status: {response.status_code}")
        success_count+=1
        total_revenue+=amt

        with open("billing_log.txt","a") as file:
            file.write(f"SUCCESS: Customer {cid} billed | Amount: {amt}\n")

    except requests.exceptions.HTTPError as e:
        fail_count+=1
        with open("billing_log.txt","a") as file:
            file.write(f"Failed: Customer {cid} | Reason :{e}\n")
        print("Failed for customer {cid) -> {e}")

print("\n===== BILLING SUMMARY =====")
print(f"Total customers billed: {len(billing_data)}")
print(f"Successful: {success_count}")
print(f"Failed: {fail_count}")
print(f"Total revenue: {total_revenue}")