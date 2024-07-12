from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, User
from . import db
import json

NameL = []
MobileL = []

views = Blueprint('views', __name__)


@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Book added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['GET', 'POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({}) 

@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        NameL = []
        MobileL = []
        BooksL = []
        search_form = request.form
        search_value = search_form['BookName']
        search = "%{0}%".format(search_value)
        BookSearch = Note.query.filter(Note.data.like(search)).all()
        for l in BookSearch:
            MatchingName = l.data
            #print(MatchingName)
            BooksL.append(MatchingName)
        #print(BookSearch)
        #print(search)
        for r in BookSearch:
            IDnumber = r.user_id
            #print(IDnumber)
            BookOwner = User.query.filter(User.id == IDnumber).all()
            for b in BookOwner:
                OwnerName = b.first_name
                OwnerMobile = b.mobile_number
                NameL.append(OwnerName)
                MobileL.append(OwnerMobile)
        lengthL = len(MobileL)
        return render_template("searchResult.html", mobiles=MobileL, searchCriteria = search_value, owner=NameL, l=lengthL, book = BooksL, user=current_user)
        return str(MobileL)

    else:
        return render_template("search.html", user=current_user)



