from odoo import fields, models, api
import datetime
from odoo.exceptions import ValidationError


class ProductWarranty(models.Model):
    _name = "product.warranty.table"
    _description = "Product Warranty"
    _rec_name = "reference_no"
    _inherit = 'mail.thread'

    reference_no = fields.Char(string='Sequence Number',
                               readonly=True)
    invoice_id = fields.Many2one('account.move',
                                 domain=[('state', '!=', 'draft'),
                                         ('move_type', '=', 'out_invoice')],
                                 required='True',  string="Invoice",)
    request_date = fields.Date(string="Request Date", required='True',
                               default=fields.Datetime.now)
    customer_id = fields.Many2one(related='invoice_id.partner_id',
                                  string="Customer Details")
    purchase_date = fields.Date(related='invoice_id.invoice_date',
                                string="Purchase Date")
    product_id = fields.Many2one('product.product', string="Product",
                                 required='True')
    lot_number_id = fields.Many2one('stock.lot', string="Lot/Serial Number")
    sample = fields.Integer(related='product_id.warranty_period')
    warranty_expiry_date = fields.Date(compute="_compute_warranty_expiry_date",
                                       string="Warranty Expiry Date")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('received', 'Product Received'),
        ('return', 'Return'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('reference_no', 'New') == 'New':
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'product.warranty.table') or 'New'
        res = super(ProductWarranty, self).create(vals)
        return res

    @api.onchange('invoice_id')
    def _onchange_invoice_id_show_products(self):
        products = self.invoice_id.invoice_line_ids.product_id.filtered(lambda sol: sol.has_warranty)
        return {'domain': {'product_id': [('id', 'in', products.ids)]}}

    @api.onchange('product_id')
    def _onchange_lot_no_change(self):
        return {'domain': {'lot_number_id': [
            ('product_id', 'in', self.product_id.ids)]}}

    @api.depends('purchase_date', 'sample')
    def _compute_warranty_expiry_date(self):
        for record in self:
            if record.purchase_date:
                days =\
                    record.purchase_date +\
                    datetime.timedelta(days=record.sample)
                record.warranty_expiry_date = days

            else:
                record.warranty_expiry_date = False

    def button_immediate_approve(self):
        self.state = 'approved'

    def button_immediate_cancel(self):
        self.state = 'cancel'

    def button_immediate_confirm(self):
        self.state = 'to_approve'
        if self.warranty_expiry_date < self.request_date:
            raise ValidationError('Warranty Expired')

    def button_immediate_received(self):
        self.state = 'received'

        product1 = self.product_id
        reference_no = self.reference_no
        source_loc = self.env.ref('stock.stock_location_customers')
        destination_loc = self.env.ref('product_warranty.warranty_location')

        move = self.env['stock.move'].create({
            'name': 'Use on Warranty location',
            'product_id': product1.id,
            'location_id': source_loc.id,
            'location_dest_id': destination_loc.id,
            'product_uom_qty': 1,
            'origin': reference_no

        })

        move._action_confirm()

        self.write({
            'state': 'received'
        })
        move.move_line_ids.write({'qty_done': 1})
        move._action_done()

    def button_immediate_return(self):
        self.state = 'return'

        product1 = self.product_id
        reference_no = self.reference_no
        source_loc = self.env.ref('product_warranty.warranty_location')
        destination_loc = self.env.ref('stock.stock_location_customers')

        move = self.env['stock.move'].create({
            'name': 'Return from Warranty location',
            'product_id': product1.id,
            'location_id': source_loc.id,
            'location_dest_id': destination_loc.id,
            'product_uom_qty': 1,
            'origin': reference_no

        })

        move._action_confirm()
        self.write({
            'state': 'done'
        })
        move.move_line_ids.write({'qty_done': 1})

        move.state = 'done'

    def smart_tab(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Move',
            'view_mode': 'tree',
            'view_id': self.env.ref('stock.view_move_tree').id,
            'res_model': 'stock.move',
            'domain': [('origin', '=', self.reference_no)]
        }
