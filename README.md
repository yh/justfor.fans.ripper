# Script to download all content from someone's JustFor.Fans

![](https://img.shields.io/badge/written%20with%20-python%203.8-gray?logo=python&logoColor=ffd143&labelColor=386e9e)
![](https://img.shields.io/badge/-but-brightgreen)
![](https://img.shields.io/badge/works%20with%20-python%203.11-gray?logo=python&logoColor=ffd143&labelColor=386e9e)

![](https://img.shields.io/github/languages/code-size/VeryEvilHumna/justfor.fans.ripper)
![](https://img.shields.io/github/license/VeryEvilHumna/justfor.fans.ripper)
![](https://img.shields.io/badge/Beautiful-SOUP%204-brightgreen)
## !!! VIDEO DOWNLOADER IS BROKEN

VIDEO SAVING IS BROKEN FOR NOW, JFF STORE MOST NEW VIDEOS IN HLS FORMAT, WHICH IS NOT SUPPORTED BY THIS SCRIPT. (TODO) (maybe)

Photos are fine 
## Usage

0. (optional) Create and activate a Python virtual environment:
     ```
    python -m venv venv
    venv\Scripts\activate
    ```
1. Install requirements: `pip install -r requirements.txt`
2. Set configuration
    1. `overwrite_existing` - will skip download if file exists
    2. `save_path` - destination folder - will save to same location as script folder if none provided
    3. `save_full_text` - will save text file with full description
    4. `file_name_format` - filename format, following values are available:
        * `name`
        * `post_date`
        * `post_id`
        * `desc`
   
3. Get UserID and UserHash values
    1.  Log into your JustFor.Fans account
    2.  Select performer's page
    3.  (in Chrome), hit F12 to open dev-console
    4.  Refresh page to view network activity
    5.  Locate `getPost.php` call, extract `UserID` and `UserHash4` values (in yellow)
    
    ![image](https://user-images.githubusercontent.com/12958294/115130004-859a5580-9fa0-11eb-9275-235d4ec51967.png)

    
    6.  Pass in as params when running script
        * `python app.py [UserID] [UserHash]`
        
        or
        specify uid and hsh in config.py

        ```
        # Authentication details
        uid = ""
        hsh = ""
        ```

## Contributors

This repo is a **fork** of the [edwardsdean's fix](https://github.com/edwardsdean/justfor.fans.ripper), which is fork of a [whats-happening-rightnow/justfor.fans.ripper](https://github.com/whats-happening-rightnow/justfor.fans.ripper), both repos are no longer updated
