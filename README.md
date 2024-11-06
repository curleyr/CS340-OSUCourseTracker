# CS340-OSUCourseTracker

## Clone Repo
- Navigate to directory on computer where you want the repo
- In terminal enter the following
```bash
git clone https://github.com/curleyr/CS340-OSUCourseTracker
```

## Set Up And Run Virtual Environment
- In terminal enter the following
```bash
python3 -m venv ./venv
source venv/bin/activate
```

## Create .env File
- Create .env file at root or your project directory and populate with the following
```python
mysql_host = "classmysql.engr.oregonstate.edu"
mysql_user = "cs340_[ONID]"  
mysql_password = "[password]"  
mysql_database = "cs340_[ONID]"
```

## Update .gitignore File
- Open the .gitignore file and add
```
.env
venv
```

### Install Packages from requirements.txt
- In terminal enter the following
```bash
pip3 install -r requirements.txt
```

### Ensure Data Is In Your MySQL Database
- Navigate to DDL.SQL file in database directory and follow instructions there

### Running Program
- In terminal enter the following, replacing port# with a number (e.g. 8000)
```bash
gunicorn --name OSUCourseTracker -b 0.0.0.0:port# -D app:app
```
- Once gunicorn is running, you can navigate to http://classwork.engr.oregonstate.edu:port#/ to see the website running
- Note: providing a name (e.g. OSUCourseTracker) provides for an easier time when you want to stop the program
- To stop the program enter the following
```bash
pkill -f 'gunicorn --name OSUCourseTracker'
```

# Git Team Workflow
1. Create Personal Branch off of current branch aka source branch (replace "BranchName" placeholder):
    ```sh
    git checkout -b BranchName
    ```
2. Code
    - If you need to pull in changes from source branch (either main or another feature branch)
    (Replace SourceBranch placeholder (e.g. main or feat/terms))
        ```sh
        git checkout SourceBranch
        git pull
        git checkout BranchName
        git merge SourceBranch
        ```
3. Commit changes using
    ```sh
    git add .
    git commit -m "change message"
    ```
4. Push changes to remote repository
    - (FOR FIRST TIME ON BRANCH) Push your local branch to remote repository 
        ```sh
        git push -u origin BranchName
        ```
    - For subsequent pushes:
        ```sh
        git push
        ```
5. Create Pull Request in Github website:
- 