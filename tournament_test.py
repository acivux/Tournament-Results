#!/usr/bin/env python
#
# Test cases for tournament.py
# Extra credit implementations:
#     - Prevent rematches between players.
#     - Not assuming an even number of players.
#     - Support more than one tournament in the database.

import os

from tournament import *


def test_make_tournament(name):
    temp_tid = register_tournament(name)
    if temp_tid:
        print "Created Tournament (%s)" % temp_tid
    else:
        raise ValueError("Tournament Not Created")
    return temp_tid


def test_delete_matches(tournament_id):
    delete_matches(tournament_id)
    print "1. Tournament (%s) matches can be deleted." % tournament_id


def test_delete_tournament_players(tournament_id):
    delete_tournament_players(tournament_id)
    print "2. Tournament (%s) player records can be deleted." % tournament_id


def test_count(tournament_id):
    delete_matches(tournament_id)
    delete_tournament_players(tournament_id)
    c = count_players(tournament_id)
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def test_register(tournament_id):
    delete_matches(tournament_id)
    delete_tournament_players(tournament_id)
    register_player_in_tournament(tournament_id,
                                  register_player("Chandra Nalaar"))
    c = count_players(tournament_id)
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def test_register_count_delete(tournament_id):
    delete_matches(tournament_id)
    delete_tournament_players(tournament_id)
    register_player_in_tournament(tournament_id,
                                  register_player("Markov Chaney"))
    register_player_in_tournament(tournament_id,
                                  register_player("Joe Malik"))
    register_player_in_tournament(tournament_id,
                                  register_player("Mao Tsu-hsi"))
    register_player_in_tournament(tournament_id,
                                  register_player("Atlanta Hope"))
    c = count_players(tournament_id)
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    delete_tournament_players(tournament_id)
    c = count_players(tournament_id)
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def test_standings_before_matches(tournament_id):
    delete_matches(tournament_id)
    delete_tournament_players(tournament_id)
    register_player_in_tournament(tournament_id,
                                  register_player("Melpomene Murray"))
    register_player_in_tournament(tournament_id,
                                  register_player("Randy Schwartz"))
    standings = player_standings(tournament_id)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before"
                         " they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if {name1, name2} != {"Melpomene Murray", "Randy Schwartz"}:
        raise ValueError("Registered players' names should appear in "
                         "standings, even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no" \
          " matches."


def test_report_matches(tournament_id):
    delete_matches(tournament_id)
    delete_tournament_players(tournament_id)
    register_player_in_tournament(tournament_id,
                                  register_player("Bruno Walton"))
    register_player_in_tournament(tournament_id,
                                  register_player("Boots O'Neal"))
    register_player_in_tournament(tournament_id,
                                  register_player("Cathy Burton"))
    register_player_in_tournament(tournament_id,
                                  register_player("Diane Grant"))
    standings = player_standings(tournament_id)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    report_match(tournament_id, id1, id2)
    report_match(tournament_id, id3, id4)
    standings = player_standings(tournament_id)
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero"
                             " wins recorded.")
    print "7. After a match, players have updated standings."


def test_report_matches_uneven(tournament_id):
    delete_matches(tournament_id)
    delete_tournament_players(tournament_id)
    register_player_in_tournament(tournament_id,
                                  register_player("Bruno Walton"))
    register_player_in_tournament(tournament_id,
                                  register_player("Boots O'Neal"))
    register_player_in_tournament(tournament_id,
                                  register_player("Cathy Burton"))
    register_player_in_tournament(tournament_id,
                                  register_player("Diane Grant"))
    register_player_in_tournament(tournament_id,
                                  register_player("Great Dane"))
    standings = player_standings(tournament_id)
    [id1, id2, id3, id4, id5] = [row[0] for row in standings]
    report_match(tournament_id, id1, id2)
    report_match(tournament_id, id3, id4)
    report_match(tournament_id, id5, None)  # A bye match
    standings = player_standings(tournament_id)
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3, id5) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero"
                             " wins recorded.")
    print "8. After a match, uneven amount of players have updated standings."


def test_pairings(tournament_id):
    delete_matches(tournament_id)
    delete_tournament_players(tournament_id)
    register_player_in_tournament(tournament_id,
                                  register_player("Twilight Sparkle"))
    register_player_in_tournament(tournament_id,
                                  register_player("Fluttershy"))
    register_player_in_tournament(tournament_id,
                                  register_player("Applejack"))
    register_player_in_tournament(tournament_id,
                                  register_player("Pinkie Pie"))
    standings = player_standings(tournament_id)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    report_match(tournament_id, id1, id2)
    report_match(tournament_id, id3, id4)
    pairings = swiss_pairings(tournament_id)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "9. After one match, players with one win are paired."


def test_pairings_uneven(tournament_id):
    delete_matches(tournament_id)
    delete_tournament_players(tournament_id)
    register_player_in_tournament(tournament_id,
                                  register_player("Twilight Sparkle"))
    register_player_in_tournament(tournament_id,
                                  register_player("Fluttershy"))
    register_player_in_tournament(tournament_id,
                                  register_player("Applejack"))
    register_player_in_tournament(tournament_id,
                                  register_player("Pinkie Pie"))
    register_player_in_tournament(tournament_id,
                                  register_player("Chocolate Mousse"))
    standings = player_standings(tournament_id)
    [id1, id2, id3, id4, id5] = [row[0] for row in standings]
    report_match(tournament_id, id1, id2)
    report_match(tournament_id, id3, id4)
    report_match(tournament_id, id5, None)  # bye match
    pairings = swiss_pairings(tournament_id)
    if (len(pairings)-1) % 2 != 0:
        raise ValueError(
            "For uneven amount of players, swissPairings should"
            " return ((#players-1) % 2) == 0 .")
    [(pid1, pname1, pid2, pname2),
     (pid3, pname3, pid4, pname4),
     (pid5, pname5, pid6, pname6)] = pairings
    correct_pairs = set([frozenset([id1, id3]),
                         frozenset([id5, id2]),
                         frozenset([id4, None])])
    actual_pairs = set([frozenset([pid1, pid2]),
                        frozenset([pid3, pid4]),
                        frozenset([pid5, pid6])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "10. After one match, uneven amount of players" \
          " are paired correctly."

if __name__ == '__main__':

    # Set up tournaments
    print os.linesep, '-' * 50, os.linesep, "Setting up", os.linesep, '-' * 50
    t1_id = test_make_tournament("Tournament 1")
    t2_id = test_make_tournament("Tournament 2")

    print os.linesep, '-' * 50, os.linesep, "Testing Tournament %s" % t1_id,\
        os.linesep, '-' * 50
    # Test tournament 1
    test_delete_matches(t1_id)
    test_delete_tournament_players(t1_id)
    test_count(t1_id)
    test_register(t1_id)
    test_register_count_delete(t1_id)
    test_standings_before_matches(t1_id)
    test_report_matches(t1_id)
    test_report_matches_uneven(t1_id)
    test_pairings(t1_id)
    test_pairings_uneven(t1_id)

    print os.linesep, '-' * 50, os.linesep, "Testing Tournament %s" % t2_id,\
        os.linesep, '-' * 50
    # Test tournament 2
    test_delete_matches(t2_id)
    test_delete_tournament_players(t2_id)
    test_count(t2_id)
    test_register(t2_id)
    test_register_count_delete(t2_id)
    test_standings_before_matches(t2_id)
    test_report_matches(t2_id)
    test_report_matches_uneven(t2_id)
    test_pairings(t2_id)
    test_pairings_uneven(t2_id)

    # Cleanup tournament players
    delete_tournament_players(t1_id)
    delete_tournament_players(t2_id)

    print os.linesep, "Cleaning... "
    # Cleanup tournaments
    delete_tournament(t1_id)
    delete_tournament(t2_id)

    # cleanup up all players
    delete_players()

    print os.linesep, "Success!  All tests pass!"
