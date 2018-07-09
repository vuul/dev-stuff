import json
import logging
import requests
import random
from app_config import settings
from flask import Flask, request, jsonify

#========== Setup app config ==========#
app = Flask(__name__)
app.config['SECRET_KEY'] = settings['APP_KEY']
APP_NAME = settings['APP_NAME']
LOG_FILENAME = settings['LOG_FILE_PATH'].format(APP_NAME)

#========== Setup logging config ==========#
log = logging.getLogger(APP_NAME)
hdlr = logging.FileHandler(LOG_FILENAME)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.INFO)

#========== This could be moved into the settings ==========#
ERROR = {"response_type": "ephemeral","text": "Sorry, that didn't work. Please try again."}
URLS = { 'apple': { 'url':'https://api.iextrading.com/1.0/stock/aapl/batch?types=quote', 
                    'response_key': ['quote', 'latestPrice'],
                    'slack_data': '{"text": "AAPL: $%s"}' }, 
         'norris': { 'url': 'http://api.icndb.com/jokes/random',
                     'response_key': ['value','joke'],
                     'slack_data': '{"text": "%s"}' },
         'dogs': { 'url':'https://dog.ceo/api/breeds/image/random', 
                   'response_key': ['message'],
                   'slack_data': '{"attachments": [{"image_url":"%s"}]}' } }


def generate_slack_data(data_type, data):
  response_keys = URLS.get(data_type).get('response_key')
  response_value = None
  for i in response_keys:
    if response_value == None:
      response_value = data.get(i)
    else:
      response_value = response_value.get(i)

  slack_response = json.loads(URLS.get(data_type).get('slack_data') %(response_value))
  log.info(slack_response)
  return slack_response


@app.route('/api/1.0/challenge', methods=['POST'])
def get_info():
  remote_host = request.remote_addr
  request_text = str(request.form.get('text')).lower()
  if request_text == str():
    request_text = random.choice(URLS.keys())

  log.info('Request from {0}: {1}'.format(remote_host, request_text))
  res = None
  if request_text in URLS.keys():
    res = requests.get(URLS.get(request_text).get('url'))

  if res:
    the_json = res.json()
    log.info(the_json)
    slack_response = generate_slack_data(request_text, the_json)
    return jsonify(slack_response)
  else:
    return jsonify(ERROR)

