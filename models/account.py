# -*- encoding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, api, _


class AccountJournal(models.Model):

    _inherit = "account.journal"

    is_support_document = fields.Boolean('Is Support Document Journal?')


class AccountMove(models.Model):

    _inherit = "account.move"

    is_support_document = fields.Boolean('Is Support Document?', compute="_compute_is_support_document", store=True)

    @api.model
    def _search_default_journal(self, journal_types):
        company_id = self._context.get('default_company_id', self.env.company.id)
        domain = [('company_id', '=', company_id), ('type', 'in', journal_types)]

        if 'purchase' in journal_types:
            is_support_document = False
            if self.env.context.get('is_support_document'):
                is_support_document = True
            domain.append(('is_support_document', '=', is_support_document))

        journal = None
        if self._context.get('default_currency_id'):
            currency_domain = domain + [('currency_id', '=', self._context['default_currency_id'])]
            journal = self.env['account.journal'].search(currency_domain, limit=1)

        if not journal:
            journal = self.env['account.journal'].search(domain, limit=1)

        if not journal:
            company = self.env['res.company'].browse(company_id)

            error_msg = _(
                "No journal could be found in company %(company_name)s for any of those types: %(journal_types)s",
                company_name=company.display_name,
                journal_types=', '.join(journal_types),
            )
            raise UserError(error_msg)

        return journal

    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = m.invoice_filter_type_domain or 'general'
            company_id = m.company_id.id or self.env.company.id
            domain = [('company_id', '=', company_id), ('type', '=', journal_type)]
            if journal_type == 'purchase' and self.env.context.get('is_support_document'):
                domain.append(('is_support_document', '=', True))
            if journal_type == 'purchase' and not self.env.context.get('is_support_document'):
                domain.append(('is_support_document', '=', False))
            m.suitable_journal_ids = self.env['account.journal'].search(domain)

    @api.onchange('journal_id', 'move_type')
    def _onchange_journal_id_type(self):
        for move in self:
            move._compute_is_support_document()

    @api.depends('journal_id', 'move_type')
    def _compute_is_support_document(self):
        for move in self:
            move.is_support_document = False
            if move.journal_id and move.journal_id.is_support_document:
                move.is_support_document = True
