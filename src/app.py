#!/usr/bin/env python

from flask import Flask, Response, request

app = Flask(__name__)

responses_files = {
    "GetVersionsAndInfo": "xml/GetVersionsAndInfoResponse.xml",
    "GetAllToneprintsFullBeta": 'xml/toneprints.xml',
    "GetAllArtistsFullBeta": "xml/artists.xml",
    "GetAllEffectsFullBeta": "xml/effects.xml",
    "GetAllProductsFullBeta": "xml/products.xml",
    "GetAllSelectTypes": "xml/selecttypes.xml",
    "GetAllProductTypesFull": "xml/producttypes.xml"
}


def get_response(action):
    file_path = responses_files.get(action)
    print(f'File: {file_path} for action: {action}')
    with open(file_path) as f:
        data = f.read()
    return data


@app.route("/TonePrintService.svc",  methods=['POST'])
def fake_service():
    print("--------------------------------")
    print("Headers: ", request.headers)
    response = Response()
    action = request.headers['Soapaction'].split('/')[-1].replace('"', '')
    print("Action:", action)

    response_text = get_response(action)
    response.data = response_text
    return response


if __name__ == "__main__":
    app.run(debug=True, port=443, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))