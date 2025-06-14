from fastapi import FastAPI
from pydantic import BaseModel
from embeddings import search_answers
import base64
import os
import uuid

app = FastAPI()

class AskRequest(BaseModel):
    question: str
    image: str | None = None  # base64 string of the image (optional)

@app.post("/api/")
async def ask(request: AskRequest):
    print("Received question:", request.question)
    image_note = ""

    if request.image:
        try:
            # Decode and save the base64 image
            image_bytes = base64.b64decode(request.image)
            filename = f"image_{uuid.uuid4().hex}.webp"
            filepath = os.path.join("images", filename)
            os.makedirs("images", exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(image_bytes)

            image_note = f"\n\n(An image was submitted by the user: {filename})"
        except Exception as e:
            image_note = f"\n\n(Note: Failed to process image - {e})"

    try:
        response = search_answers(request.question, extra_note=image_note)
        return response
    except Exception as e:
        print("Error in answering:", e)
        return {"answer": f"Error: {e}", "links": []}
