import boto3

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
db = dynamodb.Table('midog_test')
        
response = db.update_item(
    Key={
        'ReleaseNumber': releaseNumber,
        'Timestamp': result[0]['Timestamp']
    },
    UpdateExpression="set Sanity = :r",
    ExpressionAttributeValues={
        ':r': 'false',
    },
    ReturnValues="UPDATED_NEW"
)

    with db.batch_writer() as batch:

        
        
        
