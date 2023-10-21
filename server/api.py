from server import app
from flask import request
import openai
openai.api_key = "YOUR_API_KEY" # replace with your API key
@app.route('/api/upload', methods=['POST'])
def upload_text():
    data = request.get_json()
    label = data['label']
    content = data['content']
    response = openai.Embedding.create(input = content, engine="text-embedding-ada-002")
    embedding = np.array([r["embedding"] for r in response['data']], d)