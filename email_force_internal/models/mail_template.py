# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.tools.safe_eval import safe_eval


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    @api.multi
    def generate_email(self, res_ids, fields=None):
        """Don't send mails to external partners"""
        res = super(MailTemplate, self).generate_email(res_ids, fields=fields)
        multi_mode = not isinstance(res_ids, (int, long))
        IrParam = self.env['ir.config_parameter']
        check_models = IrParam.get_param('email_force_internal.models')
        check_models = safe_eval(check_models)
        if not isinstance(check_models, list):
            check_models = []

        result = res.copy()

        def _remove_external(value):
            partner_ids = []
            for partner_id in value['partner_ids']:
                domain = [('partner_id', '=', partner_id),
                          ('share', '=', False)]
                user_id = self.env['res.users'].search(domain, limit=1)
                if user_id:
                    partner_ids.append(partner_id)
            return partner_ids

        if multi_mode:
            for key, values in res.items():
                if 'model' not in values or 'partner_ids' not in values:
                    continue
                if values['model'] in check_models:
                    partner_ids = _remove_external(values)
                    result[key]['partner_ids'] = partner_ids
        else:
            partner_ids = _remove_external(res)
            result['partner_ids'] = partner_ids
        return result
