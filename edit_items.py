import boto3

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
db = dynamodb.Table('midog_test')
        
response = db.update_item(
    Key={
        'Internal_Sample_ID': 'md0043_1',
        'Run_Number': 'RUN0043'
    },
    UpdateExpression="set Bill = :r",
    ExpressionAttributeValues={
        ':r': 'NA',
    },
    ReturnValues="UPDATED_NEW"
)

   
