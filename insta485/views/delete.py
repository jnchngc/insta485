"""Delete module handles deleting a profile."""
from pathlib import Path
import flask
import insta485


@insta485.app.route('/accounts/delete/', methods=['GET', 'POST'])
def show_delete():
    """Delete a user profile."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    context = {}
    context['is_logged_in'] = True
    context['logname'] = flask.session['logname']
    logname = flask.session['logname']
    if flask.request.method == "POST":
        if 'delete' in flask.request.form:
            connection = insta485.model.get_db()
            post_filenames = connection.execute(
                "SELECT filename FROM posts WHERE owner=?",
                (logname,)
            ).fetchall()
            profilepic_filename = connection.execute(
                "SELECT filename FROM users WHERE username=?",
                (logname,)
            ).fetchall()
            all_files = post_filenames + profilepic_filename
            for file in all_files:
                delete_path = Path(insta485.app.
                                   config["UPLOAD_FOLDER"]/file['filename'])
                if delete_path.exists():
                    delete_path.unlink()
            logname = flask.session['logname']
            connection = insta485.model.get_db()
            flask.session.clear()
            connection.execute(
                "DELETE FROM users WHERE username=?",
                (logname,)
            )
            return flask.redirect(flask.url_for('create'))

    return flask.render_template("delete.html", **context)
