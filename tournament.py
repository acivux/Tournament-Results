#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    try:
        sql = "DELETE FROM matches CASCADE;"
        curs = db.cursor()
        curs.execute(sql)
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

def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    try:
        sql = "SELECT count(id) from player"
        curs = db.cursor()
        curs.execute(sql)
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
    """
    db = connect()
    try:
        sql = "INSERT INTO player VALUES(DEFAULT,%s);"
        curs = db.cursor()
        curs.execute(sql, (name,))
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
        print 'Error %s' % e
    finally:
        if db:
            db.close()


def playerStandings():
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
                player.id,
                player.fullname,
                COALESCE(wintable.wins,0) AS wins,
                COALESCE(wins,0) + COALESCE(losertable.losts, 0) AS matches
            FROM
                player LEFT JOIN
                    (SELECT
                        winner_id,
                        count(winner_id) AS wins
                     FROM matches
                     GROUP BY winner_id) AS wintable
                ON player.id = wintable.winner_id
                LEFT JOIN
                    (SELECT loser_id,
                            COUNT(loser_id) AS losts
                     FROM matches
                     GROUP BY loser_id) AS losertable
                ON player.id = losertable.loser_id
            ORDER BY wins DESC NULLS LAST;"""
        curs = db.cursor()
        curs.execute(sql)
        result = curs.fetchall()
        return result
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    try:
        sql = "INSERT INTO matches VALUES(DEFAULT,%s,%s)"
        curs = db.cursor()
        curs.execute(sql, (winner, loser))
        db.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()

def matchHistory():
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
                    matches
                WHERE
                    loser_id is not null;
              """
        curs = db.cursor()
        curs.execute(sql)
        qresult = curs.fetchall()
        result = []
        for x in qresult:
            tt = (x[1], x[0])
            if x not in result and tt not in result:
                result.append(x)
        return result
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()

def freeBe():
    db = connect()
    try:
        sql = """
                SELECT DISTINCT
                    winner_id
                FROM
                    matches
                WHERE
                    loser_id is null;
              """
        curs = db.cursor()
        curs.execute(sql)
        result = curs.fetchall()
        return [x[0] for x in result]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if db:
            db.close()

def swissPairings():
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
    standings = playerStandings()
    print [x[0] for x in standings]
    left_standings = [x[0] for x in standings]
    right_standings = [x[0] for x in standings]
    pairing = []
    skipped = []
    played_players = matchHistory()
    free_bees = freeBe()

    print ">", played_players
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

    with open("play.sql", "w") as f:
        for x in pairing:
            f.write("INSERT INTO matches VALUES(DEFAULT,%s,%s);\r\n"
                    % (x[0], x[1] or "null"))

    return pairing
