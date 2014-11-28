from google.appengine.ext import ndb

class UserRecord(ndb.Model):
    yo_handle = ndb.StringProperty(required=True)
    friend_contact = ndb.StringProperty(required=True)
    is_active = ndb.BooleanProperty(required=True, default=False)
    last_yo_received = ndb.DateTimeProperty()
    last_yo_sent = ndb.DateTimeProperty()

    @classmethod
    def active_users(cls):
        return cls.query(cls.is_active == True)

class Configuration(ndb.Model):
    entry = ndb.StringProperty(required=True)
    value = ndb.StringProperty(required=True)

    @classmethod
    def yo_interval(cls):
        interval = cls.query(cls.entry == 'yo_interval').get()
        if interval == None:
            new_interval = Configuration()
            new_interval.entry = 'yo_interval'
            new_interval.value = str(60 * 5)
            new_interval.put()
            return eval(new_interval.value)
        else:
            return eval(interval.value)

    @classmethod
    def disable_threshold(cls):
        threshold = cls.query(cls.entry == 'disable_threshold').get()
        if threshold == None:
            thresh = Configuration()
            thresh.entry = 'disable_threshold'
            thresh.value = '45'
            thresh.put()
            return eval(thresh.value)
        else:
            return eval(threshold.value)
