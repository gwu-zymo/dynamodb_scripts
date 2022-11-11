import boto3

response = table.update_item(
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
