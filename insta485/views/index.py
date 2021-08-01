"""Root page shown via this module."""
import arrow
import flask
import insta485


@insta485.app.route('/', methods=["GET", "POST"])
def show_index():
    """Display / route."""
    context = {}
    # if 'logname' not in flask.session:
    if 'logname' in flask.session:
        context['is_logged_in'] = True
    else:
        print("logname not in session")
        return flask.redirect(flask.url_for('show_login'))
    user = flask.session['logname']
    connection = insta485.model.get_db()

    if flask.request.method == "POST":
        if 'unlike' in flask.request.form:
            like_id = flask.request.form['postid']
            print(like_id)
            connection.execute(
                "DELETE FROM likes WHERE owner=? AND postid=?",
                (user, like_id,)
            )
        elif 'like' in flask.request.form:
            like_id = flask.request.form['postid']
            connection.execute(
                "INSERT INTO likes(owner, postid) VALUES (?, ?)",
                (user, like_id,)
            )
        elif 'comment' in flask.request.form:
            owner = user
            commented_postid = flask.request.form['postid']
            text = flask.request.form['text']
            connection.execute(
                "INSERT INTO comments(owner, postid, text) VALUES (?, ?, ?)",
                (owner, commented_postid, text,)
            )
    # set the current user
    # user = flask.session["user"] CHANGE THIS WHEN LOGIN PAGE IS COMPLETE

    # get a list of dictionaries of post information
    cur = connection.execute(
        "SELECT DISTINCT postid, filename, owner, posts.created " +
        "FROM posts, following WHERE username1=? AND " +
        "username2=owner OR owner=? ORDER BY posts.postid DESC",
        (user, user)
    )
    posts = cur.fetchall()

    # fills in JSON data (such as comments and likes) for each post
    for post in posts:
        postid = post['postid']
        # get the timestamp of an individual post
        post['timestamp'] = arrow.get(post['created']).humanize()
        # get comments of an individual post
        comments = connection.execute(
            "SELECT DISTINCT C.owner, C.text FROM comments C " +
            "WHERE ? = C.postid ORDER BY C.commentid ASC",
            (postid,)
        ).fetchall()
        post['comments'] = comments
        # get likes of an individual post
        likes = connection.execute(
            "SELECT COUNT(postid) FROM likes WHERE postid =?",
            (postid,)
        ).fetchone()
        post['likes'] = likes[f"{next(iter(likes))}"]
        # get profile picture of an indiviaul post
        owner_img_filename = connection.execute(
            "SELECT filename FROM users WHERE username=?",
            (post['owner'],)
        ).fetchone()
        post['owner_img_filename'] = owner_img_filename['filename']

        post['img_filename'] = post['filename']

        # check if logged in user likes this post
        logname_likes_post = connection.execute(
            "SELECT owner FROM likes WHERE owner=? AND postid=?",
            (user, postid,)
        ).fetchall()
        logname_likes_post = len(logname_likes_post)
        post['logname_likes_post'] = logname_likes_post
        # get picture of an individual post

        # post['owner_img_url'] = "/uploads/" + owner_img_filename

    # create the context object that we pass to the HTML template
    context["logname"] = user
    context["posts"] = posts

    # render HTML template based on JSON data
    return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<filename>')
def download_file(filename):
    """Download a file from database."""
    # check if logged in
    if 'logname' not in flask.session:
        flask.abort(403)
    # check if file exists
    connection = insta485.model.get_db()
    file_exits = len(connection.execute(
        "SELECT filename FROM posts WHERE filename=?",
        (filename,)
    ).fetchall())
    file_exits += len(connection.execute(
        "SELECT filename FROM users WHERE filename=?",
        (filename,)
    ).fetchall())
    if file_exits == 0:
        flask.abort(404)
    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'], filename, as_attachment=True
    )
