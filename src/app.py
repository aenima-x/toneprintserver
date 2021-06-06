#!/usr/bin/env python

from flask import Flask, Response, request, abort

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
    file_path = responses_files.get(action, None)
    if file_path:
        print(f'File: {file_path} for action: {action}')
        with open(file_path) as f:
            data = f.read()
        return data
    else:
        return None


@app.route("/TonePrintService.svc",  methods=['POST'])
def fake_service():
    print("--------------------------------")
    print("Headers: ", request.headers)
    response = Response()
    action = request.headers.get('Soapaction', '').split('/')[-1].replace('"', '')
    if action:
        print("Action:", action)
        response_text = get_response(action)
        if response_text:
            response.data = response_text
            return response
        else:
            abort(404, 'Unknown action')
    else:
        abort(400, 'Missing action')

if __name__ == "__main__":
    app.run(debug=True, port=443, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))