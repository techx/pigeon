import openai
import numpy as np
from server.config import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY
def embed_text(content):
    """Returns embedding of content."""
    response = openai.Embedding.create(input=content, engine="text-embedding-ada-002")
    embeddings = np.array([r["embedding"] for r in response["data"]], dtype=np.float32)
    return embeddings[0]