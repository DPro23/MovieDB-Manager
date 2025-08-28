""" Create the engine and connect to the database """
from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///data/movies.db"
# Create the engine to connect to the DB
engine = create_engine(DB_URL, echo=False)


def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT title, year, rating, img_url, note FROM movies"))
        movies = result.fetchall()

    return {row[0]: {
        "year": row[1],
        "rating": row[2],
        "img_url": row[3],
        "note": row[4]}
        for row in movies}


def add_movie(title, year, rating, img_url, user_id):
    """Add a new movie to the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text("""
            INSERT INTO movies (title, year, rating, img_url, user_id, note) 
            VALUES (:title, :year, :rating, :img_url, :user_id, :note)"""),
                               {
                                   "title": title,
                                   "year": year,
                                   "rating": rating,
                                   "img_url": img_url,
                                   "user_id": user_id,
                                   # title is the default note
                                   "note": title
                               })
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")


def delete_movie(title):
    """Delete a movie from the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("DELETE FROM movies WHERE title = :title"),
                {"title": title})
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")


def update_movie(title, note):
    """Add a note to a movie and store it in the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("UPDATE movies SET note = :note WHERE title = :title"),
                {"title": title, "note": note})
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")


def create_movies_table():
    """Create the movies table if it does not exist"""
    with engine.connect() as connection:
        connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL
                    );
                    """))
        connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS movies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT UNIQUE NOT NULL,
                        year INTEGER NOT NULL,
                        rating REAL NOT NULL,
                        img_url TEXT NOT NULL,
                        note TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        foreign KEY (user_id) REFERENCES users (id)
                    );
                    """))
        connection.commit()


create_movies_table()