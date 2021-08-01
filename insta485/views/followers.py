"""Display followers of a given user."""
import flask
import insta485
from insta485.views.user import check_user_slug_exists


@insta485.app.route('/u/<users_name>/followers/', methods=["GET", "POST"])
def show_followers(users_name):
    """Display /<users_name>/followers/ route."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    context = {}
    context['is_logged_in'] = True
    # check if page exists
    if not check_user_slug_exists(users_name):
        flask.abort(404)
    # Connect to database
    connection = insta485.model.get_db()

    # set the current user
    # user = flask.session["user"] CHANGE THIS WHEN LOGIN PAGE IS COMPLETE
    logname = flask.session['logname']
    context["logname"] = logname
    if flask.request.method == 'POST':
        if 'unfollow' in flask.request.form:
            followed_user = flask.request.form['username']
            connection.execute(
                "DELETE FROM following WHERE username1=? AND username2=?",
                (logname, followed_user,)
            )
        elif 'follow' in flask.request.form:
            not_followed_user = flask.request.form['username']
            connection.execute(
              "INSERT INTO following(username1, username2) VALUES(?, ?)",
              (logname, not_followed_user,)
            )

    # populate JSON file with additional information
    # get a list of dictionaries of follower information
    followers = connection.execute(
      "SELECT DISTINCT username1 AS username FROM following WHERE username2=?",
      (users_name,)
    ).fetchall()
    context['page_owner_name'] = users_name

    # fills in JSON data (profile pic and following) for each follower
    for follower in followers:
        # get profile picture of an individual follower
        user_img_url = connection.execute(
          "SELECT filename FROM users WHERE username=?",
          (follower['username'],)
        ).fetchall()
        follower['user_img_url'] = user_img_url[0]['filename']
        # see if logname follows user_name
        logname_follows_username = connection.execute(
            "SELECT * FROM following WHERE username1=? AND username2=?",
            (logname, follower['username'])
        ).fetchall()
        if len(logname_follows_username) != 0:
            follower['logname_follows_username'] = True
        else:
            follower['logname_follows_username'] = False

    # create the context object that we pass to the HTML template
    context["followers"] = followers

    # render HTML template based on JSON data
    return flask.render_template("followers.html", **context)
