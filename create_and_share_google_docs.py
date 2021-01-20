import argparse
import json

from googleapiclient.discovery import build
from googleapiclient import errors
from google_auth_oauthlib.flow import InstalledAppFlow

TYPES = {'document': 'application/vnd.google-apps.document',
         'folder': 'application/vnd.google-apps.folder',
         'spreadsheet': 'application/vnd.google-apps.spreadsheet'}

SCOPES = 'https://www.googleapis.com/auth/drive'

def create_files(drive_folder, students, type, homework_affix, instructors, is_group):
    """Creates files for students inside a Google Drive folder.

    :param drive_foder: folder inside which the files should be created.
    :param students: students in the course.
    :param type: type of file to be created, either 'document' or 'folder'.
    :param homework_affix: affix added to the file names.
    :param instructors: instructional team emails.
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
        if "team" in student.keys():
            is_team = True
            id = student['team']
            document_name = string_or_empty(homework_affix) + student['team']
            if is_group:
                folders = get_folder_id(service, id)
                folder_id = folders[0]['id']
                document_name += combine_lastnames(student['lastnames'])
        else:
            is_team = False
            id = student['lastname'] + " " + student['firstname']
            document_name = string_or_empty(homework_affix) + '_' + \
                student['lastname'] + '_' + student['firstname']

        # test if document exists for this student already
        check = service.files().list(q="mimeType = 'application/vnd.google-apps."+type+"' and name='"+document_name+"'",
                                        pageSize=1, fields="nextPageToken, files(id, name)").execute().get('files', [])
        if check:
            print(id + ' already has a file on drive for this assignment.')
        else:
            file_metadata = {
                'name': document_name,
                'mimeType': TYPES[type] if type else TYPES['document'],
                'parents': [folder_id],
                "writersCanShare": False
            }

            studentSharedDoc = service.files().create(body=file_metadata, fields='id').execute()
            file_id = studentSharedDoc.get('id')

            print(id + " " + file_id)
            student[string_or_empty(homework_affix) + ' drive id'] = file_id

            list_permissions = service.permissions().list(fileId=file_id).execute()
            permissions = list_permissions.get('permissions')

            for p in permissions:
                if p['role'] != 'owner':
                    delete_permission(file_id, p['id'], service)

            if is_team:
                for member_ccid in student['ccids']:
                    member_email = member_ccid + '@ualberta.ca'
                    add_permission(member_email, file_id, service)
            else:
                add_permission(student['email'], file_id, service)

            if instructors:
                add_permissions_to_intructors(instructors, file_id, service)

def combine_lastnames(lastnames):
    """Creates a string with the students lastnames separated by underscores.
    :param lastnames: list of student lastnames.
    :returns: a string.
    """
    string = ''
    for s in lastnames:
        string += '_' + s
    return string

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

def add_permission(email, file_id, service):
    """Adds a new writer permission to the file.

    :param email: user email.
    :param file_id: id of the file.
    :param service: Google Drive service.
    """
    new_permission = {
        'emailAddress': email,
        'type': 'user',
        'role': 'writer'
    }
    try:
        service.permissions().create(fileId=file_id, body=new_permission, sendNotificationEmail=False).execute()
    except errors.HttpError as error:
        print ('An error occurred: %s' % error)

def delete_permission(file_id, permission_id, service):
    """Removes a permission from the file.

    :param file_id: id of the file.
    :param permission_id: id of the permission being removed.
    :param service: Google Drive service.
    """
    try:
        service.permissions().delete(fileId=file_id, permissionId=permission_id).execute()
    except errors.HttpError as error:
        print ('An error occurred: %s' % error)

def add_permissions_to_intructors(instructors, file_id, service):
    """Adds writer permissions to the file for the instructional team.

    :param instructors: instructional team emails.
    :param file_id: id of the file.
    :param service: Google Drive service.
    """
    for i in instructors:
        add_permission(i['email'], file_id, service)

def string_or_empty(string):
    """Returns a string preceded by an underscore or an empty string.
    Depending on whether the string parameter is none or not.

    :param string: string.
    :returns: a new string.
    """
    return  string if string else ''

def parse_arg_list():
    """Uses argparse to parse the required parameters

    :returns: command line arguments.
    """
    parser = argparse.ArgumentParser(description='Creates and shares documents on Google Drive for students to write homework.\n\n' +
        'Needs:\n a JSON file with student names and email addresses,\n a homework affix, \n a folder name.\n '+
        'There must be a folder on the drive account named with the same name as the script\'s parameter.\n\n'+
        'Each document is named <student firstname>_<student lastname>_<homework affix> and stored \nin that folder.',
        formatter_class=argparse.RawTextHelpFormatter)
    requiredArgs = parser.add_argument_group('required arguments')
    requiredArgs.add_argument('-s', '--students', help='JSON file with student firstnames, lastnames, and emails', required=True)
    requiredArgs.add_argument('-a', '--affix', help='affix identifying assignment (e.g., cmputXXXfXX-hwZZ)', required=False)
    requiredArgs.add_argument('-f', '--folder', help='folder in Google drive where files are created', required=True)
    requiredArgs.add_argument('-t', '--type', help='type of artifact to be created (i.e., document, spreadsheet, or folder), document as default', required=False)
    requiredArgs.add_argument('-i', '--instructors', help='JSON file with instructional team emails', required=False)
    requiredArgs.add_argument('-g', '--group', help='boolean to indicate if it is a group project and the file should be inside the group folder', required=False)

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

    if args.instructors:
        instructors = read_json_into_memory(args.instructors)
    else:
        instructors = None

    create_files(args.folder, students, args.type, args.affix, instructors, args.group)

    # write back with the drive ids for the documents.
    with open(args.students, 'w') as f:
        json.dump(students, f)
        f.close()

if __name__ == '__main__':
    main()


