import json, os
import psycopg2

host     = os.environ['HOST_NAME']
database = os.environ['DB_NAME']
user     = os.environ['USERNAME']
password = os.environ['PASSWORD']
table    = os.environ['TABLE_NAME']

conn = psycopg2.connect(host=host, database=database, user=user, password=password)

def sqli_vulnerable(event, context):
    body = {}

    if event["queryStringParameters"] is not None:
        vulnString = event["queryStringParameters"].get("vuln-string")
        
        body["message"] = "Success"
        body["vulnString"] = vulnString
        
        query = "SELECT * FROM test WHERE username=%s" % vulnString

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        cur.execute(query)

        # display the result
        result = cur.fetchone()

        # close the communication with the PostgreSQL
        cur.close()

        body["query"] = query
        body["result"] = result
    else:
        body["message"] = "Please inject some SQL with ?vuln-string="
    
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    
    return response


def sqli_secure(event, context):
    body = {}

    if event["queryStringParameters"] is not None:
        vulnString = event["queryStringParameters"].get("vuln-string")
        
        body["message"] = "Success"
        body["vulnString"] = vulnString
        
        query = "SELECT * FROM test WHERE username=%s" % vulnString

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        cur.execute("SELECT * FROM test WHERE username=%s", (vulnString, ))
        
        # display the result
        result = cur.fetchone()
        
        # close the communication with the PostgreSQL
        cur.close()
        
        body["query"] = query
        body["result"] = result
    else:
        body["message"] = "Please inject some SQL with ?vuln-string="

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response