#!/usr/bin/env python
import sys
import logging
from flask import Flask, Response, request, abort
from functools import cache
import requests
import click


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

WEBSERVICE_URL = "https://tp.tcelectronic.com/TonePrintService.svc"
STATIC_XML_FILES = {
    "GetVersionsAndInfo": "xml/GetVersionsAndInfoResponse.xml",
    "GetAllToneprintsFullBeta": 'xml/toneprints.xml',
    "GetAllArtistsFullBeta": "xml/artists.xml",
    "GetAllEffectsFullBeta": "xml/effects.xml",
    "GetAllProductsFullBeta": "xml/products.xml",
    "GetAllSelectTypes": "xml/selecttypes.xml",
    "GetAllProductTypesFull": "xml/producttypes.xml"
}
ACTIONS_DATA = {}
ACTIONS = ('GetVersionsAndInfo', 'GetAllToneprintsFullBeta', 'GetAllArtistsFullBeta',
           'GetAllProductsFullBeta', 'GetAllEffectsFullBeta', 'GetAllProductTypesFull', 'GetAllSelectTypes')


app = Flask(__name__)


def patch_xml(action, xml_string):
    if action == "GetAllArtistsFullBeta":
        logger.info(f"Patch xml -> enable [edit artists toneprints]")
        xml_string = xml_string.replace("<a:CanBeEdited>false</a:CanBeEdited>", "<a:CanBeEdited>true</a:CanBeEdited>")
    return xml_string


def download_xml(action):
    payload = f"""<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><{action} xmlns = "http://tempuri.org/"><key>AX67D3F6A2YK8ZQ3_nothing</key></{action}></s:Body></s:Envelope>"""
    headers = {'Soapaction': f'"http://tempuri.org/ITonePrintService/{action}"',
               'Content-Type': 'text/xml; charset=utf-8'}
    response = requests.post(WEBSERVICE_URL, headers=headers, data=payload)
    if response.status_code == 200:
        logger.info(f"Response from Server: {response.status_code} - Length: {len(response.text)}")
        return response.text
    else:
        logger.error(f"Response error from server: {response.status_code}")
        logger.error(response.text)
        return None


def update_data(static_xml):
    global ACTIONS_DATA
    logger.info("Update xml")
    for action in ACTIONS:
        if not static_xml:
            logger.info(f"Get xml for action: {action}")
            xml = patch_xml(action, download_xml(action))
            if xml:
                ACTIONS_DATA[action] = xml
        else:
            logger.info(f"Get static xml for action: {action}")
            with open(STATIC_XML_FILES[action]) as f:
                ACTIONS_DATA[action] = f.read()


@cache
def get_response(action):
    return ACTIONS_DATA.get(action, None)


@app.route("/TonePrintService.svc",  methods=['POST'])
def fake_service():
    response = Response()
    action = request.headers.get('Soapaction', '').split('/')[-1].replace('"', '')
    if action:
        logger.info(f"Request for Action:{action}")
        logger.debug(f"Headers: {request.headers}")
        response_xml = get_response(action)
        if response_xml:
            response.data = response_xml
            return response
        else:
            logger.error(f"Unknown action: {action}")
            abort(404, 'Unknown action')
    else:
        logger.error("Missing action in request")
        abort(400, 'Missing action')


@click.command()
@click.option('-h', '--host', default="0.0.0.0", type=str, help='Listen host', show_default=True)
@click.option('-p', '--port', default=443, type=int, help='Listen port', show_default=True)
@click.option('--cert', default='ssl/cert.pem', type=click.Path(exists=True), help='Certificate File', show_default=True)
@click.option('--key', default='ssl/key.pem', type=click.Path(exists=True), help='Key File', show_default=True)
@click.option('--static-xml',is_flag=True, help="Update XML")
@click.option('--debug',is_flag=True, help="Debug mode")
def main(host, port, cert, key, static_xml, debug):
    logger.info("Toneprint Fake Server [starting...]")
    logger.info("Host: %s", host)
    logger.info("Port: %s", port)
    logger.info("Cert: %s", cert)
    logger.info("Key: %s", key)
    logger.info("Debug: %s", debug)
    update_data(static_xml)
    app.run(debug=debug, host=host, port=port, ssl_context=(cert, key))


if __name__ == "__main__":
    main()

