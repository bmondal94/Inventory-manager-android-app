import json
update_settings = json.dumps([
    {
        "type": "string",
        "title": "Image path",
        "desc": "Folder path where all the images will be saved",
        "section": "General",
        "key": "image_save_path"
    },
    {
        "type": "string",
        "title": "Database path",
        "desc": "Folder path where all the databases will be saved",
        "section": "General",
        "key": "database_save_path"
    },
    {
        "type": "string",
        "title": "Documents path",
        "desc": "Folder path where all the documents (e.g. checkout slip) will be saved",
        "section": "General",
        "key": "document_save_path",
    }
])
