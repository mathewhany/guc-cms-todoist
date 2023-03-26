# GUC CMS Todoist
The first time you run the script it will store links for all contents uploaded to the CMS, and then whenever you rerun the script it will search for any newly uploaded items and list them and also add them as tasks on Todoist.


# Changelog
## 2.0
- Support for CMS Announcements 
- Courses are now added into different Todoist sections.
  - I recommend that you try to set Todoist to view your Uni project as a board. It is so much more organized this way.
- Configuration and courses are now saved in a JSON file instead of Pickle files. 
  - JSON files can be easily opened by any text editor and inspected. 
  - You can even change your login credientials or courses aliases directly in the file. 
  - You can view all courses data in the `courses.json` file.
- A label is now attached to added tasks whether the item is a lecture, assignment, lab manual and so on. This gives you more control on how you want to organize or filter tasks in Todoist. 


## 1.1
- Added course name aliasing.
  - Now you can give an alias for the courses so for example instead naming the course `Computer System Architecture` or `CSEN601`, the script now asks you if you want to alias it to a more readable name like `CA`. 

# Download & Installation
## Windows
1. [Download](https://github.com/mathewhany/guc-cms-todoist/suites/11817070514/artifacts/617041594)
2. Extract
3. Open `GUC-CMS-Todoist.exe`

## macOS
1. [Download](https://github.com/mathewhany/guc-cms-todoist/suites/11817070514/artifacts/617041592)
2. Extract
3. Right click on `GUC-CMS-Todoist` and choose open.
4. A dialog will appear telling you that the app is from an untrusted developer (CUZ Apple LOL), click Open to allow macOS to trust the app (later you can just click on the app normally and it will open)

# Resetting password
If you changed the password of your GUC account, you would have to delete `config.json` and run the script again. It will ask you for your password again.

# Resetting saved content
When you finish semester and move to the next semester, you might want to reset the courses information by deleting `courses.json` and running the script again.

__Note:__
_When you run the script for the first time, you will be asked for your GUC username and password, this information is only stored locally on your PC in a file called 'config.json'. Whenever you change your password, you will have to delete the 'config.json' file and rerun the script to add your new password._
