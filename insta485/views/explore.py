"""Explore page handled in this module."""
import flask
import insta485


@insta485.app.route('/explore/', methods=["GET", "POST"])
def show_explore():
    """Show the explore page."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    context = {}
    context['is_logged_in'] = True
    connection = insta485.model.get_db()
    # set the current user
    # user = flask.session["user"] CHANGE THIS WHEN LOGIN PAGE IS COMPLETE
    user = flask.session['logname']
    context['logname'] = user
    if flask.request.method == 'POST':
        if 'follow' in flask.request.form:
            not_followed_uname = flask.request.form['username']
            connection.execute(
                "INSERT INTO following(username1, username2) VALUES(?, ?)",
                (user, not_followed_uname,)
            )

    not_following = connection.execute(
        "SELECT(username) FROM users EXCEPT SELECT(u.username) " +
        "FROM users u, following WHERE ?=username1 " +
        "AND username2=u.username OR u.username=?", (user, user)
    ).fetchall()

    for not_follow in not_following:
        profile_pic = connection.execute(
            "SELECT filename FROM users WHERE username=?",
            (not_follow['username'],)
        ).fetchone()
        not_follow['user_img_url'] = profile_pic['filename']
    context['not_following'] = not_following
    return flask.render_template("explore.html", **context)
