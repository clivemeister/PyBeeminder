import urllib
import requests
import configparser

# based on https://www.beeminder.com/api

class Beeminder:
    _base_url = 'https://www.beeminder.com/api/v1/'

    # Can initialise either from .ini file or via parameters
    def __init__(self, user="", token="", ini_file=""):
        if len(ini_file)>0:
            config = configparser.ConfigParser()
            config.read(ini_file)
            self.username = config['USER']['username']
            self.auth_token = config['USER']['auth_token']
        else:
            self.auth_token = token
            self.username = user

    def get_username(self):
        return self.username

    def get_user(self):
        return self._call(f'users/{self.username}')

    def get_goals(self):
        return self._call(f'users/{self.username}/goals.json')

    def get_goal(self, goalname):
        result = self._call(f'users/{self.username}/goals/{goalname.strip()}.json')
        return result

    def get_datapoints(self, goalname):
        return self._call(f'users/{self.username}/goals/{goalname}/datapoints.json')

    def create_datapoint(self, goalname, timestamp, value, comment=' ', sendmail='false'):
        values = {'auth_token':self.auth_token, 
                  'timestamp':timestamp, 
                  'value':value, 
                  'comment':comment, 
                  'sendmail':sendmail
                  }
        return self._call(f'users/{self.username}/goals/{goalname.strip()}/datapoints.json', data=values, method='POST')

    def create_goal(self, *, slug="goalname", title="", goal_type="hustler", gunits, 
                    goaldate="2099-12-31", goalval="", rate=1, buffer=0,
                    initval=0, test=False ):
        from datetime import datetime


        values = {'auth_token':self.auth_token,
                  "slug":slug, 
                  "title": title,
                  "goal_type": goal_type,
                  "gunits": gunits,
                  "runits": "d"     # need this to make rate per day, as curiously the default is "w" for per-week goals!
                  }
        
        if goaldate is not None:
            goal_dt = datetime.strptime(goaldate, '%Y-%m-%d')    
            goal_unixtime = int(goal_dt.timestamp())      # time since epoch in seconds, as a string
            values['goaldate'] = goal_unixtime
        
        if goalval is not None:
            values['goalval'] = goalval
        
        if rate is not None:
            values['rate'] = rate

        if initval is not None:
            values['initval'] = initval

        if buffer is not None:
            values['buffer_days'] = buffer

        if test is True:
            values['dryrun'] = 1
        
        return self._call(f'users/{self.username}/goals.json', data=values, method='POST')
    
    def update_road(self, goalname, new_roadall):
        slug = {"roadall": new_roadall}
        return self._call(f'users/{self.username}/goals/{goalname}.json', data=slug, method='PUT')

    def _call(self, endpoint, data=None, method='GET'):
        if data is None:
            data = {}

        if self.auth_token:
            data.update({'auth_token': self.auth_token})
        elif self._access_token:
            data.update({'access_token': self._access_token})

        url = f'{self._base_url}{endpoint}'
        result = None

        if method == 'GET':
            result = requests.get(url, data)

        if method == 'POST':
            result = requests.post(url, data)

        if method == 'PUT':
            result = requests.put(url, data)

        if not result.status_code == requests.codes.ok:
            raise Exception(f'API request {method} {url} failed with code {result.status_code}: {result.text}')
        print(f"Completed API request {method} {url} with status code {result.status_code}")

        # self._persist_result(endpoint, result)

        return None if result is None else result.json()
