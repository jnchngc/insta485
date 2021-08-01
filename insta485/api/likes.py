"""REST API for likes."""
import flask
import insta485
from insta485.api.helper_functions import check_login
from insta485.api.helper_functions import check_postid


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/',
                    methods=["GET", "DELETE", "POST"])
def get_likes(postid_url_slug):
    """Return likes on postid or deletes a like or posts a like."""
    # check if user is logged in
    logged_in_check = check_login()
    if not logged_in_check[1]:
        return flask.jsonify(**logged_in_check[0]), 403
    post_valid = check_postid(postid_url_slug)
    if not post_valid[1]:
        return flask.jsonify(**post_valid[0]), 404
    logname = flask.session['logname']
    connection = insta485.model.get_db()

    # check if logged in user likes this post
    logname_likes_this = len(connection.execute(
        "SELECT owner FROM likes WHERE owner=? AND postid=?",
        (logname, postid_url_slug,)).fetchall()
    )
    # declare JSON dictionary to fill in below
    context = {}

    # Return likes on postid
    if flask.request.method == 'GET':
        # get likes count of an individual post
        likes_count = len(connection.execute(
            "SELECT postid FROM likes WHERE postid =?",
            (postid_url_slug,)).fetchall()
        )
        # fill in JSON according to query results
        context = {
            "logname_likes_this": logname_likes_this,
            "likes_count": likes_count,
            "postid": postid_url_slug,
            "url": flask.request.path
        }
    # delete user's like for specified post
    elif flask.request.method == "DELETE":
        # delete user like for specified post
        connection.execute(
            "DELETE FROM likes WHERE postid=? AND owner=?",
            (postid_url_slug, flask.session['logname'])
        )
        # return 204 on success
        return '', 204
    # like a specific post
    elif flask.request.method == "POST":
        # Add a new like if logname doesn't like this, else return error status
        if logname_likes_this:
            context = {
                "logname": logname,
                "message": "Conflict",
                "postid": postid_url_slug,
                "status_code": 409
            }
            return flask.jsonify(**context), 409
        context = {
            "logname": logname,
            "postid": postid_url_slug,
        }
        connection.execute(
            "INSERT INTO likes (owner, postid)"
            "VALUES (?, ?)", (logname, postid_url_slug)
        )
        return flask.jsonify(**context), 201

    # return JSON data formed in the three conditionals above
    return flask.jsonify(**context)
