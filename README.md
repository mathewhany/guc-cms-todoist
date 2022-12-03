# GUC CMS Todoist
The first time you run the script it will store links for all contents uploaded to the CMS, and then whenever you rerun the script it will search for any newly uploaded items and list them and also add them as tasks on Todoist.

# Installation
    git clone https://github.com/mathewhany/guc-cms-todoist.git
    cd guc-cms-todoist
    pip install -r requirements.txt

# Usage
    python main.py

__Note:__
_When you run the script for the first time, you will be asked for your GUC username and password, this information is only stored locally on your PC in a file called 'config.pkl'. Whenever you change your password, you will have to delete the 'config.pkl' file and rerun the script to add your new password._
