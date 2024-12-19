from flask import Response

import json

class ResponseBuilder(object):
    def __init__(self):
        pass

    def jsonresponsebuilder(mssg, status_code, error_code = 0):
        response_headers = {"Content-Type": "application/json"}
        if status_code == 200:
            mssg_body = {"result":mssg}
        else:
            mssg_body = {"errorcode":error_code, "errormmessage":mssg}
        return Response(json.dumps(mssg_body), status=status_code,headers=response_headers)