import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/classroom.student-submissions.me.readonly', 
          'https://www.googleapis.com/auth/classroom.courses.readonly', 
          'https://www.googleapis.com/auth/classroom.announcements']

def log_in(credentials):
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        return credentials
    # Getting a new credential
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            './ClassroomScraping/credentials.json', SCOPES) 
        flow.run_local_server(port=0)
        return flow.credentials

class authorization(object):

    def __init__(self):
        self._creds = None

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('./ClassroomScraping/token.pickle'):
            with open('./ClassroomScraping/token.pickle', 'rb') as token:
                self._creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not self._creds or not self._creds.valid:
            self._creds = log_in(self._creds)

            # Save the credentials for the next run
            with open('./ClassroomScraping/token.pickle', 'wb') as token:
                pickle.dump(self._creds, token)

    #getter credentials
    @property
    def credentials(self):
        return self._creds

    

        
        