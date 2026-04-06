from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    university_name = fields.Char(default="Visionary Minds University")
    university_tagline = fields.Char(
        default="Bold academic operations for modern learning, teaching, and campus life."
    )
    university_code = fields.Char(default="VMU")
    university_primary_color = fields.Char(default="#005f73")
    university_secondary_color = fields.Char(default="#ee9b00")
    university_accent_color = fields.Char(default="#94d2bd")
