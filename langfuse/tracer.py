from langfuse import Langfuse
import os

# Read from env or hardcode during development
langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-lf-"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-lf-"),
    base_url=os.getenv("LANGFUSE_BASE_URL", "https://us.cloud.langfuse.com")
)

# Drop-in replacement to get full logging by changing only the import
# from langfuse.openai import OpenAI
 
# # Configure the OpenAI client to use http://localhost:11434/v1 as base url 
# client = OpenAI(
#     base_url = 'http://localhost:11434/v1',
#     api_key='ollama', # required, but unused
# )
 
# response = client.chat.completions.create(
#   model="llama3.1",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who was the first person to step on the moon?"},
#     {"role": "assistant", "content": "Neil Armstrong was the first person to step on the moon on July 20, 1969, during the Apollo 11 mission."},
#     {"role": "user", "content": "What were his first words when he stepped on the moon?"}
#   ]
# )
# print(response.choices[0].message.content)