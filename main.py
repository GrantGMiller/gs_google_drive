import time
import extronlib
from gs_oauth_tools import AuthManager
try:
    import webbrowser
except:
    pass
from google_drive import GoogleDrive

authManager = AuthManager(
    googleJSONpath=r'google.json',
)

MY_ID = '3888'

user = authManager.GetUserByID(MY_ID)
if user is None:
    d = authManager.CreateNewUser(MY_ID, authType='Google')
    try:
        webbrowser.open(d['verification_uri'])
    except:
        pass
    print(d['user_code'])

while authManager.GetUserByID(MY_ID) is None:
    time.sleep(1)

user = authManager.GetUserByID(MY_ID)
print('user=', user)

gDrive = GoogleDrive(oauthCallback=user.GetAccessToken)
file = gDrive.Upload(r'trump.jpg')

link = gDrive.GetSharingLink(file['id'])
print(link)
