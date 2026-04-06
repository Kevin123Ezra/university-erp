{
    "name": "University UI",
    "summary": "Branded entry experience and role-aware navigation for the university ERP",
    "category": "Education",
    "depends": ["web", "uni_base"],
    "application": False,
    "installable": False,
    "data": [
        "data/university_home_action.xml",
        "views/login_templates.xml",
        "views/university_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "uni_ui/static/src/scss/university_theme.scss",
            "uni_ui/static/src/js/university_home_action.js",
            "uni_ui/static/src/xml/university_home_action.xml",
        ],
        "web.assets_frontend": [
            "uni_ui/static/src/scss/university_theme.scss",
        ],
    },
    "post_init_hook": "post_init_hook",
    "license": "LGPL-3",
}
