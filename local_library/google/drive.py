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
    file_path = "../downloads_folder/" + file_name + f".pdf"
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
    
    file = drive.CreateFile({
        'title': file_name,
        'mimeType': 'application/pdf',
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
