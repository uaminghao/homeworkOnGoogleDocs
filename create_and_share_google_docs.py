from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import argparse
import json


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'

def main(token_file, students, coursePrefix, homeworkName):
    store = file.Storage(token_file)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))

    drive_folder = coursePrefix + " " + homeworkName

    # look for a directory on the drive with the homework name (e.g., "cmput391 f18 homework 1")
    results = service.files().list(q="mimeType = 'application/vnd.google-apps.folder' and name='"+drive_folder+"'",
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('Could not find folder named: "' + drive_folder+'"')
        exit(0)
    else:
        folder_id = None
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))
            folder_id = item['id']
            print('Found folder with Drive id: '+folder_id)

        for student in students:
            document_name = coursePrefix + ' ' + homeworkName + ' ' + student['name'] + ' (' + student['id']+')'

            # test if document exists for this student already
            check = service.files().list(q="mimeType = 'application/vnd.google-apps.document' and name='"+document_name+"'",
        pageSize=1, fields="nextPageToken, files(id, name)").execute().get('files', [])

            if check:
                print(student['name'] +' already has a file on drive for this assignment.')
                continue

            file_metadata = {
               'name': document_name,
               'mimeType' : 'application/vnd.google-apps.document',
               'parents': [folder_id],
               "writersCanShare": False
            }

            studentSharedDoc = service.files().create(body=file_metadata, fields='id').execute()
            file_id = studentSharedDoc.get('id')

            print(student['name'] + " " + file_id)
            student[homeworkName + ' drive id'] = file_id

            new_permission = {
                'emailAddress': student['email'],
                'type': 'user',
                'role': 'writer'
            }
            try:
                service.permissions().create(fileId=file_id, body=new_permission).execute()
            except errors.HttpError, error:
                print ('An error occurred: %s' % error)

'''

Uses argparse to parse the required outputs

'''
def parseArglist():
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='Creates and shares document on Google Drive for students to write homework.\n\n' +
        'Needs:\n a JSON \'token file\' generated when you authenticate the first time you run this program\n '+
        'a JSON file with student names and email addresses,\n a course prefix and\n a homework name.\n\n'+
        'There must be a folder on the drive account named <prefix>+\' \'+<homework>.\n\n'+
        'Each document is named <prefix>+\' \'+<homework>+\' \'+<student name> and stored \nin that folder.',
        formatter_class=RawTextHelpFormatter)
    requiredArgs = parser.add_argument_group('required arguments')
    requiredArgs.add_argument('-t', '--token', help='JSON file with token after web authentication', required=True)
    requiredArgs.add_argument('-s', '--students', help='JSON file with student names and emails', required=True)
    requiredArgs.add_argument('-c', '--course', help='course prefix (e.g., cmputXXXfXX)', required=True)
    requiredArgs.add_argument('-hw', '--homework', help='homework name', required=True)

    args = parser.parse_args()
    return args


'''

Main()


'''
if __name__ == '__main__':
    args = parseArglist()

    # read the student file into memory
    with open(args.students, 'r') as f:
        students = json.load(f)
        f.close()

    main(args.token, students, args.course, args.homework)

    # write back with the drive ids for the documents.
    with open(args.students, 'w') as f:
        json.dump(students, f)
        f.close()


