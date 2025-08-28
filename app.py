"""Run commands to manage a movie database."""
import os
import requests
import random
import statistics
import shutil
from movie_storage import movie_storage_sql as storage

API_KEY = "8da11d34"
API_URL = f"http://www.omdbapi.com/?i=tt3896198&apikey={API_KEY}&"

class BColors:
    """COLORS AND TEXT FORMATTING FOR THE CLI CONTENTS"""
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_CYAN = '\033[96m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

CLI_MAIN_MENU = f'''
{BColors.OK_CYAN}{BColors.UNDERLINE}{BColors.BOLD}{'〰️' * 5} DB from Danilo {'〰️' * 5}{BColors.ENDC}
{BColors.BOLD}{BColors.HEADER}#. Menu options{BColors.ENDC}
{BColors.OK_BLUE}0. Quit{BColors.ENDC}
{BColors.OK_BLUE}1. List movies{BColors.ENDC}
{BColors.OK_BLUE}2. Add movie{BColors.ENDC}
{BColors.OK_BLUE}3. Delete movie{BColors.ENDC}
{BColors.OK_BLUE}4. Update movie{BColors.ENDC}
{BColors.OK_BLUE}5. Stats{BColors.ENDC}
{BColors.OK_BLUE}6. Random movie{BColors.ENDC}
{BColors.OK_BLUE}7. Search movie{BColors.ENDC}
{BColors.OK_BLUE}8. Movies sorted by rating{BColors.ENDC}
{BColors.OK_BLUE}9. Generate Website{BColors.ENDC}
{'〰️' * 18}\n
{BColors.HEADER}{BColors.BOLD}Enter choice (0-9): {BColors.ENDC}'''


def command_list_movies():
    """Retrieve and display all movies from the database."""
    movies = storage.list_movies()
    print(f"\n{BColors.OK_CYAN}#️⃣ {len(movies)} movies "
          f"in total{BColors.ENDC}")

    for movie, data in movies.items():
        print(f"{BColors.OK_BLUE}🎬 {movie}: {data['rating']} "
              f"({data['year']}){BColors.ENDC}")


def command_add_movie():
    """Add a new movie to the database."""
    request_try_count = 0
    while True:
        # Break when API raise RequestException 3 times
        if request_try_count == 3:
            print(f"{BColors.FAIL}{BColors.BOLD}API is not"
                  f"available..try again later!{BColors.ENDC}")
            break

        movies =  storage.list_movies()
        title = input('\nChoose the movie title: ')

        if title == '':
            print(f"{BColors.FAIL}{BColors.BOLD}You need "
                  f"to type something!{BColors.ENDC}")
            continue

        params = {
            "type": "movie",
            't': title,
        }

        # Fetch movies data from OMDbAPI
        try:
            api_result = requests.get(API_URL, params=params).json()
        except requests.exceptions.RequestException as error:
            request_try_count += 1
            print(f"{BColors.FAIL}Can't get a valid response: "
            f"{str(error).split('(')[0]}{BColors.ENDC}")
            continue

        if api_result['Response'] == 'False' or len(api_result) == 0:
            print(f"{BColors.FAIL}{BColors.BOLD}Movie "
            f"{title} not found!{BColors.ENDC}")
            continue

        # Check if all datas are valid
        year = None
        rating = None
        img_url = None
        user_id = 0

        if len(api_result['Title']) > 0:
            title = api_result['Title']

        # Stops if movie is already in the database
        if title in movies:
            print(f"{BColors.FAIL}{BColors.BOLD}Movie {title} "
                  f"already exist!{BColors.ENDC}")
            continue

        if len(api_result['Year']) == 4:
            year = api_result['Year']

        if len(api_result['Ratings']) > 0:
            rating = api_result['Ratings'][0]['Value'].split('/')[0]

        if len(api_result['Poster']) > 0:
            img_url = api_result['Poster']

        # Stops if any of the required data is missing
        if year is None or rating is None or img_url is None:
            print(f"{BColors.FAIL}{BColors.BOLD}Movie "
                  f"{title} has some missing data!{BColors.ENDC}")
            continue

        # Adds fetched data to the database
        storage.add_movie(title, year, rating, img_url, user_id )
        print(f"\n{BColors.OK_GREEN}{BColors.BOLD}{title} ({year}) "
              f"is now in the DB with the rating of {rating}{BColors.ENDC}")
        break


def command_delete_movie():
    """Delete a movie from the database."""
    while True:
        movies =  storage.list_movies()
        title = input('\nSelect movie to delete: ')
        if title not in movies:
            print(f'\n{BColors.FAIL}{BColors.BOLD}Movie is not in the DB{BColors.ENDC}')
            break

        storage.delete_movie(title)
        print(f'{BColors.OK_GREEN}{BColors.BOLD}{title} deleted!{BColors.ENDC}')
        break


def command_update_movie():
    """Update a movie from the database."""
    movies = storage.list_movies()
    while True:
        title = input('\nChoose the movie title: ')
        if title not in movies:
            print(f'\n{BColors.FAIL}{BColors.BOLD}Movie is not in the DB{BColors.ENDC}')
            break

        note = input(f'\nAdd a note to {title}: ')
        # Add a note to the movie in the database
        storage.update_movie(title, note)
        print(f'\n{BColors.OK_GREEN}'
              f'{BColors.BOLD}{title} has a new note!{BColors.ENDC}')
        break


def command_get_stats():
    """Shows general statistics about the database."""
    movies = storage.list_movies()
    best_movies = []
    worst_movies = []
    all_ratings = []

    for title, info in movies.items():
        all_ratings.append(info['rating'])
        if info['rating'] >= max(all_ratings):
            best_movies.append(title)
        elif info['rating'] <= min(all_ratings):
            worst_movies.append(title)

    avg_rating = round(sum(all_ratings) / len(movies), 1)
    median_rating = round(statistics.median(all_ratings), 1)

    print(f'\n{BColors.OK_CYAN}Avg rating: {avg_rating}{BColors.ENDC}')
    print(f'{BColors.OK_BLUE}Median rating: {median_rating}{BColors.ENDC}')

    for best_movie in best_movies:
        movie_rating = movies[best_movie]["rating"]
        if movie_rating == max(all_ratings):
            print(f'{BColors.OK_GREEN}'
                  f'Best movie: {best_movie}, {movie_rating}{BColors.ENDC}')

    for worst_movie in worst_movies:
        movie_rating = movies[worst_movie]["rating"]
        if movie_rating == min(all_ratings):
            print(f'{BColors.WARNING}Worst movie: {worst_movie}, '
                  f'{movies[worst_movie]["rating"]}{BColors.ENDC}')


def command_random_movie():
    """Pick a random movie from the database."""
    movies = storage.list_movies()
    title, info = random.choice(list(movies.items()))
    print(f"\n{BColors.WARNING}"
          f"{BColors.BOLD}Let's watch {title}, it has a rating of {info['rating']}!{BColors.ENDC}")


def command_search_movie():
    """Search for a movie in the database by title."""
    movies = storage.list_movies()
    while True:
        search = input(f"\n{BColors.WARNING}"
                       f"{BColors.BOLD}Enter part of a movie title: {BColors.ENDC}")

        count = 0
        for title, info in movies.items():
            if search.lower() in title.lower():
                count += 1
                print(f"{BColors.OK_GREEN}{title} -> "
                      f"{info['rating']} ({info['year']}){BColors.ENDC}")

        if count == 0:
            print(f'\n{BColors.FAIL}{BColors.BOLD}Nothing found!{BColors.ENDC}')
            break
        break


def command_sort_movies():
    """Sorts the movies in the database by rating DESC."""
    movies = storage.list_movies()
    sorted_movies = sorted(movies.items(), key=lambda item: item[1]['rating'], reverse=True)
    print() # spacing for readability
    for title, info in sorted_movies:
        print(f'{BColors.OK_BLUE}{title} -> {info["rating"]} ({info["year"]}){BColors.ENDC}')


def command_generate_website():
    # Define paths
    current_dir = os.getcwd()
    index_template = "index_template.html"
    index = "index.html"
    style = "style.css"

    # Join paths for compatibility
    src_index_path = os.path.join(current_dir, "_static", index_template)
    dst_index_path = os.path.join(current_dir, "static", index)
    src_css_path = os.path.join(current_dir, "_static", style)
    dst_css_path = os.path.join(current_dir, "static", style)

    # Create static folder if it doesn't exist
    os.makedirs(os.path.dirname(dst_index_path), exist_ok=True)
    # Copy the style.css without changes
    shutil.copy(src_css_path, dst_css_path)

    # Read index_template.html from _static
    with open(src_index_path, "r") as src_index:
        html_raw = src_index.read()
        # Row where to append the list elements
        movie_grid_row = 11

    """
    Generate static files in /static
    using _static/index_template.html
    and renders movies from the database
    """
    with open(dst_index_path, "w") as dst_index:
        for line_num, line in enumerate(html_raw.split('\n'), start=1):
            # Append li elements after <ol class="movie-grid">
            if line_num == movie_grid_row:
                dst_index.write(f"{line}\n")
                # Get movies from database
                movies = storage.list_movies()
                full_list = ""
                for movie, data in movies.items():
                    # Define positive or negative ratings
                    last_negative_rating = 5.99
                    rating_class = "movie-rating-"

                    if float(data['rating']) > last_negative_rating:
                        rating_class += 'positive'
                    else:
                        rating_class += 'negative'

                    movie_to_append = f"""<li>
            <div class="movie">
                <img class="movie-poster"
                     src={data['img_url']}/>
                <div class="movie-title">{movie}</div>
                <div class="movie-year">{data['year']}</div>
                <div class={rating_class}>{data['rating']}/10</div>
            </div>
        </li>
                    """
                    full_list += movie_to_append
                dst_index.write(full_list)
            else:
                dst_index.write(f"{line}\n")

    print(f"{BColors.OK_GREEN}Website was generated successfully.{BColors.ENDC}")


def main():
    """Runs the CLI in loop"""
    is_cli_open = True
    all_options = {
      1: command_list_movies,
      2: command_add_movie,
      3: command_delete_movie,
      4: command_update_movie,
      5: command_get_stats,
      6: command_random_movie,
      7: command_search_movie,
      8: command_sort_movies,
      9: command_generate_website,
      }

    while is_cli_open:
        try:
            selected_option = int(input(CLI_MAIN_MENU))

            if selected_option in range(9):
                if selected_option == 0:
                    print(f"\n{BColors.WARNING}"
                          f"{BColors.BOLD}{'〰️' * 10} Bye!! {'〰️' * 10}{BColors.ENDC}\n")
                    break
            all_options[selected_option]()

            press_enter = input(f'\n{BColors.HEADER}'
                                f'{BColors.BOLD}Press enter to continue{BColors.ENDC}')

            if press_enter == '':
                continue

        except KeyError as key:
            print(f'\n{BColors.FAIL}{BColors.BOLD}Option {key} not valid!{BColors.ENDC}')

        except ValueError:
            print(f'\n{BColors.FAIL}{BColors.BOLD}Type a number to choose an option!{BColors.ENDC}')


if __name__ == "__main__":
    main()
