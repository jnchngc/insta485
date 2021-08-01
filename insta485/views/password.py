"""Deal with user passwords."""
import uuid
import hashlib
import flask
import insta485


def get_salted_password(password):
    """Salt an inputted password."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    print(password_db_string)
    return password_db_string


def get_password_to_check(db_password_info, password_in):
    """Compute password to check with the database."""
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    db_salt = db_password_info[1]
    password_in_salted = db_salt + password_in
    hash_obj.update(password_in_salted.encode('utf-8'))
    password_in_hash = hash_obj.hexdigest()
    return algorithm + '$' + db_salt + '$' + password_in_hash


@insta485.app.route('/accounts/password/', methods=['GET', 'POST'])
def show_password():
    """Check if a password is valid."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    context = {}
    context['logname'] = flask.session['logname']
    context['is_logged_in'] = True
    if flask.request.method == "POST":
        if 'update_password' in flask.request.form:
            connection = insta485.model.get_db()

            password_in = flask.request.form['password']
            new_password1_in = flask.request.form['new_password1']
            new_password2_in = flask.request.form['new_password2']

            # check if both passwords match, abort 401 if not
            if new_password1_in != new_password2_in:
                flask.abort(401)

            username = flask.session['logname']
            db_password = connection.execute(
                "SELECT password FROM users WHERE username=?",
                (username,)
            ).fetchone()

            db_password_info = db_password['password'].split('$')

            # check user's password
            password_to_check = get_password_to_check(db_password_info,
                                                      password_in)
            valid_user = connection.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password_to_check)
            ).fetchall()
            valid_user = len(valid_user)
            if not valid_user:
                flask.abort(403)

            salted_new_password = get_salted_password(new_password1_in)
            connection.execute(
                "UPDATE users SET password=? WHERE username=?",
                (salted_new_password, username)
            )
            return flask.redirect(flask.url_for('edit'))

    return flask.render_template("password.html", **context)
