#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#     Extra credit implementations:
#         - Prevent rematches between players.
#         - Not assuming an even number of players.
#         - Support more than one tournament in the database.

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def delete_matches(tournament_id):
    """Remove all the match records from the database."""
    db = connect()
    try:
        sql = """
                DELETE FROM matches WHERE id in (
                    SELECT
                        m_id
                    FROM
                        tournament_matches,matches
                    WHERE
                        t_id = %s);
                """
        curs = db.cursor()
        curs.execute(sql, (tournament_id,))
        db.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()


def delete_tournament(tournament_id):
    """Remove all the player records from the database."""
    db = connect()
    try:
        delete_tournament_players(tournament_id)
        delete_matches(tournament_id)
        sql = "DELETE FROM tournament where id=%s"
        curs = db.cursor()
        curs.execute(sql, (tournament_id,))
        db.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()


def delete_players():
    """Remove all the player information from the database.

    When no more players are registered in a tournament,
    this will clean out the player data.

    See `delete_tournament_players` for removing players
    registered in a tournament.
    """
    db = connect()
    try:
        sql = "DELETE FROM player;"
        curs = db.cursor()
        curs.execute(sql)
        db.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()


def delete_tournament_players(tournament_id):
    """Remove all the player records from the database.
    Args:
        tournament_id: Tournament id you want to count the players of.
    """
    db = connect()
    try:
        sql = "DELETE FROM tournament_players WHERE t_id = %s;"
        curs = db.cursor()
        curs.execute(sql, (tournament_id,))
        db.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()


def count_players(tournament_id):
    """Returns the number of players currently registered.

    Args:
        tournament_id: Tournament id you want to count the players of.

    Return:
        count: Number of players in the tournament
    """
    db = connect()
    try:
        sql = """SELECT
                    COALESCE(count(p_id),0)
                 FROM
                    tournament_players
                 WHERE t_id=%s"""
        curs = db.cursor()
        curs.execute(sql, (tournament_id,))
        result = curs.fetchone()
        return result[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()


def register_player(name):
    """Adds a player to the player table.

    The database assigns a unique serial id number for the player.

    Args:
      name: the player's full name (need not be unique).
    Returns:
      id: the of the player added
    """
    db = connect()
    try:
        sql = """INSERT INTO player VALUES(DEFAULT,%s);
                 SELECT currval('player_id_seq');"""
        curs = db.cursor()
        curs.execute(sql, (name,))
        db.commit()
        player_id = curs.fetchone()
        return player_id[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()


def register_tournament(tournament_name):
    """Creates a tournament in the database.

    The database can accommodate many different tournaments, and this
    function will add as many as you need.

    Args:
        tournament_name: Name your tournament
    Returns:
        id: The tournament id
    """
    db = connect()
    try:
        sql = """INSERT INTO tournament(name) VALUES(%s);
                 SELECT currval('tournament_id_seq');"""
        curs = db.cursor()
        curs.execute(sql, (tournament_name,))
        db.commit()
        tournament_id = curs.fetchone()
        return tournament_id[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        return None
    finally:
        if db:
            db.close()


def register_player_in_tournament(tournament_id, player_id):
    """Adds a player to a tournament.

    Links up a player with the desired tournament. A player can be assigned to
    many tournaments. Both the player and tournament needs to exist in the
    Player and Tournament tables.

    Args:
      tournament_id: The tournament id to register player in
      player_id: the id of the player to register
    """
    db = connect()
    try:
        sql = "INSERT INTO tournament_players VALUES(%s,%s);"
        curs = db.cursor()
        curs.execute(sql, (tournament_id, player_id))
        db.commit()
    except psycopg2.DatabaseError, e:
        print 'E Error %s' % e
    finally:
        if db:
            db.close()


def player_standings(tournament_id):
    """Returns a list of the players and their win records, sorted by wins.

    Args:
        tournament_id: The tournament id to list the standings for.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    try:
        sql = """
            SELECT
                tournament_players.p_id,
                player.fullname,
                COALESCE(winner_table.wins,0) AS wins,
                COALESCE(winner_table.wins,0) + COALESCE(loser_table.losts, 0)
                    AS matches
            FROM
                tournament_players LEFT JOIN winner_table
                ON tournament_players.p_id = winner_table.winner_id
                LEFT JOIN loser_table
                ON tournament_players.p_id = loser_table.loser_id
                LEFT JOIN player
                on tournament_players.p_id = player.id
            WHERE
                tournament_players.t_id = %s
            ORDER BY wins DESC NULLS LAST;"""
        curs = db.cursor()
        curs.execute(sql, (tournament_id,))
        result = curs.fetchall()
        return result
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()


def report_match(tournament_id, winner, loser):
    """Records the outcome of a single match in a tournament
    between two players.

    Args:
        tournament_id: The tournament id to log the match results to.
        winner:  the id number of the player who won
        loser:  the id number of the player who lost
    """
    db = connect()
    try:
        sql = """
            INSERT INTO
                matches
                VALUES(DEFAULT,%s,%s);
            INSERT INTO
                tournament_matches
                VALUES(%s,
                       (SELECT currval('matches_id_seq'))
                       );
            """
        curs = db.cursor()
        curs.execute(sql, (winner, loser, tournament_id))
        db.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()


def match_history(tournament_id):
    """Returns a list of unique pairs of players of previous matches in the
    tournament.

    Args:
        tournament_id: The tournament id to log the match results to.

    Returns:
     A list op tuples, each containing (id1,id2)
        id1: winner
        id2: loser
    """
    db = connect()
    try:
        sql = """
                SELECT DISTINCT
                    winner_id,
                    loser_id
                FROM
                    tournament_matches LEFT JOIN matches
                    ON tournament_matches.m_id = matches.id
                WHERE
                    loser_id is not null
                    and tournament_matches.t_id = %s
                    and winner_id < loser_id;
              """
        curs = db.cursor()
        curs.execute(sql, (tournament_id,))
        return curs.fetchall()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()


def players_with_bye_games(tournament_id):
    """Returns a list of players who had byes.

    A 'bye' match is created when an uneven count of players are registered for
    a tournament. A player is allowed to have 1 bye match.

    Args:
        tournament_id: The tournament id to log the match results to.

    Returns:
        A list of player id's
    """
    db = connect()
    try:
        sql = """
                SELECT DISTINCT
                    winner_id
                FROM
                    tournament_matches LEFT JOIN matches
                    ON tournament_matches.m_id = matches.id
                WHERE
                    loser_id is null
                    AND tournament_matches.t_id = %s;
              """
        curs = db.cursor()
        curs.execute(sql, (tournament_id,))
        result = curs.fetchall()
        return [x[0] for x in result]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()


def swiss_pairings(tournament_id):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    When uneven number of players are registered, the pairing still happens
    the same as in the case of even number of players, but the extra player
    gets assigned a bye match. A player can only have one bye match in the
    tournament.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    temp_pairing = []
    final_pairing = []
    standings = player_standings(tournament_id)
    played_players = match_history(tournament_id)
    players_with_byes = players_with_bye_games(tournament_id)

    player1_standings = [x[0] for x in standings]
    player2_standings = [x[0] for x in standings]

    # Create pairings. Here we also filter out previous parings, which
    # implements extra credit: 'Prevent rematches between players.'
    for player1 in player1_standings:
        for player2 in player2_standings:
            p2_picked = [z for z in temp_pairing
                         if z[0] == player2 or z[1] == player2]
            p1_picked = [z for z in temp_pairing
                         if z[0] == player1 or z[1] == player1]

            if p2_picked\
                or p1_picked\
                or player1 == player2\
                or (player1, player2) in played_players\
                    or (player2, player1) in played_players:
                continue
            temp_pairing.append((player1, player2))

    # Create a bye game, but only if player does not already have one.
    # It is not clearly defined what happens when a player is up for
    # a second bye, but I'm assuming this will not happen.
    temp_paired_players = set([x for t in temp_pairing for x in t])
    players_to_get_free_win = set(player1_standings)-temp_paired_players
    for x in players_to_get_free_win:
        if x not in players_with_byes:
            temp_pairing.append((x, None))

    # Create tuple of matched player ids and names
    for p in temp_pairing:
        left_id = p[0]
        right_id = p[1]
        left_name = [x[1] for x in standings if x[0] == left_id][0]
        #  If a bye match, the player on the right will be None
        if right_id:
            right_name = [x[1] for x in standings if x[0] == right_id][0]
        else:
            right_name = None
        t = (left_id, left_name, right_id, right_name)
        final_pairing.append(t)

    return final_pairing
