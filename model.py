#!/usr/bin/env python
from __future__ import division
import web, random, string

db = web.database(dbn='mysql', db = 'fantasy', user = 'fantasy_sports', pw = 'fantasy1234')

def check_for_existing_subject_record(worker_id):
    q = "select count(*) as previous from subjects where worker_id = '%s'" % (worker_id)
    count = db.query(q)[0]['previous']
    if not count == 0:
        return False
    else:
        return True

def new_subject(worker_id, condition, order, ip, bad_games):
    
    #Generate a claim code for the subject
    claim_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(7))
    claim_code += "GES"
    
    q = "insert into subjects (ip, worker_id, consent_agreed, instructions_viewed, customize, games_completed, game1, game2, game3, game4, game5, game6, game7, game8, game9, game10, game11, game12, bad1, bad2, bad3, bad4, claim_code, stage) values ('%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', 1)" % (ip, worker_id, "now()", str(1), str(condition), str(0), str(order[0]), str(order[1]), str(order[2]), str(order[3]), str(order[4]), str(order[5]), str(order[6]), str(order[7]), str(order[8]), str(order[9]), str(order[10]), str(order[11]), str(bad_games[0]), str(bad_games[1]), str(bad_games[2]), str(bad_games[3]), claim_code)
    return db.query(q)
    
def get_condition(worker_id):
    try:
        q = "select customize from subjects where worker_id = '%s'" % (worker_id)
        #return db.query(q)[0]
        condition = db.query(q)[0]['customize']
        return condition
    except IndexError:
        return 2 # 2 means there is no entry for this worker_id
    
def view_instructions(worker_id):
    q = "update subjects set instructions_viewed = instructions_viewed + 1 where worker_id = '%s'" % (worker_id)
    return db.query(q)
    
def get_game_id(worker_id):
    games_played = get_games_played(worker_id)
    
    if games_played > 11:
        return None
    
    #games_played = int(db.select('subjects', where='worker_id=$worker_id', what='games_completed')[0])
    game_field = "game" + str(games_played + 1)
    
    
    q = "select %s as game from subjects where worker_id='%s'" % (game_field, worker_id)
    return db.query(q)[0].game
    #return db.select('subjects', what = game_field, where='worker_id=$worker_id')[0]
    
def get_game_data(game_id):
    q = "select * from games where id = %s" % (str(game_id))
    data = dict(db.query(q)[0])
    data["home_pct"] = round((data["wins_h"] / (data["wins_h"] + data["losses_h"])), 3)
    data["away_pct"] = round((data["wins_a"] / (data["wins_a"] + data["losses_a"])),3)
    
    return data
    
    
    #return db.select('games', where='id=$game_id')
    
def add_customize_info(worker_id, data):
    # TODO- write this method to add the info about how the user customized the system into the db
    
    pass
    
def get_games_played(worker_id):
    q = "select games_completed from subjects where worker_id = '%s'" % (worker_id)
    games_played = int(db.query(q)[0].games_completed)
    
    return games_played

def get_prediction_quality(worker_id, game_id):
    # Returns 1 if it should be a bad prediction, 0 otherwise
    
    q = "select bad1,bad2,bad3,bad4 from subjects where worker_id = '%s'" % (worker_id)
    bg = db.query(q)[0]
    if game_id == bg.bad1:
        return 1
    elif game_id == bg.bad2:
        return 1
    elif game_id == bg.bad3:
        return 1
    elif game_id == bg.bad4:
        return 1
    else:
        return 0
    
def create_prediction_entry(worker_id, game_id):
    
    games_played = get_games_played(worker_id)
    q = "insert into predictions (worker_id, view_stats_start, game_order, game_type) values ('%s', now(), %s, %s)" % (worker_id, str(games_played+1), game_id)
    db.query(q)
    
def update_prediction_custom_start(worker_id):
    games_played = get_games_played(worker_id)
    q = "update predictions set customize_start = now() where worker_id = '%s' and game_order = %s" % (worker_id, str(games_played+1))
    db.query(q)
    
def update_prediction_start_fixed(worker_id, prediction_quality):
    games_played = get_games_played(worker_id)
    q = "update predictions set enter_predictions_start = now(), bad_recommendation = %s where worker_id = '%s' and game_order = %s" % (str(prediction_quality), worker_id, str(games_played+1))
    db.query(q) 
    
def update_prediction_start_custom(worker_id, data, prediction_quality):
    games_played = get_games_played(worker_id)
    q = "update predictions set enter_predictions_start = now(), bad_recommendation = %s, custom_category_1 = '%s', custom_category_2 = '%s', custom_category_3 = '%s', custom_category_4 = '%s', custom_category_5 = '%s' where worker_id = '%s' and game_order = %s" % (str(prediction_quality), data[1], data[2], data[3], data[4], data[5], worker_id, str(games_played+1))
    print q
    db.query(q)

def add_prediction(worker_id, data):
    games_played = get_games_played(worker_id)
    game_field = "game" + str(games_played + 1)
    
    q = "update predictions set home_score = %s, away_score = %s, enter_predictions_stop = now(), confidence = %s where worker_id = '%s' and game_order = %s" % (str(data["home"]), str(data["away"]), str(data["confidence"]), worker_id, str(games_played+1))
    db.query(q)
    
    q = "update subjects set games_completed = games_completed + 1 where worker_id = '%s'" % (worker_id)
    db.query(q)
    
def add_survey_responses(worker_id, questions):    
    q = "update subjects set survey_completed = 1, survey_completed_time = now(), "
    for u in questions:
        new = u + " = " + str(questions[u]) + ", "
        q += new
    q = q.rstrip(", ")
    q += " where worker_id = '%s'" % (worker_id)
    print q
    db.query(q)
    

def check_completion_status(worker_id):
    q = "select games_completed, survey_completed from subjects where worker_id = '%s'" % (worker_id)
    row = db.query(q)[0]
    
    if row.games_completed < 12 or row.survey_completed < 1:
        return False
    else:
        return True
    
def get_current_stage(worker_id):
    q = "select stage from subjects where worker_id = '%s'" % (worker_id)
    row = db.query(q)[0]
    
    return row.stage

def update_stage(worker_id):
    q = "update subjects set stage = stage + 1 where worker_id = '%s'" % (worker_id)
    db.query(q)
    
def check_for_existing_prediction_record(worker_id, game_id):
    q = "select count(*) as entries from predictions where worker_id = '%s' and game_type = %s" % (worker_id, str(game_id))
    return db.query(q)[0].entries
    
def check_current_game_status(worker_id, game_id):
    q = "select enter_predictions_start from predictions where worker_id = '%s' and game_type = %s" % (worker_id, str(game_id))
    return db.query(q)[0].enter_predictions_start
    
def get_claim_code(worker_id):
    q = "select claim_code from subjects where worker_id = '%s'" % (worker_id)
    row = db.query(q)[0]
    
    return row.claim_code

def check_for_existing_prediction_entered(worker_id, game_id):
    q = "select count(*) as entries from predictions where home_score is not null and worker_id = '%s' and game_type = %s" % (worker_id, game_id)
    return db.query(q)[0].entries
    
    

