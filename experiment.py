#!/usr/bin/env python

import web, random
render_main = web.template.render('templates/', base = 'layout') # This defines the layout template for pages like instructions, consent, survey
render_game = web.template.render('templates/', base = 'game_layout') # The layout and css for the game pages are different, and so they need a different layout base template

urls = (
    '/', 'Consent',
    '/create_subject', 'CreateSubject',
    '/instructions/(.*)', 'Instructions',
    '/quiz', 'Quiz',
    '/check_quiz/(.*)', 'CheckQuiz',
    '/play/(.*)', 'Play',
    '/survey', 'Survey'
    '/error/(.*)', 'Error'
)

class Consent:
    def GET(self):
        worker_id = web.input(worker_id='').worker_id
        return render_main.consent(worker_id) # You need to make the consent template called consent.html

class CreateSubject:
    def POST(self):
        worker_id = web.input(worker_id='').worker_id
        
        # get the user's ip address
        ip = web.ctx['ip']
        
        # assign to a condition
        condition = randrange(0,1) # 1 means customizable condition
        
        
        # determine the order that the user will play the games in
        # Pass a list of integers (representing game_id's) to the model function- the order of this list will indicate the order the user will play games
        
        order = range(1,13)
        shuffle(order)
        
        # put the info into the db
        
        model.new_user(worker_id, condition, order, ip)
        
        # redirect to the instructions
        raise web.seeother('/instructions/' + worker_id)
    
class Instructions:
    def GET(self, worker_id):
        #worker_id = web.input(worker_id='').worker_id
        
        # figure out which condition the user has been assigned to
        
        condition = model.get_condition(worker_id)
        
        if not condition:
            # If a condition isn't returned, redirect to an error page
            raise web.seeother('/error/1')
        
        
        return render_main.instructions(worker_id, condition)
    
class Quiz:
    def GET(self):
        
        worker_id = web.input(worker_id='').worker_id
        questions_to_display = random.sample(range(1,6), 3)
        questions = {
            1: {
                "question": "Question 1",
                "a" : "Answer a",
                "b" : "Answer b",
                "c" : "Answer c",
                "d" : "Answer d"
            },
            2: {
                "question": "Question 2",
                "a" : "Answer a",
                "b" : "Answer b",
                "c" : "Answer c",
                "d" : "Answer d"
            },
            3:
                {
                "question": "Question 3",
                "a" : "Answer a",
                "b" : "Answer b",
                "c" : "Answer c",
                "d" : "Answer d"
            },
            4:
                {
                "question": "Question 5",
                "a" : "Answer a",
                "b" : "Answer b",
                "c" : "Answer c",
                "d" : "Answer d"
            },
            5:
                {
                "question": "Question 6",
                "a" : "Answer a",
                "b" : "Answer b",
                "c" : "Answer c",
                "d" : "Answer d"
            },
        }
        
        
        return render_main.quiz(worker_id, questions, questions_to_display)
        
class CheckQuiz:
    def POST(self, worker_id):
        #worker_id = web.input(worker_id='').worker_id
        answer_key = {
            "q1": "d",
            "q2": "d",
            "q3": "a",
            "q4": "c",
            "q5": "b",
            "q6": "b"
        }
        
        passed = True
        for i in range(1,7):
            try:
                question_number = "q" + str(i)
                answer = web.input()[question_number]
            except:
                continue
            
            if answer_key[question_number] == answer:
                pass
            else:
                passed = False
                
        if passed:
            raise web.seeother('/play/' + worker_id)
        else:
            # redirect back to the instructions and record the failed try in the db
            model.view_instructions(worker_id)
            raise web.seeother('/instructions/' + worker_id)

    
class Play:
    def GET(self, worker_id):
        #worker_id = web.input(worker_id='').worker_id
        condition = model.get_condition(worker_id)
        if not condition:
            # If a condition isn't returned, redirect to an error page
            raise web.seeother('/error/1')
        
        game_id = get_game_id(worker_id)
        
        game_data = model.get_game_data(game_id)
        
        var_names_batting = {"ba": "Batting Average", "runs": "Runs", "H":"Hits", "2B":"2B", "3B":"3B", "HR":"Home Runs", "OBP":"On-Base Percentage", "SLG":"Slugging Percentage", "BB":"Walks", "SB":"Stolen Bases", "RBI":"Runs Batted In"}
        var_names_team_pitching = {"ERAp": "Earned Run Average", "BBp":"Walks", "SOp":"Strikeouts", "HRp":"Home Runs"}
        var_names_starter_pitching = {"Wsp":"Wins", "Lsp":"Losses", "ERAsp":"Earned Run Average", "Hsp": "Hits", "SOsp":"Strikeouts", "HRsp":"Home Runs", "IPsp":"Innings Pitched"}
        
        return render_game.render.game_overview(worker_id, condition, game_data, var_names_record, var_names_batting, var_names_team_pitching, var_names_starter_pitching)
    
class Survey:
    def GET(self):
        worker_id = web.input(worker_id='').worker_id
        return render_main.survey(worker_id)
        
class Error:
    def GET(self):
        pass
    
if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()