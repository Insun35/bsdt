import base64
from openai import OpenAI
from utils.config import OPENAI_API_KEY 

client = OpenAI(api_key=OPENAI_API_KEY)

def classify_image(path: str) -> tuple[str,str]:
    with open(path, "rb") as f:
        img_bytes = f.read()
    base64_img = base64.b64encode(img_bytes).decode('utf-8')

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Classify the following image into one of: "
                    "'bird', 'insect', 'human', 'leaf', 'others'. "
                    "Then give a brief reason."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_img}"
                    }
                }
            ]
        }],
        max_tokens=300
    )
    
    return resp.choices[0].message.content
