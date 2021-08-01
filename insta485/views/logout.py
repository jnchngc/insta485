"""Logout module handles logging out a user."""
import flask
import insta485


@insta485.app.route('/accounts/logout/', methods=['POST'])
def show_logout():
    """Log a user out of their account."""
    if flask.request.method != "POST":
        flask.abort(403)

    # delete the flash.session['logname']
    flask.session.clear()
    if 'logname' in flask.session:
        print('logname still in')
    else:
        print('logname popped')

    # make sure error is thrown if someone
    # tries to see previous data
    return flask.redirect(flask.url_for('show_login'))
