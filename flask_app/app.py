from flask import Flask, request
from flask_cors import CORS
from classification_module import ClassificationSystem


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

model = ClassificationSystem()

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    link = data['link'] 

    if not (link.startswith("https://blog.naver.com") or link.startswith("https://m.blog.naver.com")):
        return {'result': -1}

    classification_result = model.Classification(link)

    return {'result': classification_result}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)