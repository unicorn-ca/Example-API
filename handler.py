import json
import lorem

def endpoint(event, context):
    s = lorem.sentence()

    return {
        'statusCode': 200,
        'body': json.dumps({
            'sentence': ''.join(reversed(s)).upper(),
            'length': len(s),
            'iteration': 5
        })
    }
