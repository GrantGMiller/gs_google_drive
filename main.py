import time
import extronlib
from gs_oauth_tools import AuthManager
import webbrowser
from google_drive import GoogleDrive


authManager = AuthManager(
    googleJSONpath=r'C:\Users\gmiller\PycharmProjects\gs_oauth\google_Test Google Drive 2021-04-19 1056.json',
)

MY_ID = '3888'

user = authManager.GetUserByID(MY_ID)
if user is None:
    d = authManager.CreateNewUser(MY_ID, authType='Google')
    webbrowser.open(d['verification_uri'])
    print(d['user_code'])

while authManager.GetUserByID(MY_ID) is None:
    time.sleep(1)

user = authManager.GetUserByID(MY_ID)
print('user=', user)

gDrive = GoogleDrive(oauthCallback=user.GetAccessToken)
file = gDrive.Upload(r'trump.jpg')

gDrive.GetSharingLink(file['id'])
