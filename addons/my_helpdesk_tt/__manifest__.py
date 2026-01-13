{
    'name': 'My Helpdesk TT',
    'version': '18.0.1.0',
    'category': 'Services',
    'summary': 'Simple Helpdesk System',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/ticket_views.xml',
    ],
    'application': True,
    'installable': True,
}
