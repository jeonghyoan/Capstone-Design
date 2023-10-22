from flask import Flask, request, jsonify
from classification_module import ClassificationSystem

app = Flask(__name__)
classifier = ClassificationSystem()

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    url = data['url']
    result = classifier.Classification(url)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run()
