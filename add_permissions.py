import argparse
import json

from googleapiclient.discovery import build
from googleapiclient import errors
from google_auth_oauthlib.flow import InstalledAppFlow

TYPES = {'document': 'application/vnd.google-apps.document',
         'folder': 'application/vnd.google-apps.folder',
         'spreadsheet': 'application/vnd.google-apps.spreadsheet'}

SCOPES = 'https://www.googleapis.com/auth/drive'


def create_permissions(drive_folder, students, role):
    """Creates permissions to a Google Drive folder.

    :param drive_foder: folder.
    :param students: students in the course.
    """
    flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    service = build('drive', 'v3', credentials=creds)

    items = get_folder_id(service, drive_folder)

    folder_id = None

    for item in items:
        print('{0} ({1})'.format(item['name'], item['id']))
        folder_id = item['id']
        print('Found folder with Drive id: ' + folder_id)

    for student in students:
        add_permission(student['email'], folder_id, service, role)


def get_folder_id(service, drive_folder):
    """Retrieve folder id from Google Drive.

    :param service: Google Drive service.
    :param drive_folder: folder name.
    :returns: a list of folders that match the param name.
    """
    results = service.files().list(q="mimeType = 'application/vnd.google-apps.folder' and name='"+drive_folder+"'",
                                   pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('Could not find folder named: "' + drive_folder + '"')
        exit(0)
    return items


def add_permission(email, file_id, service, role):
    """Adds a new writer permission to the file.

    :param email: user email.
    :param file_id: id of the file.
    :param service: Google Drive service.
    :param role: permission type.
    """
    new_permission = {
        'emailAddress': email,
        'type': 'user',
        'role': role
    }
    try:
        service.permissions().create(fileId=file_id, body=new_permission, sendNotificationEmail=False).execute()
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def parse_arg_list():
    """Uses argparse to parse the required parameters

    :returns: command line arguments.
    """
    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-s', '--students', help='JSON file with student prenames, surnames, and emails', required=True)
    required_args.add_argument('-f', '--folder', help='folder in Google drive where files are created', required=True)
    required_args.add_argument('-r', '--role', help='permission role (i.e., fileOrganizer, write, commenter, or reader)', required=True)

    args = parser.parse_args()
    return args


def read_json_into_memory(filename):
    """Uses argparse to parse the required parameters

    :returns: command line arguments.
    """
    with open(filename, 'r') as f:
        values = json.load(f)
        f.close()
    return values


def main():
    args = parse_arg_list()

    # read the student file into memory
    students = read_json_into_memory(args.students)

    create_permissions(args.folder, students, args.role)

    # write back with the drive ids for the documents.
    with open(args.students, 'w') as f:
        json.dump(students, f)
        f.close()

if __name__ == '__main__':
    main()
