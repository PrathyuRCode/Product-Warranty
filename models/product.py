from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    warranty_period = fields.Integer(string="Warranty Period")
    warranty_type = fields.Selection(selection=[('one', 'Service Warranty'),
                                                ('two',
                                                 'Replacement Warranty')],
                                     string="Warranty Type")
    has_warranty = fields.Boolean(string="Has Warranty", default='True')
