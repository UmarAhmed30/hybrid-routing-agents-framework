from langfuse import Langfuse
import os
from dotenv import load_dotenv

load_dotenv()

# Read from env or use empty config for development
secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")

if secret_key and public_key:
    langfuse = Langfuse(
        secret_key=secret_key,
        public_key=public_key,
        base_url=os.getenv("LANGFUSE_BASE_URL", "https://us.cloud.langfuse.com")
    )
else:
    # Create a disabled Langfuse instance if no credentials
    langfuse = Langfuse(
        secret_key="placeholder",
        public_key="placeholder",
        base_url="http://localhost:54321",  # Disabled mode
    )
