import flask

import models
import forms
from sqlalchemy.sql import func

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://coe:CoEpasswd@localhost:5432/coedb"

models.init_app(app)


@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )


@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )
    note = models.Note()
    form.populate_obj(note)
    note.tags = []

    db = models.db
    for tag_name in form.tags.data:
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()

    return flask.render_template(
        "tags-view.html",
        tag_name=tag_name,
        notes=notes,
    )

@app.route("/notes/update/<int:note_id>", methods=["GET", "POST"])
def notes_update(note_id):
    db = models.db
    note = db.session.query(models.Note).get(note_id)
    filltag = ""
    for tag in note.tags:
        filltag += tag.name + ","

    form = forms.NoteForm(obj=note)
    
    return flask.render_template("notes-update.html", form=form, note=note, filltag=filltag)

@app.route("/notes/delete/<int:note_id>", methods=["GET"])
def notes_delete(note_id):
    db = models.db
    note = db.session.query(models.Note).get(note_id)

    #if note not null
    if note:
        db.session.delete(note)
        db.session.commit()
        print(f"Delete {note_id} success")
    return flask.redirect(flask.url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
