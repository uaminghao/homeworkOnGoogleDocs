from googleapiclient.discovery import build
from urllib.error import HTTPError
from oauth2client import file
from google_auth_oauthlib.flow import InstalledAppFlow

import argparse
import json


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'

def main(driveFolder, students, homeworkAffix):
    flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    service = build('drive', 'v3', credentials=creds)
    # look for a directory on the drive with the homework name (e.g., "cmput391 f18 homework 1")
    results = service.files().list(q="mimeType = 'application/vnd.google-apps.folder' and name='"+driveFolder+"'",
                                   pageSize=10, fields="nextPageToken, files(id, name)").execute()

    items = results.get('files', [])
    if not items:
        print('Could not find folder named: "' + driveFolder+'"')
        exit(0)
    else:
        folder_id = None

        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))
            folder_id = item['id']
            print('Found folder with Drive id: '+folder_id)

        for student in students:
            documentName =  student['prename'] + '_' + student['surname'] + '_' + homeworkAffix

            # test if document exists for this student already
            check = service.files().list(q="mimeType = 'application/vnd.google-apps.document' and name='"+documentName+"'",
                                         pageSize=1, fields="nextPageToken, files(id, name)").execute().get('files', [])

            if check:
                print(student['prename'] + " " + student['surname'] +' already has a file on drive for this assignment.')
                continue

            file_metadata = {
               'name': documentName,
               'mimeType' : 'application/vnd.google-apps.document',
               'parents': [folder_id],
               "writersCanShare": False
            }

            studentSharedDoc = service.files().create(body=file_metadata, fields='id').execute()
            file_id = studentSharedDoc.get('id')

            print(student['name'] + " " + file_id)
            student[homeworkPrefix + ' drive id'] = file_id

            new_permission = {
                'emailAddress': student['email'],
                'type': 'user',
                'role': 'writer'
            }
            try:
                service.permissions().create(fileId=file_id, body=new_permission).execute()
            except HttpError as error:
                print ('An error occurred: %s' % error)

'''

Uses argparse to parse the required parameters

'''
def parseArglist():
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='Creates and shares documents on Google Drive for students to write homework.\n\n' +
        'Needs:\n a JSON file with student names and email addresses,\n a homework affix, \n a folder name.\n '+
        'There must be a folder on the drive account named with the same name as the script\'s parameter.\n\n'+
        'Each document is named <student prename>_<student surname>_<homework affix> and stored \nin that folder.',
        formatter_class=RawTextHelpFormatter)
    requiredArgs = parser.add_argument_group('required arguments')
    requiredArgs.add_argument('-s', '--students', help='JSON file with student names and emails', required=True)
    requiredArgs.add_argument('-a', '--affix', help='affix identifying assignment (e.g., cmputXXXfXX-hwZZ)', required=False)
    requiredArgs.add_argument('-f', '--folder', help='folder in Google drive where files are created', required=True)

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

    main(args.folder, students, args.affix)

    # write back with the drive ids for the documents.
    with open(args.students, 'w') as f:
        json.dump(students, f)
        f.close()


