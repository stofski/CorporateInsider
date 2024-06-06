import typing

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
from ec2_metadata import ec2_metadata
import boto3
import json
from botocore.config import Config
from botocore.exceptions import ClientError

import os
import bs4
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import CSVLoader

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
    RAG_chain = setupRAG(secrets)
    output = runRAG(RAG_chain,prompt)
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

def setupRAG(secrets): 
    
    os.environ["OPENAI_API_KEY"] = secrets["OPENAI_API_KEY"]
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = secrets["LANGCHAIN_API_KEY"]
    loader = CSVLoader("amazon_jobs_dataset.csv")
    docs = loader.load()

    # Load, chunk and index the contents of the blog.
    bs_strainer = bs4.SoupStrainer(class_=("post-content", "post-title", "post-header"))
    loader = WebBaseLoader(
        web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
        bs_kwargs={"parse_only": bs_strainer},
    )

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

    # Retrieve and generate using the relevant snippets of the blog.
    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)


    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)
    
    return rag_chain_with_source

def runRAG(rag_chain,question):
    output = {}
    curr_key = None
    for chunk in rag_chain.stream(question):
        for key in chunk:
            if key not in output:
                output[key] = chunk[key]
            else:
                output[key] += chunk[key]
#             if key != curr_key:
#                 print(f"\n\n{key}: {chunk[key]}", end="", flush=True)
#             else:
#                 print(chunk[key], end="", flush=True)
            curr_key = key
    return output["answer"]
