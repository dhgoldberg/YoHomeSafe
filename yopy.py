#!/usr/bin/env python
"""
A simple Yo! API for python.

As of now, you can:
    1.Get the number of subscribers
    2.Send a Yo! to all subscribers
    3.Send a Yo! to a specific user

YoPy requires a Yo! API access token. You can get one by registering at http://dev.justyo.co/

Parth Dhar
2014

GAE integration by David H Goldberg 2014
"""
from google.appengine.api import urlfetch
import json

class Yo:
    def __init__(self, token):
        self.token = token

    def number(self):
        """
        Function to GET the the number of subscribers of the API user account.

        Returns:
            int: number of subscribers if request is successful.

        Raises:
            Exception: if request is unsuccessful.
        """
        number_url = "https://api.justyo.co/subscribers_count/?api_token=" + self.token
        number = urlfetch.fetch(number_url)
        if number.status_code == 200:
            inObj = json.loads(number.content)
            return inObj['result']
        else:
            raise Exception(number.status_code)

    def yo_all(self, link=''):
        """
        Function to send a Yo to all subscribers of the API user account.

        Args:
            link (str, optional): link to send with Yo. Default is neglected.

        Returns:
            bool: True if request is successful.

        Raises:
            Exception: if request is unsuccessful.
        """
        yoall_data = {"api_token": self.token, 'link':link}
        yoall_url = "https://api.justyo.co/yoall/"
        yoall = urlfetch.fetch(url=yoall_url,
                               payload=json.dumps(yoall_data),
                               method=urlfetch.POST,
                               headers={'content-type': 'application/json'})
        if yoall.status_code == 201: # not sure why 201 and not 200... 
            return True
        else:
            raise Exception(yoall.status_code)

    def yo_user(self, username, **kwargs):
        """
        Function to send a Yo to a specific username.
        
        Args:
            username (str): the Yo usernname.
            **kwargs: keyword should be either ''link'' or ''location''.
                Location should be of the form ''lat,lon'' where lat and lon are decimal degrees.

        Returns:
            bool: True if request is successful.

        Raises:
            Exception: if request is unsuccessful.
        """
        username = username.upper()
        youser_data = {"api_token": self.token, "username": username}
        for kw in kwargs:
            youser_data.update( { kw:kwargs[kw] } )
        youser_url = "https://api.justyo.co/yo/"
        youser = urlfetch.fetch(url=youser_url, 
                                payload=json.dumps(youser_data), 
                                method=urlfetch.POST,
                                headers={'content-type': 'application/json'})
        if youser.status_code == 200:
            return True
        else:
            raise Exception(youser.status_code)
