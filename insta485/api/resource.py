"""REST API for resource."""
import flask
import insta485


@insta485.app.route('/api/v1/', methods=["GET"])
def get_resource():
    """Return API resource URLs."""
    context = {
        "posts": "/api/v1/p/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context), 200
