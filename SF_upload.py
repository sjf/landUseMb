#!/usr/bin/env python3

from data.utils import *
from data.log import *
from time import sleep
import requests
import json
from credentials import TOKEN
from pathlib import Path

FILE = get_arg(1, "sf_head_2.mbtiles")
TILESET_NAME = get_arg(2, Path(FILE).stem)
USERNAME = "sjf"
CREDENTIALS_URL = f"https://api.mapbox.com/uploads/v1/{USERNAME}/credentials?access_token={TOKEN}"
UPLOAD_URL = f"https://api.mapbox.com/uploads/v1/{USERNAME}?access_token={TOKEN}"

response = requests.post(CREDENTIALS_URL)
if response.status_code != 200:
  fail(response)

json_response = response.json()
log(json_response)

accessKeyId = json_response["accessKeyId"]
bucket = json_response["bucket"]
key = json_response["key"]
secretAccessKey = json_response["secretAccessKey"]
sessionToken = json_response["sessionToken"]
url = json_response["url"]

run(f'AWS_ACCESS_KEY_ID={accessKeyId} AWS_SECRET_ACCESS_KEY={secretAccessKey} AWS_SESSION_TOKEN={sessionToken} ' +
    f'aws s3 cp {FILE} s3://{bucket}/{key} --region us-east-1')

headers = {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
body = json.dumps({'url': f"http://{bucket}.s3.amazonaws.com/{key}", 'tileset': f"{USERNAME}.{TILESET_NAME}" })
print(body)
response = requests.post(UPLOAD_URL, data=body, headers=headers)
if response.status_code not in [200, 201]:
  fail(response)

json_response = response.json()
log(json_response)
upload_id = json_response['id']

UPLOAD_STATUS_URL = f"https://api.mapbox.com/uploads/v1/sjf/{upload_id}?access_token={TOKEN}"
while True:
  sleep(5)
  log(UPLOAD_STATUS_URL)
  response = requests.get(UPLOAD_STATUS_URL)
  if response.status_code != 200:
    fail(response)
  json_response = response.json()
  log(json_response)
  if json_response['complete']:
    break