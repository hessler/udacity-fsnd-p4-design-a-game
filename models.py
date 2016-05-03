"""models.py - Class definitions for Datastore entities used."""

import random
from datetime import date, datetime
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile."""
    username = ndb.StringProperty(required=True)
    display_name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    total_games = ndb.IntegerProperty()
    wins = ndb.IntegerProperty()
    win_percentage = ndb.FloatProperty()
    longest_win_streak = ndb.IntegerProperty()

    def to_form(self):
        """Returns a UserForm representation of the User."""
        form = UserForm()
        form.username = self.username
        form.display_name = self.display_name
        form.email = self.email
        return form

    def to_rank_form(self):
        """Returns a UserRankingForm representation of the User."""
        form = UserRankingForm()
        form.username = self.username
        form.display_name = self.display_name
        form.total_games = self.total_games
        form.wins = self.wins
        form.win_percentage = '%.4f' % self.win_percentage
        return form

    def to_score_form(self):
        """Returns a UserScoreForm representation of the User."""
        form = UserScoreForm()
        form.username = self.username
        form.display_name = self.display_name
        form.score = self.longest_win_streak
        return form


class Move(ndb.Model):
    """Move object."""
    play = ndb.StringProperty(required=True, default='')
    ai_play = ndb.StringProperty(required=True, default='')
    result = ndb.StringProperty(required=True, default='')

    def to_dict(self):
        """Convenience method to return Move as dictionary."""
        return {'play': str(self.play), 'ai_play': str(self.ai_play),\
                'result': str(self.result)}


class Game(ndb.Model):
    """Game object."""
    play = ndb.StringProperty(required=True, default='')
    ai_play = ndb.StringProperty(required=True, default='')
    game_over = ndb.BooleanProperty(required=True, default=False)
    won = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateTimeProperty(required=True)
    message = ndb.StringProperty(required=True, default='')
    cancelled = ndb.BooleanProperty(required=True, default=False)
    moves = ndb.StructuredProperty(Move, repeated=True)

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game."""
        game = Game(user=user,
                    date=datetime.today(),
                    game_over=False)
        game.put()
        return game

    def to_form(self, message=''):
        """Returns a GameForm representation of the Game."""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.username = self.user.get().username
        form.game_over = self.game_over
        form.message = message if message != '' else self.message
        form.ai_play = self.ai_play
        form.play = self.play
        form.won = self.won
        form.date = str(self.date)
        form.cancelled = self.cancelled
        for index, move in enumerate(self.moves):
            self.moves[index] = move.to_dict()
        form.moves = ', '.join(map(str, self.moves))
        return form

    def to_history_form(self):
        """Returns a StringMessage representation of the Game moves."""
        # Convert each move to a dictionary for pretty output
        for index, move in enumerate(self.moves):
            self.moves[index] = move.to_dict()
        return StringMessage(message=', '.join(map(str, self.moves)))

    def end_game(self, won=False):
        """Ends the game. Update necessary attributes for Game object."""
        self.game_over = True
        self.won = won
        self.date = datetime.today()
        self.put()


class GameForm(messages.Message):
    """GameForm for outbound game state information."""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(2, required=True)
    message = messages.StringField(3, required=True)
    username = messages.StringField(4, required=True)
    ai_play = messages.StringField(5, required=True)
    play = messages.StringField(6, required=True)
    won = messages.BooleanField(7, required=True, default=False)
    date = messages.StringField(8, required=True)
    cancelled = messages.BooleanField(9, required=True, default=False)
    moves = messages.StringField(10, required=True)


class GameForms(messages.Message):
    """Return multiple GameForm objects."""
    games = messages.MessageField(GameForm, 1, repeated=True)


class GameHistoryForm(messages.Message):
    """GameHistoryForm for outbound game history information."""
    moves = messages.StringField(1, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    username = messages.StringField(1, required=True)


class MakePlayForm(messages.Message):
    """Used to make a play in an existing game."""
    play = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """UserForm for outbound User information."""
    username = messages.StringField(1, required=True)
    display_name = messages.StringField(2, required=True)
    email = messages.StringField(3, required=True)


class UserForms(messages.Message):
    """Return multiple UserForms."""
    users = messages.MessageField(UserForm, 1, repeated=True)


class UserRankingForm(messages.Message):
    """UserRankingForm for outbound User Ranking information."""
    username = messages.StringField(1, required=True)
    display_name = messages.StringField(2, required=True)
    total_games = messages.IntegerField(3, required=True)
    wins = messages.IntegerField(4, required=True)
    win_percentage = messages.StringField(5, required=True)


class UserRankingForms(messages.Message):
    """Return multiple UserRankingForms."""
    rankings = messages.MessageField(UserRankingForm, 1, repeated=True)


class UserScoreForm(messages.Message):
    """UserScoreForm for outbound User score information. Scores are\
    determined by the longest winning streak for each user."""
    username = messages.StringField(1, required=True)
    display_name = messages.StringField(2, required=True)
    score = messages.IntegerField(3, required=True)


class UserScoreForms(messages.Message):
    """Return multiple UserScoreForms."""
    scores = messages.MessageField(UserScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
