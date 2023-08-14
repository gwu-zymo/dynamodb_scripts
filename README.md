# dynamodb_scripts

1.	Start an instance on EC2 from service catalog
2.	Setup boto3:
a.  sudo apt update
b.  sudo apt install python3-pip 
c.	pip install boto3
4.	get TOC ready
5.	get the scripts: https://github.com/gwu-zymo/dynamodb_scripts 
6.	run pull.py to pull abundance data from S3, resulting in a large table with both metadata and species abundance data
7.	run import.py to load it onto DynamoDB
8.	run managedynamodb.py for queries; https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/LegacyConditionalParameters.KeyConditions.html 
