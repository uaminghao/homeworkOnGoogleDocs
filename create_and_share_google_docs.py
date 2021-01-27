import argparse
import json

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from constant import SCOPES, TYPES
from utils import add_permission, delete_permission,\
                  get_folder_id, read_json_into_memory


def create_files(drive_folder, students, type, homework_affix,
                 instructors, is_group):
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
            groud_folder_id = student['team']
            document_name = string_or_empty(homework_affix) + student['team']
            if is_group:
                folders = get_folder_id(service, groud_folder_id)
                folder_id = folders[0]['id']
                document_name += combine_lastnames(student['lastnames'])
        else:
            is_team = False
            student_name = student['lastname'] + " " + student['firstname']
            document_name = string_or_empty(homework_affix) + '_' + \
                student['lastname'] + '_' + student['firstname']

        # test if document exists for this student already
        check = service.files().list(
                    q="mimeType = 'application/vnd.google-apps."+type+"' and name='"+document_name+"'",
                    pageSize=1, fields="nextPageToken, files(id, name)").execute().get('files', [])
        if check:
            print(student_name, 'already has a file on drive for this assignment.')
            file_id = check[0]['id']
        else:
            file_metadata = {
                'name': document_name,
                'mimeType': TYPES[type] if type else TYPES['document'],
                'parents': [folder_id],
                "writersCanShare": False
            }

            student_shared_doc = service.files().create(body=file_metadata, fields='id').execute()
            file_id = student_shared_doc.get('id')

        print(student_name, file_id)
        student[string_or_empty(homework_affix) + ' drive id'] = file_id

        list_permissions = service.permissions().list(fileId=file_id).execute()
        permissions = list_permissions.get('permissions')

        for p in permissions:
            if p['role'] != 'owner':
                delete_permission(file_id, p['id'], service)

        if is_team:
            for member_ccid in student['ccids']:
                member_email = member_ccid + '@ualberta.ca'
                add_permission(member_email, file_id, service, 'writer')
        else:
            add_permission(student['email'], file_id, service, 'writer')

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


def add_permissions_to_intructors(instructors, file_id, service):
    """Adds writer permissions to the file for the instructional team.

    :param instructors: instructional team emails.
    :param file_id: id of the file.
    :param service: Google Drive service.
    """
    for i in instructors:
        add_permission(i['email'], file_id, service, 'writer')


def string_or_empty(string):
    """Returns a string preceded by an underscore or an empty string.
    Depending on whether the string parameter is none or not.

    :param string: string.
    :returns: a new string.
    """
    return string if string else ''


def parse_arg_list():
    """Uses argparse to parse the required parameters

    :returns: command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Creates and shares documents on Google Drive for students to write homework.\n\n' +
        'Needs:\n a JSON file with student names and email addresses,\n a homework affix, \n a folder name.\n '+
        'There must be a folder on the drive account named with the same name as the script\'s parameter.\n\n'+
        'Each document is named <student firstname>_<student lastname>_<homework affix> and stored \nin that folder.',
        formatter_class=argparse.RawTextHelpFormatter)
    requiredArgs = parser.add_argument_group('required arguments')
    requiredArgs.add_argument(
        '-s', '--students',
        help='JSON file with student firstnames, lastnames, and emails',
        required=True)
    requiredArgs.add_argument(
        '-a', '--affix',
        help='affix identifying assignment (e.g., cmputXXXfXX-hwZZ)',
        required=False)
    requiredArgs.add_argument(
        '-f', '--folder',
        help='folder in Google drive where files are created',
        required=True)
    requiredArgs.add_argument(
        '-t', '--type',
        help='type of artifact to be created (i.e., document, spreadsheet, or folder), document as default',
        required=False)
    requiredArgs.add_argument(
        '-i', '--instructors',
        help='JSON file with instructional team emails',
        required=False)
    requiredArgs.add_argument(
        '-g', '--group',
        help='boolean to indicate if the file should be inside a group folder',
        required=False)

    args = parser.parse_args()
    return args


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
