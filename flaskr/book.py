from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.db import get_db
from flask import Blueprint, request, jsonify
from pydantic import BaseModel
from flask_pydantic import validate
from werkzeug.exceptions import BadRequest
from typing import Optional

bp = Blueprint('book', __name__)



@bp.route('/books', methods=['GET'])
def get_books():
    db = get_db()
    books = db.execute(
        'SELECT id, title, author, year, isbn FROM book'
    ).fetchall()
    # Convert query result to a list of dictionaries
    books_list = [dict(row) for row in books]
    return jsonify(books_list)

@bp.route('/books', methods=['POST'])
def create_book():
    try:
        data = request.get_json()
        title = data.get('title')
        author = data.get('author')
        year = data.get('year')
        isbn = data.get('isbn')

        if not title or not author:
            raise BadRequest('Title and author are required.')

        db = get_db()
        db.execute(
            'INSERT INTO book (title, author, year, isbn) VALUES (?, ?, ?, ?)',
            (title, author, year, isbn)
        )
        db.commit()

        return jsonify({'message': 'Book created successfully'}), 201
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500
    
@bp.route('/books/<int:id>', methods=['GET'])
def get_book_by_id(id):
    db = get_db()
    book = db.execute(
        'SELECT id, title, author, year, isbn FROM book WHERE id = ?',
        (id,)
    ).fetchone()

    if book is None:
        return jsonify({'error': 'Book not found'}), 404

    # Convert the row to a dictionary
    book_data = dict(book)
    return jsonify(book_data)
@bp.route('/books/<int:id>', methods=['PUT'])
def update_book_by_id(id):
    try:
        data = request.get_json()
        title = data.get('title')
        author = data.get('author')
        year = data.get('year')
        isbn = data.get('isbn')

        if not (title or author or year or isbn):
            return jsonify({'error': ''}), 400

        db = get_db()
        book = db.execute('SELECT id FROM book WHERE id = ?', (id,)).fetchone()

        if book is None:
            return jsonify({'error': 'Book not found'}), 404

        db.execute(
            '''
            UPDATE book
            SET title = COALESCE(?, title),
                author = COALESCE(?, author),
                year = COALESCE(?, year),
                isbn = COALESCE(?, isbn)
            WHERE id = ?
            ''',
            (title, author, year, isbn, id)
        )
        db.commit()

        return jsonify({'message': 'Book updated !'}), 200

    except Exception as e:
        return jsonify({'error':  {str(e)}}), 500

@bp.route('/books/<int:id>', methods=['DELETE'])
def delete_book_by_id(id):
    try:
        db = get_db()
        book = db.execute('SELECT id FROM book WHERE id = ?', (id,)).fetchone()

        if book is None:
            return jsonify({'error': 'Book not found'}), 404

        db.execute('DELETE FROM book WHERE id = ?', (id,))
        db.commit()

        return jsonify({'message': 'Book Deleted'}), 200

    except Exception as e:
        return jsonify({'error': f'Une erreur inattendue : {str(e)}'}), 500