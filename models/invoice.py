from odoo import fields, models


class InvoiceTemplate(models.Model):
    _inherit = 'account.move'

    new_field = fields.One2many("product.warranty.table",
                                "invoice_id", String='')
