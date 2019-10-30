# Deploy magic: 6
import json, os
import psycopg2

host     = os.environ['HOST_NAME']
database = os.environ['DB_NAME']
user     = os.environ['USERNAME']
password = os.environ['PASSWORD']

def sqli_vulnerable(event, context):
    body = {}

    if event["queryStringParameters"] is not None:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)

        vulnString = str(event["queryStringParameters"].get("vuln-string"))
        
        body["result"] = "Success"
        body["vulnString"] = vulnString
        
        query = "SELECT * FROM test WHERE username='%s'" % vulnString

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

        conn.close()
    else:
        body["result"] = "Please inject some SQL with ?vuln-string="
    
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    
    return response


def sqli_secure(event, context):
    body = {}

    if event["queryStringParameters"] is not None:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        vulnString = event["queryStringParameters"].get("vuln-string")
        
        body["result"] = "Success"
        body["vulnString"] = vulnString
        
        query = "SELECT * FROM test WHERE username='%s'" % vulnString

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        cur.execute("SELECT * FROM test WHERE username='%s'", (vulnString, ))
        
        # display the result
        result = cur.fetchone()
        
        # close the communication with the PostgreSQL
        cur.close()
        
        body["query"] = query
        body["result"] = result
        conn.close()
    else:
        body["result"] = "Please inject some SQL with ?vuln-string="

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
