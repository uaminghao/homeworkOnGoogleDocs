from googleapiclient import errors


def get_folder_id(service, drive_folder):
    """Retrieve folder id from Google Drive.
    :param service: Google Drive service.
    :param drive_folder: folder name.
    :returns: a list of folders that match the param name.
    """
    results = service.files().list(
        q="mimeType = 'application/vnd.google-apps.folder' and name='"+drive_folder+"'",
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('Could not find folder named: "' + drive_folder + '"')
        exit(0)
    return items


def delete_permission(file_id, permission_id, service):
    """Removes a permission from the file.

    :param file_id: id of the file.
    :param permission_id: id of the permission being removed.
    :param service: Google Drive service.
    """
    try:
        service.permissions().delete(
            fileId=file_id, permissionId=permission_id).execute()
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


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
        service.permissions().create(
            fileId=file_id, body=new_permission,
            sendNotificationEmail=False).execute()
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def read_json_into_memory(filename):
    """Uses argparse to parse the required parameters

    :returns: command line arguments.
    """
    with open(filename, 'r') as f:
        values = json.load(f)
        f.close()
    return values