import argparse
import json

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from constant import SCOPES
from utils import add_permission, delete_permission, \
                  get_folder_id, read_json_into_memory


def delete_existing_permissions(service, drive_folder):
    instructors = ["demmanse@ualberta.ca", "ywang3@ualberta.ca",
                   "minghaocai@ualberta.ca", "fariaswa@ualberta.ca",
                   "bpowers@ualberta.ca", "boytang@ualberta.ca"]

    results = service.files().list(
        q="mimeType = 'application/vnd.google-apps.folder' and name='"+drive_folder+"'",
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    for item in items:
        print('{0} ({1})'.format(item['name'], item['id']))
        folder_id = item['id']

    list_permissions = service.permissions().list(fileId=folder_id, fields='*').execute()
    permissions = list_permissions.get('permissions')

    for p in permissions:
        if p['role'] != 'owner' and p['emailAddress'] not in instructors:
            delete_permission(folder_id, p['id'], service)


def create_permissions(service, drive_folder, students, role):
    """Creates permissions to a Google Drive folder.

    :param drive_foder: folder.
    :param students: students in the course.
    """
    items = get_folder_id(service, drive_folder)

    folder_id = None

    for item in items:
        print('{0} ({1})'.format(item['name'], item['id']))
        folder_id = item['id']
        print('Found folder with Drive id: ' + folder_id)

    for student in students:
        add_permission(student['email'], folder_id, service, role)


def parse_arg_list():
    """Uses argparse to parse the required parameters

    :returns: command line arguments.
    """
    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument(
        '-s', '--students',
        help='JSON file with student prenames, surnames, and emails', required=True)
    required_args.add_argument(
        '-f', '--folder',
        help='folder in Google drive where files are created', required=True)
    required_args.add_argument(
        '-r', '--role',
        help='permission role (i.e., fileOrganizer, writer, commenter, or reader)', required=True)

    args = parser.parse_args()
    return args


def main():
    args = parse_arg_list()

    # read the student file into memory
    students = read_json_into_memory(args.students)

    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    service = build('drive', 'v3', credentials=creds)

    delete_existing_permissions(service, args.folder)
    create_permissions(service, args.folder, students, args.role)

    # write back with the drive ids for the documents.
    with open(args.students, 'w') as f:
        json.dump(students, f)
        f.close()

if __name__ == '__main__':
    main()
