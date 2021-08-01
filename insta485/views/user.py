"""User module shows user page."""
import pathlib
import uuid
import flask
import insta485


def check_user_slug_exists(user_slug):
    """Return number of users with username=slug."""
    check_connection = insta485.model.get_db()
    user_check = len(check_connection.execute(
        "SELECT username FROM users WHERE username=?",
        (user_slug,)).fetchall())
    return user_check


@insta485.app.route('/u/<user_url_slug>/', methods=['GET', 'POST'])
def show_user(user_url_slug):
    """Display the user page and facilitates editing a users own page."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    context = {}
    context['is_logged_in'] = True
    # check if page exists
    if not check_user_slug_exists(user_url_slug):
        flask.abort(404)
    connection = insta485.model.get_db()
    logname = flask.session['logname']

    # check if the user using the forms
    if flask.request.method == 'POST':
        # check if the user logs out
        if 'logout' in flask.request.form:
            return flask.redirect(flask.url_for('show_logout'))
        # check if the user uploads a post
        # then add it to database/uploads folder
        if 'create_post' in flask.request.form:
            if 'file' in flask.request.files:
                # Unpack flask object
                fileobj = flask.request.files["file"]
                # add the actual file to the uploads folder
                # Compute base name (filename without directory).
                # We use a UUID to avoid file clashes
                uuid_basename = "{stem}{suffix}".format(
                    stem=uuid.uuid4().hex,
                    suffix=pathlib.Path(fileobj.filename).suffix
                )
                # Save to disk
                path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
                fileobj.save(path)

                # add the filename to the database
                connection = insta485.model.get_db()
                connection.execute(
                    "INSERT INTO posts (filename, owner) VALUES (?, ?)",
                    (uuid_basename, logname)
                )
            else:
                flask.abort(400)
        elif 'unfollow' in flask.request.form:
            page_owner = flask.request.form['username']
            connection.execute(
                "DELETE FROM following WHERE username1=? AND username2=?",
                (logname, page_owner,)
            )
        elif 'follow' in flask.request.form:
            not_followed_owner = flask.request.form['username']
            connection.execute(
                "INSERT INTO following(username1, username2) VALUES(?, ?)",
                (logname, not_followed_owner,)
            )

    # populate JSON object
    context['logname'] = logname
    context['username'] = user_url_slug
    following_check = connection.execute(
        "SELECT DISTINCT username1 FROM following " +
        "WHERE username1=? AND username2=?",
        (logname, user_url_slug,)
    ).fetchall()
    following_check = len(following_check)
    if following_check == 0:
        context['logname_follows_username'] = False
    else:
        context['logname_follows_username'] = True
    fullname = connection.execute(
        "SELECT DISTINCT fullname FROM users WHERE username=?",
        (user_url_slug,)
    ).fetchone()['fullname']
    context['fullname'] = fullname
    context['following'] = len(connection.execute(
        "SELECT username1 FROM following WHERE username1=?",
        (user_url_slug,)).fetchall())
    followers_count = connection.execute(
        "SELECT username1 FROM following WHERE username2=?",
        (user_url_slug,)
    ).fetchall()
    context['followers'] = len(followers_count)
    posts_count = connection.execute(
        "SELECT postid FROM posts WHERE owner=?",
        (user_url_slug,)
    ).fetchall()
    context['total_posts'] = len(posts_count)
    posts = connection.execute(
        "SELECT DISTINCT postid, filename FROM posts " +
        "WHERE owner=? ORDER BY postid ASC",
        (user_url_slug,)
    ).fetchall()
    for post in posts:
        post['img_url'] = post['filename']
    context['posts'] = posts

    # return a template rendered from the JSON object we created
    return flask.render_template("user.html", **context)
