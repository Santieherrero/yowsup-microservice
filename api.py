from flask import Flask, request
from flasgger import Swagger
from nameko.standalone.rpc import ClusterRpcProxy
from flasgger.utils import swag_from
import logging
import os

app = Flask(__name__)
Swagger(app)

CONFIG = {'AMQP_URI': "pyamqp://guest:guest@localhost"}

@app.route('/send', methods=['GET','POST'])
@swag_from('docs/send.yml')
def send():
    logger = app.logger
    valid_auth = verify_auth(request.headers,logger)
    logger.info(valid_auth)
    if not valid_auth:
        return "Unauthorized for this action", 401
    type = request.json.get('type')
    body = request.json.get('body')
    address = request.json.get('address')
    logger.info('Get message: %s,%s,%s' % (type,body,address))

    with ClusterRpcProxy(CONFIG) as rpc:
        # asynchronously spawning and email notification
        rpc.yowsup.send(type,body,address)

    msg = "The message was sucessfully sended to the queue"
    return msg, 200

def verify_auth(headers,logger):
    if headers["Authorization"]:
        auth = request.headers["Authorization"]
        logger.info('Token => ' + auth)
        if(auth == 'TOKEN_AU'):
            return True
        else:
            return False
    else:
        return False

if __name__ == "__main__":
	app.run(debug=True) #,host='0.0.0.0', port=80
