#!/usr/bin/env python2.7


####TODO's

#4. Validate forms
#5. Style the game pages
#       Add more instruction info to the game pages
#       Add some sort of "delay" to mimic the simulator taking a bit to generate the simulations

from __future__ import division
import web, random, model, string
render_main = web.template.render('templates/', base = 'layout') # This defines the layout template for pages like instructions, consent, survey
render_game = web.template.render('templates/', base = 'game_layout') # The layout and css for the game pages are different, and so they need a different layout base template

urls = (
    '/', 'Consent',
    '/create_subject', 'CreateSubject',
    '/instructions/(.*)', 'Instructions',
    '/quiz', 'Quiz',
    '/check_quiz', 'CheckQuiz',
    '/play/(.*)/(.*)', 'Play',
    '/customize_simulator/(.*)/(.*)', 'CustomizeSimulator',
    '/submit_customization/(.*)/(.*)', 'SubmitCustomization',
    '/view_prediction/(.*)/(.*)', 'ViewPrediction',
    '/submit_prediction/(.*)', 'SubmitPrediction',
    '/survey/(.*)', 'Survey',
    '/claim_code/(.*)', 'Claim',
    '/error/(.*)', 'Error',
    '/restore', 'Restore'
)

var_names_batting = {"ba": "Batting Average", "runs": "Runs", "H":"Hits", "2B":"2B", "3B":"3B", "HR":"Home Runs", "OBP":"On-Base Percentage", "SLG":"Slugging Percentage", "BB":"Walks", "SB":"Stolen Bases", "RBI":"Runs Batted In"}
var_names_team_pitching = {"ERAp": "ERA (team)", "BBp":"Walks", "SOp":"Strikeouts", "HRp":"Home Runs"}
var_names_starter_pitching = {"Wsp":"Wins", "Lsp":"Losses", "ERAsp":"ERA (starter)", "Hsp": "Hits", "SOsp":"Strikeouts", "HRsp":"Home Runs", "IPsp":"Innings Pitched"}
   

class Consent:
    def GET(self):
        worker_id = web.input(worker_id='').worker_id
        if worker_id == '':
            raise web.seeother('/error/3')
        return render_main.consent(worker_id)

class CreateSubject:
    def POST(self):
        worker_id = web.input(worker_id='').worker_id
        
        #Check that this is really a new subject
        check = model.check_for_existing_subject_record(worker_id)
        if not check:
            raise web.seeother('/restore?worker_id=' + worker_id)
            #raise web.seeother('/error/4')
        
        # get the user's ip address
        ip = web.ctx['ip']
        
        # assign to a condition
        condition = random.randrange(0,2) # 1 means customizable condition
        
        
        # determine the order that the user will play the games in
        # Pass a list of integers (representing game_id's) to the model function- the order of this list will indicate the order the user will play games
        
        order = range(1,13)
        random.shuffle(order)
        
        
        # a dict with difficulties as keys and a list with id's from the game table as the value, the lists contain games that have that difficulty
        # the code will randomly choose 1 game from each difficulty level to recieve a "bad" recommendation
        game_difficulties = {1:[10,11], 2:[1,3,8,9], 3:[2,4,5,7], 4:[6,12]}
        bad_games = []
        for g in game_difficulties:
            bad = random.choice(game_difficulties[g])
            bad_games.append(bad)
        
        # put the info into the db
        
        model.new_subject(worker_id, condition, order, ip, bad_games)
        
        # redirect to the instructions
        raise web.seeother('/instructions/' + worker_id)
    
class Instructions:
    def GET(self, worker_id):
        #worker_id = web.input(worker_id='').worker_id
        
        # figure out which condition the user has been assigned to
        
        condition = model.get_condition(worker_id)
        
        if condition > 1:
            # If a condition isn't returned, redirect to an error page
            raise web.seeother('/error/3')
            
        model.update_instructions_views(worker_id)
        
        
        return render_main.instructions(worker_id, condition)
    
class Quiz:
    def GET(self):
        
        worker_id = web.input(worker_id='').worker_id
        condition = model.get_condition(worker_id)
        
        model.update_quiz_tries(worker_id)
        
        # Prevent question 7 from being available to non-customizable users
        if condition == 1:
            max_question_number = 8
        elif condition > 1:
            raise web.seeother('/error/3')
        else:
            max_question_number = 6
        questions_to_display = random.sample(range(1,max_question_number+1), 3)
        questions = {
            1: {
                "question": "How many games will you make predictions for?",
                "a" : "6",
                "b" : "8",
                "c" : "10",
                "d" : "12"
            },
            2: {
                "question": "How many points do the simulator's predictions score on average?",
                "a" : "10",
                "b" : "21",
                "c" : "15",
                "d" : "17"
            },
            3:
                {
                "question": "If you wager 5 confidence points, and you earn 16 points from your prediction, how many additional points do you earn?",
                "a" : "15",
                "b" : "0",
                "c" : "5",
                "d" : "10"
            },
            4:
                {
                "question": "If you predict Away: 7 | Home: 2 and the final score is Away: 5 | Home: 6, how many points do you earn for your prediction?",
                "a" : "0",
                "b" : "10",
                "c" : "4",
                "d" : "9"
            },
            5:
                {
                "question": "The statistics about the teams are ...",
                "a" : "... totals from the last 5 games.",
                "b" : "... totals and averages from the current season up to the day of the game.",
                "c" : "... totals from the past 5 seasons.",
                "d" : "... averages for the past 5 seasons."
            },
            6:
                {
                "question": "Which of the following statements is FALSE?",
                "a" : "You will be shown statistical information about each of the teams prior to making your predictions.",
                "b" : "You will not be shown the names of the teams",
                "c" : "You will be shown your scores for the game within 1 week through a bonus payment made to your MTurk account",
                "d" : "The simulator's prediction always scores exactly 15 points"
            },
            7:
                {
                "question": "Which of the following statements is TRUE?",
                "a": "You will NOT have the opportunity to customize the simulator's algorithm",
                "b": "You can select six statistical comparisons for the simulator to focus on",
                "c": "The simulator's performance can be improved by customizing it to give more weight to more important categories",
                "d": "By default, the simulator treats winning percentage as the most important statistical comparison between the teams"
                },
            8:
            	{
            	"question": "Which of the following statements is FALSE?",
            	"a": "By default, the simulator treats all statistical comparisons between the teams equally",
            	"b": "A statistical category that you have selected to customize the simulator is given more weight in the simulation than one that you have not chosen",
            	"c": "A statistical category that you have placed at #1 in your list is given more weight than a category at #3 in your list in the simulation",
            	"d": "By default, the records of each team is given the most weight in the simulation"
            	}
        }
        
        
        return render_main.quiz(worker_id, questions, questions_to_display)
        
class CheckQuiz:
    def POST(self):
    
    	worker_id = web.input(worker_id='').worker_id
    	
    	#Check that they haven't already passed the quiz
    	
    	check = model.check_for_passed_quiz(worker_id)
    	if check:
    		raise web.seeother("/restore?worker_id=" + worker_id)
    
        
        answer_key = {
            "q1": "d",
            "q2": "c",
            "q3": "a",
            "q4": "c",
            "q5": "b",
            "q6": "d",
            "q7": "c",
            "q8": "d"
        }
        
        
        passed = True
        questions_answered = 0
        for i in range(1,9):
            try:
                question_number = "q" + str(i)
                answer = web.input()[question_number]
            except:
                continue
            
            if answer_key[question_number] == answer:
            	questions_answered += 1
                continue
            else:
                passed = False
                break
        if questions_answered < 3:
        	passed = False
                
        if passed:
            model.update_stage(worker_id)
            model.update_quiz_completed(worker_id)
            raise web.seeother('/play/' + worker_id + "/1")
        else:
            #redirect back to the instructions and record the failed try in the db
            model.view_instructions(worker_id)
            raise web.seeother('/instructions/' + worker_id)

    
class Play:
    def GET(self, worker_id, game_number):
        #var_names_batting = {"ba": "Batting Average", "runs": "Runs", "H":"Hits", "2B":"2B", "3B":"3B", "HR":"Home Runs", "OBP":"On-Base Percentage", "SLG":"Slugging Percentage", "BB":"Walks", "SB":"Stolen Bases", "RBI":"Runs Batted In"}
        #var_names_team_pitching = {"ERAp": "Earned Run Average", "BBp":"Walks", "SOp":"Strikeouts", "HRp":"Home Runs"}
        #var_names_starter_pitching = {"Wsp":"Wins", "Lsp":"Losses", "ERAsp":"Earned Run Average", "Hsp": "Hits", "SOsp":"Strikeouts", "HRsp":"Home Runs", "IPsp":"Innings Pitched"}
        
        #worker_id = web.input(worker_id='').worker_id
        condition = model.get_condition(worker_id)
        if condition > 1:
            # If a condition isn't returned, redirect to an error page
            raise web.seeother('/error/3')
        
        # Returns an int with the id number of the next game, or None if 12 games have been played
        #game_number = model.get_games_played(worker_id) + 1
        game_number = int(game_number)
        game_id = model.get_game_id(worker_id, game_number)
        if not game_id:
            raise web.seeother('/survey/' + worker_id)
        game_data = model.get_game_data(game_id)
        
        # First, check to see if there is an existing prediction entry for this user with this game
        check1 = model.check_for_existing_prediction_record(worker_id, game_id)
        
        if check1 != 0:
            check2 = model.check_current_game_status(worker_id, game_id)
            
            if not check2:
                if condition == 1:
                    raise web.seeother('/customize_simulator/' + worker_id + "/" + str(game_number))
                else:
                    print "check2 caught"
                    return render_game.game_overview(worker_id, condition, game_data, var_names_batting, var_names_team_pitching, var_names_starter_pitching, game_number)
                
            else:
                raise web.seeother('/view_prediction/' + worker_id + "/" + str(game_number))
            
            
        
        
        
        ## If all games have been played, redirect to the survey
        #if not game_id:
        #    model.update_stage(worker_id)
        #    raise web.seeother('/survey/' + worker_id)
        #    
        ##Figure out if this game has already begun, and if so, redirect to the correct point in the game
        #status_check = model.get_current_game_status(worker_id, game_id)
        #if status_check == 2:
        #    raise web.seeother("/view_prediction/" + worker_id)
            
        ## create an entry in the predictions table for this game and this user
        #if status_check == 0:
        #    model.create_prediction_entry(worker_id, game_id)
        
        model.create_prediction_entry(worker_id, game_id)
        if condition == 1:
            raise web.seeother('/customize_simulator/' + worker_id + "/" + str(game_number))
        else:
            return render_game.game_overview(worker_id, condition, game_data, var_names_batting, var_names_team_pitching, var_names_starter_pitching, game_number)
    
class Survey:
    def GET(self, worker_id):
        condition = model.get_condition(worker_id)
        if condition > 1:
            raise web.seeother('/error/3')
        survey_questions = {
            "helpful": {"question": "How helpful was the simulator?", "low": "Not at all helpful", "high": "Very helpful"},
            "accurate": {"question": "How accurate do you think the simulator was at predicting the outcome of games?", "low": "Not at all accurate", "high": "Very accurate"},
            "important": {"question": "How important were the simulator's predictions in informing your predictions?" , "low": "Not at all important", "high": "Very important"},
            "control": {"question": "I was able to control the accuracy of the simulator" , "low": "Strongly Disagree", "high": "Strongly Agree"},
        }
        
        customize_questions = {
            "information": {"question": "The information I provided to the simulator was helpful." , "low": "Strongly Disagree", "high": "Strongly Agree"},
            "effort": {"question": "How much effort was required to customize the simulator?", "low": "No effort", "high": "A very high level of effort"}
        }
        
        elm_question = {
            "prompt": "When performing this task, I was...",
            "elm_a": "... extending a good deal of cognitive effort",
            "elm_b": "... resting my mind",
            "elm_c": "... doing my best to think about making the best prediction",
            "low": "Strongly Disagree",
            "high": "Strongly Agree"
        }
        
        return render_main.survey(worker_id, survey_questions, customize_questions, elm_question, condition)
        
    def POST(self, worker_id):
        questions = {
            "age":0,
            "gender":0,
            "helpful":0,
            "accurate":0,
            "important":0,
            "control":0,
            "information":0,
            "effort":0,
            "elm_a":0,
            "elm_b":0,
            "elm_c":0
        }
        
        for q in questions:
            try:
                questions[q] = web.input()[q]
            except KeyError:
                continue
        
        if questions["age"] == "":
            questions["age"] = str(0)
        model.add_survey_responses(worker_id, questions)
        model.update_stage(worker_id)
        
        # redirect to the page final page
        raise web.seeother("/claim_code/" + worker_id)
        
class CustomizeSimulator:
    def GET(self, worker_id, game_number):
        model.update_prediction_custom_start(worker_id)
        #game_number = model.get_games_played(worker_id) + 1
        game_number = int(game_number)
        game_id = model.get_game_id(worker_id, game_number)
        game_data = model.get_game_data(game_id)
        
        #check that they haven't already customized
        check = model.check_current_game_status(worker_id, game_id)
        if check:
            raise web.seeother('/error/5?worker_id=' + worker_id)
        
        return render_game.customize(worker_id, game_data, var_names_batting, var_names_team_pitching, var_names_starter_pitching, game_number)
        
    
class ViewPrediction:
    def GET(self, worker_id, game_number):
        condition = model.get_condition(worker_id)
        
        if condition > 1:
            raise web.seeother('/error/3')
        
        #game_number = model.get_games_played(worker_id) + 1
        game_number = int(game_number)
        game_id = model.get_game_id(worker_id, game_number)
        game_data = model.get_game_data(game_id)
        prediction_quality = model.get_prediction_quality(worker_id, game_id)
        if condition == 0:
            model.update_prediction_start_fixed(worker_id, prediction_quality)
        return render_game.predictions(worker_id, condition, game_data, var_names_batting, var_names_team_pitching, var_names_starter_pitching, prediction_quality, game_number)  

class SubmitCustomization:        
    def POST(self, worker_id, game_number):
        # First make sure the user hasn't already customized
        
        game_id = model.get_game_id(worker_id, game_number)
        print "checking current game status"
        check = model.check_current_game_status(worker_id, game_id)
        if check:
            raise web.seeother('/error/5?worker_id=' + worker_id)
        
        
        post_data = web.input()
        selections = post_data.selections
        ## Put the selections into a dict
        
        temp = selections.split(',')
        data = {}
        i = 1
        while i < 6:
            try:
                data[i] = temp[i-1]
            except IndexError:
                data[i] = "NULL"
            i += 1
        
        condition = model.get_condition(worker_id)   
        
        game_data = model.get_game_data(game_id)
        #game_number = model.get_games_played(worker_id) + 1
        game_number = int(game_number)
        prediction_quality = model.get_prediction_quality(worker_id, game_id)
        model.update_prediction_start_custom(worker_id, data, prediction_quality)
        
        raise web.seeother("/view_prediction/" + worker_id + "/" + str(game_number))
        #return render_game.predictions(worker_id, condition, game_data, var_names_batting, var_names_team_pitching, var_names_starter_pitching, prediction_quality, game_number)
        
class SubmitPrediction:
    def POST(self, worker_id):
        
        #First check that the user has not already made a prediction for this game        
        data = web.input()
        game_id = data["game_id"]
        check = model.check_for_existing_prediction_entered(worker_id, game_id)
        if check > 0:
            raise web.seeother('/error/6?worker_id=' + worker_id)
        
        
        model.add_prediction(worker_id, data)
        next_game = model.get_games_played(worker_id) + 1
        raise web.seeother('/play/' + worker_id + "/" + str(next_game))
        
class Error:
    def GET(self, error_num):
        worker_id = web.input(worker_id='').worker_id
        
        # The values are a list, with the first item being a 1 if the message should include a link to the "restore" function and 0 otherwise
        error_dict = {
            1:[0,"An unspecified error has occured. Please contact solomo93@msu.edu"], # display unspecifified error message
            2:[1,"You have not yet completed the experiment."], #Display a message- include a link to a "restore" method that figures out where a player is in the experiment and sends them to the right place
            3:[0,"In order to complete this HIT, you must accept the HIT on mturk.com and click the link inside the hit."], #Display a message that you must log in through mturk
            4:[0,"You have already completed this HIT. If you believe this is an error, please contact solomo93@msu.edu."], # Display a message. If the worker has already finished the experiment, the message should give a link to their claim code. If the worker has not completed, the link should be to the restore method
            5:[1,"You have already customized the simulator for this game. This can only be done once per game."],
            6:[1, "You have already submitted a prediction for this game."],
            7:"Selects more than 5 statistics", ##displays a message- better done with javascript
            8:"Doesn't enter a score", #Displays a message, javascript
            9:"Doesn't enter a confidence prediction", #Displays a message- javascript
            10:"Enters a non-sensical score, such as a tie, only one team, or non-integers" # displays a message, javascript            
        }
        #<a href='restore?worker_id=$worker_id'>Please click this link to try to correct the error</a>.
        msg = error_dict[int(error_num)][1]
        include_link = error_dict[int(error_num)][0]
        
        return render_main.error(worker_id, msg, include_link)
        
class Restore: #Figures out where in the experiment the user is at and redirect him there
    def GET(self):
        worker_id = web.input(worker_id='').worker_id
        
        stage = model.get_current_stage(worker_id)
        
        stages = {
            1:"/instructions/",
            2:"/play/",
            3:"/survey/",
            4:"/claim_code/"
        }
        
        if stage == 2:
        	next_game = model.get_games_played(worker_id) + 1
        	raise web.seeother('/play/' + worker_id + '/' + str(next_game))
        else:
	        raise web.seeother(stages[stage] + worker_id)

    
class Claim:
    def GET(self, worker_id):
        # check that the subject has actually completed the task
        
        completed = model.check_completion_status(worker_id)
        
        if completed:
            code = model.get_claim_code(worker_id)
            return render_main.claim(worker_id,code)
        else:
            raise web.seeother('/error/2?worker_id=' + worker_id)

#Uncomment the lines below to run in development mode
    
# if __name__ == '__main__':
#     app = web.application(urls, globals())
#     app.run()


# Uncomment out the following lines to run in development mode
app = web.application(urls, globals())
web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)    
if __name__ == '__main__':
    app.run()
