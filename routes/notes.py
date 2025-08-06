from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models.note import Note
from extensions import db

notes_bp = Blueprint("notes", __name__, url_prefix="/api/notes")

@notes_bp.route("/ui", methods=["GET"])
def notes_list():
    """
    View all notes (HTML UI)
    """
    notes = Note.query.all()
    return render_template("notes_list.html", notes=notes)


@notes_bp.route("/ui/new", methods=["GET", "POST"])
def new_note():
    if request.method == "POST":
        content = request.form["content"]
        diagnosis_id = request.form["diagnosis_id"]
        note = Note(content=content, diagnosis_id=diagnosis_id)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for("notes.notes_list"))
    return render_template("note_form.html", note=None)


@notes_bp.route("/ui/edit/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if request.method == "POST":
        note.content = request.form["content"]
        note.diagnosis_id = request.form["diagnosis_id"]
        db.session.commit()
        return redirect(url_for("notes.notes_list"))
    return render_template("note_form.html", note=note)


@notes_bp.route("/ui/delete/<int:note_id>", methods=["GET"])
def delete_note_ui(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for("notes.notes_list"))



@notes_bp.route("/", methods=["POST"])
def create_note():
    """
    Create a new note
    ---
    tags:
      - Notes
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - content
            - diagnosis_id
          properties:
            content:
              type: string
            diagnosis_id:
              type: integer
    responses:
      201:
        description: Note created successfully
      400:
        description: Invalid input
    """
    data = request.get_json()
    if not data or "content" not in data or "diagnosis_id" not in data:
        return jsonify({"error": "Missing fields"}), 400

    note = Note(content=data["content"], diagnosis_id=data["diagnosis_id"])
    db.session.add(note)
    db.session.commit()
    return jsonify({
        "message": "Note created",
        "note": {
            "id": note.id,
            "content": note.content,
            "diagnosis_id": note.diagnosis_id
        }
    }), 201



@notes_bp.route("/<int:note_id>", methods=["GET"])
def get_note(note_id):
    """
    Get a note by ID
    ---
    tags:
      - Notes
    parameters:
      - in: path
        name: note_id
        required: true
        type: integer
    responses:
      200:
        description: Note retrieved successfully
      404:
        description: Note not found
    """
    note = db.session.get(Note, note_id)
    if not note:
        return jsonify({"error": "Note not found"}), 404
    return jsonify({
        "id": note.id,
        "content": note.content,
        "diagnosis_id": note.diagnosis_id
    }), 200


@notes_bp.route("/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    """
    Update a note
    ---
    tags:
      - Notes
    parameters:
      - in: path
        name: note_id
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - content
          properties:
            content:
              type: string
    responses:
      200:
        description: Note updated successfully
      400:
        description: Missing content
      404:
        description: Note not found
    """
    data = request.get_json()
    note = db.session.get(Note, note_id)
    if not note:
        return jsonify({"error": "Note not found"}), 404

    if "content" not in data:
        return jsonify({"error": "Missing content"}), 400

    note.content = data["content"]
    db.session.commit()
    return jsonify({"message": "Note deleted"}), 200

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note_api(note_id):
    """
    Delete a note by ID
    ---
    parameters:
      - name: note_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Note deleted successfully
      404:
        description: Note not found
    """
    note = db.session.get(Note, note_id)
    if not note:
        return jsonify({'message': 'Note not found'}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'Note deleted'}), 200