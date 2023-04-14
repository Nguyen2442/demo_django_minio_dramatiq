from core.database.minio import minio_client

async def get_url_from_minio(data):
    file_name = data.name
    folder_type = data.type
    
    if folder_type == 'excel':
        file_name = f'{data.name}.xlsx'
    
    elif folder_type == 'mp3':
        file_name = f'{data.name}.mp3'
    
    elif folder_type == 'video':
        file_name = f'{data.name}.mp4'
    
    elif folder_type == 'images':
        file_name = f'{data.name}.jpg'
    
    url_file = minio_client.get_url_object(folder_type, file_name)
    if url_file:
        return url_file
    return False