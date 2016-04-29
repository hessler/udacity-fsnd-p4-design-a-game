#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity

from api import RockPaperScissorsApi

from models import User


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('<!doctype html><head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/foundation/6.0.1/css/foundation.css"></head><html><body><div class="row"><div class="columns"><h1>Rock, Paper, Scissors Game API</h1><p>Nothing to see here, folks. You need to go to the <a href="/_ah/api/explorer/">Rock, Paper, Scissors Game API</a>.</p></div></div></body></html>')


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            subject = 'This is a reminder!'
            body = 'Hello {}, try out Guess A Number!'.format(user.username)
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)


class UpdateAverageMovesRemaining(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        GuessANumberApi._cache_average_attempts()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
], debug=True)
