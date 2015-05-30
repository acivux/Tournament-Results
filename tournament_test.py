#!/usr/bin/env python
#
# Test cases for tournament.py

from mtournament import *

TID = 3

def testMakeTournament():
    registerTournament("testing 123", TID)
    print "0. Created Tournament"

def testDeleteMatches():
    deleteMatches(TID)
    print "1. Existing Matches can be deleted."


def testDelete():
    deleteTournamentPlayers(TID)
    print "2. Tournament Player records can be deleted."


def testCount():
    deleteMatches(TID)
    deleteTournamentPlayers(TID)
    c = countPlayers(TID)
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches(TID)
    deleteTournamentPlayers(TID)
    registerPlayerInTournament(TID, registerPlayer("Chandra Nalaar"))
    c = countPlayers(TID)
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches(TID)
    deleteTournamentPlayers(TID)
    registerPlayerInTournament(TID, registerPlayer("Markov Chaney"))
    registerPlayerInTournament(TID, registerPlayer("Joe Malik"))
    registerPlayerInTournament(TID, registerPlayer("Mao Tsu-hsi"))
    registerPlayerInTournament(TID, registerPlayer("Atlanta Hope"))
    c = countPlayers(TID)
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deleteTournamentPlayers(TID)
    c = countPlayers(TID)
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches(TID)
    deleteTournamentPlayers(TID)
    registerPlayerInTournament(TID, registerPlayer("Melpomene Murray"))
    registerPlayerInTournament(TID, registerPlayer("Randy Schwartz"))
    standings = playerStandings(TID)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in "
                         "standings, even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches(TID)
    deleteTournamentPlayers(TID)
    registerPlayerInTournament(TID, registerPlayer("Bruno Walton"))
    registerPlayerInTournament(TID, registerPlayer("Boots O'Neal"))
    registerPlayerInTournament(TID, registerPlayer("Cathy Burton"))
    registerPlayerInTournament(TID, registerPlayer("Diane Grant"))
    standings = playerStandings(TID)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(TID, id1, id2)
    reportMatch(TID, id3, id4)
    standings = playerStandings(TID)
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches(TID)
    deleteTournamentPlayers(TID)
    registerPlayerInTournament(TID, registerPlayer("Twilight Sparkle"))
    registerPlayerInTournament(TID, registerPlayer("Fluttershy"))
    registerPlayerInTournament(TID, registerPlayer("Applejack"))
    registerPlayerInTournament(TID, registerPlayer("Pinkie Pie"))
    standings = playerStandings(TID)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(TID, id1, id2)
    reportMatch(TID, id3, id4)
    pairings = swissPairings(TID)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


if __name__ == '__main__':
    testMakeTournament()
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    deleteTournament(TID)
    deletePlayers()
    print "Success!  All tests pass!"
