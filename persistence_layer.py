import sqlalchemy as sqla
import sqlalchemy.orm as orm

# налаштування під'єднання до БД
engine = sqla.create_engine("postgresql://hhsyeatpctzfcw:3cda28b97042c503fca2e0cd9266a03e5f3568646c94eb6a6050fe29b6125477@ec2-54-74-77-126.eu-west-1.compute.amazonaws.com:5432/d1akqstdn93ni2")
Base = orm.declarative_base()
Session = orm.sessionmaker(bind=engine)
db_session = Session()


# сутність "Користувач"
class User(Base):
    __tablename__ = 'User'
    login = sqla.Column(sqla.String, primary_key = True)
    password = sqla.Column(sqla.String, nullable = False)
    name = sqla.Column(sqla.String, nullable = False, unique = True)

    songs = orm.relationship("Song", back_populates="owner")
    playlists = orm.relationship("Playlist", back_populates="owner")

    def __repr__(self):
        return "<User(login='%s'; password='%s'; name='%s')>" % (self.login, self.password, self.name)

    def create(self):
        db_session.add(self)
        db_session.commit()
        return self

    @classmethod
    def find(cls, *columns, **where):
        if columns:
            # які колонки повернути
            columns = [cls.__table__.columns[column_name] for column_name in columns]
        else:
            columns = [cls]
        if where:
            # які умови фільтрації
            return db_session.query(*columns).filter(sqla.and_( 
                *[cls.__table__.columns[column_name] == column_value  
                for column_name, column_value in where.items()] )).all()
        return db_session.query(*columns).all()



# сутність "Виконавець"
class Performer(Base):
    __tablename__ = 'Performer'
    name = sqla.Column(sqla.String, primary_key = True)

    songs = orm.relationship("Song", back_populates="performer")
    albums = orm.relationship("Album", back_populates="performer")

    def __repr__(self):
        return "<Performer(name='%s')>" % (self.name)

    def create(self):
        db_session.add(self)
        db_session.commit()
        return self

    def delete_self(self):
        db_session.delete(self)
        db_session.commit()

    @classmethod
    def find(cls, *columns, **where):
        if columns:
            # які колонки повернути
            columns = [cls.__table__.columns[column_name] for column_name in columns]
        else:
            columns = [cls]
        if where:
            # які умови фільтрації
            return db_session.query(*columns).filter(sqla.and_( 
                *[cls.__table__.columns[column_name] == column_value  
                for column_name, column_value in where.items()] )).all()
        return db_session.query(*columns).all()



# сутність "Альбом"
class Album(Base):
    __tablename__ = "Album"
    name = sqla.Column(sqla.String, primary_key = True)
    performer_name = sqla.Column(sqla.String, sqla.ForeignKey('Performer.name'), primary_key = True)

    performer = orm.relationship("Performer", back_populates="albums")
    songs = orm.relationship("Song", back_populates="album")

    def __repr__(self):
        return "<Album(name='%s'; performer_name='%s')>" % (self.name, self.performer_name)

    def create(self):
        db_session.add(self)
        db_session.commit()
        return self

    def delete_self(self):
        db_session.delete(self)
        db_session.commit()

    @classmethod
    def find(cls, *columns, **where):
        if columns:
            # які колонки повернути
            columns = [cls.__table__.columns[column_name] for column_name in columns]
        else:
            columns = [cls]
        if where:
            # які умови фільтрації
            return db_session.query(*columns).filter(sqla.and_( 
                *[cls.__table__.columns[column_name] == column_value  
                for column_name, column_value in where.items()] )).all()
        return db_session.query(*columns).all()

    def find_like(query):
        return db_session.query(Album).filter(sqla.or_(
            Album.name.ilike(f'%{query}%'), 
            Album.performer_name.ilike(f'%{query}%')
        )).all()


PlaylistElements = sqla.Table('PlaylistElements', Base.metadata,
    sqla.Column('song_name', primary_key = True),
    sqla.Column('performer_name', primary_key = True),
    sqla.Column('playlist_name', primary_key = True),
    sqla.Column('owner_id', primary_key = True),
    sqla.ForeignKeyConstraint(['song_name', 'performer_name'], ['Song.name', 'Song.performer_name']),
    sqla.ForeignKeyConstraint(['playlist_name', 'owner_id'], ['Playlist.name', 'Playlist.owner_id']),
)


# сутність "Пісня"
class Song(Base):
    __tablename__ = 'Song'
    name = sqla.Column(sqla.String, primary_key = True)
    performer_name = sqla.Column(sqla.String, sqla.ForeignKey('Performer.name'), primary_key = True)
    owner_id = sqla.Column(sqla.String, sqla.ForeignKey('User.login'), nullable = False)
    audio_file = sqla.Column(sqla.String)
    album_name = sqla.Column(sqla.String)
    __table_args__ = (sqla.ForeignKeyConstraint(['album_name', 'performer_name'], ['Album.name', 'Album.performer_name']), {})

    owner = orm.relationship("User", back_populates="songs")
    performer = orm.relationship("Performer", back_populates="songs")
    album = orm.relationship("Album", back_populates="songs")
    # багато до багатьох Song<->Playlist
    playlists = orm.relationship('Playlist',
                        secondary=PlaylistElements,
                        back_populates='songs')


    def __repr__(self):
        return "<Song(name='%s'; performer_name='%s'; owner_id='%s'; album_name='%s'; audio_file='%s')>" % (
            self.name, self.performer_name, self.owner_id, self.album_name, self.audio_file)


    def create(self):
        db_session.add(self)
        db_session.commit()
        return self

    def delete_self(self):
        db_session.delete(self)
        db_session.commit()

    def update_self(self, name, performer_name, album_name):
        playlists = self.playlists
        old_name = self.name
        old_performer_name = self.performer_name

        delete_query = PlaylistElements.delete().where(
                PlaylistElements.c.song_name == old_name,
                PlaylistElements.c.performer_name == old_performer_name
            )
        db_session.execute(delete_query)

        self.name = name
        self.performer_name = performer_name
        self.album_name = album_name
        db_session.commit()

        for playlist in playlists:
            insert_query = PlaylistElements.insert().values(
                    song_name = name,
                    performer_name = performer_name,
                    playlist_name = playlist.name,
                    owner_id = playlist.owner_id
                )
            db_session.execute(insert_query)
        db_session.commit()

    @classmethod
    def find(cls, *columns, **where):
        if columns:
            # які колонки повернути
            columns = [cls.__table__.columns[column_name] for column_name in columns]
        else:
            columns = [cls]
        if where:
            # які умови фільтрації
            return db_session.query(*columns).filter(sqla.and_( 
                *[cls.__table__.columns[column_name] == column_value  
                for column_name, column_value in where.items()] )).all()
        return db_session.query(*columns).all()


    def find_like(query):
        return db_session.query(Song).filter(sqla.or_(
            Song.name.ilike(f'%{query}%'), 
            Song.performer_name.ilike(f'%{query}%')
        )).all()



# сутність "Плейліст"
class Playlist(Base):
    __tablename__ = "Playlist"
    name = sqla.Column(sqla.String, primary_key = True)
    owner_id = sqla.Column(sqla.String, sqla.ForeignKey('User.login'), primary_key = True)
    private = sqla.Column(sqla.Boolean, nullable = False)

    owner = orm.relationship("User", back_populates="playlists")
    # багато до багатьох Song<->Playlist
    songs = orm.relationship('Song',
                        secondary=PlaylistElements,
                        back_populates='playlists')

    def __repr__(self):
        return "<Playlist(name='%s'; owner_id='%s'; private='%s')>" % (
            self.name, self.owner_id, self.private)

    def create(self):
        db_session.add(self)
        db_session.commit()
        return self

    def update_self(self, private):
        self.private = private
        db_session.commit()

    def delete_self(self):
        db_session.delete(self)
        db_session.commit()

    @classmethod
    def find(cls, *columns, **where):
        if columns:
            # які колонки повернути
            columns = [cls.__table__.columns[column_name] for column_name in columns]
        else:
            columns = [cls]
        if where:
            # які умови фільтрації
            return db_session.query(*columns).filter(sqla.and_( 
                *[cls.__table__.columns[column_name] == column_value  
                for column_name, column_value in where.items()] )).all()
        return db_session.query(*columns).all()

    def find_like(query, user_id):
        return db_session.query(Playlist).filter(sqla.and_(
            Playlist.name.ilike(f'%{query}%'), sqla.or_(
            Playlist.private == False, Playlist.owner_id == user_id)
        )).all()



"""Base.metadata.drop_all(bind=engine)
db_session.commit()"""

# створити описані вище таблиці
Base.metadata.create_all(engine)


"""
hlib = User(login='hlib@kpi.ua', password='my_pass', name='Гліб').create()
alice = User(login='2', password='my_pass', name='Alice').create()
hollow_coves = Performer(name='Hollow Coves').create()
ajr = Performer(name='AJR').create()
home = Album(name='Home', performer_name='Hollow Coves').create()
click = Album(name='The Click', performer_name='AJR').create()
woods = Song(name='The Woods', performer_name='Hollow Coves', owner_id='1', album_name='Home', audio_file='Hollow Coves - The Woods.mp3').create()
sober_up = Song(name='Sober Up', performer_name='AJR', owner_id='2', album_name='The Click', audio_file='AJR - Sober Up.mp3').create()
hlib_playlist = Playlist(name="Hlib's playlist", owner_id='1', private=False).create()
alice_playlist = Playlist(name="Alice's playlist", owner_id='2', private=False).create()
hlib_playlist.songs.extend([woods, sober_up])
alice_playlist.songs.append(sober_up)"""



db_session.commit()
