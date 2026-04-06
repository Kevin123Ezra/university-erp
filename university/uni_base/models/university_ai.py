import json
import os
from urllib import error, request

from odoo import api, fields, models


class UniStudentRiskSnapshot(models.Model):
    _name = "uni.student.risk.snapshot"
    _description = "Student Risk Snapshot"
    _order = "generated_on desc, id desc"

    student_id = fields.Many2one("uni.student", required=True, ondelete="cascade")
    term_id = fields.Many2one("uni.term")
    attendance_rate = fields.Float()
    average_grade = fields.Float()
    missed_submissions = fields.Integer()
    late_submissions = fields.Integer()
    risk_level = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        required=True,
        default="low",
    )
    top_reason_1 = fields.Char()
    top_reason_2 = fields.Char()
    generated_on = fields.Datetime(default=fields.Datetime.now, required=True)
    source = fields.Selection([("gemini", "Gemini"), ("heuristic", "Heuristic")], default="heuristic", required=True)


class UniStudentAiMixin(models.Model):
    _inherit = "uni.student"

    risk_snapshot_ids = fields.One2many("uni.student.risk.snapshot", "student_id")
    risk_level = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        compute="_compute_risk_state",
    )
    risk_reason_summary = fields.Char(compute="_compute_risk_state")
    risk_generated_on = fields.Datetime(compute="_compute_risk_state")

    def _compute_risk_state(self):
        snapshot_model = self.env["uni.student.risk.snapshot"].sudo()
        for student in self:
            latest = snapshot_model.search([("student_id", "=", student.id)], limit=1, order="generated_on desc,id desc")
            student.risk_level = latest.risk_level if latest else "low"
            student.risk_reason_summary = ", ".join(filter(None, [latest.top_reason_1, latest.top_reason_2])) if latest else ""
            student.risk_generated_on = latest.generated_on if latest else False


class UniAiService(models.Model):
    _name = "uni.ai.service"
    _description = "University AI Service"

    def _load_env_file_value(self, key):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        env_path = os.path.join(root_dir, ".env")
        if not os.path.exists(env_path):
            return ""
        try:
            with open(env_path, "r", encoding="utf-8") as env_file:
                for raw_line in env_file:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    name, value = line.split("=", 1)
                    if name.strip() == key:
                        return value.strip().strip('"').strip("'")
        except OSError:
            return ""
        return ""

    def _get_api_key(self):
        company = self.env.company
        return (
            os.getenv("UNI_GEMINI_API_KEY")
            or self._load_env_file_value("UNI_GEMINI_API_KEY")
            or company.gemini_api_key
            or ""
        )

    def _call_gemini_json(self, prompt, schema_hint, inline_parts=None):
        api_key = self._get_api_key()
        if not api_key:
            return None
        payload = {
            "contents": [{"parts": ([{"text": f"{prompt}\n\nReturn JSON only. Schema: {schema_hint}"}] + (inline_parts or []))}],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={api_key}"
        )
        req = request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, ValueError):
            return None
        candidates = body.get("candidates") or []
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts if isinstance(part, dict)).strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except ValueError:
            return None

    def _risk_metrics(self, student):
        submissions = student.submission_ids
        graded_scores = [record.score for record in submissions if record.score not in (False, None)]
        return {
            "attendance_rate": round(student.attendance_rate or 0.0, 2),
            "average_grade": round(sum(graded_scores) / len(graded_scores), 2) if graded_scores else round(student.current_gpa * 25, 2),
            "missed_submissions": student.assignment_due_count - len(submissions.filtered(lambda item: item.state in ("submitted", "late", "graded"))),
            "late_submissions": len(submissions.filtered(lambda item: item.state == "late")),
        }

    def _heuristic_risk(self, student, metrics):
        reasons = []
        attendance = metrics["attendance_rate"]
        avg_grade = metrics["average_grade"]
        missed = max(metrics["missed_submissions"], 0)
        late = metrics["late_submissions"]
        if attendance < 60:
            level = "critical"
            reasons.append("Attendance is below 60 percent.")
        elif attendance < 75:
            level = "high"
            reasons.append("Attendance is below the 75 percent threshold.")
        elif avg_grade < 65 or missed >= 2:
            level = "medium"
        else:
            level = "low"
        if avg_grade < 60:
            level = "critical" if level in ("high", "critical") else "high"
            reasons.append("Average assessed score is below 60.")
        elif avg_grade < 70:
            reasons.append("Average assessed score is trending below a strong pass.")
        if missed > 0:
            reasons.append(f"{missed} assignment submission(s) are missing.")
        if late > 0:
            reasons.append(f"{late} submission(s) were late.")
        if not reasons:
            reasons = ["Attendance is stable.", "Assessment performance is currently on track."]
        return {"risk_level": level, "reasons": reasons[:2], "source": "heuristic"}

    def build_risk_assessment(self, student):
        metrics = self._risk_metrics(student)
        prompt = (
            "You are classifying university student academic risk.\n"
            f"Student: {student.name}\n"
            f"Attendance rate: {metrics['attendance_rate']}\n"
            f"Average grade: {metrics['average_grade']}\n"
            f"Missed submissions: {metrics['missed_submissions']}\n"
            f"Late submissions: {metrics['late_submissions']}\n"
            "Return low, medium, high, or critical plus two short plain-English reasons."
        )
        schema_hint = '{"risk_level":"low|medium|high|critical","reasons":["reason one","reason two"]}'
        result = self._call_gemini_json(prompt, schema_hint)
        if result and result.get("risk_level") in {"low", "medium", "high", "critical"}:
            return {
                "risk_level": result["risk_level"],
                "reasons": list((result.get("reasons") or []))[:2],
                "metrics": metrics,
                "source": "gemini",
            }
        heuristic = self._heuristic_risk(student, metrics)
        heuristic["metrics"] = metrics
        return heuristic

    def run_weekly_risk_scan(self):
        snapshot_model = self.env["uni.student.risk.snapshot"].sudo()
        notification_model = self.env["uni.notification"].sudo()
        activity_model = self.env["mail.activity"].sudo()
        todo_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        students = self.env["uni.student"].sudo().search([])
        for student in students:
            assessment = self.build_risk_assessment(student)
            metrics = assessment["metrics"]
            snapshot = snapshot_model.create(
                {
                    "student_id": student.id,
                    "term_id": student.term_id.id,
                    "attendance_rate": metrics["attendance_rate"],
                    "average_grade": metrics["average_grade"],
                    "missed_submissions": max(metrics["missed_submissions"], 0),
                    "late_submissions": metrics["late_submissions"],
                    "risk_level": assessment["risk_level"],
                    "top_reason_1": (assessment["reasons"] + [""])[:2][0],
                    "top_reason_2": (assessment["reasons"] + [""])[:2][1],
                    "source": assessment["source"],
                }
            )
            if snapshot.risk_level in ("high", "critical") and student.advisor_id and student.advisor_id.user_id:
                notification_model.create(
                    {
                        "name": f"At-risk alert: {student.name}",
                        "notification_type": "system_issue",
                        "audience": "faculty",
                        "state": "queued",
                        "message": f"{student.name} is currently flagged as {snapshot.risk_level}. Reasons: {student.risk_reason_summary or snapshot.top_reason_1}.",
                    }
                )
                if todo_type:
                    activity_model.create(
                        {
                            "activity_type_id": todo_type.id,
                            "summary": f"Review at-risk student: {student.name}",
                            "note": "\n".join(filter(None, [snapshot.top_reason_1, snapshot.top_reason_2])),
                            "res_model_id": self.env["ir.model"]._get_id("uni.student"),
                            "res_id": student.id,
                            "user_id": student.advisor_id.user_id.id,
                        }
                    )
        return True

    def build_study_assistant(self, notes, course_name="", file_name="", file_data=""):
        inline_parts = []
        if file_name and file_data:
            mime_type = "application/pdf" if str(file_name).lower().endswith(".pdf") else "text/plain"
            inline_parts.append({"inlineData": {"mimeType": mime_type, "data": file_data}})
        prompt = (
            "You are a university study assistant.\n"
            f"Course: {course_name or 'General'}\n"
            f"Notes:\n{notes or 'See attached notes file.'}\n\n"
            "Return a short summary, three key bullets, five practice MCQs with correct answers, and one gap analysis note."
        )
        schema_hint = (
            '{"summary":["bullet 1","bullet 2","bullet 3"],'
            '"mcqs":[{"question":"...","options":["A","B","C","D"],"answer":"A"}],'
            '"gap_analysis":"..."}'
        )
        result = self._call_gemini_json(prompt, schema_hint, inline_parts=inline_parts)
        if result:
            return result
        sentences = [segment.strip() for segment in notes.replace("\n", " ").split(".") if segment.strip()]
        summary = sentences[:3] or ["Your notes were analyzed and condensed into study highlights."]
        seed = course_name or "this course"
        return {
            "summary": [item[:180] for item in summary[:3]],
            "mcqs": [
                {
                    "question": f"What is the strongest takeaway from {seed} topic {index + 1}?",
                    "options": ["Core concept", "Irrelevant detail", "Historical footnote", "Formatting choice"],
                    "answer": "Core concept",
                }
                for index in range(5)
            ],
            "gap_analysis": f"Review any missing worked examples, diagrams, and edge cases for {seed}.",
        }

    def build_feedback_draft(self, assignment_title, student_name, score, short_note):
        prompt = (
            "Write a concise constructive feedback paragraph for a student.\n"
            f"Assignment: {assignment_title}\nStudent: {student_name}\nScore: {score}\nFaculty notes: {short_note}\n"
            "Return JSON with one key named feedback."
        )
        result = self._call_gemini_json(prompt, '{"feedback":"2-3 sentence feedback"}')
        if result and result.get("feedback"):
            return result["feedback"]
        score = float(score or 0.0)
        if score >= 85:
            tone = "Your work shows strong understanding and consistent execution."
        elif score >= 70:
            tone = "Your work is on the right track, with a solid base in the core ideas."
        else:
            tone = "Your submission needs a stronger grasp of the core concepts and clearer execution."
        note = short_note or "Focus on the main requirements and support your ideas with clearer evidence."
        return f"{tone} {note} Keep refining the structure and accuracy of your responses before the next submission."
