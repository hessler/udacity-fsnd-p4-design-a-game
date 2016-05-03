#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or cronjobs."""

import webapp2
from google.appengine.api import mail, app_identity

from api import RockPaperScissorsApi

from models import User, Game


class MainHandler(webapp2.RequestHandler):
    """Main handler for requests."""
    def get(self):
        """Return generic HTML page with link to API Explorer."""
        self.response.write("""<!doctype html><head><link rel="stylesheet"\
            href="https://cdnjs.cloudflare.com/ajax/libs/foundation/6.0.1/css/foundation.css">\
            </head><html><body><div class="row"><div class="columns">\
            <h1>Rock, Paper, Scissors Game API</h1>\
            <p>Nothing to see here, folks. You need to go to the\
            <a href="/_ah/api/explorer/">Rock, Paper, Scissors Game API</a>.</p>\
            </div></div></body></html>""")


class SendReminderEmail(webapp2.RequestHandler):
    """Handler for requests for sending reminder emails."""
    def get(self):
        """Send a reminder email to each User with incomplete games."""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            games = Game.query().filter(Game.game_over == False).filter(Game.user == user.key)
            if games.count() > 0:
                subject = 'Time to Make Your Move in Rock, Paper, Scissors!'
                body = """Hello {}, it looks like you have some incomplete\
                          games of Rock, Paper, Scissors waiting for you.""".format(user.username)
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/crons/send_reminder', SendReminderEmail),
], debug=True)
