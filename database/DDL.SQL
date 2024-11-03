-- -----------------------------------------------------
-- MyOSUPlanner: Student Course Planner 
-- Team 88
-- Project Team:
--  April Wang
--  Bobby Curley
-- -----------------------------------------------------

-- -----------------------------------------------------
-- STEPS TO RUN FILE:
--  1. Save this file to directory 
--  2. Open terminal in that directory
--  3. Type following commands:
--      mysql -u cs340_[ONID] -h classmysql.engr.oregonstate.edu -p
--      * enter password when prompted *
--      use cs340_[ONID];
--      source DDL.SQL;
-- -----------------------------------------------------

-- Disable Foreign Key checks and automatic commits. These are set back at the end of the file.
SET FOREIGN_KEY_CHECKS=0;
SET AUTOCOMMIT = 0;

-- -----------------------------------------------------
-- Create 'Courses' Entity Table
-- -----------------------------------------------------
CREATE OR REPLACE TABLE Courses (
  courseID INT NOT NULL AUTO_INCREMENT,
  code VARCHAR(15) UNIQUE NOT NULL,
  name VARCHAR(45) NOT NULL,
  credit INT NOT NULL,
  PRIMARY KEY (courseID)
);

-- -----------------------------------------------------
-- Insert Data Into 'Courses' Entity Table
-- -----------------------------------------------------
INSERT INTO Courses (
  code, 
  name, 
  credit
)
VALUES
  ('CS161', 'INTRODUCTION TO COMPUTER SCIENCE I', 4),
  ('CS162', 'INTRODUCTION TO COMPUTER SCIENCE II', 4),
  ('CS225', 'DISCRETE STRUCTURES IN COMPUTER SCIENCE', 4), 
  ('CS261', 'DATA STRUCTURES', 4), 
  ('CS271', 'COMPUTER ARCHITECTURE AND ASSEMBLY LANGUAGE', 4),
  ('CS166', 'INTRODUCTION TO JAVA (Proposed)', 4);

-- -----------------------------------------------------
-- Create 'Terms' Entity Table
-- -----------------------------------------------------
CREATE OR REPLACE TABLE Terms (
  termID INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(15) UNIQUE NOT NULL,
  startDate DATE NOT NULL,
  endDate DATE NOT NULL,
  PRIMARY KEY (termID)
);

-- -----------------------------------------------------
-- Insert Data Into 'Terms' Entity Table
-- -----------------------------------------------------
INSERT INTO Terms (
  name,
  startDate,
  endDate
)
VALUES
  ('Winter 2024', '2024-01-08', '2024-03-22'),
  ('Spring 2024', '2024-04-01', '2024-06-14'),
  ('Summer 2024', '2024-06-24', '2024-09-06'),
  ('Fall 2024', '2024-09-25', '2024-12-13');

-- -----------------------------------------------------
-- Create 'Students' Entity Table
-- -----------------------------------------------------
CREATE OR REPLACE TABLE Students (
  studentID VARCHAR(9) NOT NULL,
  firstName VARCHAR(45) NOT NULL,
  lastName VARCHAR(45) NOT NULL,
  PRIMARY KEY (studentID)
);

-- -----------------------------------------------------
-- Insert Data Into 'Students' Entity Table
-- -----------------------------------------------------
INSERT INTO Students (
  studentID, 
  firstName,
  lastName
)
VALUES
  ('000000001', 'April', 'Wang'),
  ('000000002', 'Bobby', 'Curley'),
  ('000000003', 'Jane', 'Doe');

-- -----------------------------------------------------
-- Create 'StudentTermPlans' Entity Table
-- -----------------------------------------------------
CREATE OR REPLACE TABLE StudentTermPlans (
  studentTermPlanID INT NOT NULL AUTO_INCREMENT,
  studentID VARCHAR(9) NOT NULL,
  termID INT NOT NULL,
  advisorApproved TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (studentTermPlanID),
  UNIQUE (studentID, termID),
  FOREIGN KEY (studentID) REFERENCES Students (studentID) ON DELETE CASCADE,
  FOREIGN KEY (termID) REFERENCES Terms (termID) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Insert Data Into 'StudentTermPlans' Entity Table
-- -----------------------------------------------------
INSERT INTO StudentTermPlans (
  studentID,
  termID,
  advisorApproved
)
VALUES
  ('000000001', (SELECT termID FROM Terms WHERE name='Winter 2024'), 1),
  ('000000001', (SELECT termID FROM Terms WHERE name='Spring 2024'), 1),
  ('000000002', (SELECT termID FROM Terms WHERE name='Spring 2024'), 1),
  ('000000001', (SELECT termID FROM Terms WHERE name='Summer 2024'), 0),
  ('000000002', (SELECT termID FROM Terms WHERE name='Summer 2024'), 0);

-- -----------------------------------------------------
-- Create 'Prerequisites' Linking Table
-- -----------------------------------------------------
CREATE OR REPLACE TABLE Prerequisites (
  courseID INT NOT NULL,
  prerequisiteCourseID INT NOT NULL,
  PRIMARY KEY (courseID, prerequisiteCourseID),
  FOREIGN KEY (courseID) REFERENCES Courses (courseID) ON DELETE CASCADE,
  FOREIGN KEY (prerequisiteCourseID) REFERENCES Courses (courseID) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Insert Data Into 'Prerequisites' Linking Table
-- -----------------------------------------------------
INSERT INTO Prerequisites (
  courseID,
  prerequisiteCourseID
)
VALUES
  ((SELECT courseID FROM Courses WHERE code='CS162'), (SELECT courseID FROM Courses WHERE code='CS161')),
  ((SELECT courseID FROM Courses WHERE code='CS261'), (SELECT courseID FROM Courses WHERE code='CS162')),
  ((SELECT courseID FROM Courses WHERE code='CS261'), (SELECT courseID FROM Courses WHERE code='CS225')),
  ((SELECT courseID FROM Courses WHERE code='CS271'), (SELECT courseID FROM Courses WHERE code='CS161'));

-- -----------------------------------------------------
-- Create 'StudentTermPlans_has_Courses' Linking Table
-- -----------------------------------------------------
CREATE OR REPLACE TABLE StudentTermPlans_has_Courses (
  studentTermPlanID INT NOT NULL,
  courseID INT NOT NULL,
  PRIMARY KEY (studentTermPlanID, courseID),
  FOREIGN KEY (studentTermPlanID) REFERENCES StudentTermPlans (studentTermPlanID) ON DELETE CASCADE,
  FOREIGN KEY (courseID) REFERENCES Courses (courseID) ON DELETE CASCADE
);

-- ---------------------------------------------------------------
-- Insert Data Into 'StudentTermPlans_has_Courses' Linking Table
-- ---------------------------------------------------------------
INSERT INTO StudentTermPlans_has_Courses (
  studentTermPlanID,
  courseID
)
VALUES
  ((SELECT studentTermPlanID FROM StudentTermPlans WHERE studentID='000000001' AND termID=(SELECT termID FROM Terms WHERE name='Winter 2024')), (SELECT courseID FROM Courses WHERE code='CS161')),
  ((SELECT studentTermPlanID FROM StudentTermPlans WHERE studentID='000000001' AND termID=(SELECT termID FROM Terms WHERE name='Spring 2024')), (SELECT courseID FROM Courses WHERE code='CS162')),
  ((SELECT studentTermPlanID FROM StudentTermPlans WHERE studentID='000000001' AND termID=(SELECT termID FROM Terms WHERE name='Spring 2024')), (SELECT courseID FROM Courses WHERE code='CS225')),
  ((SELECT studentTermPlanID FROM StudentTermPlans WHERE studentID='000000002' AND termID=(SELECT termID FROM Terms WHERE name='Spring 2024')), (SELECT courseID FROM Courses WHERE code='CS161')),
  ((SELECT studentTermPlanID FROM StudentTermPlans WHERE studentID='000000001' AND termID=(SELECT termID FROM Terms WHERE name='Summer 2024')), (SELECT courseID FROM Courses WHERE code='CS261')),
  ((SELECT studentTermPlanID FROM StudentTermPlans WHERE studentID='000000002' AND termID=(SELECT termID FROM Terms WHERE name='Summer 2024')), (SELECT courseID FROM Courses WHERE code='CS162'));

-- -----------------------------------------------------
-- Create 'Terms_has_Courses' Linking Table
-- -----------------------------------------------------
CREATE OR REPLACE TABLE Terms_has_Courses (
  termID INT NOT NULL,
  courseID INT NOT NULL,
  PRIMARY KEY (termID, courseID),
  FOREIGN KEY (termID) REFERENCES Terms (termID) ON DELETE CASCADE,
  FOREIGN KEY (courseID) REFERENCES Courses (courseID) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Insert Data Into 'Terms_has_Courses' Linking Table
-- -----------------------------------------------------
INSERT INTO Terms_has_Courses (
  termID,
  courseID
)
VALUES
  ((SELECT termID FROM Terms WHERE name='Winter 2024'), (SELECT courseID FROM Courses WHERE code='CS161')),
  ((SELECT termID FROM Terms WHERE name='Spring 2024'), (SELECT courseID FROM Courses WHERE code='CS161')),
  ((SELECT termID FROM Terms WHERE name='Summer 2024'), (SELECT courseID FROM Courses WHERE code='CS161')),
  ((SELECT termID FROM Terms WHERE name='Fall 2024'), (SELECT courseID FROM Courses WHERE code='CS161')),
  ((SELECT termID FROM Terms WHERE name='Winter 2024'), (SELECT courseID FROM Courses WHERE code='CS162')),
  ((SELECT termID FROM Terms WHERE name='Spring 2024'), (SELECT courseID FROM Courses WHERE code='CS162')),
  ((SELECT termID FROM Terms WHERE name='Summer 2024'), (SELECT courseID FROM Courses WHERE code='CS162')),
  ((SELECT termID FROM Terms WHERE name='Fall 2024'), (SELECT courseID FROM Courses WHERE code='CS162')),
  ((SELECT termID FROM Terms WHERE name='Winter 2024'), (SELECT courseID FROM Courses WHERE code='CS225')),
  ((SELECT termID FROM Terms WHERE name='Spring 2024'), (SELECT courseID FROM Courses WHERE code='CS225')),
  ((SELECT termID FROM Terms WHERE name='Summer 2024'), (SELECT courseID FROM Courses WHERE code='CS225')),
  ((SELECT termID FROM Terms WHERE name='Fall 2024'), (SELECT courseID FROM Courses WHERE code='CS225'));

-- Re-enable Foreign Key checks and commit file to database.
SET FOREIGN_KEY_CHECKS=1;
COMMIT;