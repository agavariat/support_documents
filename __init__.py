# -*- encoding: utf-8 -*-

from . import models
from odoo import api, SUPERUSER_ID


def _set_support_documents_journal(env):
    JournalObj = env['account.journal']
    companies = env['res.company'].search([])
    for company in companies:
        vals_journal = {
            'name': 'Support Documents',
            'type': 'purchase',
            'code': 'SD',
            'color': 11,
            'sequence': 6,
            'is_support_document': True,
            'company_id': company.id,
        }
        journal = JournalObj.create(vals_journal)


def support_documents_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _set_support_documents_journal(env)
