"""REST API for comments."""
import json
import flask
import insta485
from insta485.api.helper_functions import check_login
from insta485.api.helper_functions import check_postid


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/comments/',
                    methods=["GET", "POST"])
def get_comments(postid_url_slug):
    """Return comments on postid or creates a comment."""
    # check if user is logged in
    logged_in_status = check_login()
    if not logged_in_status[1]:
        return flask.jsonify(**logged_in_status[0]), 403
    post_valid = check_postid(postid_url_slug)
    if not post_valid[1]:
        return flask.jsonify(**post_valid[0]), 404
    # get the logname
    logname = flask.session['logname']
    connection = insta485.model.get_db()

    # check if post is out of range
    if len(connection.execute(
            "SELECT postid FROM posts WHERE postid=?",
            (postid_url_slug,)).fetchall()) == 0:
        error_context = {
            'message': 'Not Found',
            'status_code': 404
        }
        return flask.jsonify(**error_context), 404

    # add a comment to a specific post
    if flask.request.method == "POST":
        # convert json string sent over the CLI to comment data
        new_comment = flask.request.get_data(as_text=True)
        new_comment = json.loads(new_comment)
        new_comment = new_comment['text']
        # Add a new comment to the post
        connection.execute(
            "INSERT INTO comments(owner, postid, text) VALUES (?, ?, ?)",
            (logname, postid_url_slug, new_comment)
        )

    # execute common logic before doing more POST specific logic
    # get comments from a given post and fill in JSON according to results
    comments = connection.execute(
        "SELECT commentid, owner, postid, text FROM comments WHERE postid=?",
        (postid_url_slug,)
    ).fetchall()
    # add owner_show_url to JSON object
    for comment in comments:
        comment['owner_show_url'] = f"/u/{comment['owner']}/"
    context = {
        "comments": comments,
        "url": flask.request.path
    }

    # return comment created in POST request
    if flask.request.method == 'POST':
        # select last inserted value from database
        created_comment_id = connection.execute(
            "SELECT last_insert_rowid()",
            ()
        ).fetchone()
        created_comment_id = created_comment_id['last_insert_rowid()']

        created_comment_context = connection.execute(
            """SELECT commentid, owner, postid, text
            FROM comments WHERE commentid=?""",
            (created_comment_id,)
        ).fetchone()
        created_comment_context['owner_show_url'] = f"/u/{logname}/"
        # return context for the last created comment
        return flask.jsonify(**created_comment_context), 201

    # return JSON data for GET request
    return flask.jsonify(**context)
