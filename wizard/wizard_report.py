import json

from odoo import fields, models
from odoo.exceptions import ValidationError
from odoo.tools import date_utils


class WarrantyReportWizard(models.TransientModel):
    _name = "warranty.wizard"

    product_ids = fields.Many2many('product.product', String="Product")
    customer_id = fields.Many2one('res.partner', string="Customer")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    def button_report(self, data=None):
        cr = self._cr
        query = """	select res_partner.name AS customer, reference_no,account_move.name AS invoice_id,product_template.name->>'en_US' As product,request_date from product_warranty_table
	inner join product_product
	on product_warranty_table.product_id =product_product.id
	inner join product_template
	on product_product.product_tmpl_id = product_template.id
	inner join account_move
	on product_warranty_table.invoice_id = account_move.id
	inner join res_partner
	on account_move.partner_id = res_partner.id where 1=1"""

        if self.product_ids:
            query += """ AND product_product.id = '%s'""" % self.product_ids.id

        if self.customer_id:
            query += """ AND account_move.partner_id =
             '%s'""" % self.customer_id.id
        if self.start_date:
            query += """ AND product_warranty_table.request_date >=
             '%s'""" % self.start_date
        if self.end_date:
            query += """ AND product_warranty_table.request_date <=
             '%s'""" % self.end_date

        cr.execute(query)
        sql_dict = cr.dictfetchall()
        data = {
            'product_ids': self.product_ids.name,
            'customer_id': self.customer_id.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'sql_data': sql_dict
        }
        return\
            self.env.ref('product_warranty.action_product_warranty').report_action(None,
                                                                                   data=data)

    def button_xl_report(self):

        return {
            'type': 'ir.actions.act_url',
            'url': '/product_warranty/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def get_report_lines(self, data=None):

        cr = self._cr
        query = """	select res_partner.name AS customer, reference_no,account_move.name AS invoice_id,product_template.name->>'en_US' As product,request_date from product_warranty_table
        	inner join product_product
        	on product_warranty_table.product_id =product_product.id
        	inner join product_template
        	on product_product.product_tmpl_id = product_template.id
        	inner join account_move
        	on product_warranty_table.invoice_id = account_move.id
        	inner join res_partner
        	on account_move.partner_id = res_partner.id where 1=1"""

        if self.product_ids:
            query += """ AND product_product.id =
             '%s'""" % self.product_ids.id

        if self.customer_id:
            query += """ AND account_move.partner_id =
             '%s'""" % self.customer_id.id
        if self.start_date:
            query += """ AND product_warranty_table.request_date >=
             '%s'""" % self.start_date
        if self.end_date:
            query += """ AND product_warranty_table.request_date <=
             '%s'""" % self.end_date

        cr.execute(query)
        sql_dict = cr.dictfetchall()
        if self.start_date > self.end_date:
            raise ValidationError('Start Date must be less than End Date')
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

        data = {
            'product_ids': self.product_ids.name,
            'customer_id': self.customer_id.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'sql_data': sql_dict
        }
        return data

    def button_js_report(self):
        if self.start_date > self.end_date:
            raise ValidationError('Start Date must be less than End Date')
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'product_ids': self.product_ids.id,
            'customer_id': self.customer_id.id
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'warranty.wizard',
                'options': json.dumps(data,
                                      default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': 'Excel Report',
            },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        cr = self._cr
        query = """	select res_partner.name AS customer, reference_no,account_move.name AS invoice_id,product_template.name->>'en_US' As product,request_date from product_warranty_table
               	inner join product_product
               	on product_warranty_table.product_id =product_product.id
               	inner join product_template
               	on product_product.product_tmpl_id = product_template.id
               	inner join account_move
               	on product_warranty_table.invoice_id = account_move.id
               	inner join res_partner
               	on account_move.partner_id = res_partner.id where 1=1"""

        if (data.get('product_ids')):
            query = query + """ AND product_product.id =
             '%s' """ % (data.get('product_ids'))

        if (data.get('customer_id')):
            query += """ AND account_move.partner_id =
             '%s'""" % (data.get('customer_id'))

        if (data.get('start_date')):
            query += """ AND product_warranty_table.request_date >=
             '%s'""" % (data.get('start_date'))

        if (data.get('end_date')):
            query += """ AND product_warranty_table.request_date <=
             '%s'""" % (data.get('end_date'))

        cr.execute(query)
        sql_dict = cr.dictfetchall()

        data = {
            'product_ids': self.product_ids.name,
            'customer_id': self.customer_id.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'sql_data': sql_dict
        }
        return data
