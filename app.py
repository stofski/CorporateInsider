import typing

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
from ec2_metadata import ec2_metadata
import boto3
import json
from botocore.config import Config
from botocore.exceptions import ClientError
import RAG

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
#bedrock = boto3.client(service_name='bedrock-runtime', config=my_config)

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

@app.get("/RAG")
def RAG(prompt: str):
    secrets = get_secret()
    RAG_chain = RAG.setupRAG(secrets)
    output = RAG.runRAG(RAG_chain,prompt)
    return output

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

def get_secret():

    secret_name = "OPENAI"
    region_name = "us-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # returns in this format:
    # {"OPENAI_API_KEY":"<secret>","LANGCHAIN_API_KEY":"<secret>"}
    return get_secret_value_response['SecretString']