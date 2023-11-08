from flask import Flask, request
from flask_cors import CORS
from classification_module import ClassificationSystem


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

#create classification model object
model = ClassificationSystem()

#Respond to classification request with the link received
@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    link = data['link'] 

    #if given link is not a naver blog review about restaurant, it is regarded as invalid link and return -1
    if not (link.startswith("https://blog.naver.com") or link.startswith("https://m.blog.naver.com")):
        print('System : Inalid page - Please give us any link of naver review about restaurants')
        return {'result': -1}

    #let model make classification about the link
    classification_result = model.Classification(link)

    #return result within variable named 'result', further control is passed to 'renderResult' method in App.js
    return {'result': classification_result}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)