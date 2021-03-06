import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for


def get_db_connection():
    database_conn = sqlite3.connect('database.db')
    database_conn.row_factory = sqlite3.Row
    return database_conn


app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'this should be a secret random string'

hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])


@app.route('/', methods=('GET', 'POST'))
def index():
    database_conn = get_db_connection()

    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('The URL is required!')
            return redirect(url_for('index'))

        url_data = database_conn.execute('INSERT INTO urls (original_url) VALUES (?)',
                                         (url,))
        database_conn.commit()
        database_conn.close()

        url_id = url_data.lastrowid
        hashid = hashids.encode(url_id)
        short_url = request.host_url + hashid

        return render_template('index.html', short_url=short_url)

    return render_template('index.html')


@app.route('/<id>')
def url_redirect(id):
    database_conn = get_db_connection()

    original_id = hashids.decode(id)
    if original_id:
        original_id = original_id[0]
        url_data = database_conn.execute('SELECT original_url, clicks FROM urls'
                                         ' WHERE id = (?)', (original_id,)
                                         ).fetchone()
        original_url = url_data['original_url']
        clicks = url_data['clicks']

        database_conn.execute('UPDATE urls SET clicks = ? WHERE id = ?',
                              (clicks+1, original_id))

        database_conn.commit()
        database_conn.close()
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template("about.html")
