from openai import OpenAI

client = OpenAI(api_key="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDU0MDJAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.K64O0PbK3iKww6-DbegKFT9WSd9U6bImWlQRsr4ZENA")

def generate_answer(question, context):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{
            "role": "system",
            "content": f"Answer using: {context}"
        }, {
            "role": "user", 
            "content": question
        }]
    )
    return response.choices[0].message.content
