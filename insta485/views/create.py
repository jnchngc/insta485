"""Create a user account."""
import uuid
import pathlib
import flask
import insta485
from insta485.views.password import get_salted_password


@insta485.app.route('/accounts/create/', methods=['GET', 'POST'])
def create():
    """Create an account for a new user."""
    # if user logged in redirect to /accounts/edit/
    if 'logname' in flask.session:
        return flask.redirect(flask.url_for('edit'))
    if flask.request.method == 'POST':
        connection = insta485.model.get_db()
        if 'file' in flask.request.files:
            filename_in = flask.request.files['file'].filename
            # Upload the profile pic
            # Unpack flask object
            fileobj = flask.request.files["file"]
            filename = fileobj.filename
            # add the actual file to the uploads folder
            # Compute base name (filename without directory).
            # Use UUID to avoid file clashes
            uuid_basename = "{stem}{suffix}".format(
                stem=uuid.uuid4().hex,
                suffix=pathlib.Path(filename).suffix
            )
            # Save to disk
            path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
            fileobj.save(path)
        else:
            uuid_basename = ""
        print(filename_in)
        print("lala")
        fullname_in = flask.request.form['fullname']
        username_in = flask.request.form['username']
        email_in = flask.request.form['email']
        password_in = flask.request.form['password']

        # if entered username already exists abort 409
        existing_user = connection.execute(
            "SELECT * FROM users WHERE username=?", (username_in,)
        ).fetchall()

        existing_user = len(existing_user)
        if existing_user:
            flask.abort(409)
        # if password entered is empty abort 400
        if len(password_in) == 0:
            flask.abort(400)
        # create account and log user in
        password_in = get_salted_password(password_in)
        connection.execute(
            "INSERT INTO users " +
            "(username, fullname, email, filename, password) " +
            "VALUES (?, ?, ?, ?, ?)",
            (username_in, fullname_in, email_in, uuid_basename, password_in)
        )
        flask.session['logname'] = username_in
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("create.html")
