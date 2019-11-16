import json, os
import psycopg2
import boto3

identifier = ''
if 'IDENTIFIER' in os.environ:
    identifier = os.environ['IDENTIFIER']
    database = os.environ['DB_NAME']
    user = os.environ['USERNAME']
    password = os.environ['PASSWORD']

source = boto3.client('rds', region_name='ap-southeast-2')
instances = source.describe_db_instances(DBInstanceIdentifier=identifier)
host = instances.get('DBInstances')[0].get('Endpoint').get('Address')


def handler(event, context):
    body = {}
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)

    body["result"] = "Success"
    query = "CREATE TABLE IF NOT EXISTS test (username text PRIMARY KEY)"
    # create a cursor
    cur = conn.cursor()

    # create table
    cur.execute(query)
    for value in ['username1', 'username2', 'username3']:
        cur.execute("INSERT INTO test values ('{username}')".format(username=value))
    # display the result
    result = cur.fetchall()

    # close the communication with the PostgreSQL
    cur.close()

    body["query"] = query
    body["result"] = result

    conn.close()

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    pass
