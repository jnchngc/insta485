"""Helper file for API."""
import flask
import insta485


def check_login():
    """Check if user is logged in."""
    if 'logname' not in flask.session:
        error_context = {
            'message': 'Forbidden',
            'status_code': 403
        }
        return (error_context, False)
    return ({}, True)


def check_postid(postid):
    """Check if postid is valid."""
    connection = insta485.model.get_db()
    postid_exists = len(connection.execute(
        "SELECT postid FROM posts WHERE postid=?", (postid,)
    ).fetchall())
    if postid_exists == 0:
        error_context = {
            "message": "Not Found",
            "status_code": 404
        }
        return (error_context, False)
    return ({}, True)
