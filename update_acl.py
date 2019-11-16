import subprocess
import json
import sys

if __name__ == "__main__":
    output = subprocess.Popen(f'aws s3api get-object-acl --bucket {sys.argv[1]} --key {sys.argv[2]}',
                              stdout=subprocess.PIPE, shell=True)
    data = json.loads(output.stdout.read())
    open_read = {
        "Grantee": {
            "Type": "Group",
            "URI": "http://acs.amazonaws.com/groups/global/AllUsers"
        },
        "Permission": "READ"
    }
    data['Grants'].append(open_read)
    with open('acl.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    f.close()
