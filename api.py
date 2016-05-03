# -*- coding: utf-8 -*-`
"""api.py - Main Game API."""


from __future__ import division
import endpoints
import random

from protorpc import remote, messages

from models import User, Game
from models import StringMessage, MakePlayForm, Move, NewGameForm,\
    GameForms, GameForm, UserForm, UserForms, UserRankingForms, UserScoreForms
from utils import get_by_urlsafe


VALID_PLAYS = ["rock", "paper", "scissors"]
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)
MAKE_PLAY_REQUEST = endpoints.ResourceContainer(MakePlayForm,
                                                urlsafe_game_key=messages.StringField(1),)
GET_USER_REQUEST = endpoints.ResourceContainer(username=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(username=messages.StringField(1),
                                           display_name=messages.StringField(2),
                                           email=messages.StringField(3))


@endpoints.api(name='rock_paper_scissors', version='v1')
class RockPaperScissorsApi(remote.Service):
    """Main Game API"""

    #-------------------------------------------------------------------
    # create_user
    #-------------------------------------------------------------------
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=UserForm,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username."""
        if User.query(User.username == request.username).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        user = User(username=request.username,
                    display_name=request.display_name,
                    email=request.email)
        user.put()
        return user.to_form()


    #-------------------------------------------------------------------
    # get_user
    #-------------------------------------------------------------------
    @endpoints.method(request_message=GET_USER_REQUEST,
                      response_message=UserForm,
                      path='get_user',
                      name='get_user',
                      http_method='GET')
    def get_user(self, request):
        """Return a User object for specified username. Requires a unique username."""
        user = User.query(User.username == request.username).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        return user.to_form()


    #-------------------------------------------------------------------
    # get_users
    #-------------------------------------------------------------------
    @endpoints.method(response_message=UserForms,
                      path='users',
                      name='get_users',
                      http_method='GET')
    def get_users(self, request):
        """Return all users, sorted by username."""
        return UserForms(users=[user.to_form() for user in User.query().order(User.username)])


    #-------------------------------------------------------------------
    # new_game
    #-------------------------------------------------------------------
    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game."""
        user = User.query(User.username == request.username).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        game = Game.new_game(user.key)
        return game.to_form('Good luck playing Rock, Paper, Scissors!')


    #-------------------------------------------------------------------
    # get_game
    #-------------------------------------------------------------------
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a play!')
        else:
            raise endpoints.NotFoundException('Game not found!')


    #-------------------------------------------------------------------
    # cancel_game
    #-------------------------------------------------------------------
    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}/cancel',
                      name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):
        """Cancels the specified game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.cancelled:
                raise endpoints.ConflictException("""This game has already been\
                    cancelled!""")
            if game.game_over:
                raise endpoints.ConflictException("""This game is already over.\
                    You cannot cancel it!""")
            game.cancelled = True
            game.end_game(True)
            return game.to_form('Game cancelled!')
        else:
            raise endpoints.NotFoundException('Game not found!')


    #-------------------------------------------------------------------
    # make_play
    #-------------------------------------------------------------------
    @endpoints.method(request_message=MAKE_PLAY_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_play',
                      http_method='PUT')
    def make_play(self, request):
        """Makes a play. Returns a game state with message."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')

        if game.game_over:
            return game.to_form('Game already over!')

        # Get plays of AI and user, making sure they're valid.
        ai_play = random.choice(VALID_PLAYS)
        user_play = request.play.lower()
        if not user_play in VALID_PLAYS:
            msg = 'Uh-oh. You need to specify either Rock, Paper, or Scissors.'
            game.put()
            return game.to_form(msg)

        if user_play == ai_play:
            msg = 'Looks like we both picked {}. Play again!'.format(user_play.title())
            game.moves.append(Move(play=user_play, ai_play=ai_play, result=msg))
            game.put()
            return game.to_form(msg)

        # Attach plays to game attributes
        game.ai_play = ai_play
        game.play = user_play

        # Set other applicable game attributes, including outgoing message for form.
        if user_play == 'scissors' and ai_play == 'paper' or\
           user_play == 'rock' and ai_play == 'scissors' or\
           user_play == 'paper' and ai_play == 'rock':
            msg = """Congratulations, your {} beats my {}.\
                You win!""".format(user_play.title(), ai_play.title())
            game.message = msg
            game.moves.append(Move(play=user_play, ai_play=ai_play, result=msg))
            game.put()
            game.end_game(True)
            return game.to_form(msg)
        else:
            msg = """Sorry, my {} beats your {}. You lose!"""\
                .format(ai_play.title(), user_play.title())
            game.message = msg
            game.moves.append(Move(play=user_play, ai_play=ai_play, result=msg))
            game.put()
            game.end_game(False)
            return game.to_form(msg)


    #-------------------------------------------------------------------
    # get_games
    #-------------------------------------------------------------------
    @endpoints.method(response_message=GameForms,
                      path='games',
                      name='get_games',
                      http_method='GET')
    def get_games(self, request):
        """Return all games, ordered by most recent game date."""
        return GameForms(games=[game.to_form() for game in Game.query().order(-Game.date)])


    #-------------------------------------------------------------------
    # get_user_games
    #-------------------------------------------------------------------
    @endpoints.method(request_message=GET_USER_REQUEST,
                      response_message=GameForms,
                      path='user_games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all active (unfinished) games for specified user."""
        user = User.query(User.username == request.username).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        query = Game.query()\
            .filter(Game.game_over == False)\
            .filter(Game.user == user.key)
        return GameForms(games=[game.to_form() for game in query])


    #-------------------------------------------------------------------
    # get_user_rankings
    #-------------------------------------------------------------------
    @endpoints.method(response_message=UserScoreForms,
                      path='high_scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Return player high scores in the format of longest win streak."""
        # Iterate through users, getting all completed (and not cancelled)
        # games, sorted by date. Iterate through the games and calculate
        # number of consecutive wins to determine user's longest win streak.
        all_users = User.query()
        for user in all_users:
            curr_streak = 0
            longest_streak = 0
            all_games = Game.query()\
                .filter(Game.game_over == True)\
                .filter(Game.cancelled == False)\
                .filter(Game.user == user.key).order(-Game.date)
            for game in all_games:
                if game.won:
                    curr_streak += 1
                    if curr_streak >= longest_streak:
                        longest_streak = curr_streak
                else:
                    curr_streak = 0
            user.longest_win_streak = longest_streak
            user.put()
        all_users = User.query().order(-User.longest_win_streak)
        return UserScoreForms(scores=[user.to_score_form() for user in all_users])



    #-------------------------------------------------------------------
    # get_user_rankings
    #-------------------------------------------------------------------
    @endpoints.method(response_message=UserRankingForms,
                      path='user_rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return player rankings based on winning percentage."""
        # Iterate through users, getting count of completed (not cancelled)
        # games as well as count of games won. Use these to determine the
        # user's win percentage.
        all_users = User.query()
        for user in all_users:
            total_games = Game.query()\
                .filter(Game.game_over == True)\
                .filter(Game.cancelled == False)\
                .filter(Game.user == user.key).count()
            wins = Game.query()\
                .filter(Game.game_over == True)\
                .filter(Game.cancelled == False)\
                .filter(Game.user == user.key)\
                .filter(Game.won == True).count()
            win_percentage = float(wins / total_games) if total_games > 0 else 0.00
            user.total_games = total_games
            user.wins = wins
            user.win_percentage = win_percentage
            user.put()
        all_users = User.query().order(-User.win_percentage)
        return UserRankingForms(rankings=[user.to_rank_form() for user in all_users])


    #-------------------------------------------------------------------
    # get_game_history
    #-------------------------------------------------------------------
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a history of moves for game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        return game.to_history_form()


api = endpoints.api_server([RockPaperScissorsApi])
