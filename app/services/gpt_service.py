import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from app.core.logger import logger

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_logs(log_text: str) -> str:
    start_time = time.time()
    
    system_prompt = "You are a DevOps expert. Your task is to analyze logs and identify potential causes of errors and propose solutions."
    
    try:
        logger.debug("Sending request to OpenAI API")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": log_text}
            ],
            temperature=0.3,
        )
        
        duration = time.time() - start_time
        logger.info(f"OpenAI API response received in {duration:.3f}s")
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"OpenAI API error after {duration:.3f}s: {str(e)}")
        raise
