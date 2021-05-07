from flask import Flask, render_template, session as flask_session, redirect, url_for, escape, request, flash
from werkzeug.utils import secure_filename
import os
from persistence_layer import *
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jgt8~dd)^h876.Jld8!!jP9X sSa!y&mJI?'
SONGS_UPLOAD_FOLDER = 'static/music'
ALLOWED_EXTENSIONS = set(['mp3', 'm4a'])
FAVOURITES_PLAYLIST = 'Улюблене'
app.config['UPLOAD_FOLDER'] = SONGS_UPLOAD_FOLDER
#flask_session['user_name'] = None

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        email = request.form['floatingInput']
        password = request.form['floatingPassword']
        users = User.find(login=email, password=password)
        if len(users) > 0:
            user = users[0]
            flask_session['user_name'] = user.name
            flask_session['user_id'] = user.login
            return redirect(url_for('show_songs'))
        else:
            flash("Неправильний логін чи пароль!")
            return render_template('sign-in.html')

    if 'user_name' not in flask_session:
        return render_template('sign-in.html')
    #return redirect(url_for('login'))
    #return render_template('sign-in.html')
    return redirect(url_for('show_songs'))




@app.route('/sign-up', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        email = request.form['floatingInput']
        password = request.form['floatingPassword']
        name = request.form['floatingName']

        users_with_login = User.find(login=email)
        users_with_name = User.find(name=name)
        if len(users_with_login) > 0:
            flash("Користувач з даним логіном вже існує!")
            return render_template('sign-up.html')
        elif len(users_with_name) > 0:
            flash("Користувач з даним іменем вже існує!")
            return render_template('sign-up.html')
        else:
            # створити нового користувача
            # так, я знаю, що паролі не можна зберігати у відкритому виді
            user = User(login=email, password=password, name=name).create()
            # створити плейлист "Улюблене" для нового користувача
            Playlist(name="Улюблене", owner_id=email, private=True).create()
            flask_session['user_name'] = user.name
            flask_session['user_id'] = user.login
            return redirect(url_for('show_songs'))

    if 'user_name' not in flask_session:
        return render_template('sign-up.html')
    #return redirect(url_for('login'))
    #return render_template('sign-in.html')
    return redirect(url_for('show_songs'))



@app.route('/songs', methods=('GET', 'POST'))
def show_songs():
    """print(Performer.find())
    print(Album.find())
    print(Song.find())"""
    playlists = Playlist.find(owner_id=flask_session['user_id'])
    # запит пошуку пісні
    if request.method == 'POST':
        if 'song_query' in request.form: #and request.form['song_query'] != '':
            songs = Song.find_like(request.form['song_query'])
            return render_template('songs.html', user_name=flask_session['user_name'], user_id=flask_session['user_id'],
                songs=songs, subtitle=f"Знайдені пісні за запитом `{request.form['song_query']}`", all_playlists=playlists)
        
    songs = Song.find(owner_id=flask_session['user_id'])
    return render_template('songs.html', user_name=flask_session['user_name'], user_id=flask_session['user_id'],
        songs=songs,subtitle='Усі пісні, які ви завантажили на Replay.', all_playlists=playlists)




@app.route('/playlists', methods=('GET', 'POST'))
def show_playlists():
    # запит пошуку плейліста
    if request.method == 'POST':
        if 'playlist_query' in request.form: 
            playlists = Playlist.find_like(request.form['playlist_query'], flask_session['user_id'])
            return render_template('playlists.html', user_name=flask_session['user_name'], user_id=flask_session['user_id'],
                playlists=playlists, subtitle=f"Знайдені плейлісти за запитом `{request.form['playlist_query']}`")

    playlists = Playlist.find(owner_id=flask_session['user_id'])
    return render_template('playlists.html', user_name=flask_session['user_name'], user_id=flask_session['user_id'],
        subtitle='Усі плейлісти, які Ви створили.', playlists=playlists)




@app.route('/albums', methods=('GET', 'POST'))
def show_albums():
    # запит пошуку плейліста
    if request.method == 'POST':
        if 'album_query' in request.form: 
            albums = Album.find_like(request.form['album_query'])
            return render_template('albums.html', user_name=flask_session['user_name'], user_id=flask_session['user_id'],
                albums=albums, subtitle=f"Знайдені альбоми за запитом `{request.form['album_query']}`")

    return render_template('albums.html', user_name=flask_session['user_name'], user_id=flask_session['user_id'],
        subtitle='Знайдіть альбом, який Вам до вподоби.', albums=[])




@app.route('/songs/<owner_id>/<playlist_name>')
def show_playlist_content(owner_id, playlist_name):
    all_playlists = Playlist.find(owner_id=flask_session['user_id'])
    current_playlist = Playlist.find(owner_id=owner_id, name=playlist_name)[0]
    owner_name = User.find(login=owner_id)[0].name
    songs = current_playlist.songs
    return render_template('playlist_content.html', user_name=flask_session['user_name'], user_id=flask_session['user_id'],
        songs=songs, all_playlists=all_playlists, owner_name=owner_name, current_playlist=current_playlist)



@app.route('/album_songs/<performer_name>/<album_name>')
def show_album_content(performer_name, album_name):
    all_playlists = Playlist.find(owner_id=flask_session['user_id'])
    album = Album.find(name=album_name, performer_name=performer_name)[0]
    songs = album.songs
    return render_template('album_content.html', user_name=flask_session['user_name'], user_id=flask_session['user_id'],
        songs=songs, all_playlists=all_playlists, album=album)




@app.route('/add_song/<playlist_name>/<song_name>_<performer_name>')
def add_to_playlist(playlist_name, song_name, performer_name):
    # перевірити, чи є ця пісня вже в плейлісті
    playlist = Playlist.find(name=playlist_name, owner_id=flask_session['user_id'])[0]
    song = Song.find(name=song_name, performer_name=performer_name)[0]
    if song in playlist.songs:
        flash("Ця пісня вже існує у вказаному плейлісті!")
    playlist.songs.append(song)
    db_session.commit()
    return redirect(request.referrer)




@app.route('/delete_song/<playlist_name>/<song_name>_<performer_name>')
def delete_from_playlist(playlist_name, song_name, performer_name):
    playlist = Playlist.find(name=playlist_name, owner_id=flask_session['user_id'])[0]
    song = Song.find(name=song_name, performer_name=performer_name)[0]
    playlist.songs.remove(song)
    db_session.commit()
    return redirect(request.referrer)




@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    # якщо нічого не ввели
    if not request.form['playlist_name']:
        flash("Ви не ввели назву плейлісту!")
    # якщо плейлист вже існує
    elif Playlist.find(owner_id=flask_session['user_id'], name=request.form['playlist_name']):
        flash("Плейліст з такою назвою вже існує!")
    else:
        Playlist(owner_id=flask_session['user_id'], name=request.form['playlist_name'], private=True).create()
    return redirect('/playlists')



@app.route('/delete_playlist/<playlist_name>')
def delete_playlist(playlist_name):
    playlist = Playlist.find(owner_id=flask_session['user_id'], name=playlist_name)[0]
    playlist.delete_self()
    return redirect('/playlists')





@app.route('/update_privacy/<playlist_name>', methods=['POST'])
def update_privacy(playlist_name):
    playlist = Playlist.find(owner_id=flask_session['user_id'], name=playlist_name)[0]
    private = request.form.get('privateCheckbox')
    private = True if private == 'on' else False
    playlist.update_self(private=private)
    return redirect('/playlists')




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS




@app.route('/upload', methods=('GET', 'POST'))
def upload():
    # якщо завантажуємо пісню
    if request.method == 'POST':
        # якщо ввели назву пісні і ім'я виконавця
        if 'song_name' in request.form.keys() and 'performer_name' in request.form.keys() and request.form['song_name'] and request.form['performer_name']:
            music_file = request.files['music_file']
            # якщо завантажили пісню
            if music_file and allowed_file(music_file.filename):
                filename = secure_filename(music_file.filename)
                # якщо такого виконавця ще не існує -- створити нового
                if not Performer.find(name=request.form['performer_name']):
                    Performer(name=request.form['performer_name']).create()
                # якщо такого альбому ще не існує -- створити новий
                if request.form['album_name'] and not Album.find(name=request.form['album_name'], performer_name=request.form['performer_name']):
                    Album(name=request.form['album_name'], performer_name=request.form['performer_name']).create()
                # якщо такої пісні ще не існує
                if not Song.find(name=request.form['song_name'], performer_name=request.form['performer_name']):
                    
                    # створити нову пісню
                    Song(name=request.form['song_name'],
                        performer_name=request.form['performer_name'],
                        album_name=request.form['album_name'] if request.form['album_name'] else None,
                        owner_id=flask_session['user_id'],
                        audio_file=filename).create()
                    # зберегти пісню в папку
                    music_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    return redirect('/songs')
                else:
                    flash('Така пісня вже існує! :(')
            else:
                flash('Помилка читання файлу! :(')
        else:
            flash('Помилка з даними про пісню! :(')
    
    return render_template('upload.html', user_name=flask_session['user_name'])




@app.route('/delete/song/<performer_name>/<name>')
def delete_song(performer_name, name):
    song = Song.find(name=name, performer_name=performer_name)[0]
    if song.owner_id == flask_session['user_id']:
        album_name, performer_name = song.album_name, song.performer_name
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], song.audio_file))
        song.delete_self()
        # якщо в альбомі не залишилось пісень -- видалити альбом
        if album_name and not Song.find(album_name=album_name, performer_name=performer_name):
            album = Album.find(name=album_name, performer_name=performer_name)[0]
            album.delete_self()
        # якщо у виконавця не залишилось пісень -- видалити виконавця
        if not Song.find(performer_name=performer_name):
            performer = Performer.find(name=performer_name)[0]
            performer.delete_self()
    return redirect('/songs')



@app.route('/update/song/<performer_name>/<name>', methods=('GET', 'POST'))
def update_song(performer_name, name):
    # не забути оновити інформацію про пісню у плейлистах??????????????????????????????????????????????????????????????????????????????
    if request.method == 'POST':
        song = Song.find(name=name, performer_name=performer_name)[0]
        old_performer_name = performer_name
        new_performer_name = request.form['performer_name']
        old_song_name = name
        new_song_name = request.form['song_name']
        old_album_name = song.album_name
        new_album_name = request.form['album_name'] if request.form['album_name'] else None
        # якщо не ввели назву пісні чи ім'я виконавця -- вивести помилку
        if not (new_performer_name and new_song_name):
            flash("Введіть назву пісні та ім'я виконавця!")
            return render_template('update_song.html', user_name=flask_session['user_name'], song=song)

        # якщо нового виконавця не існує -- створити його
        if not Performer.find(name=new_performer_name):
            Performer(name=new_performer_name).create()
        # аналогічно з альбомом
        if new_album_name and not Album.find(name=new_album_name, performer_name=new_performer_name):
            Album(name=new_album_name, performer_name=new_performer_name).create()
        # оновити інформацію про пісню (зокрема інформацію в плейлісті)
        song.update_self(name=new_song_name, performer_name=new_performer_name, album_name=new_album_name)
        
        # якщо в старому альбомі більше нема пісень -- видалити його
        if old_album_name and not Song.find(album_name=old_album_name, performer_name=old_performer_name):
            album = Album.find(name=old_album_name, performer_name=old_performer_name)[0]
            album.delete_self()
        # аналогічно з виконавцем
        if not Song.find(performer_name=old_performer_name):
            performer = Performer.find(name=old_performer_name)[0]
            performer.delete_self()
        
        return redirect('/songs')
        
        
    song = Song.find(name=name, performer_name=performer_name)[0]
    return render_template('update_song.html', user_name=flask_session['user_name'], song=song)




@app.route('/logout')
def logout():
    flask_session.pop('user_name')
    flask_session.pop('user_id')   
    return redirect(url_for('index'))






if __name__ == '__main__':
    app.run()