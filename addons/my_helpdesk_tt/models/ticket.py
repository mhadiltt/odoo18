from odoo import models, fields

class HelpdeskTicket(models.Model):
    _name = "my_helpdesk.ticket"
    _description = "Helpdesk Ticket"

    name = fields.Char(string="Subject", required=True)
    customer_name = fields.Char(string="Customer Name")
    email = fields.Char(string="Email")
    description = fields.Text(string="Description")
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], default='medium')
    state = fields.Selection([
        ('new', 'New'),
        ('open', 'Open'),
        ('done', 'Done'),
    ], default='new')
    assigned_to = fields.Many2one('res.users', string="Assigned To")
