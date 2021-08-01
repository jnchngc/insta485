"""Edit a user profile."""
import pathlib
import uuid
import flask
import insta485


@insta485.app.route('/accounts/edit/', methods=["GET", "POST"])
def edit():
    """Edit the database profilepic, fullname, and email."""
    # redirect to login if not logged in
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    context = {}
    context['is_logged_in'] = True
    # determine who the current user is
    current_user = flask.session['logname']

    # change the user's information
    if flask.request.method == 'POST':
        if 'update' in flask.request.form:
            # get new values from form
            # Unpack flask object
            fileobj = flask.request.files["file"]
            new_filename = fileobj.filename
            new_fullname = flask.request.form['fullname']
            new_email = flask.request.form['email']
            # open connection to database
            connection = insta485.model.get_db()
            # replace old profile pic in database if a new one is supplied
            if new_filename:
                # Compute base name (filename without directory).
                # We use a UUID to avoid file clashes
                # clashes with existing files
                old_filename = connection.execute(
                    "SELECT filename FROM users WHERE username=?",
                    (current_user,)
                ).fetchone()['filename']
                delete_path = insta485.app.config["UPLOAD_FOLDER"]/old_filename
                if delete_path.exists():
                    delete_path.unlink()
                uuid_basename = "{stem}{suffix}".format(
                    stem=uuid.uuid4().hex,
                    suffix=pathlib.Path(new_filename).suffix
                )
                # Save to disk
                path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
                fileobj.save(path)

                connection.execute(
                    "UPDATE users SET filename=? WHERE username=?",
                    (uuid_basename, current_user)
                )
            # replace old fullname
            connection.execute(
                "UPDATE users SET fullname=? WHERE username=?",
                (new_fullname, current_user)
            )
            # replace old email
            connection.execute(
                "UPDATE users SET email=? WHERE username=?",
                (new_email, current_user)
            )
            # return account page when updating is complete
            # return flask.redirect(flask.url_for('show_user',
            # user_url_slug=current_user))

    # re-render the current page
    context['logname'] = current_user
    context['url'] = '/accounts/edit/'
    # open connection to database
    connection = insta485.model.get_db()
    information = connection.execute(
        "SELECT DISTINCT filename, fullname, email " +
        "FROM users WHERE username=?",
        (current_user,)
    ).fetchone()
    context['filename'] = information['filename']
    context['fullname'] = information['fullname']
    context['email'] = information['email']
    # return the edit html file for GUI
    return flask.render_template("edit.html", **context)
