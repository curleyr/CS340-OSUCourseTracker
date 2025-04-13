# CS340-OSUCourseTracker
- OSUCourseTracker is a web-based application designed for Oregon State University (OSU) to help track and manage student course plans across multiple terms, or semesters. Driven by a relational database backend, this application tracks courses students plan to take during specific terms, while ensuring each student course plan meets both course prerequisite requirements and course availability.
- The current MyDegrees Planner tool offered via BeaverHub does not check prerequisites or course offering conditions, which means advisors need to manually check for conflicts whenever plans are updated.
- Our goal is to not only help efficiently track students’ course roadmap, but also alleviate the review process for advisors, as the tool will enforce both prerequisite requirements and course availability conditions.

## Course Project Details
- Project idea developed and created collaboratively by a team of two students (April Wang and Bobby Curley) for CS340 - Introduction to Databases at OSU during Fall 2025 quarter (September through December 2025)
- Project Requirements:
    - Database should have at least 4 entities and at least 4 relationships, one of which must be a many-to-many relationship.
    - Primary user is the administrator of the database
- Functionality requirements:
    - It should be possible to INSERT entries into every table individually.
    - Every table should be used in at least one SELECT query.
    - CRUD needs to be implemented for at least one entity and one intersection table.
        - Deleting from a M:M relationship shouldn't create data anomalies in related tables.
    - Website needs to dynamically populate drop-downs/inputs rather than manually entering foreign key IDs
    - One relationship must be NULLable using UPDATE to remove the relationship
## Database Schema
![schema](https://github.com/user-attachments/assets/5b640c39-7e74-49a2-adf2-5c8c3af98cf4)

## UI Screenshots
- Pages are dynamically generated based on the database contents
- Dropdown, input, checkbox, and radio button values are dynamically generated based on database contents
- The screenshots below are non-exhaustive and do not show every UI or form.
### Courses & Courses_has_Prerequisites
![READ Courses](https://github.com/user-attachments/assets/e2d498ae-aec6-45c3-85d5-7f9c4bc1d742)
![CREATE Courses](https://github.com/user-attachments/assets/d7ad4386-935a-4f90-9ed7-636f190a6424)
### Terms & Terms_has_Courses
![READ Terms](https://github.com/user-attachments/assets/87550fe0-e6c4-452d-9136-866cd7fce3d7)
![CREAT Terms](https://github.com/user-attachments/assets/1f36e4da-8f7c-4c32-9f4b-d17920517af9)
#### CREATE Terms_has_Courses
![CREATE Terms has courses](https://github.com/user-attachments/assets/bfe8d2ea-801a-4b4a-86e3-971e6d59f077)
### StudentTermPlans & StudentTermPlans_has_Courses
![READ Student Term Plans](https://github.com/user-attachments/assets/f5b46e60-3115-4a2e-8235-ea7183d0bac2)
![CREATE Student Term Plans](https://github.com/user-attachments/assets/bb6c90da-a41a-42a0-a96b-13e3ea2f4cec)
#### CREATE/UPDATE/DELETE StudentTermPlans_has_Courses
- Note, this updates and deletes a many to many relationship

![CUD Studenttermplans has courses](https://github.com/user-attachments/assets/ada40730-02f3-47c9-9019-d282faf22355)
### Students
![READ Students](https://github.com/user-attachments/assets/26ebdbd7-cf99-4be6-8307-471d64cbd7c2)

# Local Dev Environment Setup Instructions
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
## For creator of PR aka person making changes
1. For creating branch
    - Select current branch aka source branch
        ```sh
        git checkout SourceName
        ```
    - Create Personal Branch off of current branch aka source branch (replace "BranchName" placeholder):
        ```sh
        git checkout -b BranchName
        ```
2. Code
    - If you need to pull in changes from source branch (either main or another feature branch)
    (Replace SourceName placeholder (e.g. main or feat/terms))
        ```sh
        git checkout SourceName
        git pull
        git checkout BranchName
        git merge SourceName
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
        In CLI, this will print a message saying "Create a pull request for [...]" and provide a link. Command + Click that link to automatically generate pull request.
    - For subsequent pushes:
        ```sh
        git push
        ```
5. Create Pull Request in Github website (by command clicking the link described in step 4):
    - Verify base that you want to merge into is correct
    - Add title and description if appropriate
    - Request reviewer on the right hand side
    - Click Create Pull Request
6. If at the top of the PR, it does not say "Able to merge" in green with a check mark:
    - Do step 2

## FOR REVIEWER OF PR:
1. Open Pull request in github website
2. Go to "Files Changed" tab
3. Review code, click on line number to leave comment (you can click and drag to select multiple lines)
4. Submit review comments
5. Communicate with teammate
