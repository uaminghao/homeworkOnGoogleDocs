import argparse

from googleapiclient.discovery import build
from googleapiclient import errors
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = 'https://www.googleapis.com/auth/drive'

def change_permissions(drive_folder, affix):
    """Updates permissions for selected files.
    :param drive_foder: files' parent folder.
    :param affix: affix used to filter the file names.
    """
    flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    service = build('drive', 'v3', credentials=creds)

    items = get_folder_id(service, drive_folder)

    folder_id = items[0]['id']

    files = service.files().list(q="'"+folder_id+"' in parents",
                                 pageSize=500, fields="nextPageToken, files(id, name)").execute().get('files', [])
    updated_permission = {
        'role': 'reader'
    }

    for file in files:
        if not affix or affix in file['name']:
            try:
                file_id = file['id']
                list_permissions = service.permissions().list(fileId=file_id).execute()
                permissions = list_permissions.get('permissions')
                for p in permissions:
                    if p['role'] != 'owner':
                        try:
                            service.permissions().update(fileId=file_id, permissionId=p['id'], body=updated_permission).execute()
                        except errors.HttpError as error:
                            print('An error occurred: %s' % error)
            except errors.HttpError as error:
                print('An error occurred: %s' % error)

def get_folder_id(service, drive_folder):
    """Retrieve folder id from Google Drive.
    :param service: Google Drive service.
    :param drive_folder: folder name.
    :returns: a list of folders that match the param name.
    """
    # look for a directory on the drive with the homework name (e.g., "cmput391 f18 homework 1")
    results = service.files().list(q="mimeType = 'application/vnd.google-apps.folder' and name='"+drive_folder+"'",
                                   pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('Could not find folder named: "' + drive_folder + '"')
        exit(0)
    return items

def parse_arg_list():
    """Uses argparse to parse the required parameters

    :returns: command line arguments.
    """
    parser = argparse.ArgumentParser(description='Changes permissions of files inside the folder to commenter after deadline.',
        formatter_class=argparse.RawTextHelpFormatter)
    requiredArgs = parser.add_argument_group('required arguments')
    requiredArgs.add_argument('-f', '--folder', help='folder name', required=True)
    requiredArgs.add_argument('-a', '--affix', help='documents\' affix to filter which permissions to update', required=False)

    args = parser.parse_args()
    return args

def main():
    args = parse_arg_list()

    change_permissions(args.folder, args.affix)

if __name__ == '__main__':
    main()