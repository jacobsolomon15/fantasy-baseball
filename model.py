#!/usr/bin/env python

import web

db = web.database(dbn='mysql', db = 'fantasy', user = 'fantasy_sports', pw = 'fantasy1234')

def new_subject(worker_id, condition, order, ip):
    
    q = "insert into subjects (ip, worker_id, consent_agreed, instructions_viewed, customize, games_completed, game1, game2, game3, game4, game5, game6, game7, game8, game9, game10, game11, game12) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (ip, worker_id, "now()", str(1), str(condition), str(0), str(order[0]), str(order[1]), str(order[2]), str(order[3]), str(order[4]), str(order[5]), str(order[6]), str(order[7]), str(order[8]), str(order[9]), str(order[10]), str(order[11]))
    return db.query(q)
    
def get_condition(worker_id):
    try:
        return db.select('subjects', what='customize', where='worker_id = $worker_id')[0]
    except IndexError:
        return None
    
def view_instructions(worker_id):
    q = "update subjects set instructions_viewed = instructions_viewed + 1 where worker_id = %s" % (worker_id)
    return db.query(q)
    
def get_game_id(worker_id):
    games_played = int(db.select('subjects', where='woker_id=$worker_id', what='games_completed')[0])
    game_field = "game" + str(games_played + 1)
    
    return db.select('subjects', what = game_field, where='worker_id=$worker_id')[0]
    
def get_game_data(game_id):
    return db.select('games', where='id=$game_id')
    
    

