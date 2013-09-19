#calculate_bonuses.py

import MySQLdb as mysql
import math

def update_score(i, worker_id):
	q = "select home_score, away_score, confidence, bad_recommendation, game_type, game_order from predictions where worker_id = '%s' and game_order = %s" % (worker_id, str(i))
	c.execute(q)
	results = c.fetchone()
	
	home_score = int(results[0])
	away_score = int(results[1])
	confidence = int(results[2])
	bad_recommendation = int(results[3])
	game_type = results[4]
	game_order = results[5]
	
	#get the correct score and the predicted score for a bad recommendation
	q = "select score_h, score_a, bad_score_h, bad_score_a from games where id = %s" % (str(game_type))
	c.execute(q)
	
	results = c.fetchone()
	
	real_home_score = results[0]
	real_away_score = results[1]
	
	recommended_home_score = results[2]
	recommended_away_score = results[3]
	
	if real_home_score > real_away_score:
		real_winner = "home"
	else:
		real_winner = "away"
		
	if home_score > away_score:
		predicted_winner = "home"
	else:
		predicted_winner = "away"
		
	points = 20
	
	if real_winner != predicted_winner:
		points -= 10
	
	home_diff = math.fabs(real_home_score - home_score)
	away_diff = math.fabs(real_away_score - away_score)
	
	points -= home_diff
	points -= away_diff
	
	if points < 0:
		points = 0
		
	#calculate earnings from confidence wagers
	if points > 14:
		confidence_earnings = (10 - confidence) + (3 * confidence)
	else:
		confidence_earnings = 10-confidence
		
	# Calculate proximity to prediction
	if bad_recommendation == 1:
		rec_points = 20
		if recommended_away_score > recommended_home_score:
			rec_winner = "away"
		else:
			rec_winner = "home"
		
		if predicted_winner != rec_winner:
			rec_points -= 10
		rec_home_diff = math.fabs(recommended_home_score - home_score)
		rec_away_diff = math.fabs(recommended_away_score - away_score)
		
		rec_points -= rec_home_diff
		rec_points -= rec_away_diff
	else:
		rec_points = points
		
	if rec_points > 10:
		winner_agreement = str(1)
	else:
		winner_agreement = str(0)
	
	q = "update predictions set real_points = %s, confidence_winnings = %s, agreement = %s, winner_agreement = %s where worker_id = '%s' and game_type = %s" % (str(points), str(confidence_earnings), str(rec_points), winner_agreement, worker_id, str(game_type))
	c.execute(q)
	conn.commit()

db = "fantasy_baseball_analysis"
host = "localhost"
user = "fantasy_sports"
pw = "fantasy1234"

conn = mysql.connect(host,user,pw,db)
c = conn.cursor()

q = "select worker_id from subjects where survey_completed_time is not null"
c.execute(q)

results = c.fetchall()

for r in results:
	worker_id = r[0]
	
	for i in range(1,13):
		update_score(i, worker_id)
		
	
	
	

	

	
	
	
	
	
