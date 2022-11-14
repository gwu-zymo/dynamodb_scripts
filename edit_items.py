import boto3

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
db = dynamodb.Table('midog_test')
        
response = db.update_item(
    Key={
        'Internal_Sample_ID': releaseNumber,
        'Run_Number': result[0]['Timestamp']
    },
    UpdateExpression="set Sanity = :r",
    ExpressionAttributeValues={
        ':r': 'false',
    },
    ReturnValues="UPDATED_NEW"
)

   
