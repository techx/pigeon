from server import app

@app.route('/api/upload', methods=['POST'])
def upload_document():
    data = request.get_json()
    