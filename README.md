# GUC CMS Todoist
The first time you run the script it will store links for all contents uploaded to the CMS, and then whenever you rerun the script it will search for any newly uploaded items and list them and also add them as tasks on Todoist.

# Installation
First make sure you have Python 3.11 installed on your PC and that you included Python in the PATH environment variable. Then you just need to clone and the repo and install required packages by just following these commands.

    git clone https://github.com/mathewhany/guc-cms-todoist.git
    cd guc-cms-todoist
    pip install -r requirements.txt

# Usage
Just run the `cms-notify.bat` file. Or even better, just create a desktop shortcut for it, and whenever you want to check any changes to the CMS, just open that desktop shortcut. 

# Resetting password
If you changed the password of your GUC account, you would have to delete `config.pkl` and run the script again. It will ask you for your password again.

# Resetting saved content
When you finish semester and move to the next semester, you might want to reset the courses information by deleting `courses.pkl` and running the script again.

__Note:__
_When you run the script for the first time, you will be asked for your GUC username and password, this information is only stored locally on your PC in a file called 'config.pkl'. Whenever you change your password, you will have to delete the 'config.pkl' file and rerun the script to add your new password._
