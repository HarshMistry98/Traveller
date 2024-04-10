from odoo import fields, models, api
import requests

class ordersDetails(models.Model):
    _inherit = 'sale.order'
    _description = 'Order Details'

    shopify_orders_id = fields.Char("Shopify ID")
    def update_orders(self, response_data):

        for rec in self:
            orderenv = self.env['sale.order']

            orders = response_data.get('orders')
            for order in orders:

                customer_shopify_id = str(order.get('customer').get('id'))
                customer_id = self.env['res.partner'].search([('shopify_customer_id', '=', str(customer_shopify_id))])

                billing_name = order.get('billing_address').get('name')
                billing_id = self.env['res.partner'].search([('name', '=', billing_name)], limit=1)

                shipping_name = order.get('shipping_address').get('name')
                shipping_id = self.env['res.partner'].search([('name', '=', shipping_name)], limit=1)

                financial_status = order.get('financial_status')
                if financial_status in ['paid','partially_paid']:
                    payment_status = 'sale'
                else:
                    payment_status = 'draft'

                values = {
                    'shopify_orders_id': order.get('id'),
                    'partner_id': customer_id.id,
                    'partner_invoice_id': billing_id.id,
                    'partner_shipping_id': shipping_id.id,
                    'state': payment_status,
                }

                order_id = orderenv.search([('shopify_orders_id', '=', str(order.get('id')))])
                if not order_id:
                    order_id = orderenv.create(values)
                else:
                    order_id.write(values)

                line_items = order.get('line_items')
                for line_item in line_items:
                    variant_id = line_item.get('variant_id')

                    product_variant = self.env['product.product'].search([('shopify_variant_id', '=', str(variant_id) )])
                    product_variant_id = product_variant.id
                    product = product_variant.shopify_product_id

                    tax_ids = []
                    for tax in line_item.get('tax_lines'):
                        tax_rate = (tax.get('rate'))*100
                        tax_title = tax.get('title')
                        tax_group_id = self.env['account.tax.group'].search([('name','=',tax_title)], limit=1).id
                        tax_id = self.env['account.tax'].search([('type_tax_use','=','sale'),
                                                                 ('amount','=',tax_rate),
                                                                 ('tax_group_id','=',tax_group_id)]).id
                        tax_ids.append(tax_id)

                    print(tax_ids)

                    order_line_values = {
                        'order_id': order_id.id,
                        'product_id': product_variant_id,
                        'product_uom_qty': line_item.get('quantity'),
                        'tax_id': [(6, 0, tax_ids)],
                        'discount': float(line_item.get('total_discount')) * 100,
                    }

                    order_line = self.env['sale.order.line'].search([
                        ('order_id', '=', order_id.id),
                        ('product_id', '=', product_variant_id),
                        ('product_uom_qty', '=', line_item.get('quantity')),
                        ('tax_id', '=', tax_ids),
                        ('discount', '=', float(line_item.get('total_discount')) * 100),
                    ])
                    if not order_line:
                        order_line = self.env['sale.order.line'].create(order_line_values)
                    else:
                        order_line.write(order_line_values)

