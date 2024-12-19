import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort


blp = Blueprint("stores",__name__,description="Operations on stores")


@blp.route("/store/<string:strong_id>")
class Store(MethodView):
    def get(self, strong_id):
        pass

