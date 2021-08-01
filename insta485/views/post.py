"""Post path module."""
from pathlib import Path
import arrow
import flask
import insta485


@insta485.app.route('/p/<postid_url_slug>/', methods=["GET", "POST"])
def show_post(postid_url_slug):
    """Deal with individual post pages."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['logname']
    connection = insta485.model.get_db()
    context = {}
    context['is_logged_in'] = True

    post_exists = len(connection.execute(
        "SELECT postid FROM posts WHERE postid=?",
        (postid_url_slug,)).fetchall())
    if post_exists == 0:
        flask.abort(404)
    # post_exists = len(connection.execute(
    # "SELECT FROM posts WHERE postid=?",
    # (postid_url_slug,)).fetchall())

    if flask.request.method == "POST":
        if 'uncomment' in flask.request.form:
            print(flask.request.url)
            comment_exists = connection.execute(
                "SELECT commentid, owner FROM comments WHERE commentid=?",
                (flask.request.form['commentid'],)).fetchall()
            if len(comment_exists) == 0:
                flask.abort(404)
            # access control check
            if comment_exists[0]['owner'] != logname:
                flask.abort(403)
            connection.execute(
                "DELETE FROM comments WHERE commentid=?",
                (flask.request.form['commentid'],)
            )
        elif 'delete' in flask.request.form:
            # delete post image from file system
            cur = connection.execute(
                "SELECT filename, owner FROM posts WHERE postid=?",
                (flask.request.form['postid'],)
            ).fetchone()
            filename = cur['filename']
            # access control check
            if logname != cur['owner']:
                flask.abort(403)
            delete_path = Path(insta485.app.config["UPLOAD_FOLDER"]/filename)
            if delete_path.exists():
                delete_path.unlink()

            # delete post from database
            connection.execute(
                "DELETE FROM posts WHERE postid=?",
                (flask.request.form['postid'],)
            )
            return flask.redirect(flask.url_for('show_user',
                                                user_url_slug=logname))
        elif 'unlike' in flask.request.form:
            connection.execute(
                "DELETE FROM likes WHERE owner=? AND postid=?",
                (logname, flask.request.form['postid'],)
            )
        elif 'like' in flask.request.form:
            connection.execute(
                "INSERT INTO likes(owner, postid) VALUES (?, ?)",
                (logname, flask.request.form['postid'],)
            )
        elif 'comment' in flask.request.form:
            owner = logname
            id_arg = flask.request.form['postid']
            text = flask.request.form['text']
            connection.execute(
                "INSERT INTO comments(owner, postid, text) VALUES (?, ?, ?)",
                (owner, id_arg, text,)
            )

    context['logname'] = logname
    context['postid'] = postid_url_slug
    post = connection.execute(
        "SELECT DISTINCT filename, owner, created FROM posts WHERE postid=?",
        (postid_url_slug,)
    ).fetchone()
    context['owner'] = post['owner']

    # get the timestamp of an individual post
    context['timestamp'] = arrow.get(post['created']).humanize()
    # get comments of an individual post
    comments = connection.execute(
        "SELECT DISTINCT C.owner, C.text, C.commentid FROM comments C " +
        "WHERE ? = C.postid ORDER BY C.commentid ASC",
        (postid_url_slug,)
    ).fetchall()
    context['comments'] = comments
    # get likes of an individual post
    context['likes'] = len(connection.execute(
        "SELECT postid FROM likes WHERE postid =?",
        (postid_url_slug,)).fetchall())
    # get profile picture of an indiviaul post
    context['owner_img_filename'] = connection.execute(
        "SELECT filename FROM users WHERE username=?",
        (post['owner'],)).fetchone()['filename']

    context['img_filename'] = post['filename']

    # check if logged in user likes this post
    logname_likes_post = len(connection.execute(
        "SELECT owner FROM likes WHERE owner=? AND postid=?",
        (logname, postid_url_slug,)).fetchall())
    context['logname_likes_post'] = logname_likes_post

    return flask.render_template("post.html", **context)
