// //////// //
// FUNCTION //
// //////// //
// Handle toggling page from viewing terms to adding a term and back
function toggleTermForm(section_to_display, reload = false) {
    if (reload) {
        location.reload()
        return
    }

    const sections = [
        "view_terms_section",
        "add_term_section",
        "edit_term_courses_section"
    ]

    for (const section of sections) {
        if (section === section_to_display) {
            document.getElementById(section).style.display = "block"
        } else {
            document.getElementById(section).style.display = "none"
        }
    }
}

// //////// //
// FUNCTION //
// //////// //
// Handle add new term form submission
async function addTerm(event) {
    // Prevent page from refreshing
    event.preventDefault();

    // Instantiate FormData object
    const formData = new FormData(event.target);
    // Initialize data object. This will be built below
    const data = {};

    // Iterate through each key value pair from formData
    formData.forEach((value, key) => {
        // Course ID array needs to be constructed
        if (key === "term_course_ids") {
            // Create empty term_course_ids array if not already included in data object
            if (!data[key]) {
                data[key] = [];
            }
            // Push course ID to term_course_ids array
            data[key].push(value);

            // All non-course keys can be pushed directly as separate data object properties
        } else {
            data[key] = value;
        }
    });
    // Logging to console for debugging purposes
    console.log(data);

    // Call Flask route to add term and courses
    const response = await fetch(
        "/add-term", {
        headers: {
            "Content-Type": "application/json"
        },
        method: "POST",
        body: JSON.stringify(data)
    }
    )

    const message = await response.json();
    console.log(JSON.stringify(message));

    // Display confirmation/error popup on screen
    window.alert(message["message"].replace('"', ''));

    // Successful Response
    if (response.status == 200) {
        toggleTermForm("view_terms_section", reload = true)
    }
}

// ////////////////////////////////////// //
// FUNCTION                               //
// BUILD UPDATE TERM SECTION //
// ////////////////////////////////////// //
// Handle building the update term section and toggling display of it to on
function buildUpdateTermSection(event, term_id, term_name, courses) {
    // Prevent page from refreshing
    event.preventDefault();

    // Build array from comma separated string and trim white space
    const courses_array = courses.split(",").map(course => course.trim());

    const edit_section = document.getElementById("edit_term_courses_section");
    edit_section.innerHTML = "";

    let edit_section_html = `
          <h2>${term_name} Term Courses</h2>
          <h3>Add Course</h3>
          <button id="cancel_edit_term_courses_section" type="button" onclick="toggleTermForm('view_terms_section', reload=true)">Cancel</button>
          <table border="1">
            <tr>
              <th>New Course</th>
              <th>Submit</th>
            </tr>
            <tr>
              <td>
                <select name="term_add_course" id="term_add_course"aria-label="Course">
                  <option value="" disabled selected>Select a course</option>
        `;

    for (const course_object of window.courses) {
        const is_current_course = courses_array.includes(course_object["course"]);

        edit_section_html += `
            <option value="${course_object['id']}" ${is_current_course ? "disabled" : ""}>
              ${course_object["course"]}
            </option>
          `;
    }

    edit_section_html += `
            </select>
            </td>
            <td><button type="button" onclick="addTermCourse(event, ${term_id}, this)">Submit</button></td>
          </tr>
        `
    edit_section_html += "</table>";

    // Apply html to section and toggle view to on
    edit_section.innerHTML = edit_section_html;
    toggleTermForm("edit_term_courses_section");
}

// /////////////// //
// FUNCTION        //
// ADD TERM COURSE //
// /////////////// //
// Handle adding a term course
async function addTermCourse(event, term_id, button_element) {
    // Prevent page from refreshing
    event.preventDefault();

    // Get new course ID from value of closest select option
    const new_course_id = button_element.closest("tr").querySelector("select").value;

    // Call Flask route to add term course
    const response = await fetch(
        "/add-term-course", {
        headers: {
            "Content-Type": "application/json"
        },
        method: "PATCH",
        body: JSON.stringify({ "term_id": term_id, "new_course_id": new_course_id })
    }
    )

    const message = await response.json();
    console.log(JSON.stringify(message));

    // Display confirmation/error popup on screen
    window.alert(message["message"].replace('"', ''));

    // Successful Response
    if (response.status == 200) {
        toggleTermForm("view_terms_section", refresh = true)
    }
}

// Add listeners
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("add_term_form").onsubmit = addTerm;
})