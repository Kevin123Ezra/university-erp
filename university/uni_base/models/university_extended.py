from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniExam(models.Model):
    _name = "uni.exam"
    _description = "Exam"
    _order = "exam_date, start_hour"

    name = fields.Char(required=True)
    course_id = fields.Many2one("uni.course", required=True)
    term_id = fields.Many2one("uni.term", required=True)
    exam_date = fields.Date(required=True)
    start_hour = fields.Float(required=True)
    end_hour = fields.Float(required=True)
    room = fields.Char(required=True)
    capacity = fields.Integer(default=40)
    invigilator_id = fields.Many2one("uni.faculty")
    delivery_mode = fields.Selection([("online", "Online")], default="online", required=True)
    question_ids = fields.One2many("uni.exam.question", "exam_id")
    question_count = fields.Integer(compute="_compute_question_count")
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("visible", "Visible")],
        default="draft",
        required=True,
    )

    def _compute_question_count(self):
        for record in self:
            record.question_count = len(record.question_ids)

    @api.constrains("start_hour", "end_hour")
    def _check_exam_hours(self):
        for record in self:
            if record.end_hour <= record.start_hour:
                raise ValidationError("Exam end time must be after start time.")


class UniCourseRegistration(models.Model):
    _name = "uni.course.registration"
    _description = "Course Registration"
    _order = "create_date desc"

    student_id = fields.Many2one("uni.student", required=True)
    course_id = fields.Many2one("uni.course", required=True)
    term_id = fields.Many2one("uni.term", required=True)
    status = fields.Selection(
        [("registered", "Registered"), ("waitlist", "Waitlist"), ("dropped", "Dropped")],
        default="registered",
        required=True,
    )
    registered_on = fields.Date(default=fields.Date.context_today, required=True)
    note = fields.Char()

    _sql_constraints = [
        (
            "uni_course_registration_uniq",
            "unique(student_id, course_id, term_id)",
            "A student can only have one registration per course and term.",
        ),
    ]


class UniFeeInvoice(models.Model):
    _name = "uni.fee.invoice"
    _description = "Fee Invoice"
    _order = "due_date desc"

    name = fields.Char(required=True)
    student_id = fields.Many2one("uni.student", required=True)
    term_id = fields.Many2one("uni.term", required=True)
    amount_total = fields.Float(required=True)
    amount_paid = fields.Float(default=0.0)
    due_date = fields.Date(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted"), ("partial", "Partial"), ("paid", "Paid"), ("overdue", "Overdue")],
        default="draft",
        required=True,
    )
    scholarship_id = fields.Many2one("uni.scholarship")
    balance_due = fields.Float(compute="_compute_balance_due", store=True)

    @api.depends("amount_total", "amount_paid")
    def _compute_balance_due(self):
        for record in self:
            record.balance_due = max((record.amount_total or 0.0) - (record.amount_paid or 0.0), 0.0)


class UniScholarship(models.Model):
    _name = "uni.scholarship"
    _description = "Scholarship"
    _order = "name"

    name = fields.Char(required=True)
    scholarship_type = fields.Selection(
        [("merit", "Merit Based"), ("need", "Need Based")],
        required=True,
        default="merit",
    )
    amount = fields.Float(required=True)
    student_id = fields.Many2one("uni.student")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="draft",
        required=True,
    )
    note = fields.Char()


class UniLibraryItem(models.Model):
    _name = "uni.library.item"
    _description = "Library Item"
    _order = "title"

    title = fields.Char(required=True)
    author = fields.Char()
    isbn = fields.Char()
    course_id = fields.Many2one("uni.course")
    available_copies = fields.Integer(default=1)
    digital_link = fields.Char()


class UniLibraryLoan(models.Model):
    _name = "uni.library.loan"
    _description = "Library Loan"
    _order = "borrow_date desc"

    item_id = fields.Many2one("uni.library.item", required=True)
    student_id = fields.Many2one("uni.student", required=True)
    borrow_date = fields.Date(default=fields.Date.context_today, required=True)
    due_date = fields.Date(required=True)
    return_date = fields.Date()
    state = fields.Selection(
        [("borrowed", "Borrowed"), ("returned", "Returned"), ("overdue", "Overdue")],
        default="borrowed",
        required=True,
    )
    fine_amount = fields.Float(default=0.0)


class UniNotification(models.Model):
    _name = "uni.notification"
    _description = "University Notification"
    _order = "schedule_date desc, id desc"

    name = fields.Char(required=True)
    notification_type = fields.Selection(
        [
            ("class_cancelled", "Class Cancelled"),
            ("assignment_due", "Assignment Due"),
            ("result_published", "Result Published"),
            ("fee_overdue", "Fee Overdue"),
            ("system_issue", "System Issue"),
        ],
        required=True,
        default="assignment_due",
    )
    audience = fields.Selection(
        [("student", "Student"), ("faculty", "Faculty"), ("admin", "Admin"), ("all", "All Users")],
        required=True,
        default="student",
    )
    schedule_date = fields.Datetime(default=fields.Datetime.now, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("queued", "Queued"), ("sent", "Sent")],
        default="draft",
        required=True,
    )
    message = fields.Text(required=True)


class UniAdmission(models.Model):
    _name = "uni.admission"
    _description = "Admission Application"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "application_date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    department_id = fields.Many2one("uni.department", required=True, tracking=True)
    term_id = fields.Many2one("uni.term", required=True, tracking=True)
    application_date = fields.Date(default=fields.Date.context_today, required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("review", "In Review"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            ("enrolled", "Enrolled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    notes = fields.Text()
    student_id = fields.Many2one("uni.student", readonly=True)

    def action_mark_submitted(self):
        self.write({"state": "submitted"})

    def action_accept(self):
        self.write({"state": "accepted"})

    def action_reject(self):
        self.write({"state": "rejected"})

    def action_enroll(self):
        student_model = self.env["uni.student"]
        for record in self:
            if not record.student_id:
                student = student_model.create(
                    {
                        "name": record.name,
                        "email": record.email,
                        "student_number": self.env["ir.sequence"].next_by_code("uni.student.number") or f"STU-{record.id}",
                        "department_id": record.department_id.id,
                        "term_id": record.term_id.id,
                        "state": "enrolled",
                    }
                )
                record.student_id = student.id
            record.state = "enrolled"


class UniAssignmentSubmission(models.Model):
    _name = "uni.assignment.submission"
    _description = "Assignment Submission"
    _order = "submission_date desc, id desc"

    assignment_id = fields.Many2one("uni.assignment", required=True)
    student_id = fields.Many2one("uni.student", required=True)
    submission_date = fields.Datetime(default=fields.Datetime.now, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("late", "Late"), ("graded", "Graded")],
        default="draft",
        required=True,
    )
    file_name = fields.Char()
    file_data = fields.Binary(attachment=True)
    score = fields.Float()
    feedback = fields.Text()
    submission_type = fields.Selection(related="assignment_id.assignment_type", readonly=True)
    answer_ids = fields.One2many("uni.assignment.answer", "submission_id")

    @api.constrains("assignment_id", "student_id")
    def _check_unique_submission(self):
        for record in self:
            dup = self.search(
                [
                    ("assignment_id", "=", record.assignment_id.id),
                    ("student_id", "=", record.student_id.id),
                    ("id", "!=", record.id),
                ],
                limit=1,
            )
            if dup:
                raise ValidationError("Each student can only submit one record per assignment.")

    def action_submit(self):
        for record in self:
            if record.assignment_id.assignment_type == "quiz":
                state = "graded"
                record.score = sum(record.answer_ids.mapped("awarded_marks"))
            else:
                state = "submitted"
                if record.assignment_id.due_date and fields.Date.to_date(record.submission_date.date()) > record.assignment_id.due_date:
                    state = "late"
            record.state = state

    def action_mark_graded(self):
        self.write({"state": "graded"})


class UniExamResult(models.Model):
    _name = "uni.exam.result"
    _description = "Exam Result"
    _order = "exam_id, student_id"

    exam_id = fields.Many2one("uni.exam", required=True)
    student_id = fields.Many2one("uni.student", required=True)
    score = fields.Float(required=True)
    auto_score = fields.Float(default=0.0)
    manual_score = fields.Float(default=0.0)
    submitted_on = fields.Datetime(default=fields.Datetime.now)
    answer_ids = fields.One2many("uni.exam.answer", "result_id")
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("visible", "Visible")],
        default="draft",
        required=True,
    )
    note = fields.Char()

    def sync_scores(self):
        for record in self:
            auto_score = sum(record.answer_ids.filtered(lambda answer: answer.question_id.question_type == "mcq").mapped("awarded_marks"))
            manual_score = sum(record.answer_ids.filtered(lambda answer: answer.question_id.question_type != "mcq").mapped("awarded_marks"))
            record.write({"auto_score": auto_score, "manual_score": manual_score, "score": auto_score + manual_score})


class UniResitRequest(models.Model):
    _name = "uni.resit.request"
    _description = "Resit Request"
    _order = "request_date desc, id desc"

    exam_result_id = fields.Many2one("uni.exam.result", required=True)
    student_id = fields.Many2one("uni.student", required=True)
    request_date = fields.Date(default=fields.Date.context_today, required=True)
    reason = fields.Text()
    fee_invoice_id = fields.Many2one("uni.fee.invoice", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="draft",
        required=True,
    )

    def action_submit(self):
        self.write({"state": "submitted"})

    def action_approve(self):
        fee_model = self.env["uni.fee.invoice"]
        for record in self:
            if not record.fee_invoice_id:
                fee = fee_model.create(
                    {
                        "name": f"Resit Fee - {record.exam_result_id.exam_id.name}",
                        "student_id": record.student_id.id,
                        "term_id": record.exam_result_id.exam_id.term_id.id,
                        "amount_total": 250.0,
                        "amount_paid": 0.0,
                        "due_date": fields.Date.context_today(self),
                        "state": "posted",
                    }
                )
                record.fee_invoice_id = fee.id
            record.state = "approved"

    def action_reject(self):
        self.write({"state": "rejected"})


class UniStudentExtended(models.Model):
    _inherit = "uni.student"

    admission_ids = fields.One2many("uni.admission", "student_id")
    submission_ids = fields.One2many("uni.assignment.submission", "student_id")
    exam_result_ids = fields.One2many("uni.exam.result", "student_id")
    resit_request_ids = fields.One2many("uni.resit.request", "student_id")
    fee_invoice_ids = fields.One2many("uni.fee.invoice", "student_id")
    overdue_invoice_count = fields.Integer(compute="_compute_finance_metrics")
    exam_blocked = fields.Boolean(compute="_compute_finance_metrics")

    def _compute_finance_metrics(self):
        today = fields.Date.context_today(self)
        for student in self:
            overdue = student.fee_invoice_ids.filtered(
                lambda inv: inv.balance_due > 0 and inv.due_date and inv.due_date < today and inv.state in ("posted", "partial", "overdue")
            )
            student.overdue_invoice_count = len(overdue)
            student.exam_blocked = bool(overdue)


class UniAssignmentExtended(models.Model):
    _inherit = "uni.assignment"

    submission_ids = fields.One2many("uni.assignment.submission", "assignment_id")
    submission_count = fields.Integer(compute="_compute_submission_count")
    assignment_type = fields.Selection([("upload", "Upload"), ("quiz", "Quiz")], default="upload", required=True)
    instruction_file_name = fields.Char()
    instruction_file_data = fields.Binary(attachment=True)
    question_ids = fields.One2many("uni.assignment.question", "assignment_id")
    question_count = fields.Integer(compute="_compute_submission_count")

    def _compute_submission_count(self):
        for assignment in self:
            assignment.submission_count = len(assignment.submission_ids)
            assignment.question_count = len(assignment.question_ids)


class UniExamExtended(models.Model):
    _inherit = "uni.exam"

    result_ids = fields.One2many("uni.exam.result", "exam_id")
    result_state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("visible", "Visible")],
        default="draft",
        required=True,
    )

    def action_approve_results(self):
        self.write({"result_state": "approved"})
        self.mapped("result_ids").write({"state": "approved"})

    def action_publish_results(self):
        self.write({"result_state": "visible", "state": "visible"})
        self.mapped("result_ids").write({"state": "visible"})


class UniExamQuestion(models.Model):
    _name = "uni.exam.question"
    _description = "Exam Question"
    _order = "sequence, id"

    exam_id = fields.Many2one("uni.exam", required=True)
    sequence = fields.Integer(default=10)
    question_text = fields.Text(required=True)
    question_type = fields.Selection([("mcq", "MCQ"), ("text", "Text"), ("upload", "Upload")], required=True, default="mcq")
    marks = fields.Float(default=1.0, required=True)
    option_a = fields.Char()
    option_b = fields.Char()
    option_c = fields.Char()
    option_d = fields.Char()
    correct_option = fields.Selection([("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")])


class UniExamAnswer(models.Model):
    _name = "uni.exam.answer"
    _description = "Exam Answer"
    _order = "id"

    result_id = fields.Many2one("uni.exam.result", required=True)
    question_id = fields.Many2one("uni.exam.question", required=True)
    selected_option = fields.Selection([("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")])
    answer_text = fields.Text()
    file_name = fields.Char()
    file_data = fields.Binary(attachment=True)
    awarded_marks = fields.Float(default=0.0)


class UniAssignmentQuestion(models.Model):
    _name = "uni.assignment.question"
    _description = "Assignment Quiz Question"
    _order = "sequence, id"

    assignment_id = fields.Many2one("uni.assignment", required=True)
    sequence = fields.Integer(default=10)
    question_text = fields.Text(required=True)
    marks = fields.Float(default=1.0, required=True)
    option_a = fields.Char(required=True)
    option_b = fields.Char(required=True)
    option_c = fields.Char(required=True)
    option_d = fields.Char(required=True)
    correct_option = fields.Selection([("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], required=True)


class UniAssignmentAnswer(models.Model):
    _name = "uni.assignment.answer"
    _description = "Assignment Quiz Answer"
    _order = "id"

    submission_id = fields.Many2one("uni.assignment.submission", required=True)
    question_id = fields.Many2one("uni.assignment.question", required=True)
    selected_option = fields.Selection([("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")])
    awarded_marks = fields.Float(default=0.0)


class UniFeeInvoiceExtended(models.Model):
    _inherit = "uni.fee.invoice"

    scholarship_discount = fields.Float(compute="_compute_balance_due", store=True)
    is_exam_blocking = fields.Boolean(compute="_compute_flags", store=True)

    @api.depends("amount_total", "amount_paid", "scholarship_id.amount", "scholarship_id.state")
    def _compute_balance_due(self):
        for invoice in self:
            discount = invoice.scholarship_id.amount if invoice.scholarship_id and invoice.scholarship_id.state == "approved" else 0.0
            net_total = max((invoice.amount_total or 0.0) - discount, 0.0)
            invoice.scholarship_discount = discount
            invoice.balance_due = max(net_total - (invoice.amount_paid or 0.0), 0.0)

    @api.depends("balance_due", "due_date", "state")
    def _compute_flags(self):
        today = fields.Date.context_today(self)
        for invoice in self:
            invoice.is_exam_blocking = bool(
                invoice.balance_due > 0 and invoice.due_date and invoice.due_date < today and invoice.state in ("posted", "partial", "overdue")
            )
