import logging
import boto3
from boto3 import Session
from boto3 import resource
from contextlib import closing
from botocore.exceptions import BotoCoreError, ClientError
import uuid
import json

def to_speech(event, context):
    data = json.loads(event['body'])
    text = data['text']
    print("Text is " + text)
    
    bucket_name = 'cross-bose-speech'
    logging.info("Using bucket: %s" % bucket_name)

    session = Session(region_name="eu-west-1")
    polly = session.client("polly")
    s3 = resource('s3')
    bucket = s3.Bucket(bucket_name)

    logging.info("getting list of existing objects in the given bucket")

    filename = "%s.mp3" % str(uuid.uuid4())
    try:
     logging.info("Will try to synthesize " + text)
     response = polly.synthesize_speech(
             Text=text,
             OutputFormat="mp3",
             VoiceId="Joanna")
     with closing(response["AudioStream"]) as stream:
         bucket.put_object(Key=filename, Body=stream.read(), ACL='public-read')
    except BotoCoreError as error:
     logging.error(error)

    full_path = 'https://s3-eu-west-1.amazonaws.com/cross-bose-speech/' + filename

    print(full_path)

    payload = {
        "path": full_path
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(payload)
    }

    return response
