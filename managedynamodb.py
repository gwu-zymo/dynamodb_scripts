import boto3
import csv
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

def get_dynamodb_client():
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")
    #dynamodb = boto3.client("dynamodb", region_name="us-east-1", endpoint_url="http://localhost:8000")
    """ :type : pyboto3.dynamodb"""
    return dynamodb

def get_dynamodb_resource():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    """ :type : pyboto3.dynamodb"""
    return dynamodb

def scan_whole_table_for_items():
    filter_expression = Attr('Species').contains('unny') | Attr('Species').contains('eporidae') | Attr('Breed').contains('unny') | Attr('Breed').contains('eporidae')
    #filter_expression = Key('k_F_g_Cladosporium_s_Cladosporium_sp').gt(Decimal('0')) & Key('Breed').eq('French Bulldog')
    #projection_expression = "#rd, Run_Number, Tube_ID, #rd2, AMR1, Age, k_B_g_Staphylococcus_s_aureus, ITS"
    #ean = {"#rd": "k_F_g_Cladosporium_s_Cladosporium_sp", "#rd2": "Breed"}

    # filter_expression = Key('Patient_Name').between('A', 'S')
    # projection_expression = "#rd, Run_Number, Tube_ID, Breed, AMR1, Age, k_B_g_Staphylococcus_s_aureus, ITS"
    # ean = {"#rd": "Patient_Name", }

    # filter_expression = Key('k_F_g_Penicillium_s_Penicillium_polonicum').gt(Decimal('0'))

    # filter_expression = Attr('Sample_Type ').begins_with('Skin') | Attr('Sample_Type ').begins_with('skin')
    # filter_expression = Attr('Sample_Type ').contains('Skin') | Attr('Sample_Type ').contains('skin')
    # projection_expression = "#rd, Run_Number, Tube_ID, Breed, AMR1, Age, k_B_g_Staphylococcus_s_aureus, ITS, Health_Status_d"
    # ean = {"#rd": "Sample_Type ",}

    #filter_expression = Attr('Species').contains('Healthy') | Attr('Health_Status_d').contains('healthy')
    #filter_expression = Attr('Species').contains('Canine') | Attr('Sample_Type').contains('skin')
    #projection_expression = "#rd, Run_Number, Tube_ID, Breed, AMR1, Age, k_B_g_Staphylococcus_s_aureus, ITS"
    #ean = {"#rd": "Health_Status_d", }

    response = get_dynamodb_resource().Table("midog_test").scan(
        FilterExpression=filter_expression
        #ProjectionExpression=projection_expression,
        #ExpressionAttributeNames=ean
    )

    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = get_dynamodb_resource().Table("midog_test").scan(
            FilterExpression=filter_expression,
            #ProjectionExpression=projection_expression,
            #ExpressionAttributeNames=ean,
            ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])


    keys = []
    for sample in data:
        for key in sample.keys():
            if key not in keys:
                keys.append(key)

    output_file = open('selected_samples.csv', 'w')
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data)
    output_file.close()

    for sample in data:
        print(str(sample))


if __name__ == '__main__':
    scan_whole_table_for_items()

