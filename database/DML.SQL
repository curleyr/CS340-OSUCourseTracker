-- -----------------------------------------------------
-- MyOSUPlanner: Student Course Planner 
-- Team 88
-- Project Team:
--  April Wang
--  Bobby Curley
-- -----------------------------------------------------

-- -----------------------------------------------------
-- DATA MANIPULATION QUERIES
-- In all queries, a colon : character is used to 
-- denote the variables that will have data from the 
-- backend programming language
-- -----------------------------------------------------

  -- -----------------------------------------------------
  -- COURSES & PREREQUISITES PAGE
  -- This page combines data from the Courses Table and 
  -- Courses_has_Prerequisites table.
  -- Has ability to view all and also add new course
  -- -----------------------------------------------------

    -- SELECT all courses and prerequisites 
    -- Prerequisites concatenated into a comma separated string for display
    SELECT
      c.courseID,
      CONCAT(c.code, ' ', c.name) AS course,
      c.credit,  
      GROUP_CONCAT(CONCAT(pc.code, ' ', pc.name) ORDER BY pc.code SEPARATOR ', ') AS prerequisites 
    FROM Courses c
    LEFT JOIN Courses_has_Prerequisites p   
      ON c.courseID = p.courseID 
    LEFT JOIN Courses pc  
      ON p.prerequisiteID = pc.courseID 
    GROUP BY c.courseID 
    ORDER BY c.code ASC;

    -- INSERT new course
    -- First can insert course when form is submitted
    INSERT INTO Courses (code, name, credit)
    VALUES (:codeInput, :nameInput, :creditInput);

    -- Then can also insert prerequisite for each prerequisite checkbox submitted on form
    INSERT INTO Courses_has_Prerequisites (courseID, prerequisiteCourseID)
    VALUES ((SELECT courseID FROM Courses WHERE code = :codeInput), :prerequisiteCourseID_From_Checkbox_Input);

  -- ---------------------------------------------------------
  -- TERMS PAGE
  -- Has ability to view all and also add new term
  -- This page combines data from terms and Terms_has_courses
  -- ---------------------------------------------------------
    -- SELECT all terms
    SELECT 
      t.*, 
      GROUP_CONCAT(CONCAT(c.code, ' ', c.name) ORDER BY c.courseID ASC SEPARATOR ', ') AS courses
    FROM Terms t
    LEFT JOIN Terms_has_Courses thc ON t.termID = thc.termID
    LEFT JOIN Courses c ON thc.courseID = c.courseID
    GROUP BY t.termID
    ORDER BY t.startDate ASC;

    -- INSERT new term
    -- First need query to retrieve all courses to formulate courses checkboxes on form
    SELECT 
      CONCAT(code, ' ', name) AS course,
      courseID
    FROM Courses
    ORDER BY code ASC;

    -- Then can insert term when form is submitted  
    INSERT INTO Terms (name, startDate, endDate)
    VALUES (:nameInput, :startDate_From_Date_Input, :endDate_From_Date_Input);

    -- Then can insert into Terms_has_Courses for each course checkbox submitted on form
    INSERT INTO Terms_has_Courses (termID, courseID)
    VALUES ((SELECT termID FROM Terms WHERE name = :nameInput), :courseID_From_Checkbox_Input);

  -- -----------------------------------------------------
  -- STUDENT TERM PLANS
  -- This page combines data from the StudentTermPlans,
  -- Terms, and StudentTermPlans_has_Courses tables. 
  -- Has ability to view all and also add new plan
  -- -----------------------------------------------------
    -- SELECT all plans
    SELECT 
      stp.studentTermPlanID,
      stp.studentID, 
      CONCAT(s.firstName, ' ', s.lastName) AS studentName,
      t.name AS termName, 
      GROUP_CONCAT((SELECT CONCAT(code, ' ', name) FROM Courses WHERE courseID = stpc.courseID) ORDER BY stpc.courseID ASC SEPARATOR ', ') AS courses,
      CASE WHEN stp.advisorApproved = 1 THEN 'Yes' ELSE 'No' End AS advisorApproved
    FROM StudentTermPlans stp
    INNER JOIN Terms t ON stp.termID = t.termID
	  INNER JOIN Students s ON s.studentID = stp.studentID
    INNER JOIN StudentTermPlans_has_Courses stpc ON stp.studentTermPlanID = stpc.studentTermPlanID
    GROUP BY stp.studentTermPlanID
    ORDER BY stp.studentTermPlanID ASC

    -- INSERT new plan
    -- First need query to retrieve all students to use in dropdown on form
    SELECT 
      CONCAT(lastName, ', ', firstName, ' - ', studentID) AS student,
      studentID
    FROM Students
    ORDER BY lastName ASC;

    -- Then need query to retrieve all terms to use in dropdown on form
    SELECT 
      name, 
      termID
    FROM Terms
    ORDER BY startDate ASC;
      
    -- Then need query to retrieve all courses to formulate courses checkboxes on form
    SELECT 
      CONCAT(code, ' ', name) AS course,
      courseID
    FROM Courses
    ORDER BY code ASC;

    -- Then can insert plan once form is submitted
    INSERT INTO StudentTermPlans (studentID, termID, advisorApproved)
    VALUES (:studentID_From_Dropdown_Input, :termID_From_Dropdown_Input, :advisorApproved_From_Radio_Input);

    -- Then can insert into StudentTermPlans_has_Courses for each course checkbox submitted on form
    INSERT INTO StudentTermPlans_has_Courses (studentTermPlanID, courseID)
    VALUES ((SELECT studentTermPlanID FROM StudentTermPlans WHERE studentID = :studentID_From_Dropdown_Input AND termID = :termID_From_Dropdown_Input), :courseID_From_Checkbox_Input);

    -- For Updating row of StudentTermPlans_has_Courses (courseID can be updated to NULL)
    UPDATE  StudentTermPlans_has_Courses
    SET courseID = :courseID_from_Dropdown_input
    WHERE studentTermPlanCourseID = (SELECT studentTermPlanCourseID FROM StudentTermPlans_has_Courses WHERE studentTermPlanID = :studentID_From_Dropdown_Input AND courseID = :courseID_From_Checkbox_Input)

    -- For Deleting row of StudentTermPlans_has_Courses
    DELETE FROM StudentTermPlans_has_Courses
    WHERE studentTermPlanCourseID = :studentTermPlanCourseID_passed_into_delete_component;

  -- -----------------------------------------------------
  -- STUDENTS
  -- Has ability to view all, add a student, and also delete or update
  -- -----------------------------------------------------
    -- SELECT all students
    SELECT *
    FROM Students
    ORDER BY lastName ASC;

    -- INSERT new student
    INSERT INTO Students (studentID, firstName, lastName)
    VALUES (:studentID_From_Input, :firstName_From_Input, :lastName_From_Input);

    -- DELETE student
    DELETE FROM Students
    WHERE studentID = :studentID_From_Input;

    -- UPDATE student
    UPDATE Students
    SET firstName = :firstName_From_Input, lastName = :lastName_From_Input
    WHERE studentID = :studentID_From_Input;