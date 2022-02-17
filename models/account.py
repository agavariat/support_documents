# -*- encoding: utf-8 -*-

from odoo import models, fields, api

TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}


class AccountJournal(models.Model):

    _inherit = "account.journal"

    is_support_document = fields.Boolean('Is Support Document Journal?')


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    is_support_document = fields.Boolean(
        'Is Support Document?', compute="_compute_is_support_document", store=True)

    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', [TYPE2JOURNAL[ty] for ty in inv_types if ty in TYPE2JOURNAL]),
            ('company_id', '=', company_id),
        ]
        if self._context.get('type', 'out_invoice') == 'in_invoice' and self._context.get('is_support_document'):
            domain.append(('is_support_document', '=', True))

        company_currency_id = self.env['res.company'].browse(company_id).currency_id.id
        currency_id = self._context.get('default_currency_id') or company_currency_id
        currency_clause = [('currency_id', '=', currency_id)]
        if currency_id == company_currency_id:
            currency_clause = ['|', ('currency_id', '=', False)] + currency_clause
        return (
            self.env['account.journal'].search(domain + currency_clause, limit=1)
            or self.env['account.journal'].search(domain, limit=1)
        )

    def _get_journal_domain(self):
        domain = "[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale'], 'in_refund': ['purchase'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id)]"
        if self._context.get('type', '') == 'in_invoice' and self._context.get('is_support_document'):
            domain = "[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale'], 'in_refund': ['purchase'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id), ('is_support_document', '=', True)]"
        elif self._context.get('type', '') == 'in_invoice' and not self._context.get('is_support_document'):
            domain = "[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale'], 'in_refund': ['purchase'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id), ('is_support_document', '=', False)]"
        return domain

    journal_id = fields.Many2one('account.journal', string='Journal',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=_default_journal,
                                 domain=_get_journal_domain)

    @api.onchange('journal_id', 'type')
    def _onchange_journal_id_type(self):
        for move in self:
            move._compute_is_support_document()

    @api.depends('journal_id', 'type')
    def _compute_is_support_document(self):
        for move in self:
            move.is_support_document = False
            if move.journal_id and move.journal_id.is_support_document:
                move.is_support_document = True
