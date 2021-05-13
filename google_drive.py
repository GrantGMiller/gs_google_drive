try:
    import requests
except:
    print('importing gs_requests as requests')
    import gs_requests as requests

#import mimetypes  # blocked by Global Scripter
from pathlib import Path
from extronlib.system import File


def GuessMimeType(src):
    return {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.gif': 'image/gif',
        '.ico': 'image/x-icon',
        '.jfif': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.txt': 'text/plain',
        '.py': 'text/plain',
        '.mp4': 'video/mp4',
    }[Path(src).suffix.lower()]


class GoogleDrive:
    def __init__(self, oauthCallback):
        self._oauthCallback = oauthCallback

    def Upload(self, src):
        '''
        https://developers.google.com/drive/api/v3/manage-uploads
        :param src: str
        :param dst:
        :return: dict like {
             "kind": "drive#file",
             "id": "this_is_a_fake_id",
             "name": "Untitled",
             "mimeType": "image/jpeg"
            }
        '''
        print('GoogleDrive.Upload(', src)
        name = Path(src).name
        print('name=', name)
        resp = self._Post(
            url='https://www.googleapis.com/upload/drive/v3/files?uploadType=media',
            data=File(src, 'rb'),
            headers={
                'Content-Type': GuessMimeType(src),
            },
        )
        print('resp.text=', resp.text)
        ID = resp.json()['id']

        # the file has been uploaded, now update the file name in the metadata
        respPatchName = self._Patch(
            url='https://www.googleapis.com/drive/v3/files/{}'.format(ID),
            json={
                'name': name,
            },
        )
        print('respPatchName.json()=', respPatchName.json())

        return respPatchName.json()

    def GetSharingLink(self, fileID):
        '''
        Makes the file readable by anyone and returns the sharing URL
        :param fileID:
        :return:
        '''

        # check if the file is already shareable
        respGetPermissions = self._Get(
            url='https://www.googleapis.com/drive/v3/files/{fileId}/permissions'.format(
                fileId=fileID
            ),
        )
        print('respGetPermissions.json()=', respGetPermissions.json())

        for permission in respGetPermissions.json()['permissions']:
            print('permission=', permission)
            if permission.get('type', None) == 'anyone' and permission.get('role', None) == 'reader':
                print('permission found')
                break
        else:
            print('sharing permission not found, add a permission')
            respPostPermission = self._Post(
                url='https://www.googleapis.com/drive/v3/files/{fileId}/permissions'.format(
                    fileId=fileID,
                ),
                json={
                    'type': 'anyone',
                    'role': 'reader', }
            )
            print('respPostPermission.json()=', respPostPermission.json())

        # get the sharing URL
        respGetMeta = self._Get(
            url='https://www.googleapis.com/drive/v3/files/{fileId}'.format(
                fileId=fileID
            ),
            params={
                'fields': ','.join([
                    'webViewLink'
                ])
            }
        )
        print('respGetMeta.json()=', respGetMeta.json())

        return respGetMeta.json()['webViewLink']

    ############################################

    def _Get(self, *a, **k):
        return self._SendRequest(
            method='Get',
            *a, **k,
        )

    def _Post(self, *a, **k):
        return self._SendRequest(
            method='POST',
            *a, **k,
        )

    def _Patch(self, *a, **k):
        return self._SendRequest(
            method='PATCH',
            *a, **k,
        )

    def _SendRequest(self, method, *a, **k):
        headers = k.get('headers', {})
        headers['Authorization'] = 'Bearer {}'.format(self._oauthCallback())
        k['headers'] = headers

        resp = requests.request(
            method=method,
            *a,
            **k,
        )
        print('resp.text=', resp.text)
        return resp
