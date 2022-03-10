import requests
import json
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

#authenticate Google
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


def download_file(file_link, file_name):
    """
    Downloads a file from a link.
    
    Args:
        file_link: A string representing the link to the file.
        file_name: A string representing the name of the file.
        
    Returns:
        file_path: A string representing a path to the downloaded file.
    """
    
    r = requests.get(file_link, allow_redirects=True)
    file_path = "downloads/" + file_name + f".pdf"
    open(file_path, 'wb').write(r.content)
    
    return file_path


def upload_file(file_name, file_path, folder_id):
    """
    Uploads a file to google shared drive folder.
    
    Args:
        file_name: A string representing the name of the file.
        file_path: A string representing a path to the file.
        folder_id: A string representing the ID of the folder the file is to be uploaded to.
        
    Returns:
        _: None
    """
    
    mime_types = {'docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'pdf':'application/pdf'}
    #print(file_path.spit('.')[1])
    mime_type = mime_types[file_path.split('.')[1]]
    
    file = drive.CreateFile({
        'title': file_name,
        'mimeType': mime_type,
        'parents': [{
            'kind': 'drive',
            'teamDriveId': '0ALGjY-PCeStEUk9PVA',
            'id': folder_id
        }]
    })
    
    file.SetContentFile(file_path)
    
    file.Upload(param={'supportsTeamDrives': True})
    
    return


def delete_local_file(file_path):
    """
    Deletes local file if it exists.
    
    Args:
        file_path: A string representing a path to the file.
    
    Returns:
        _: A boolean indicating if a file existed or not.
    """
    
    #delete local file
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def upload_to_gdrive(file_link, file_name, folder_id):
    """
    Uploads a file to google drive directly from a link.
    
    Args:
        file_link: A string representing the link to the file.
        file_name: A string representing the name of the file.
        folder_id: A string representing the ID of the folder the file is to be uploaded to.
        
    Returns:
        _: A boolean indicating if the file upload was a success or not.
    """
    
    if not file_link:
        return False
    file_path = download_file(file_link, file_name)
    if not file_path:
        return False
    upload_file(file_name, file_path, folder_id)
    if delete_local_file(file_path):
        return True
    return False


def list_files(folder_id):
    '''
    list all files in a google folder
    
    Args:
        folder_id: the google id of the parent folder
    
    Returns:
        file_list: a list of files in the parent folder
    '''
    
    file_list = drive.ListFile(
        {
            'q': "'{}' in parents and trashed=false".format(folder_id),
            'corpora': "teamDrive",
            'teamDriveId': "0AL2boqVPcgjKUk9PVA",
            'includeTeamDriveItems': "true",
            'supportsTeamDrives': "true"
        }
    ).GetList()
    return file_list


def create_folder(parent_folder_id, folder_name, email=''):
    '''
    create folder if it does not exist
    
    Args:
        parent_folder_id: the google id of the parent folder
        folder_name: the name of the folder created
    
    Returns:
        folder_id: the google id if the created folder
    '''

    file_list = list_files(parent_folder_id)
    folder_id = ''
    for folder in file_list:
        if folder['title'] == folder_name:
            return folder['id']
    if not folder_id:
        folder = drive.CreateFile({'parents': [{'id': parent_folder_id}], 'title': folder_name,
                                   'mimeType': 'application/vnd.google-apps.folder'})
        folder.Upload(param={'supportsTeamDrives': True})
        
        if email:
            share_folder(folder, email)

        return folder['id']
    return False


def share_folder(folder, email):
    '''
    Gives editor access to a google drive file or folder.
    
    Args:
        folder: a google drive folder or file object.
        email: an email address to share google file or folders with.
        
    Returns:
        _: NA.
    '''
    
    new_permission = {
        'type': 'user',
        'value': email,
        'role': 'writer'
    }
    permission = folder.auth.service.permissions().insert(
        fileId=folder['id'], body=new_permission, supportsTeamDrives=True).execute(http=folder.http)
        