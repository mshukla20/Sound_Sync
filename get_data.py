import db_connect
import youtube_dl
import urllib2, re


def clean_string(s):
    if "(" in s:
        s = s.split("(")[0].strip()
    if "[" in s:
        s = s.split("[")[0].strip()
    if "\"" in s:
        s = s.split("\"")[0].strip()
    s = s.replace("&amp", "and").replace(";", "").replace("&quot", "").replace("&#39i", "i").replace("&#39m",
                                                                                                     "m").replace(
        "&#39s", "s").replace("&#39", "'").decode('ascii', errors='ignore').encode()
    s = s.rstrip(".")
    name = ""
    for word in s.split(" "):
        if "and" not in word and "of" not in word:
            name = name + " " + word.lower().capitalize()
        else:
            name = name + " " + word.lower()
    name = name.replace("!", "i")
    return name.lstrip().rstrip()


def filter_data(data):
    global artists
    global titles

    artists = []
    titles = []
    for pair in data:
        pair = pair.lstrip("-")
        artist = clean_string(pair.split("=")[1].split("-")[0].strip().strip("\""))
        if "-" in pair:
            title = clean_string(pair.split("-")[1].strip())
        else:
            title = clean_string(pair.strip())
        if "Official" in pair.split("-")[0] or "[" in pair.split("-")[0]:
            tmp = title
            title = artist
            artist = tmp
        title_, artist_ = unique_cases(title, artist)
        artists.append(artist_)
        titles.append(title_)


def get_remote_data(url):
    page = urllib2.urlopen(url)
    data = page.read()
    artist_song = re.findall("-title=.*?\">", data)
    return artist_song


def get_db_data():
    global db_artists, db_titles
    select_stat_a = "select artist_name from musicsync.artist;"
    select_stat_t = "select title_name from musicsync.title;"
    db_artists = db.sql_query(select_stat_a)
    db_titles = db.sql_query(select_stat_t)


def insert_artist(artist_name):
    insert_stat = "insert into musicsync.artist values(DEFAULT,\"" + artist_name + "\");"
    if db_artists:
        if artist_name not in db_artists:
            db.sql_insert(insert_stat)
    else:
        db.sql_insert(insert_stat)


def unique_cases(title_name, artist_name):
    if title_name.isdigit():
        title_name = "1 Percent African"
    if artist_name == "Set" or artist_name == "Video" or artist_name == "Title=":
        artist_name = "Chris Brown"  # Better logic needed here
    if "Robin" in title_name:
        artist_name = "Robin Schulz"
        title_name = "OK"
    if "Official" in title_name:
        artist_name = "YBN Nahmir"
        title_name = "Rubbin Off the Paint"
    return title_name, artist_name


def insert_title(title_name, artist_name):
    check_artist_stat = "select artist_id from musicsync.artist where artist_name like \"" + artist_name + "\";"
    artist_id = db.sql_query(check_artist_stat)
    title_stat = "insert into musicsync.title values(DEFAULT,\"" + title_name + "\"," + str(artist_id[0]) + ");"
    try:
        if db_titles:
            if title_name not in db_titles:
                db.sql_insert(title_stat)
        else:
            db.sql_insert(title_stat)
    except Exception, err:
        print "ERROR: " + str(err)


def truncate_db():
    truncate_artist = "truncate musicsync.artist;"
    truncate_title = "truncate musicsync.title;"
    for cmd in [truncate_artist, truncate_title]:
        db.sql_query(cmd)


def main():
    global db
    global artists, titles

    data = get_remote_data("https://www.youtube.com/playlist?list=PLx0sYbCqOb8TBPRdmBHs5Iftvv9TPboYG")
    db = db_connect.Database()
    truncate_db()
    filter_data(data)
    for curr_artist, curr_title in zip(artists, titles):
        get_db_data()
        insert_artist(curr_artist)
        insert_title(curr_title, curr_artist)
    db.conn.close()


if __name__ == '__main__':
    main()