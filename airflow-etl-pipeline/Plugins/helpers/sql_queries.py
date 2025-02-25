class SqlQueries:
    songplay_table_insert = ("""
        INSERT INTO songplays (playid, start_time, userid, level, songid, artistid, sessionid, location, user_agent)
        SELECT
                md5(events.sessionid || events.start_time) songplay_id,
                events.start_time, 
                events.userid, 
                events.level, 
                songs.song_id, 
                songs.artist_id, 
                events.sessionid, 
                events.location, 
                events.useragent
        FROM (SELECT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' AS start_time, *
              FROM staging_events
              WHERE page='NextSong') events
        LEFT JOIN staging_songs songs
        ON events.song = songs.title
        AND events.artist = songs.artist_name
        AND events.length = songs.duration
    """)

    user_table_insert = ("""
        INSERT INTO users (userid, first_name, last_name, gender, level)
        SELECT DISTINCT userid, firstname, lastname, gender, level
        FROM staging_events
        WHERE page='NextSong'
    """)

    song_table_insert = ("""
        INSERT INTO songs (songid, title, artistid, year, duration)
        SELECT DISTINCT song_id, title, artist_id, year, duration
        FROM staging_songs
    """)

    artist_table_insert = ("""
        INSERT INTO artists (artistid, name, location, latitude, longitude)  -- ✅ Fixed spelling of 'latitude'
        SELECT DISTINCT artist_id, artist_name, artist_location, artist_latitude, artist_longitude
        FROM staging_songs
    """)

    time_table_insert = ("""
        INSERT INTO time (start_time, hour, day, week, month, year, weekday)  -- ✅ Changed 'dayofweek' to 'weekday'
        SELECT start_time, 
               EXTRACT(hour FROM start_time), 
               EXTRACT(day FROM start_time), 
               EXTRACT(week FROM start_time), 
               EXTRACT(month FROM start_time), 
               EXTRACT(year FROM start_time), 
               EXTRACT(dow FROM start_time)  -- ✅ Corrected PostgreSQL syntax
        FROM songplays
    """)
