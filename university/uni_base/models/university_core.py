from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniDepartment(models.Model):
    _name = "uni.department"
    _description = "University Department"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("uni_department_code_uniq", "unique(code)", "Department code must be unique."),
    ]


class UniTerm(models.Model):
    _name = "uni.term"
    _description = "Academic Term"
    _order = "start_date desc, name"

    name = fields.Char(required=True)
    academic_year = fields.Char(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("open", "Open"), ("closed", "Closed")],
        default="draft",
        required=True,
    )

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("Term end date must be after the start date.")


class UniFaculty(models.Model):
    _name = "uni.faculty"
    _description = "Faculty Member"
    _rec_name = "display_name"
    _order = "name"

    name = fields.Char(required=True)
    display_name = fields.Char(compute="_compute_display_name")
    user_id = fields.Many2one("res.users")
    user_login = fields.Char(related="user_id.login", readonly=True)
    department_id = fields.Many2one("uni.department")
    title = fields.Char()
    max_load_hours = fields.Float(default=12.0)
    course_ids = fields.One2many("uni.course", "faculty_id")
    issue_ids = fields.One2many("uni.issue", "assignee_faculty_id")

    @api.depends("name", "title")
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.title} {record.name}".strip() if record.title else record.name


class UniStudent(models.Model):
    _name = "uni.student"
    _description = "Student"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    user_id = fields.Many2one("res.users", tracking=True)
    user_login = fields.Char(related="user_id.login", readonly=True)
    email = fields.Char()
    student_number = fields.Char(required=True, copy=False, tracking=True)
    department_id = fields.Many2one("uni.department", tracking=True)
    advisor_id = fields.Many2one("uni.faculty", tracking=True)
    term_id = fields.Many2one("uni.term", tracking=True)
    state = fields.Selection(
        [
            ("applied", "Applied"),
            ("accepted", "Accepted"),
            ("enrolled", "Enrolled"),
            ("graduated", "Graduated"),
            ("inactive", "Inactive"),
        ],
        default="applied",
        required=True,
        tracking=True,
    )
    attendance_rate = fields.Float(compute="_compute_metrics")
    current_gpa = fields.Float(compute="_compute_metrics")
    assignment_due_count = fields.Integer(compute="_compute_metrics")
    issue_ids = fields.One2many("uni.issue", "student_id")
    grade_ids = fields.One2many("uni.grade", "student_id")
    attendance_ids = fields.One2many("uni.attendance", "student_id")

    _sql_constraints = [
        ("uni_student_number_uniq", "unique(student_number)", "Student number must be unique."),
    ]

    @api.depends("attendance_ids.status", "grade_ids.grade_point", "grade_ids.credit_hours")
    def _compute_metrics(self):
        for student in self:
            attendances = student.attendance_ids
            total_sessions = len(attendances)
            present_sessions = len(attendances.filtered(lambda a: a.status in ("present", "late")))
            student.attendance_rate = (present_sessions / total_sessions * 100.0) if total_sessions else 0.0

            weighted_points = sum(grade.grade_point * grade.credit_hours for grade in student.grade_ids)
            total_credits = sum(student.grade_ids.mapped("credit_hours"))
            student.current_gpa = weighted_points / total_credits if total_credits else 0.0

            student.assignment_due_count = self.env["uni.assignment"].search_count(
                [
                    ("term_id", "=", student.term_id.id),
                    ("state", "in", ("published", "late")),
                ]
            )


class UniCourse(models.Model):
    _name = "uni.course"
    _description = "Course"
    _order = "code"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    department_id = fields.Many2one("uni.department")
    faculty_id = fields.Many2one("uni.faculty")
    term_id = fields.Many2one("uni.term")
    credit_hours = fields.Float(default=3.0)
    seat_limit = fields.Integer(default=30)
    active = fields.Boolean(default=True)
    timetable_ids = fields.One2many("uni.timetable", "course_id")
    assignment_ids = fields.One2many("uni.assignment", "course_id")

    _sql_constraints = [
        ("uni_course_code_uniq", "unique(code)", "Course code must be unique."),
    ]


class UniTimetable(models.Model):
    _name = "uni.timetable"
    _description = "Timetable Slot"
    _order = "weekday, start_hour"

    name = fields.Char(compute="_compute_name", store=True)
    course_id = fields.Many2one("uni.course", required=True)
    faculty_id = fields.Many2one("uni.faculty", required=True)
    term_id = fields.Many2one("uni.term", required=True)
    room = fields.Char(required=True)
    weekday = fields.Selection(
        [
            ("mon", "Monday"),
            ("tue", "Tuesday"),
            ("wed", "Wednesday"),
            ("thu", "Thursday"),
            ("fri", "Friday"),
            ("sat", "Saturday"),
            ("sun", "Sunday"),
        ],
        required=True,
    )
    start_hour = fields.Float(required=True)
    end_hour = fields.Float(required=True)

    @api.depends("course_id", "weekday", "start_hour", "room")
    def _compute_name(self):
        for record in self:
            record.name = f"{record.course_id.code or ''} {record.weekday or ''} {record.start_hour:.2f} {record.room or ''}".strip()

    @api.constrains("start_hour", "end_hour")
    def _check_hours(self):
        for record in self:
            if record.end_hour <= record.start_hour:
                raise ValidationError("Timetable end time must be after start time.")


class UniAttendance(models.Model):
    _name = "uni.attendance"
    _description = "Attendance Entry"
    _order = "session_date desc"

    student_id = fields.Many2one("uni.student", required=True)
    course_id = fields.Many2one("uni.course", required=True)
    faculty_id = fields.Many2one("uni.faculty")
    session_date = fields.Date(required=True, default=fields.Date.context_today)
    status = fields.Selection(
        [("present", "Present"), ("late", "Late"), ("absent", "Absent")],
        default="present",
        required=True,
    )
    note = fields.Char()


class UniAssignment(models.Model):
    _name = "uni.assignment"
    _description = "Assignment"
    _order = "due_date"

    name = fields.Char(required=True)
    course_id = fields.Many2one("uni.course", required=True)
    faculty_id = fields.Many2one("uni.faculty")
    owner_login = fields.Char(related="faculty_id.user_id.login", readonly=True)
    term_id = fields.Many2one("uni.term")
    due_date = fields.Date(required=True)
    total_marks = fields.Float(default=100.0)
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("late", "Late"), ("closed", "Closed")],
        default="draft",
        required=True,
    )
    instructions = fields.Text()


class UniGrade(models.Model):
    _name = "uni.grade"
    _description = "Grade"
    _order = "term_id desc, course_id"

    student_id = fields.Many2one("uni.student", required=True)
    course_id = fields.Many2one("uni.course", required=True)
    term_id = fields.Many2one("uni.term", required=True)
    credit_hours = fields.Float(default=3.0)
    percentage = fields.Float(required=True)
    letter_grade = fields.Char(compute="_compute_grade_fields", store=True)
    grade_point = fields.Float(compute="_compute_grade_fields", store=True)
    note = fields.Char()

    @api.depends("percentage")
    def _compute_grade_fields(self):
        for grade in self:
            pct = grade.percentage or 0.0
            if pct >= 90:
                grade.letter_grade = "A"
                grade.grade_point = 4.0
            elif pct >= 80:
                grade.letter_grade = "B"
                grade.grade_point = 3.0
            elif pct >= 70:
                grade.letter_grade = "C"
                grade.grade_point = 2.0
            elif pct >= 60:
                grade.letter_grade = "D"
                grade.grade_point = 1.0
            else:
                grade.letter_grade = "F"
                grade.grade_point = 0.0


class UniIssue(models.Model):
    _name = "uni.issue"
    _description = "Operational Issue"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "opened_on desc, priority desc"

    name = fields.Char(required=True, tracking=True)
    issue_type = fields.Selection(
        [
            ("crash", "Crash"),
            ("data", "Data Issue"),
            ("schedule", "Schedule Conflict"),
            ("registration", "Registration Blocker"),
            ("support", "Support Request"),
        ],
        required=True,
        default="support",
        tracking=True,
    )
    priority = fields.Selection(
        [("0", "Low"), ("1", "Medium"), ("2", "High"), ("3", "Critical")],
        default="1",
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [("open", "Open"), ("investigating", "Investigating"), ("blocked", "Blocked"), ("resolved", "Resolved")],
        default="open",
        required=True,
        tracking=True,
    )
    opened_on = fields.Date(default=fields.Date.context_today, required=True)
    assignee_faculty_id = fields.Many2one("uni.faculty", string="Assigned Faculty")
    student_id = fields.Many2one("uni.student")
    course_id = fields.Many2one("uni.course")
    description = fields.Text()
