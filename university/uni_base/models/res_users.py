from odoo import SUPERUSER_ID, api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _uni_table_ready(self, model_name):
        model = self.env.get(model_name)
        return bool(model)

    @api.model
    def ensure_university_demo_users(self):
        company = self.env.ref("base.main_company")
        company.write(
            {
                "university_name": "Visionary Minds University",
                "university_tagline": "Bold academic operations for modern learning, teaching, and campus life.",
                "university_code": "VMU",
            }
        )
        department_model = self.env["uni.department"]
        term_model = self.env["uni.term"]
        faculty_model = self.env["uni.faculty"]
        student_model = self.env["uni.student"]
        course_model = self.env["uni.course"]
        timetable_model = self.env["uni.timetable"]
        assignment_model = self.env["uni.assignment"]
        grade_model = self.env["uni.grade"]
        attendance_model = self.env["uni.attendance"]
        issue_model = self.env["uni.issue"]
        exam_model = self.env["uni.exam"]
        registration_model = self.env["uni.course.registration"]
        fee_model = self.env["uni.fee.invoice"]
        scholarship_model = self.env["uni.scholarship"]
        library_item_model = self.env["uni.library.item"]
        library_loan_model = self.env["uni.library.loan"]
        notification_model = self.env["uni.notification"]
        admission_model = self.env["uni.admission"]
        submission_model = self.env["uni.assignment.submission"]
        exam_result_model = self.env["uni.exam.result"]
        resit_request_model = self.env["uni.resit.request"]

        cs_department = department_model.search([("code", "=", "CSE")], limit=1)
        if not cs_department:
            cs_department = department_model.create({"name": "Computer Science", "code": "CSE"})
        term = term_model.search([("name", "=", "Spring 2026")], limit=1)
        if not term:
            term = term_model.create(
                {
                    "name": "Spring 2026",
                    "academic_year": "2025/2026",
                    "start_date": "2026-01-12",
                    "end_date": "2026-05-20",
                    "state": "open",
                }
            )
        demo_users = [
            {
                "name": "Student Demo",
                "login": "student",
                "password": "student123",
                "email": "student@university.local",
                "groups": [
                    self.env.ref("base.group_user").id,
                    self.env.ref("uni_base.group_university_student").id,
                ],
            },
            {
                "name": "Faculty Demo",
                "login": "faculty",
                "password": "faculty123",
                "email": "faculty@university.local",
                "groups": [
                    self.env.ref("base.group_user").id,
                    self.env.ref("uni_base.group_university_faculty").id,
                ],
            },
            {
                "name": "Faculty One Demo",
                "login": "faculty1",
                "password": "faculty123",
                "email": "faculty1@university.local",
                "groups": [
                    self.env.ref("base.group_user").id,
                    self.env.ref("uni_base.group_university_faculty").id,
                ],
            },
            {
                "name": "University Admin Demo",
                "login": "uniadmin",
                "password": "uniadmin123",
                "email": "uniadmin@university.local",
                "groups": [
                    self.env.ref("base.group_user").id,
                    self.env.ref("uni_base.group_university_admin").id,
                ],
            },
        ]

        for values in demo_users:
            login = values["login"]
            user = self.search([("login", "=", login)], limit=1)
            write_vals = {
                "name": values["name"],
                "password": values["password"],
                "email": values["email"],
                "company_id": company.id,
                "company_ids": [(6, 0, [company.id])],
                "group_ids": [(6, 0, values["groups"])],
            }
            if user:
                user.with_context(no_reset_password=True).write(write_vals)
            else:
                self.with_context(no_reset_password=True).create(
                    {
                        "login": login,
                        **write_vals,
                    }
                )

        faculty_user = self.search([("login", "=", "faculty")], limit=1)
        faculty_user_2 = self.search([("login", "=", "faculty1")], limit=1)
        student_user = self.search([("login", "=", "student")], limit=1)
        admin_user = self.search([("login", "=", "uniadmin")], limit=1)

        faculty = faculty_model.search([("user_id", "=", faculty_user.id)], limit=1)
        if not faculty:
            faculty = faculty_model.create(
                {
                    "name": "Amina Rahman",
                    "title": "Dr.",
                    "user_id": faculty_user.id,
                    "department_id": cs_department.id,
                    "max_load_hours": 15.0,
                }
            )
        else:
            faculty.write({"department_id": cs_department.id})

        faculty_two = faculty_model.search([("user_id", "=", faculty_user_2.id)], limit=1)
        if not faculty_two:
            faculty_two = faculty_model.create(
                {
                    "name": "Nadia Karim",
                    "title": "Dr.",
                    "user_id": faculty_user_2.id,
                    "department_id": cs_department.id,
                    "max_load_hours": 15.0,
                }
            )
        else:
            faculty_two.write({"department_id": cs_department.id})

        student = student_model.search([("user_id", "=", student_user.id)], limit=1)
        if not student:
            student = student_model.create(
                {
                    "name": "Omar Haddad",
                    "user_id": student_user.id,
                    "email": "student@university.local",
                    "student_number": "STU-2026-001",
                    "department_id": cs_department.id,
                    "advisor_id": faculty.id,
                    "term_id": term.id,
                    "state": "enrolled",
                }
            )
        else:
            student.write({"department_id": cs_department.id, "advisor_id": faculty.id, "term_id": term.id})

        course = course_model.search([("code", "=", "CSE401")], limit=1)
        if not course:
            course = course_model.create(
                {
                    "name": "Distributed Systems",
                    "code": "CSE401",
                    "department_id": cs_department.id,
                    "faculty_id": faculty.id,
                    "term_id": term.id,
                    "credit_hours": 3.0,
                    "seat_limit": 40,
                }
            )
        else:
            course.write({"department_id": cs_department.id, "faculty_id": faculty.id, "term_id": term.id})

        course_two = course_model.search([("code", "=", "CSE402")], limit=1)
        if not course_two:
            course_two = course_model.create(
                {
                    "name": "Cloud Computing",
                    "code": "CSE402",
                    "department_id": cs_department.id,
                    "faculty_id": faculty_two.id,
                    "term_id": term.id,
                    "credit_hours": 3.0,
                    "seat_limit": 35,
                }
            )
        else:
            course_two.write({"department_id": cs_department.id, "faculty_id": faculty_two.id, "term_id": term.id})

        course_three = course_model.search([("code", "=", "CSE403")], limit=1)
        if not course_three:
            course_three = course_model.create(
                {
                    "name": "Applied Machine Learning",
                    "code": "CSE403",
                    "department_id": cs_department.id,
                    "faculty_id": faculty.id,
                    "term_id": term.id,
                    "credit_hours": 3,
                    "seat_limit": 30,
                }
            )
        else:
            course_three.write({"department_id": cs_department.id, "faculty_id": faculty.id, "term_id": term.id})

        course_four = course_model.search([("code", "=", "CSE404")], limit=1)
        if not course_four:
            course_four = course_model.create(
                {
                    "name": "Cybersecurity Operations",
                    "code": "CSE404",
                    "department_id": cs_department.id,
                    "faculty_id": faculty_two.id,
                    "term_id": term.id,
                    "credit_hours": 3,
                    "seat_limit": 30,
                }
            )
        else:
            course_four.write({"department_id": cs_department.id, "faculty_id": faculty_two.id, "term_id": term.id})

        if not timetable_model.search([("course_id", "=", course.id), ("weekday", "=", "mon")], limit=1):
            timetable_model.create(
                {
                    "course_id": course.id,
                    "faculty_id": faculty.id,
                    "term_id": term.id,
                    "weekday": "mon",
                    "start_hour": 9.0,
                    "end_hour": 10.5,
                    "room": "B-201",
                }
            )
        if not timetable_model.search([("course_id", "=", course.id), ("weekday", "=", "wed")], limit=1):
            timetable_model.create(
                {
                    "course_id": course.id,
                    "faculty_id": faculty.id,
                    "term_id": term.id,
                    "weekday": "wed",
                    "start_hour": 9.0,
                    "end_hour": 10.5,
                    "room": "B-201",
                }
            )
        if not timetable_model.search([("course_id", "=", course_two.id), ("weekday", "=", "tue")], limit=1):
            timetable_model.create(
                {
                    "course_id": course_two.id,
                    "faculty_id": faculty_two.id,
                    "term_id": term.id,
                    "weekday": "tue",
                    "start_hour": 11.0,
                    "end_hour": 12.5,
                    "room": "C-301",
                }
            )
        if not timetable_model.search([("course_id", "=", course_two.id), ("weekday", "=", "thu")], limit=1):
            timetable_model.create(
                {
                    "course_id": course_two.id,
                    "faculty_id": faculty_two.id,
                    "term_id": term.id,
                    "weekday": "thu",
                    "start_hour": 11.0,
                    "end_hour": 12.5,
                    "room": "C-301",
                }
            )
        if not timetable_model.search([("course_id", "=", course_three.id), ("weekday", "=", "mon")], limit=1):
            timetable_model.create(
                {
                    "course_id": course_three.id,
                    "faculty_id": faculty.id,
                    "term_id": term.id,
                    "weekday": "mon",
                    "start_hour": 14.0,
                    "end_hour": 15.5,
                    "room": "ML-201",
                }
            )
        if not timetable_model.search([("course_id", "=", course_three.id), ("weekday", "=", "thu")], limit=1):
            timetable_model.create(
                {
                    "course_id": course_three.id,
                    "faculty_id": faculty.id,
                    "term_id": term.id,
                    "weekday": "thu",
                    "start_hour": 14.0,
                    "end_hour": 15.5,
                    "room": "ML-201",
                }
            )
        if not timetable_model.search([("course_id", "=", course_four.id), ("weekday", "=", "tue")], limit=1):
            timetable_model.create(
                {
                    "course_id": course_four.id,
                    "faculty_id": faculty_two.id,
                    "term_id": term.id,
                    "weekday": "tue",
                    "start_hour": 15.0,
                    "end_hour": 16.5,
                    "room": "SEC-110",
                }
            )
        if not timetable_model.search([("course_id", "=", course_four.id), ("weekday", "=", "fri")], limit=1):
            timetable_model.create(
                {
                    "course_id": course_four.id,
                    "faculty_id": faculty_two.id,
                    "term_id": term.id,
                    "weekday": "fri",
                    "start_hour": 10.0,
                    "end_hour": 11.5,
                    "room": "SEC-110",
                }
            )

        if not assignment_model.search([("name", "=", "Microservices Design Brief"), ("course_id", "=", course.id)], limit=1):
            assignment_model.create(
                {
                    "name": "Microservices Design Brief",
                    "course_id": course.id,
                    "faculty_id": faculty.id,
                    "term_id": term.id,
                    "due_date": "2026-04-10",
                    "total_marks": 100.0,
                    "state": "published",
                    "instructions": "Submit a service decomposition and deployment plan.",
                }
            )
        assignment = assignment_model.search([("name", "=", "Microservices Design Brief"), ("course_id", "=", course.id)], limit=1)
        if not assignment_model.search([("name", "=", "Cloud Migration Case Study"), ("course_id", "=", course_two.id)], limit=1):
            assignment_model.create(
                {
                    "name": "Cloud Migration Case Study",
                    "course_id": course_two.id,
                    "faculty_id": faculty_two.id,
                    "term_id": term.id,
                    "due_date": "2026-04-16",
                    "total_marks": 100.0,
                    "state": "published",
                    "instructions": "Prepare a migration plan for a legacy university service.",
                }
            )
        assignment_two = assignment_model.search([("name", "=", "Cloud Migration Case Study"), ("course_id", "=", course_two.id)], limit=1)

        if not grade_model.search([("student_id", "=", student.id), ("course_id", "=", course.id)], limit=1):
            grade_model.create(
                {
                    "student_id": student.id,
                    "course_id": course.id,
                    "term_id": term.id,
                    "credit_hours": 3.0,
                    "percentage": 87.0,
                    "note": "Strong project work.",
                }
            )
        if not grade_model.search([("student_id", "=", student.id), ("course_id", "=", course_two.id)], limit=1):
            grade_model.create(
                {
                    "student_id": student.id,
                    "course_id": course_two.id,
                    "term_id": term.id,
                    "credit_hours": 3.0,
                    "percentage": 91.0,
                    "note": "Consistent work on cloud labs.",
                }
            )

        if not attendance_model.search([("student_id", "=", student.id), ("course_id", "=", course.id)], limit=1):
            attendance_model.create(
                [
                    {
                        "student_id": student.id,
                        "course_id": course.id,
                        "faculty_id": faculty.id,
                        "session_date": "2026-04-01",
                        "status": "present",
                    },
                    {
                        "student_id": student.id,
                        "course_id": course.id,
                        "faculty_id": faculty.id,
                        "session_date": "2026-04-03",
                        "status": "late",
                    },
                ]
            )
        if not attendance_model.search([("student_id", "=", student.id), ("course_id", "=", course_two.id)], limit=1):
            attendance_model.create(
                [
                    {
                        "student_id": student.id,
                        "course_id": course_two.id,
                        "faculty_id": faculty_two.id,
                        "session_date": "2026-04-02",
                        "status": "present",
                    },
                    {
                        "student_id": student.id,
                        "course_id": course_two.id,
                        "faculty_id": faculty_two.id,
                        "session_date": "2026-04-04",
                        "status": "present",
                    },
                ]
            )

        issue_specs = [
            ("Crash on assignment submission", "crash", "3", "open"),
            ("Duplicate timetable entry detected", "schedule", "2", "investigating"),
            ("Student blocked from registration", "registration", "2", "blocked"),
        ]
        for name, issue_type, priority, state in issue_specs:
            if not issue_model.search([("name", "=", name)], limit=1):
                issue_model.create(
                    {
                        "name": name,
                        "issue_type": issue_type,
                        "priority": priority,
                        "state": state,
                        "student_id": student.id,
                        "course_id": course.id,
                        "assignee_faculty_id": faculty.id if admin_user else faculty.id,
                    }
                )

        if not exam_model.search([("name", "=", "Distributed Systems Midterm"), ("course_id", "=", course.id)], limit=1):
            exam_model.create(
                {
                    "name": "Distributed Systems Midterm",
                    "course_id": course.id,
                    "term_id": term.id,
                    "exam_date": "2026-04-18",
                    "start_hour": 10.0,
                    "end_hour": 12.0,
                    "room": "Main Hall 1",
                    "capacity": 120,
                    "invigilator_id": faculty.id,
                    "state": "approved",
                }
            )
        exam = exam_model.search([("name", "=", "Distributed Systems Midterm"), ("course_id", "=", course.id)], limit=1)
        if not exam_model.search([("name", "=", "Cloud Computing Quiz 1"), ("course_id", "=", course_two.id)], limit=1):
            exam_model.create(
                {
                    "name": "Cloud Computing Quiz 1",
                    "course_id": course_two.id,
                    "term_id": term.id,
                    "exam_date": "2026-04-22",
                    "start_hour": 13.0,
                    "end_hour": 14.0,
                    "room": "Online",
                    "capacity": 200,
                    "invigilator_id": faculty_two.id,
                    "state": "approved",
                }
            )
        exam_two = exam_model.search([("name", "=", "Cloud Computing Quiz 1"), ("course_id", "=", course_two.id)], limit=1)

        if not registration_model.search([("student_id", "=", student.id), ("course_id", "=", course.id), ("term_id", "=", term.id)], limit=1):
            registration_model.create(
                {
                    "student_id": student.id,
                    "course_id": course.id,
                    "term_id": term.id,
                    "status": "registered",
                    "registered_on": "2026-01-15",
                    "note": "Seeded registration for demo data.",
                }
            )
        if not registration_model.search([("student_id", "=", student.id), ("course_id", "=", course_two.id), ("term_id", "=", term.id)], limit=1):
            registration_model.create(
                {
                    "student_id": student.id,
                    "course_id": course_two.id,
                    "term_id": term.id,
                    "status": "registered",
                    "registered_on": "2026-01-15",
                    "note": "Seeded second-course registration for demo data.",
                }
            )

        if not admission_model.search([("email", "=", "applicant@university.local")], limit=1):
            admission_model.create(
                {
                    "name": "Sara Noor",
                    "email": "applicant@university.local",
                    "phone": "+971500000001",
                    "department_id": cs_department.id,
                    "term_id": term.id,
                    "application_date": "2026-03-15",
                    "state": "review",
                    "notes": "Application under advisor review.",
                }
            )

        scholarship = scholarship_model.search([("student_id", "=", student.id), ("name", "=", "Merit Scholarship 2026")], limit=1)
        if not scholarship:
            scholarship = scholarship_model.create(
                {
                    "name": "Merit Scholarship 2026",
                    "scholarship_type": "merit",
                    "student_id": student.id,
                    "amount": 1500.0,
                    "state": "approved",
                    "note": "Awarded for high semester performance.",
                }
            )

        tuition_invoice = fee_model.search([("student_id", "=", student.id), ("name", "=", "Spring 2026 Tuition")], limit=1)
        if not tuition_invoice:
            tuition_invoice = fee_model.create(
                {
                    "name": "Spring 2026 Tuition",
                    "student_id": student.id,
                    "term_id": term.id,
                    "amount_total": 6000.0,
                    "amount_paid": 0.0,
                    "due_date": "2026-04-20",
                    "state": "posted",
                    "scholarship_id": scholarship.id,
                }
            )
        else:
            tuition_invoice.write(
                {
                    "amount_paid": 0.0,
                    "state": "posted",
                    "due_date": "2026-04-20",
                    "scholarship_id": scholarship.id,
                }
            )

        library_item = library_item_model.search([("title", "=", "Designing Data-Intensive Applications")], limit=1)
        if not library_item:
            library_item = library_item_model.create(
                {
                    "title": "Designing Data-Intensive Applications",
                    "author": "Martin Kleppmann",
                    "isbn": "9781449373320",
                    "course_id": course.id,
                    "available_copies": 4,
                    "digital_link": "https://dataintensive.net/",
                }
            )
        library_item_two = library_item_model.search([("title", "=", "Cloud Native Patterns")], limit=1)
        if not library_item_two:
            library_item_two = library_item_model.create(
                {
                    "title": "Cloud Native Patterns",
                    "author": "Cornelia Davis",
                    "isbn": "9781617294297",
                    "course_id": course_two.id,
                    "available_copies": 3,
                    "digital_link": "https://www.manning.com/books/cloud-native-patterns",
                }
            )

        if not library_loan_model.search([("item_id", "=", library_item.id), ("student_id", "=", student.id)], limit=1):
            library_loan_model.create(
                {
                    "item_id": library_item.id,
                    "student_id": student.id,
                    "borrow_date": "2026-04-02",
                    "due_date": "2026-04-16",
                    "state": "borrowed",
                    "fine_amount": 0.0,
                }
            )
        if not library_loan_model.search([("item_id", "=", library_item_two.id), ("student_id", "=", student.id)], limit=1):
            library_loan_model.create(
                {
                    "item_id": library_item_two.id,
                    "student_id": student.id,
                    "borrow_date": "2026-04-05",
                    "due_date": "2026-04-19",
                    "state": "borrowed",
                    "fine_amount": 0.0,
                }
            )

        notification_specs = [
            ("Assignment due in 24 hours", "assignment_due", "student", "queued", "Microservices Design Brief is due tomorrow."),
            ("Exam timetable published", "result_published", "student", "draft", "Midterm examination schedule is now available."),
            ("System incident under investigation", "system_issue", "all", "queued", "Assignment upload errors are under investigation."),
        ]
        for name, ntype, audience, state, message in notification_specs:
            if not notification_model.search([("name", "=", name)], limit=1):
                notification_model.create(
                    {
                        "name": name,
                        "notification_type": ntype,
                        "audience": audience,
                        "schedule_date": fields.Datetime.now(),
                        "state": state,
                        "message": message,
                    }
                )

        if assignment and not submission_model.search([("assignment_id", "=", assignment.id), ("student_id", "=", student.id)], limit=1):
            submission_model.create(
                {
                    "assignment_id": assignment.id,
                    "student_id": student.id,
                    "submission_date": fields.Datetime.now(),
                    "state": "submitted",
                    "file_name": "microservices-brief.pdf",
                    "feedback": "Awaiting faculty grading.",
                }
            )
        if assignment_two and not submission_model.search([("assignment_id", "=", assignment_two.id), ("student_id", "=", student.id)], limit=1):
            submission_model.create(
                {
                    "assignment_id": assignment_two.id,
                    "student_id": student.id,
                    "submission_date": fields.Datetime.now(),
                    "state": "graded",
                    "file_name": "cloud-migration-plan.pdf",
                    "feedback": "Good coverage of the migration stages.",
                    "score": 92.0,
                }
            )

        if exam and not exam_result_model.search([("exam_id", "=", exam.id), ("student_id", "=", student.id)], limit=1):
            exam_result_model.create(
                {
                    "exam_id": exam.id,
                    "student_id": student.id,
                    "score": 78.0,
                    "state": "approved",
                    "note": "Approved and awaiting publication.",
                }
            )
        if exam_two and not exam_result_model.search([("exam_id", "=", exam_two.id), ("student_id", "=", student.id)], limit=1):
            exam_result_model.create(
                {
                    "exam_id": exam_two.id,
                    "student_id": student.id,
                    "score": 88.0,
                    "state": "visible",
                    "note": "Published cloud quiz result.",
                }
            )

        exam_result = exam_result_model.search([("exam_id", "=", exam.id), ("student_id", "=", student.id)], limit=1) if exam else False
        if exam_result and not resit_request_model.search([("exam_result_id", "=", exam_result.id)], limit=1):
            resit_request_model.create(
                {
                    "exam_result_id": exam_result.id,
                    "student_id": student.id,
                    "request_date": "2026-04-21",
                    "reason": "Student requested a resit after borderline result.",
                    "state": "submitted",
                }
            )
        return True

    def _get_university_home_action(self):
        return self.env.ref("uni_base.action_university_home", raise_if_not_found=False)

    def _is_university_user(self):
        self.ensure_one()
        university_groups = (
            "uni_base.group_university_student",
            "uni_base.group_university_faculty",
            "uni_base.group_university_admin",
            "uni_base.group_university_advisor",
        )
        return any(self.has_group(group_xmlid) for group_xmlid in university_groups)

    def _sync_university_home_action(self):
        action = self._get_university_home_action()
        if not action:
            return
        for user in self:
            if user._is_university_user():
                if user.action_id != action:
                    user.with_context(skip_university_home_sync=True).action_id = action.id
            elif user.action_id == action:
                user.with_context(skip_university_home_sync=True).action_id = False

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        users._sync_university_home_action()
        return users

    def write(self, vals):
        result = super().write(vals)
        if not self.env.context.get("skip_university_home_sync") and (
            "groups_id" in vals or "action_id" in vals
        ):
            self._sync_university_home_action()
        return result

    @api.model
    def get_university_dashboard_data(self):
        user = self.env.user
        company = user.company_id
        student_model = self.env["uni.student"].sudo()
        faculty_model = self.env["uni.faculty"].sudo()
        timetable_model = self.env["uni.timetable"].sudo()
        assignment_model = self.env["uni.assignment"].sudo()
        issue_model = self.env["uni.issue"].sudo()
        role = "admin"
        highlights = [
            "Monitor open crashes, registration blockers, and timetable conflicts.",
            "Track unresolved operational issues before they impact students.",
        ]
        cards = [
            {"label": "Open Issues", "value": str(issue_model.search_count([("state", "=", "open")]) if issue_model else 0), "hint": "Issues awaiting action"},
            {"label": "Critical Crashes", "value": str(issue_model.search_count([("issue_type", "=", "crash"), ("priority", "=", "3"), ("state", "!=", "resolved")]) if issue_model else 0), "hint": "Production-impacting failures"},
            {"label": "Blocked Work", "value": str(issue_model.search_count([("state", "=", "blocked")]) if issue_model else 0), "hint": "Processes currently blocked"},
        ]
        quick_links = [
            {"label": "Issues", "xmlid": "uni_base.action_uni_issues"},
            {"label": "Students", "xmlid": "uni_base.action_uni_students"},
            {"label": "Admissions", "xmlid": "uni_base.action_uni_admissions"},
            {"label": "Fees", "xmlid": "uni_base.action_uni_fee_invoices"},
            {"label": "University Settings", "xmlid": "base.action_res_company_form"},
            {"label": "Users", "xmlid": "base.action_res_users"},
        ]
        if user.has_group("uni_base.group_university_student"):
            student = student_model.search([("user_id", "=", user.id)], limit=1) if student_model else False
            today_classes = timetable_model.search_count([("term_id", "=", student.term_id.id)]) if student and timetable_model else 0
            gpa = f"{student.current_gpa:.2f}" if student else "0.00"
            role = "student"
            highlights = [
                "Your timetable, assignments, and attendance are now backed by real records.",
                "Course registration, fees, and document requests still need to be built next.",
            ]
            cards = [
                {"label": "Scheduled Classes", "value": str(today_classes), "hint": "This term's timetable slots"},
                {"label": "Pending Work", "value": str(student.assignment_due_count if student else 0), "hint": "Published assignments"},
                {"label": "Current GPA", "value": gpa, "hint": "Current weighted GPA"},
            ]
            quick_links = [{"label": "My Grades", "xmlid": "uni_base.action_uni_grades"}, {"label": "My Timetable", "xmlid": "uni_base.action_uni_timetable"}, {"label": "My Fees", "xmlid": "uni_base.action_uni_fee_invoices"}]
        elif user.has_group("uni_base.group_university_faculty"):
            faculty = faculty_model.search([("user_id", "=", user.id)], limit=1) if faculty_model else False
            lecture_count = timetable_model.search_count([("faculty_id", "=", faculty.id)]) if faculty and timetable_model else 0
            ungraded = assignment_model.search_count([("faculty_id", "=", faculty.id), ("state", "=", "published")]) if faculty and assignment_model else 0
            faculty_issues = issue_model.search_count([("assignee_faculty_id", "=", faculty.id), ("state", "!=", "resolved")]) if faculty and issue_model else 0
            role = "faculty"
            highlights = [
                "Teaching load now comes from courses and timetable slots.",
                "Open incidents assigned to you are counted alongside course work.",
            ]
            cards = [
                {"label": "Scheduled Lectures", "value": str(lecture_count), "hint": "Current term timetable slots"},
                {"label": "Active Assignments", "value": str(ungraded), "hint": "Published assignment queue"},
                {"label": "Assigned Issues", "value": str(faculty_issues), "hint": "Operational issues on your desk"},
            ]
            quick_links = [{"label": "Attendance", "xmlid": "uni_base.action_uni_attendance"}, {"label": "Assignments", "xmlid": "uni_base.action_uni_assignments"}, {"label": "Exam Results", "xmlid": "uni_base.action_uni_exam_results"}]
        return {
            "role": role,
            "university_name": company.university_name or company.name,
            "tagline": company.university_tagline,
            "highlights": highlights,
            "cards": cards,
            "quick_links": quick_links,
        }

    @api.model
    def get_university_portal_data(self):
        dashboard = self.get_university_dashboard_data()

        def safe_records(model_name, fields_list, domain=None, limit=20, order=None):
            try:
                model = self.env[model_name].sudo()
                return model.search_read(domain or [], fields_list, limit=limit, order=order)
            except Exception:
                return []

        user = self.env.user
        student = None
        faculty = None
        student_course_ids = []
        student_term_id = False
        student = self.env["uni.student"].sudo().search([("user_id", "=", user.id)], limit=1)
        faculty = self.env["uni.faculty"].sudo().search([("user_id", "=", user.id)], limit=1)
        if student:
            student_term_id = student.term_id.id
        if student:
            student_course_ids = self.env["uni.course.registration"].sudo().search(
                [("student_id", "=", student.id)]
            ).mapped("course_id").ids
        faculty_course_ids = self.env["uni.course"].sudo().search([("faculty_id", "=", faculty.id)]).ids if faculty else []

        student_domain = [("student_id", "=", student.id)] if student else []
        if student_course_ids:
            course_domain = [("id", "in", student_course_ids)]
            timetable_domain = [("course_id", "in", student_course_ids)]
            assignment_domain = [("course_id", "in", student_course_ids), ("state", "in", ["published", "late", "closed"])]
            exam_domain = [("course_id", "in", student_course_ids), ("state", "=", "visible")]
            library_item_domain = [("course_id", "in", student_course_ids)]
        elif student_term_id:
            course_domain = [("term_id", "=", student_term_id)]
            timetable_domain = [("term_id", "=", student_term_id)]
            assignment_domain = [("term_id", "=", student_term_id), ("state", "in", ["published", "late", "closed"])]
            exam_domain = [("term_id", "=", student_term_id), ("state", "=", "visible")]
            library_item_domain = ["|", ("course_id", "=", False), ("course_id.term_id", "=", student_term_id)]
        elif faculty:
            course_domain = [("faculty_id", "=", faculty.id)]
            timetable_domain = [("faculty_id", "=", faculty.id)]
            assignment_domain = [("faculty_id", "=", faculty.id)]
            exam_domain = [("course_id", "in", faculty_course_ids)]
            library_item_domain = []
        else:
            course_domain = []
            timetable_domain = []
            assignment_domain = []
            exam_domain = []
            library_item_domain = []
        faculty_issue_domain = [("assignee_faculty_id", "=", faculty.id)] if faculty else []
        if faculty:
            faculty_exam_ids = self.env["uni.exam"].sudo().search(exam_domain).ids
            result_domain = [("exam_id", "in", faculty_exam_ids)] if faculty_exam_ids else [("id", "=", 0)]
            submission_domain = [("assignment_id.faculty_id", "=", faculty.id)]
            faculty_student_rows = self.env["uni.course.registration"].sudo().search(
                [("course_id", "in", faculty_course_ids)],
                order="course_id,student_id",
            )
            student_page_records = [
                {
                    "id": registration.id,
                    "course": registration.course_id.name,
                    "course_code": registration.course_id.code,
                    "student": registration.student_id.name,
                    "student_number": registration.student_id.student_number,
                    "username": registration.student_id.user_login,
                    "status": registration.status,
                    "registered_on": registration.registered_on,
                }
                for registration in faculty_student_rows
            ]
        else:
            result_domain = student_domain if student else []
            submission_domain = student_domain if student else []
            student_page_records = safe_records(
                "uni.student",
                ["name", "student_number", "user_login", "state", "attendance_rate", "current_gpa", "overdue_invoice_count", "exam_blocked"],
                limit=50,
                order="name",
            )
        if dashboard["role"] == "student":
            notification_domain = [("audience", "in", ["student", "all"])]
        elif dashboard["role"] == "faculty":
            notification_domain = [("audience", "in", ["faculty", "all"])]
        else:
            notification_domain = []

        pages = {
            "students": student_page_records,
            "faculty": safe_records(
                "uni.faculty",
                ["name", "display_name", "title", "user_login", "max_load_hours", "department_id"],
                limit=50,
                order="name",
            ),
            "courses": safe_records(
                "uni.course",
                ["code", "name", "credit_hours", "seat_limit", "faculty_id", "term_id"],
                course_domain,
                limit=50,
                order="code",
            ),
            "timetable": safe_records(
                "uni.timetable",
                ["course_id", "weekday", "start_hour", "end_hour", "room", "faculty_id"],
                timetable_domain,
                limit=50,
                order="weekday,start_hour",
            ),
            "assignments": safe_records(
                "uni.assignment",
                ["name", "course_id", "faculty_id", "owner_login", "term_id", "due_date", "state", "total_marks", "submission_count", "instructions", "assignment_type", "instruction_file_name", "instruction_file_data", "question_count"],
                assignment_domain,
                limit=50,
                order="due_date desc",
            ),
            "submissions": safe_records(
                "uni.assignment.submission",
                ["assignment_id", "student_id", "submission_date", "state", "score", "file_name", "file_data", "feedback", "submission_type"],
                submission_domain,
                limit=50,
                order="submission_date desc",
            ),
            "exams": safe_records(
                "uni.exam",
                ["name", "course_id", "term_id", "exam_date", "start_hour", "end_hour", "room", "state", "result_state", "delivery_mode", "question_count"],
                exam_domain,
                limit=50,
                order="exam_date desc",
            ),
            "results": safe_records(
                "uni.exam.result",
                ["exam_id", "student_id", "score", "auto_score", "manual_score", "state", "note", "submitted_on"],
                result_domain,
                limit=50,
                order="id desc",
            ),
            "resits": safe_records(
                "uni.resit.request",
                ["exam_result_id", "request_date", "state", "fee_invoice_id"],
                student_domain if student else [],
                limit=50,
                order="request_date desc",
            ),
            "registrations": safe_records(
                "uni.course.registration",
                ["student_id", "course_id", "term_id", "status", "registered_on"],
                student_domain if student else [],
                limit=50,
                order="registered_on desc",
            ),
            "fees": safe_records(
                "uni.fee.invoice",
                ["name", "amount_total", "scholarship_discount", "amount_paid", "balance_due", "due_date", "state", "is_exam_blocking"],
                student_domain if student else [],
                limit=50,
                order="due_date desc",
            ),
            "scholarships": safe_records(
                "uni.scholarship",
                ["name", "scholarship_type", "amount", "state", "note"],
                student_domain if student else [],
                limit=50,
                order="name",
            ),
            "libraryItems": safe_records(
                "uni.library.item",
                ["title", "author", "isbn", "available_copies", "digital_link", "course_id"],
                library_item_domain,
                limit=50,
                order="title",
            ),
            "libraryLoans": safe_records(
                "uni.library.loan",
                ["item_id", "borrow_date", "due_date", "return_date", "state", "fine_amount"],
                student_domain if student else [],
                limit=50,
                order="borrow_date desc",
            ),
            "notifications": safe_records(
                "uni.notification",
                ["name", "notification_type", "audience", "schedule_date", "state", "message"],
                notification_domain,
                limit=50,
                order="schedule_date desc",
            ),
            "issues": safe_records(
                "uni.issue",
                ["name", "issue_type", "priority", "state", "opened_on", "course_id"],
                faculty_issue_domain if faculty else [],
                limit=50,
                order="opened_on desc",
            ),
        }

        return {
            "dashboard": dashboard,
            "pages": pages,
            "role": dashboard["role"],
            "context": {
                "student_id": student.id if student else False,
                "faculty_id": faculty.id if faculty else False,
            },
            "lookups": {
                "departments": safe_records("uni.department", ["name", "code"], limit=100, order="name"),
                "terms": safe_records("uni.term", ["name", "academic_year", "state"], limit=100, order="start_date desc"),
                "registration_courses": safe_records(
                    "uni.course",
                    ["code", "name", "credit_hours", "seat_limit", "faculty_id", "term_id"],
                    [("term_id", "=", student_term_id)] if student_term_id else [],
                    limit=100,
                    order="code",
                ),
                "assignment_questions": safe_records(
                    "uni.assignment.question",
                    ["assignment_id", "question_text", "marks", "option_a", "option_b", "option_c", "option_d", "correct_option", "sequence"],
                    [("assignment_id", "in", [record["id"] for record in pages["assignments"]])] if pages["assignments"] else [("id", "=", 0)],
                    limit=500,
                    order="sequence,id",
                ),
                "exam_questions": safe_records(
                    "uni.exam.question",
                    ["exam_id", "question_text", "question_type", "marks", "option_a", "option_b", "option_c", "option_d", "correct_option", "sequence"],
                    [("exam_id", "in", [record["id"] for record in pages["exams"]])] if pages["exams"] else [("id", "=", 0)],
                    limit=500,
                    order="sequence,id",
                ),
                "exam_answers": safe_records(
                    "uni.exam.answer",
                    ["result_id", "question_id", "selected_option", "answer_text", "file_name", "file_data", "awarded_marks"],
                    [("result_id", "in", [record["id"] for record in pages["results"]])] if pages["results"] else [("id", "=", 0)],
                    limit=1000,
                    order="id",
                ),
            },
        }


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.users"].ensure_university_demo_users()
    env["res.users"].search([])._sync_university_home_action()
