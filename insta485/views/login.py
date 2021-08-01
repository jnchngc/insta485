"""Login to an existing profile."""
import flask
import insta485
from insta485.views.password import get_password_to_check


@insta485.app.route('/accounts/login/', methods=['GET', 'POST'])
def show_login():
    """Deal with a user logging in."""
    # user is not logged in and has to log in to continue
    # when the user inputs their info, check if they are a valid user
    if 'logname' in flask.session:
        return flask.redirect('/')
    if flask.request.method == "POST":
        print(flask.request.form)
        connection = insta485.model.get_db()
        # 1. Take in user password input
        username_in = flask.request.form['username']
        password_in = flask.request.form['password']
        # 2. Database query password string for user
        db_password = connection.execute(
            "SELECT password FROM users WHERE username=?", (username_in,)
        ).fetchall()

        # username doesn't exist
        if len(db_password) == 0:
            flask.abort(403)

        # 3. Split the database string: [algorithm, salt, hashed_password]
        db_password_info = db_password[0]['password'].split('$')

        # 4 Take salt and calculate hash with input password
        # 5 check if = to hashed password in db
        password_to_check = get_password_to_check(db_password_info,
                                                  password_in)

        # SQL for user lookup
        valid_user = connection.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username_in, password_to_check)
        ).fetchall()
        valid_user = len(valid_user)
        print("before if")
        if valid_user:
            print("after if")
            flask.session['logname'] = username_in
            return flask.redirect(flask.url_for('show_index'))
        flask.abort(403)
    context = {}
    context['is_logged_in'] = False
    return flask.render_template("login.html")
