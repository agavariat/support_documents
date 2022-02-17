# -*- encoding: utf-8 -*-
{
    'name': 'Support Documents',
    'version': '12.0.0.1',
    'description': """Support Documents""",
    'depends': [
        'account',
    ],
    'data': [
        'views/account_view.xml',
    ],
    'post_init_hook': 'support_documents_post_init',
    'installable': True,
    'application': True,
}
