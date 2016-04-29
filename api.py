# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakePlayForm,\
    ScoreForms, UserForm, UserForms
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_PLAY_REQUEST = endpoints.ResourceContainer(
    MakePlayForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(username=messages.StringField(1),
                                           display_name=messages.StringField(2),
                                           email=messages.StringField(3))

#MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='rock_paper_scissors', version='v1')
class RockPaperScissorsApi(remote.Service):
    """Main Game API"""
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
        user = User(username=request.username, display_name=request.display_name, email=request.email)
        user.put()
        return user.to_form()

    @endpoints.method(response_message=UserForms,
                      path='users',
                      name='get_users',
                      http_method='GET')
    def get_users(self, request):
        """Return all users, sorted by username."""
        return UserForms(users=[user.to_form() for user in User.query().order(User.username)])

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

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        #taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Rock, Paper, Scissors!')

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

    @endpoints.method(request_message=MAKE_PLAY_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_play',
                      http_method='PUT')
    def make_play(self, request):
        """Makes a play. Returns a game state with message."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')

        user_play = request.play.lower()
        if user_play == game.ai_play:
            msg = 'Looks like we both picked {}. Play again!'.format(user_play.title())
            game.put()
            return game.to_form(msg)

        if user_play == 'scissors' and game.ai_play == 'paper' or\
           user_play == 'rock' and game.ai_play == 'scissors' or\
           user_play == 'paper' and game.ai_play == 'rock':
            game.end_game(user_play, True)
            return game.to_form('Congratulations, your {} beats my {}. You win!'.format(user_play.title(), game.ai_play.title()))
        else:
            game.end_game(user_play, False)
            return game.to_form('Sorry, my {} beats your {}. You lose!'.format(game.ai_play.title(), user_play.title()))

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores, ordered by most recent game date."""
        return ScoreForms(scores=[score.to_form() for score in Score.query().order(-Score.date)])

    #@endpoints.method(request_message=USER_REQUEST,
    #                  response_message=ScoreForms,
    #                  path='scores/user/{username}',
    #                  name='get_user_scores',
    #                  http_method='GET')
    #def get_user_scores(self, request):
    #    """Returns all of an individual User's scores"""
    #    user = User.query(User.username == request.username).get()
    #    if not user:
    #        raise endpoints.NotFoundException(
    #                'A User with that name does not exist!')
    #    scores = Score.query(Score.user == user.key)
    #    return ScoreForms(items=[score.to_form() for score in scores])

    #@endpoints.method(response_message=StringMessage,
    #                  path='games/average_attempts',
    #                  name='get_average_attempts_remaining',
    #                  http_method='GET')
    #def get_average_attempts(self, request):
    #    """Get the cached average moves remaining"""
    #    return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    #@staticmethod
    #def _cache_average_attempts():
    #    """Populates memcache with the average moves remaining of Games"""
    #    games = Game.query(Game.game_over == False).fetch()
    #    if games:
    #        count = len(games)
    #        total_attempts_remaining = sum([game.attempts_remaining
    #                                    for game in games])
    #        average = float(total_attempts_remaining)/count
    #        memcache.set(MEMCACHE_MOVES_REMAINING,
    #                     'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([RockPaperScissorsApi])
