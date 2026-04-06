from odoo.exceptions import AccessError, ValidationError
from odoo.http import Controller, request, route


class UniversityApiController(Controller):
    def _require_admin(self):
        if not request.env.user.has_group("uni_base.group_university_admin"):
            raise AccessError("Only university admins can perform this action.")

    def _current_student(self):
        return request.env["uni.student"].sudo().search([("user_id", "=", request.env.user.id)], limit=1)

    def _current_faculty(self):
        return request.env["uni.faculty"].sudo().search([("user_id", "=", request.env.user.id)], limit=1)

    def _require_student_or_admin(self):
        user = request.env.user
        if user.has_group("uni_base.group_university_admin"):
            return None
        if not user.has_group("uni_base.group_university_student"):
            raise AccessError("Only students or university admins can perform this action.")
        student = self._current_student()
        if not student:
            raise ValidationError("No student record is linked to this user.")
        return student

    def _require_faculty_or_admin(self):
        user = request.env.user
        if user.has_group("uni_base.group_university_admin"):
            return None
        if not user.has_group("uni_base.group_university_faculty"):
            raise AccessError("Only faculty or university admins can perform this action.")
        faculty = self._current_faculty()
        if not faculty:
            raise ValidationError("No faculty record is linked to this user.")
        return faculty

    def _create_assignment_questions(self, assignment, questions):
        question_model = request.env["uni.assignment.question"].sudo()
        assignment.question_ids.unlink()
        for index, question in enumerate(questions or [], start=1):
            question_model.create(
                {
                    "assignment_id": assignment.id,
                    "sequence": index * 10,
                    "question_text": question.get("question_text"),
                    "marks": float(question.get("marks", 1.0)),
                    "option_a": question.get("option_a"),
                    "option_b": question.get("option_b"),
                    "option_c": question.get("option_c"),
                    "option_d": question.get("option_d"),
                    "correct_option": question.get("correct_option"),
                }
            )

    def _create_exam_questions(self, exam, questions):
        question_model = request.env["uni.exam.question"].sudo()
        exam.question_ids.unlink()
        for index, question in enumerate(questions or [], start=1):
            question_model.create(
                {
                    "exam_id": exam.id,
                    "sequence": index * 10,
                    "question_text": question.get("question_text"),
                    "question_type": question.get("question_type", "mcq"),
                    "marks": float(question.get("marks", 1.0)),
                    "option_a": question.get("option_a"),
                    "option_b": question.get("option_b"),
                    "option_c": question.get("option_c"),
                    "option_d": question.get("option_d"),
                    "correct_option": question.get("correct_option"),
                }
            )

    @route("/uni/api/dashboard", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def university_dashboard(self):
        return request.env["res.users"].get_university_dashboard_data()

    @route("/uni/api/portal_data", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def university_portal_data(self):
        return request.env["res.users"].get_university_portal_data()

    @route("/uni/api/admissions/create", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def create_admission(self, values):
        admission = request.env["uni.admission"].sudo().create(values)
        return {"id": admission.id, "name": admission.name}

    @route("/uni/api/students/create", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def create_student(self, values):
        self._require_admin()
        payload = dict(values)
        user = False
        login = payload.pop("login", False)
        password = payload.pop("password", False)
        if login:
            user = request.env["res.users"].sudo().with_context(no_reset_password=True).create(
                {
                    "name": payload["name"],
                    "login": login,
                    "password": password or "student123",
                    "email": payload.get("email"),
                    "group_ids": [(6, 0, [
                        request.env.ref("base.group_user").id,
                        request.env.ref("uni_base.group_university_student").id,
                    ])],
                }
            )
        if user:
            payload["user_id"] = user.id
        student = request.env["uni.student"].sudo().create(payload)
        return {"id": student.id, "name": student.name, "user_login": student.user_login}

    @route("/uni/api/faculty/create", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def create_faculty(self, values):
        self._require_admin()
        payload = dict(values)
        user = False
        login = payload.pop("login", False)
        password = payload.pop("password", False)
        if login:
            user = request.env["res.users"].sudo().with_context(no_reset_password=True).create(
                {
                    "name": payload["name"],
                    "login": login,
                    "password": password or "faculty123",
                    "email": payload.get("email"),
                    "group_ids": [(6, 0, [
                        request.env.ref("base.group_user").id,
                        request.env.ref("uni_base.group_university_faculty").id,
                    ])],
                }
            )
        if user:
            payload["user_id"] = user.id
        faculty = request.env["uni.faculty"].sudo().create(payload)
        return {"id": faculty.id, "name": faculty.name, "user_login": faculty.user_login}

    @route("/uni/api/courses/create", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def create_course(self, values):
        self._require_admin()
        course = request.env["uni.course"].sudo().create(values)
        return {"id": course.id, "name": course.name, "code": course.code}

    @route("/uni/api/courses/update", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def update_course(self, course_id, values):
        self._require_admin()
        course = request.env["uni.course"].sudo().browse(course_id).exists()
        if not course:
            raise ValidationError("Course not found.")
        course.write(values)
        return {"id": course.id, "name": course.name, "code": course.code}

    @route("/uni/api/registrations/create", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def create_registration(self, values):
        student = self._require_student_or_admin()
        payload = dict(values)
        if student:
            payload["student_id"] = student.id
        course = request.env["uni.course"].sudo().browse(payload.get("course_id")).exists()
        if not course:
            raise ValidationError("Course not found.")
        term_id = payload.get("term_id") or course.term_id.id
        if not term_id:
            raise ValidationError("Course term is missing.")
        registration_model = request.env["uni.course.registration"].sudo()
        existing = registration_model.search(
            [("student_id", "=", payload["student_id"]), ("course_id", "=", course.id), ("term_id", "=", term_id)],
            limit=1,
        )
        if existing:
            return {"id": existing.id, "status": existing.status}
        active_count = registration_model.search_count([("course_id", "=", course.id), ("term_id", "=", term_id), ("status", "=", "registered")])
        status = "waitlist" if course.seat_limit and active_count >= course.seat_limit else "registered"
        registration = registration_model.create(
            {
                "student_id": payload["student_id"],
                "course_id": course.id,
                "term_id": term_id,
                "status": status,
                "note": payload.get("note"),
            }
        )
        return {"id": registration.id, "status": registration.status}

    @route("/uni/api/assignments/create", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def create_assignment(self, values):
        faculty = self._require_faculty_or_admin()
        payload = dict(values)
        questions = payload.pop("questions", [])
        if faculty:
            payload["faculty_id"] = faculty.id
        assignment = request.env["uni.assignment"].sudo().create(payload)
        if payload.get("assignment_type") == "quiz":
            self._create_assignment_questions(assignment, questions)
        return {"id": assignment.id, "name": assignment.name, "state": assignment.state}

    @route("/uni/api/assignments/update", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def update_assignment(self, assignment_id, values):
        faculty = self._require_faculty_or_admin()
        assignment = request.env["uni.assignment"].sudo().browse(assignment_id).exists()
        if not assignment:
            raise ValidationError("Assignment not found.")
        if faculty and assignment.faculty_id != faculty:
            raise AccessError("You can only edit your own assignments.")
        payload = dict(values)
        questions = payload.pop("questions", None)
        assignment.write(payload)
        if questions is not None:
            if assignment.assignment_type == "quiz":
                self._create_assignment_questions(assignment, questions)
            else:
                assignment.question_ids.unlink()
        return {"id": assignment.id, "name": assignment.name, "state": assignment.state}

    @route("/uni/api/assignments/publish", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def publish_assignment(self, assignment_id):
        faculty = self._require_faculty_or_admin()
        assignment = request.env["uni.assignment"].sudo().browse(assignment_id).exists()
        if not assignment:
            raise ValidationError("Assignment not found.")
        if faculty and assignment.faculty_id != faculty:
            raise AccessError("You can only publish your own assignments.")
        assignment.write({"state": "published"})
        return {"id": assignment.id, "state": assignment.state}

    @route("/uni/api/assignments/delete", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def delete_assignment(self, assignment_id):
        faculty = self._require_faculty_or_admin()
        assignment = request.env["uni.assignment"].sudo().browse(assignment_id).exists()
        if not assignment:
            raise ValidationError("Assignment not found.")
        if faculty and assignment.faculty_id != faculty:
            raise AccessError("You can only delete your own assignments.")
        assignment.unlink()
        return {"ok": True}

    @route("/uni/api/submissions/grade", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def grade_submission(self, submission_id, score, feedback=None):
        faculty = self._require_faculty_or_admin()
        submission = request.env["uni.assignment.submission"].sudo().browse(submission_id).exists()
        if not submission:
            raise ValidationError("Submission not found.")
        if faculty and submission.assignment_id.faculty_id != faculty:
            raise AccessError("You can only grade submissions for your own assignments.")
        submission.write({"score": float(score), "feedback": feedback or submission.feedback})
        submission.action_mark_graded()
        return {"id": submission.id, "state": submission.state, "score": submission.score}

    @route("/uni/api/submissions/create", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def create_submission(self, values):
        student = self._require_student_or_admin()
        payload = dict(values)
        if student:
            payload["student_id"] = student.id
        assignment = request.env["uni.assignment"].sudo().browse(payload.get("assignment_id")).exists()
        if not assignment:
            raise ValidationError("Assignment not found.")
        quiz_answers = payload.pop("quiz_answers", [])
        submission = request.env["uni.assignment.submission"].sudo().create(payload)
        if assignment.assignment_type == "quiz":
            answer_model = request.env["uni.assignment.answer"].sudo()
            for answer in quiz_answers:
                question = request.env["uni.assignment.question"].sudo().browse(answer.get("question_id")).exists()
                if not question or question.assignment_id != assignment:
                    continue
                awarded_marks = question.marks if answer.get("selected_option") == question.correct_option else 0.0
                answer_model.create(
                    {
                        "submission_id": submission.id,
                        "question_id": question.id,
                        "selected_option": answer.get("selected_option"),
                        "awarded_marks": awarded_marks,
                    }
                )
        submission.action_submit()
        return {"id": submission.id, "state": submission.state}

    @route("/uni/api/exams/create", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def create_exam(self, values):
        faculty = self._require_faculty_or_admin()
        payload = dict(values)
        questions = payload.pop("questions", [])
        if faculty and not payload.get("invigilator_id"):
            payload["invigilator_id"] = faculty.id
        exam = request.env["uni.exam"].sudo().create(payload)
        self._create_exam_questions(exam, questions)
        return {"id": exam.id, "name": exam.name, "state": exam.state}

    @route("/uni/api/exams/update", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def update_exam(self, exam_id, values):
        faculty = self._require_faculty_or_admin()
        exam = request.env["uni.exam"].sudo().browse(exam_id).exists()
        if not exam:
            raise ValidationError("Exam not found.")
        if faculty and exam.course_id.faculty_id != faculty:
            raise AccessError("You can only edit your own exams.")
        payload = dict(values)
        questions = payload.pop("questions", None)
        exam.write(payload)
        if questions is not None:
            self._create_exam_questions(exam, questions)
        return {"id": exam.id, "name": exam.name, "state": exam.state}

    @route("/uni/api/exams/publish", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def publish_exam(self, exam_id):
        faculty = self._require_faculty_or_admin()
        exam = request.env["uni.exam"].sudo().browse(exam_id).exists()
        if not exam:
            raise ValidationError("Exam not found.")
        if faculty and exam.course_id.faculty_id != faculty:
            raise AccessError("You can only publish your own exams.")
        exam.write({"state": "visible"})
        return {"id": exam.id, "state": exam.state}

    @route("/uni/api/exams/delete", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def delete_exam(self, exam_id):
        faculty = self._require_faculty_or_admin()
        exam = request.env["uni.exam"].sudo().browse(exam_id).exists()
        if not exam:
            raise ValidationError("Exam not found.")
        if faculty and exam.course_id.faculty_id != faculty:
            raise AccessError("You can only delete your own exams.")
        exam.unlink()
        return {"ok": True}

    @route("/uni/api/exam_results/upsert", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def upsert_exam_result(self, values):
        faculty = self._require_faculty_or_admin()
        payload = dict(values)
        exam = request.env["uni.exam"].sudo().browse(payload.get("exam_id")).exists()
        if not exam:
            raise ValidationError("Exam not found.")
        if faculty and exam.course_id.faculty_id != faculty:
            raise AccessError("You can only manage results for your own exams.")
        result_model = request.env["uni.exam.result"].sudo()
        result = result_model.search(
            [("exam_id", "=", exam.id), ("student_id", "=", payload.get("student_id"))],
            limit=1,
        )
        write_vals = {
            "score": float(payload.get("score", 0.0)),
            "note": payload.get("note"),
        }
        if result:
            result.write(write_vals)
        else:
            result = result_model.create(
                {
                    "exam_id": exam.id,
                    "student_id": payload.get("student_id"),
                    **write_vals,
                }
            )
        return {"id": result.id, "state": result.state, "score": result.score}

    @route("/uni/api/exams/submit", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def submit_exam(self, exam_id, answers):
        student = self._require_student_or_admin()
        exam = request.env["uni.exam"].sudo().browse(exam_id).exists()
        if not exam:
            raise ValidationError("Exam not found.")
        result_model = request.env["uni.exam.result"].sudo()
        answer_model = request.env["uni.exam.answer"].sudo()
        result = result_model.search([("exam_id", "=", exam.id), ("student_id", "=", student.id)], limit=1)
        if not result:
            result = result_model.create({"exam_id": exam.id, "student_id": student.id, "score": 0.0, "state": "draft"})
        else:
            result.answer_ids.unlink()
        for answer in answers or []:
            question = request.env["uni.exam.question"].sudo().browse(answer.get("question_id")).exists()
            if not question or question.exam_id != exam:
                continue
            awarded_marks = 0.0
            if question.question_type == "mcq":
                awarded_marks = question.marks if answer.get("selected_option") == question.correct_option else 0.0
            answer_model.create(
                {
                    "result_id": result.id,
                    "question_id": question.id,
                    "selected_option": answer.get("selected_option"),
                    "answer_text": answer.get("answer_text"),
                    "file_name": answer.get("file_name"),
                    "file_data": answer.get("file_data"),
                    "awarded_marks": awarded_marks,
                }
            )
        result.sync_scores()
        return {"id": result.id, "state": result.state, "score": result.score}

    @route("/uni/api/exam_results/grade_written", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def grade_written_exam_answers(self, result_id, grades=None, note=None):
        faculty = self._require_faculty_or_admin()
        result = request.env["uni.exam.result"].sudo().browse(result_id).exists()
        if not result:
            raise ValidationError("Exam result not found.")
        if faculty and result.exam_id.course_id.faculty_id != faculty:
            raise AccessError("You can only grade results for your own exams.")
        for grade in grades or []:
            answer = request.env["uni.exam.answer"].sudo().browse(grade.get("answer_id")).exists()
            if answer and answer.result_id == result and answer.question_id.question_type != "mcq":
                answer.write({"awarded_marks": float(grade.get("awarded_marks", 0.0))})
        if note is not None:
            result.write({"note": note})
        result.sync_scores()
        return {"id": result.id, "score": result.score, "state": result.state}

    @route("/uni/api/resits/create", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def create_resit_request(self, values):
        student = self._require_student_or_admin()
        payload = dict(values)
        if student:
            payload["student_id"] = student.id
        resit = request.env["uni.resit.request"].sudo().create(payload)
        resit.action_submit()
        return {"id": resit.id, "state": resit.state}

    @route("/uni/api/fees/pay", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def pay_fee_invoice(self, invoice_id, amount):
        student = self._require_student_or_admin()
        invoice = request.env["uni.fee.invoice"].sudo().browse(invoice_id).exists()
        if not invoice:
            return {"ok": False, "message": "Invoice not found"}
        if student and invoice.student_id != student:
            raise AccessError("You can only pay your own invoices.")
        new_paid = (invoice.amount_paid or 0.0) + float(amount)
        state = "partial"
        if new_paid >= invoice.amount_total:
            state = "paid"
        invoice.write({"amount_paid": new_paid, "state": state})
        return {"ok": True, "amount_paid": invoice.amount_paid, "balance_due": invoice.balance_due, "state": invoice.state}

    @route("/uni/api/exams/approve_results", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def approve_exam_results(self, exam_id):
        faculty = self._require_faculty_or_admin()
        exam = request.env["uni.exam"].sudo().browse(exam_id).exists()
        if not exam:
            return {"ok": False, "message": "Exam not found"}
        if faculty and exam.course_id.faculty_id != faculty:
            raise AccessError("You can only approve results for your own exams.")
        exam.action_approve_results()
        return {"ok": True, "state": exam.result_state}

    @route("/uni/api/exams/publish_results", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def publish_exam_results(self, exam_id):
        faculty = self._require_faculty_or_admin()
        exam = request.env["uni.exam"].sudo().browse(exam_id).exists()
        if not exam:
            return {"ok": False, "message": "Exam not found"}
        if faculty and exam.course_id.faculty_id != faculty:
            raise AccessError("You can only publish results for your own exams.")
        exam.action_publish_results()
        return {"ok": True, "state": exam.result_state}
