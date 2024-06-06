import typing

from fastapi import FastAPI, File, HTTPException, UploadFile
# from pydantic import BaseModel, Field
from ec2_metadata import ec2_metadata
import boto3
import json
from botocore.config import Config
import botocore.session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

my_config = Config(
    region_name = ec2_metadata.region,
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)
bedrock = boto3.client(service_name='bedrock-runtime', config=my_config)

@app.get("/test")
def test():
    return "Hello World!"

@app.post("/resume")
def resume(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded file: {file.filename}, containing: {contents}"}

@app.get("/mlTest")
def ml_test(prompt: str):
    body = json.dumps({
        "prompt": f"\n\nHuman:Structure your response in html tags. Format your response as a single line. {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 800,
        "temperature": 0.1,
        "top_p": 0.9,
    })
    
    modelId = 'anthropic.claude-v2'
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

    response_body = json.loads(response.get('body').read())

    # text
    return response_body.get('completion')

@app.get("/whichJob")
def which_job(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded file: {file.filename}, containing: {contents}"}
