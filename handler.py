# Deploy magic: 7
import json, os, uuid
import psycopg2
import jwt
import base64
import boto3
import requests

identifier = ''
if 'IDENTIFIER' in os.environ:
    identifier = os.environ['IDENTIFIER']
    database = os.environ['DB_NAME']
    user = os.environ['USERNAME']
    password = os.environ['PASSWORD']

print('Fetch RDS hostname')
print(os.environ['AWS_SECRET_ACCESS_KEY'], os.environ['AWS_ACCESS_KEY_ID'])
source = boto3.client('rds', region_name='ap-southeast-2')
instances = source.describe_db_instances(DBInstanceIdentifier=identifier)
host = instances.get('DBInstances')[0].get('Endpoint').get('Address')
print(host)


def setup_mock_data():
    body = {}
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)

    body["result"] = "Success"
    create_query = "CREATE TABLE IF NOT EXISTS test (username text PRIMARY KEY)"
    delete_query = "DELETE FROM test"
    # create a cursor
    cur = conn.cursor()

    # create table
    cur.execute(create_query)
    cur.execute(delete_query)
    for value in ['username1', 'username2', 'username3']:
        cur.execute("INSERT INTO test values ('{username}')".format(username=value))
    # display the result
    conn.commit()
    result = cur.fetchall()

    # close the communication with the PostgreSQL
    cur.close()

    body["query"] = create_query
    body["result"] = result

    conn.close()

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def sqli_vulnerable(event, context):
    setup_mock_data()
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
        result = cur.fetchall()

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
    setup_mock_data()
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
        cur.execute("SELECT * FROM test WHERE username='%s'", (vulnString,))

        # display the result
        result = cur.fetchall()

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


def myjwt_encode(data):
    return jwt.encode(data, password, algorithm='HS256')


def myjwt_decode(data):
    try:
        header = data.split('.')[0]
        header += '=' * (-len(header) % 4)
        alg = json.loads(base64.b64decode(header).decode())['alg']
    except:
        return None

    return jwt.decode(data, password, algorithms=['HS256'], verify=(alg != "none"))


def myjwt_decode_secure(data):
    try:
        return jwt.decode(data, password, algorithms=['HS256'])
    except:
        return None


def jwt_insecure(event, context):
    return do_jwt(event, context, myjwt_encode, myjwt_decode)


def jwt_secure(event, context):
    return do_jwt(event, context, myjwt_encode, myjwt_decode_secure)


def do_jwt(event, context, myjwt_encode, myjwt_decode):
    ret = lambda code, msg: {'statusCode': code, 'body': json.dumps({'result': msg})}
    get_params = event['queryStringParameters']

    if get_params is None or 'action' not in get_params:
        return ret(400, 'Please specify an action using ?action=')

    if get_params['action'] == 'new':
        jwt = myjwt_encode({'admin': 0}).decode()
        return ret(200, jwt)
    elif get_params['action'] == 'public':
        if 'token' not in get_params:
            return ret(401, 'Please request a token from ?action=new first')
        else:
            jwt = myjwt_decode(get_params['token'])
            return (
                ret(400, 'Invalid jwt') if jwt is None else
                ret(200, f'Hello {"admin" if jwt["admin"] == 1 else "user"}!')
            )
    elif get_params['action'] == 'secret':
        if 'token' not in get_params:
            return ret(401, 'Please request a token from ?action=new first')
        jwt = myjwt_decode(get_params['token'])
        if jwt is None: return ret(400, 'Invalid jwt')

        if jwt['admin'] != 1:
            return ret(403, 'You are not admin. Go away!')
        else:
            return ret(200, 'Hi admin! The secret is "password" (jk its not actually)')
    else:
        return ret(404, f'Unknown action {get_params["action"]}')


def ssrf_secure(event, context):
    ret = lambda code, msg: {'statusCode': code, 'body': json.dumps({'result': msg})}
    url = event["queryStringParameters"].get("url")
    proxies = {
        "http": "http://10.10.1.10:3128",
        "https": "http://10.10.1.10:1080",
    }
    # User is only allowed to get requests for unsw.com domain
    os.environ['NO_PROXY'] = 'unsw.com'
    # User is only allowed to pass through the proxy which only accept certain domains
    r = requests.get(url=url, proxies=proxies)
    return ret(r.status_code, r.content)


def ssrf_insecure(event, context):
    ret = lambda code, msg: {'statusCode': code, 'body': json.dumps({'result': msg})}
    url = event["queryStringParameters"].get("url")
    proxies = {
        "http": None,
        "https": None,
    }
    # Supposed to return contents of file user gives. But can be used for any purpose.
    r = requests.get(url=url, proxies=proxies)
    return ret(r.status_code, r.content)