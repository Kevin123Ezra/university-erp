from odoo import SUPERUSER_ID, api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _get_university_home_action(self):
        return self.env.ref("uni_ui.action_university_home", raise_if_not_found=False)

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
        role = "admin"
        highlights = [
            "Enrollment and success metrics will aggregate here.",
            "Cross-module alerts will replace static placeholders as models are added.",
        ]
        cards = [
            {"label": "Enrollment", "value": "0", "hint": "Active students"},
            {"label": "Revenue", "value": "$0", "hint": "Current semester billed"},
            {"label": "Risk Alerts", "value": "0", "hint": "Students needing follow-up"},
        ]
        quick_links = [
            {"label": "University Settings", "xmlid": "base.action_res_company_form"},
            {"label": "Users", "xmlid": "base.action_res_users"},
        ]
        if user.has_group("uni_base.group_university_student"):
            role = "student"
            highlights = [
                "Today's classes and attendance status will appear here.",
                "Assignments, GPA, and fee status widgets belong on this home screen.",
            ]
            cards = [
                {"label": "Today's Classes", "value": "0", "hint": "Scheduled lectures"},
                {"label": "Pending Work", "value": "0", "hint": "Assignments awaiting submission"},
                {"label": "Current GPA", "value": "0.00", "hint": "Semester GPA"},
            ]
            quick_links = []
        elif user.has_group("uni_base.group_university_faculty"):
            role = "faculty"
            highlights = [
                "Today's teaching load and grading queue will replace these placeholders.",
                "At-risk students can be surfaced directly from attendance and grades.",
            ]
            cards = [
                {"label": "Today's Lectures", "value": "0", "hint": "Scheduled sessions"},
                {"label": "Ungraded Work", "value": "0", "hint": "Submissions awaiting review"},
                {"label": "At-Risk Students", "value": "0", "hint": "Students needing intervention"},
            ]
            quick_links = []
        return {
            "role": role,
            "university_name": company.university_name or company.name,
            "tagline": company.university_tagline,
            "highlights": highlights,
            "cards": cards,
            "quick_links": quick_links,
        }


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.users"].search([])._sync_university_home_action()
