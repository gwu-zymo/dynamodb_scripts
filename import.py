import csv
import boto3
from decimal import Decimal
import sys

maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

float_list = ["ct_16S", "ct_ITS", "ct_AMR1", "ct_AMR2", "ct_AMRm", "Age_Years", "total_abs_in_cp_nr"]
date_list = []

def convert_csv_to_json_list(file):
    items = []
    with open(file, newline='', encoding = "utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data = {}
            print(row['Internal_Sample_ID'], row['Gender'])
            for key in row:
                if key != None:
                    if row[key] != '':
                        val = row[key]
                        if val == '0':
                            val = None
                        elif key in float_list or key.startswith('k_') or key.startswith('d_'):
                            try:
                                val = Decimal(val)
                            except:
                                pass
                        data[key] = val
            items.append(data)
    return items

def removeEmptyString(lst):
    nl = []
    for dic in lst:
        for e in dic:
            if isinstance(dic[e], dict):
                dic[e] = removeEmptyString(dic[e])
            if (isinstance(dic[e], str) and dic[e] == ""):
                dic[e] = None
            if isinstance(dic[e], list):
                for entry in dic[e]:
                    removeEmptyString(entry)
        nl.append(dic)
    return nl

def batch_write(items):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
#endpoint_url="http://localhost:8000"
    db = dynamodb.Table('midog_test')

    with db.batch_writer() as batch:
        for item in items:
            print(item['Internal_Sample_ID'])
            batch.put_item(Item=item)


if __name__ == '__main__':
    json_data = convert_csv_to_json_list('./abundance.csv')
    json_data_m = removeEmptyString(json_data)
    batch_write(json_data_m)
