{
    "name": "University Base",
    "summary": "University ERP foundation, branding, and role-aware entry experience",
    "category": "Education",
    "depends": ["base", "mail", "web"],
    "application": True,
    "data": [
        "data/university_security.xml",
        "data/university_home_action.xml",
        "data/university_demo_users.xml",
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/university_core_views.xml",
        "views/university_extended_views.xml",
        "views/login_templates.xml",
        "views/university_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "uni_base/static/src/scss/university_theme.scss",
            "uni_base/static/src/js/university_home_action.js",
            "uni_base/static/src/xml/university_home_action.xml",
        ],
        "web.assets_frontend": [
            "uni_base/static/src/scss/university_theme.scss",
        ],
    },
    "post_init_hook": "post_init_hook",
    "license": "LGPL-3",
}
