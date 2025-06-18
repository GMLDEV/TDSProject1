



from fastapi import FastAPI, Request
from pydantic import BaseModel
import base64
import io
from PIL import Image
app = FastAPI()
class AskPayload(BaseModel):
    question: str
    image: str = None  # optional

@app.post("/api/")
async def answer_question(payload: AskPayload):
    question = payload.question
    image_data = payload.image

    if image_data:
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            # Optional: run OCR on image and add to question
        except Exception as e:
            print("Invalid image:", e)

    result = search_answers(question)  # Your function
    return result

