import flask

import models
import forms


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://coe:CoEpasswd@localhost:5432/coedb"
)

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


@app.route("/notes/create", methods=["GET", "POST"], defaults={"note_id": None})
@app.route("/notes/<note_id>/edit", methods=["GET", "POST"])
def notes_create_or_edit(note_id):
    db = models.db
    form = forms.NoteForm()
    note = models.Note()

    if note_id:
        note = (
            db.session.execute(db.select(models.Note).where(models.Note.id == note_id))
            .scalars()
            .first()
        )

        note.tag = note.tags
        form = forms.NoteForm(obj=note)

    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
            note_id=note_id,
        )

    form.populate_obj(note)

    note.tags = []

    for tag_name in form.tag.data:
        print(tag_name)
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        note.tags.append(tag)

    if note_id:
        db.session.commit()
    else:
        db.session.add(note)
        db.session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/notes/<note_id>/delete_note")
def delete_note(note_id):
    db = models.db
    note = (
        db.session.execute(db.select(models.Note).where(models.Note.id == note_id))
        .scalars()
        .first()
    )

    db.session.delete(note)
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


if __name__ == "__main__":
    app.run(debug=True)
