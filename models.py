"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date, datetime
from protorpc import messages
from google.appengine.ext import ndb


valid_plays = ["rock", "paper", "scissors"]


class User(ndb.Model):
    """User profile."""
    username = ndb.StringProperty(required=True)
    display_name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)

    def to_form(self):
        """Returns a UserForm representation of the User."""
        form = UserForm()
        form.username = self.username
        form.display_name = self.display_name
        form.email = self.email
        return form


class Game(ndb.Model):
    """Game object."""
    ai_play = ndb.StringProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    play = ndb.StringProperty(required=True, default='')

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game."""
        game = Game(user=user,
                    ai_play=random.choice(valid_plays),
                    game_over=False)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game."""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.username = self.user.get().username
        form.game_over = self.game_over
        form.message = message
        form.ai_play = self.ai_play
        form.play = self.play
        return form

    def end_game(self, user_play, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.play = user_play
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=datetime.today(), won=won,
                      play=self.play, ai_play=self.ai_play)
        score.put()


class Score(ndb.Model):
    """Score object."""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateTimeProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    play = ndb.StringProperty(required=True)
    ai_play = ndb.StringProperty(required=True)

    def to_form(self):
        return ScoreForm(username=self.user.get().username, won=self.won,
                         date=str(self.date), play=self.play, ai_play=self.ai_play)


#
# TODO: Combine score with game form? Add "won" attribute to GameForm and assign when game is done?
#
class GameForm(messages.Message):
    """GameForm for outbound game state information."""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(2, required=True)
    message = messages.StringField(3, required=True)
    username = messages.StringField(4, required=True)
    ai_play = messages.StringField(5, required=True)
    play = messages.StringField(6, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    username = messages.StringField(1, required=True)


class MakePlayForm(messages.Message):
    """Used to make a play in an existing game."""
    play = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information."""
    username = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    play = messages.StringField(4, required=True)
    ai_play = messages.StringField(5, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms."""
    scores = messages.MessageField(ScoreForm, 1, repeated=True)


class UserForm(messages.Message):
    """UserForm for outbound User information."""
    username = messages.StringField(1, required=True)
    display_name = messages.StringField(2, required=True)
    email = messages.StringField(3, required=True)


class UserForms(messages.Message):
    """Return multiple UserForms."""
    users = messages.MessageField(UserForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
