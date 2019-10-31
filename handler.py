import json, os
import html

def xss_vulnerable(event, context):
    body = {}

    if event["body"] is not None and event["body"] is not None:
        

        username = event["body"]["username"]
        password = html.escape(event["body"]["password"])

        # Lets pretend a silly business is emailing their clients
        # their usernames and passwords for 'safe' keeping, after
        # they have signed up to the businesses service.
        # The api return may look something like this, afterwhich the
        # username and password can be formatted into an email 
        body["body"] = username + password
    else:
        body["message"] = "No username or password POSTed"

    response = {
        "statusCode": 200,
        "body": json.dumps(event)
    }
    
    return response