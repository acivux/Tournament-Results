#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches(tournament_id):
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

def deleteTournament(tournament_id):
    """Remove all the player records from the database."""
    db = connect()
    try:
        deleteTournamentPlayers(tournament_id)
        deleteMatches(tournament_id)
        sql = "DELETE FROM tournament where id=%s"
        curs = db.cursor()
        curs.execute(sql, (tournament_id,))
        db.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()

def deletePlayers():
    """Remove all the player records from the database."""
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

def deleteTournamentPlayers(tournament_id):
    """Remove all the player records from the database."""
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

def countPlayers(tournament_id):
    """Returns the number of players currently registered."""
    db = connect()
    try:
        sql = "SELECT COALESCE(count(p_id),0) from tournament_players WHERE t_id=%s"
        curs = db.cursor()
        curs.execute(sql, (tournament_id,))
        result = curs.fetchone()
        return result[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    Returns:
      id: the of the player added
    """
    db = connect()
    try:
        sql = "INSERT INTO player VALUES(DEFAULT,%s); SELECT currval('player_id_seq');"
        curs = db.cursor()
        curs.execute(sql, (name,))
        db.commit()
        id = curs.fetchone()
        return id[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()

def registerTournament(tournament_name, tournament_id="DEFAULT"):
    """fff"""
    db = connect()
    try:
        sql = "INSERT INTO tournament VALUES(%s,%s);"
        curs = db.cursor()
        curs.execute(sql, (tournament_id, tournament_name))
        db.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()

def registerPlayerInTournament(tournament_id, player_id):
    """ddd"""
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


def playerStandings(tournament_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

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
                COALESCE(wintable.wins,0) AS wins,
                COALESCE(wins,0) + COALESCE(losertable.losts, 0) AS matches
            FROM
                tournament_players LEFT JOIN
                    (SELECT
                        winner_id,
                        count(winner_id) AS wins
                     FROM matches
                     GROUP BY winner_id) AS wintable
                ON tournament_players.p_id = wintable.winner_id
                LEFT JOIN
                    (SELECT loser_id,
                            COUNT(loser_id) AS losts
                     FROM matches
                     GROUP BY loser_id) AS losertable
                ON tournament_players.p_id = losertable.loser_id
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
        print 'D Error %s' % e
    finally:
        if db:
            db.close()

def reportMatch(tournament_id, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    try:
        sql = """
            INSERT INTO matches VALUES(DEFAULT,%s,%s);
            INSERT INTO tournament_matches VALUES(%s, (SELECT currval('matches_id_seq')));
            """
        curs = db.cursor()
        curs.execute(sql, (winner, loser, tournament_id))
        db.commit()
    except psycopg2.DatabaseError, e:
        print 'C Error %s' % e
    finally:
        if db:
            db.close()

def matchHistory(tournament_id):
    """Returns a list of pairs of players of previous matches

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
                    tournament_matches left join matches
                    on tournament_matches.m_id = matches.id
                WHERE
                    loser_id is not null
                    and tournament_matches.t_id = %s;
              """
        curs = db.cursor()
        curs.execute(sql, (tournament_id,))
        qresult = curs.fetchall()
        result = []
        for x in qresult:
            tt = (x[1], x[0])
            if x not in result and tt not in result:
                result.append(x)
        return result
    except psycopg2.DatabaseError, e:
        print 'B Error %s' % e
    finally:
        if db:
            db.close()

def freeBe(tournament_id):
    db = connect()
    try:
        sql = """
                SELECT DISTINCT
                    winner_id
                FROM
                    tournament_matches left join matches
                    on tournament_matches.m_id = matches.id
                WHERE
                    loser_id is null
                    and tournament_matches.t_id = %s;
              """
        curs = db.cursor()
        curs.execute(sql, (tournament_id,))
        result = curs.fetchall()
        return [x[0] for x in result]
    except psycopg2.DatabaseError, e:
        print 'A Error %s' % e
    finally:
        if db:
            db.close()

def swissPairings(tournament_id):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings(tournament_id)
    left_standings = [x[0] for x in standings]
    right_standings = [x[0] for x in standings]
    pairing = []
    played_players = matchHistory(tournament_id)
    free_bees = freeBe(tournament_id)

    for left in left_standings:
        for right in right_standings:
            if [z for z in pairing if z[0] == right or z[1] == right]\
                    or [z for z in pairing if z[0] == left or z[1] == left]\
                    or left == right\
                    or (left, right) in played_players\
                    or (right, left) in played_players\
                    or (left, right) in pairing\
                    or (right, left) in pairing:
                continue
            pairing.append((left, right))

    used = set([x for t in pairing for x in t])
    free_win = set(left_standings)-used
    for x in free_win:
        if x not in free_bees:
            pairing.append((x, None))

    final_pairing = []
    for p in pairing:
        tlname = [x[1] for x in standings if x[0] == p[0]][0]
        if p[1]:
            trname = [x[1] for x in standings if x[0] == p[1]][0]
        else:
            trname = None
        t = (p[0], tlname, p[1], trname)
        final_pairing.append(t)

    return final_pairing
