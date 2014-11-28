
import os
import webapp2
import jinja2
import yopy 
import datetime
from google.appengine.ext import ndb
from data_models import UserRecord, Configuration
from secrets import yo_token

#if os.environ['SERVER_SOFTWARE'].startswith('Development'):
if UserRecord.query().count() == 0:
        me = UserRecord()
        me.yo_handle = 'DHGOLDBERG'
        me.friend_contact = 'asdf'
        me.is_active = False
        me.last_yo_received = datetime.datetime.now()
        me.last_yo_sent = datetime.datetime.now()
        me.put()

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

yo = yopy.Yo(yo_token)  ## see https://github.com/dhgoldberg/YoPy

signup_template_values = {
                    'username': '',
                    'handle_input_key': 'handle_input',
                    'friend_contact_key': 'friend_contact'}

class yoCallback(webapp2.RequestHandler):
    def get(self):
        try:
            name = self.request.get('username')
            qry = UserRecord.query(UserRecord.yo_handle == name).get()

            if qry != None:
                # user is in database
                # call function for stuff
                user_checkin(qry)
            else:
                if len(name) > 0:
                    # send link to signup page in a link yo.
                    url = self.request.host_url + '?username=' + name
                    yo.yo_user(name, link=url)
        except Exception, e:
            raise e

class homepage(webapp2.RequestHandler):
    def get(self):
        username = self.request.get('username') # returns '' if username not there.
        # return the signup page with the username fileld in.
        signup_template_values['username'] = username

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(signup_template_values))

class signup(webapp2.RequestHandler):
    def post(self):
        username = self.request.get(signup_template_values['handle_input_key']).upper()
        friend = self.request.get(signup_template_values['friend_contact_key'])
        response_values = {'username':username, 'friend': friend, 'update_text':'added'}
        if len(username) > 0:
            user = UserRecord.query(UserRecord.yo_handle == username).get()
            if (user == None):
                new_user = UserRecord()
                new_user.yo_handle = username
                new_user.friend_contact = friend
                new_user.last_yo_sent = datetime.datetime.now()
                new_user.last_yo_received = datetime.datetime.now()
                new_user.put()
            else:
                user.friend_contact = friend
                user.put()
                response_values['update_text'] = 'updated'
            template = JINJA_ENVIRONMENT.get_template('signup_success.html')
            self.response.write(template.render(response_values))
        else:
            self.redirect('/')



class scheduled_task(webapp2.RequestHandler):
    def get(self):
        ## find who's active
        active_users = UserRecord.active_users()
        if active_users.count() > 0:
            yo_interval = Configuration.yo_interval()
            time = datetime.datetime.now()
            for user in active_users:
                if (time - user.last_yo_sent).seconds >= yo_interval:
                    if user.last_yo_received > user.last_yo_sent:
                        ## send new yo
                        yo.yo_user(user.yo_handle)
                        user.last_yo_sent = time
                    else:
                        ## contact friend_contact
                        user.is_active = False

                    user.put()


def user_checkin(user):
        if(user.is_active):
            disable_threshold = Configuration.disable_threshold()
            time = datetime.datetime.now()
            delta = (time - user.last_yo_received).seconds
            if delta <= disable_threshold:
                user.is_active = False
            else:
                user.last_yo_received = time

        else:
            user.is_active = True;
            user.last_yo_received = datetime.datetime.now()

        user.put()

application = webapp2.WSGIApplication([
        ('/', homepage),
        ('/signup', signup),
        ('/checkin', yoCallback),
        ('/cron_task', scheduled_task)
    ], debug=True)

