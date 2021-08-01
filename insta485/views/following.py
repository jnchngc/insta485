"""Show users following a given user."""
import flask
import insta485
from insta485.views.user import check_user_slug_exists


@insta485.app.route('/u/<follower_u>/following/', methods=["GET", "POST"])
def show_following(follower_u):
    """Display /<follower_u>/following/ route."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    context = {}
    context['is_logged_in'] = True
    # check if page exists
    if not check_user_slug_exists(follower_u):
        flask.abort(404)
    # Connect to database
    connection = insta485.model.get_db()

    logname = flask.session['logname']
    if flask.request.method == 'POST':
        if 'follow' in flask.request.form:
            not_followed_username = flask.request.form['username']
            connection.execute(
                "INSERT INTO following(username1, username2) VALUES(?, ?)",
                (logname, not_followed_username,)
            )
        elif 'unfollow' in flask.request.form:
            followed_username = flask.request.form['username']
            connection.execute(
                "DELETE FROM following WHERE username1=? AND username2=?",
                (logname, followed_username,)
            )

    # set the current user
    # user = flask.session["user"] CHANGE THIS WHEN LOGIN PAGE IS COMPLETE
    context['page_owner_name'] = follower_u
    # populate JSON file with additional information

    # get a list of dictionaries of follower information
    following = connection.execute(
        "SELECT DISTINCT username2 AS username FROM following " +
        "WHERE username1=?", (follower_u,)
    ).fetchall()

    # fills in JSON data (profile pic and if followed follows user)
    for followed in following:
        # get profile picture of an individual followed
        user_img_url = connection.execute(
            "SELECT filename FROM users WHERE username=?",
            (followed['username'],)
        ).fetchall()
        followed['user_img_url'] = user_img_url[0]['filename']
        # see if logname follows follower_u
        logname_follows_username = connection.execute(
            "SELECT * FROM following WHERE username1=? AND username2=?",
            (logname, followed['username'])
        ).fetchall()
        if len(logname_follows_username) != 0:
            followed['logname_follows_username'] = True
        else:
            followed['logname_follows_username'] = False

    # create the context object that we pass to the HTML template
    context["logname"] = logname
    context["following"] = following

    # render HTML template based on JSON data
    return flask.render_template("following.html", **context)
