import subprocess
import json
import sys, uuid, string, random

if __name__ == "__main__":
    print(random.choice(string.ascii_letters) + uuid.uuid4().hex)

