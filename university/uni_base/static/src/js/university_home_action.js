/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class UniversityHomeAction extends Component {
    static template = "uni_base.UniversityHomeAction";
    static props = {
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        className: { type: String, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.state = useState({
            loading: true,
            role: "admin",
            university_name: "",
            tagline: "",
            highlights: [],
            cards: [],
            quick_links: [],
        });

        onWillStart(async () => {
            const data = await this.orm.call("res.users", "get_university_dashboard_data", []);
            Object.assign(this.state, data, { loading: false });
        });
    }

    openAction(xmlid) {
        if (!xmlid) {
            return;
        }
        this.actionService.doAction(xmlid);
    }
}

registry.category("actions").add("uni_base.university_home", UniversityHomeAction);
