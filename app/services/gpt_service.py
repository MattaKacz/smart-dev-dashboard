import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_logs(log_text: str) -> str:
    system_prompt = "Jesteś ekspertem DevOps. Twoim zadaniem jest przeanalizować logi i wskazać potencjalne przyczyny błędów oraz zaproponować rozwiązania."
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": log_text}
        ],
        temperature=0.3,
    )
    
    return response.choices[0].message.content.strip()
