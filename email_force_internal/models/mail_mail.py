# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.tools.safe_eval import safe_eval


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        """Don't send invitations to external partners"""
        IrParam = self.env['ir.config_parameter']
        check_models = IrParam.get_param('email_force_internal.models')
        check_models = safe_eval(check_models)
        if not isinstance(check_models, list):
            check_models = []
        for mail in self:
            if mail.model in check_models:
                partners_ids = []
                for partner in mail.recipient_ids:
                    domain = [('partner_id', '=', partner.id),
                              ('share', '=', False)]
                    user_id = self.env['res.users'].search(domain, limit=1)
                    if user_id:
                        partners_ids.append(partner.id)
                mail.write({'recipients_ids': [(6, 0, partners_ids)]})
        return super(MailMail, self).send(auto_commit=auto_commit,
                                          raise_exception=raise_exception)
