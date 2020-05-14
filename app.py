import hashlib
import json
import os

from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, request, jsonify


def user_id(data):
    return hashlib.md5('{name} 6_)6hF_qHPxV$_TzPPG9d@nhHY3j&+8-q!W]Gs&/'.format(**data).encode('utf-8')).hexdigest()


def user_dict(data):
    return {
        'device_id': str(data['device_id']),
        'name': str(data['name']),
        'score': int(data['score'])
    }


# Initialize Flask App
app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('firebase.json')
firebase_app = initialize_app(cred)
db = firestore.client()
collection = db.collection('users')


@app.route('/')
def root():
    return 'OK', 200


@app.route('/save', methods=['POST', 'PUT'])
def save():
    data = request.get_json(force=True)
    print('Received SAVE data: {}'.format(data))
    user_ref = collection.document(user_id(data))
    user = user_ref.get()
    if user.exists:
        user_d = user.to_dict()
        if user_d['device_id'] == data['device_id']:
            if user_d['score'] < data['score']:
                user_ref.set(user_dict(data))
                return 'Update user score', 200
            else:
                return 'Skip lower score', 200
        else:
            return 'Different device ID', 403
    else:
        user_ref.set(user_dict(data))
        return 'Save new user', 200


@app.route('/top', methods=['GET'])
def top():
    query = collection.order_by('score', direction=firestore.Query.DESCENDING).limit(10)
    data = [{'score': x.to_dict()['score'], 'name': x.to_dict()['name']} for x in query.stream()]
    return jsonify({'RecordsList': data})


port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
