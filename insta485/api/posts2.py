"""REST API for Feed."""
import flask
import insta485
from insta485.api.helper_functions import check_login
from insta485.api.helper_functions import check_postid

# return N'th page of posts


@insta485.app.route('/api/v1/p/', methods=["GET"])
def get_post_page():
    """Return posts."""
    logged_in = check_login()
    if not logged_in[1]:
        return flask.jsonify(**logged_in[0]), 403
    connection = insta485.model.get_db()
    logname = flask.session['logname']

    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    if page < 0 or size <= 0:
        context = {
            "message": "Bad Request",
            "status_code": 400
        }
        return flask.jsonify(**context), 400

    context = {
        'next': '',
        'results': [],
        'url': '/api/v1/p/'
    }

    offset = page * size
    limit = size
    # return page of posts by the user or that user follows
    # in order of most recently created
    posts = connection.execute(
        """SELECT postid FROM posts WHERE owner=? OR owner IN
        (SELECT username2 FROM following WHERE username1=?)
        ORDER BY postid DESC LIMIT ? OFFSET ?""",
        (logname, logname, limit, offset)
    ).fetchall()

    for post in posts:
        post_dict = {
            'postid': post['postid'],
            'url': ('/api/v1/p/' + str(post['postid']) + '/')
        }
        context['results'].append(post_dict)
    # change next url if another pages is possible
    if len(connection.execute(
        """SELECT postid FROM posts WHERE owner=? OR owner IN
        (SELECT username2 FROM following WHERE username1=?)
        ORDER BY postid DESC LIMIT ? OFFSET ?""",
        (logname, logname, limit, offset + size)
    ).fetchall()) != 0:
        context['next'] = '/api/v1/p/?size='+str(size)+'&page='+str(page + 1)

    return flask.jsonify(**context)

# return post details


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/', methods=["GET"])
def get_post_details(postid_url_slug):
    """Return post details."""
    # redirects to login if user is not logged in
    logged_in = check_login()
    if not logged_in[1]:
        return flask.jsonify(**logged_in[0]), 403
    post_valid = check_postid(postid_url_slug)
    if not post_valid[1]:
        return flask.jsonify(**post_valid[0]), 404
    # open connection to database
    connection = insta485.model.get_db()
    context = {
        'post_show_url': ('/p/' + str(postid_url_slug) + '/'),
        'url': ('/api/v1/p/' + str(postid_url_slug) + '/')
    }
    post_info = connection.execute(
        """SELECT posts.filename, posts.owner, posts.created,
        users.filename AS profile_pic
        FROM posts INNER JOIN users ON posts.owner=users.username
        WHERE posts.postid=?""",
        (postid_url_slug,)
    ).fetchone()
    context['age'] = post_info['created']
    context['img_url'] = '/uploads/' + post_info['filename']
    context['owner'] = post_info['owner']
    context['owner_img_url'] = '/uploads/' + post_info['profile_pic']
    context['owner_show_url'] = '/u/' + post_info['owner'] + '/'

    return flask.jsonify(**context)
