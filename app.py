from fastapi import FastAPI, File, HTTPException, UploadFile
# from pydantic import BaseModel, Field

app = FastAPI()

@app.post("/resume")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded file: {file.filename}, containing: {contents}"}
