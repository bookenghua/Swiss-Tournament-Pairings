#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM matches")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM players")
    DB.commit()
    DB.close()

def deleteTournaments():
    """Remove all the tournament records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM tournaments")
    DB.commit()
    DB.close()


def deleteScoreboard():
    """Remove all the scoreboard records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM scoreboard")
    DB.commit()
    DB.close()

def createTournament(name):
    """Create a new tournament.
    Args:
        Name of tournament
    """
    DB = connect()
    c = DB.cursor()
    sql = "INSERT INTO tournaments (t_name) VALUES (%s) RETURNING t_id"
    c.execute(sql, (name,))
    tid = c.fetchone()[0]
    DB.commit()
    DB.close()
    return tid

def countPlayers(tid):
    """Returns the number of players currently registered for a tournament.
    Args:
        tid: id of tournament
    """
    DB = connect()
    c = DB.cursor()
    sql = """SELECT count(p_id) AS num
             FROM scoreboard
             WHERE t_id = %s"""
    c.execute(sql, (tid,))
    players = c.fetchone()[0]
    DB.close()
    return players

def registerPlayer(name, tid):
    """Adds a player to the tournament database.
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
    Args:
      name: the player's full name (need not be unique).
      tid: id of tournament they are entering.
    """
    DB = connect()
    c = DB.cursor()
    player = "INSERT INTO players (p_name) VALUES (%s) RETURNING p_id"
    scoreboard = "INSERT INTO scoreboard VALUES (%s,%s,%s,%s,%s)"
    c.execute(player, (name,))
    pid = c.fetchone()[0]
    c.execute(scoreboard, (tid,pid,0,0,0))
    DB.commit()
    DB.close()


def playerStandings(tid):
    """Returns a list of the players and their scores, sorted by scores and omw
    for the specific tournament in question.
    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.
    Args:
        tid: t_id of tournament getting standings for
    Returns:
      A list of tuples, each of which contains (id, name, score, matches, bye, omw):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        score: the player's score derived from computation of wins, draws and byes
        matches: the number of matches the player has played
        bye: the player's bye record (1 or null)
        omw: the opponent's (winner or loser) match wins 
    """
    DB = connect()
    c = DB.cursor()
    players = """SELECT s.p_id, p.p_name, s.score, s.matches, s.bye,
                    (SELECT SUM(s2.score)
                     FROM scoreboard AS s2
                     WHERE s2.p_id IN (SELECT loser_id
                                     FROM matches
                                     WHERE winner_id = s.p_id
                                     AND t_id = %s)
                     OR s2.p_id IN(SELECT winner_id
                                 FROM matches
                                 WHERE loser_id = s.p_id
                                 AND t_id = %s)) AS omw
                 FROM scoreboard AS s
                 INNER JOIN players AS p on p.p_id = s.p_id
                 WHERE t_id = %s
                 ORDER BY s.score DESC, omw DESC, s.matches DESC"""
    c.execute(players, (tid,tid,tid))
    ranks = []
    for row in c.fetchall():
        ranks.append(row)
    DB.close()
    return ranks

def reportMatch(tid, winner_id, loser_id, draw = 'False'):
    """Records the outcome of a single match between two players.
    Args:
      tid: the id of the tournament match was in
      winner_id:  the id of the player who won
      loser_id:  the id of the player who lost
      draw:  if the match was a draw
    """
    if draw == 'TRUE':
        w_points = 1
        l_points = 1
    else:
        w_points = 3
        l_points = 0

    DB = connect()
    c = DB.cursor()
    ins = "INSERT INTO matches (t_id, winner_id, loser_id, draw) VALUES (%s,%s,%s,%s)"
    win = "UPDATE scoreboard SET score = score + %s, matches = matches + 1 WHERE p_id = %s AND t_id = %s"
    los = "UPDATE scoreboard SET score = score + %s, matches = matches + 1 WHERE p_id = %s AND t_id = %s"
    c.execute(ins, (tid, winner_id, loser_id, draw))
    c.execute(win, (w_points, winner_id, tid))
    c.execute(los, (l_points, loser_id, tid))
    DB.commit()
    DB.close()

def hasBye(pid, tid):
    """Checks if player has bye.
    Args:
        pid: p_id of player to check
    Returns true or false.
    """
    DB = connect()
    c= DB.cursor()
    sql = """SELECT bye
             FROM scoreboard
             WHERE p_id = %s
             AND t_id = %s"""
    c.execute(sql, (pid,tid))
    bye = c.fetchone()[0]
    DB.close()
    if bye == 1:
        return True
    else:
        return False

def reportBye(pid, tid):
    """Assign points for a bye.
    Args:
      pid: p_id of player who receives a bye.
      tid: the t_id of the tournament
    """
    DB = connect()
    c = DB.cursor()
    bye = "UPDATE scoreboard SET score = score + 3, bye = bye + 1 WHERE p_id = %s AND t_id = %s"
    c.execute(bye, (pid,tid))
    DB.commit()
    DB.close()

def checkNoByes(tid, ranks, index):
    """Checks if players have no byes
    Args:
        tid: tournament id
        ranks: list of current ranks from swissPairings()
        index: index to check
    Returns first id that is without bye or original id if none are found.
    """
    while abs(index) <= len(ranks):
        if hasBye(ranks[index][0], tid):
            index -= 1
        else:
            return index
    return index

def validPair(player1, player2, tid):
    """Checks if two players have already played against each other
    Args:
        player1: the id number of first player to check
        player2: the id number of potentail paired player
        tid: the id of the tournament
    Return true if valid pair, false if not
    """
    DB = connect()
    c = DB.cursor()
    sql = """SELECT winner_id, loser_id
             FROM matches
             WHERE ((winner_id = %s AND loser_id = %s)
                    OR (winner_id = %s AND loser_id = %s))
             AND t_id = %s"""
    c.execute(sql, (player1, player2, player2, player1, tid))
    matches = c.rowcount
    DB.close()
    if matches > 0:
        return False
    return True

def checkPairs(tid, ranks, id1, id2):
    """Checks if two players have already had a match against each other.
    If they have, recursively checks through the list until a valid match is
    found.
    Args:
        tid: id of tournament
        ranks: list of current ranks from swissPairings()
        id1: player needing a match
        id2: potential matched player
    Returns id of matched player or original match if none are found.
    """
    if id2 >= len(ranks):
        return id1 + 1
    elif validPair(ranks[id1][0], ranks[id2][0], tid):
        return id2
    else:
        return checkPairs(tid, ranks, id1, (id2 + 1))

def swissPairings(tid):
    """Returns a list of pairs of players for the next round of a match.
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
    Args:
        tid: id of tournament you are gettings standings for
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    ranks = playerStandings(tid)
    pairs = []

    numPlayers = countPlayers(tid)
    if numPlayers % 2 != 0:
        bye = ranks.pop(checkNoByes(tid, ranks, -1))
        reportBye(bye[0], tid)

    while len(ranks) > 1:
        validMatch = checkPairs(tid,ranks,0,1)
        player1 = ranks.pop(0)
        player2 = ranks.pop(validMatch - 1)
        pairs.append((player1[0],player1[1],player2[0],player2[1]))

    return pairs