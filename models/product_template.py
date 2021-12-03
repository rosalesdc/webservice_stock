# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #Algunos campos que se deberían empatar con el otro sistema
    owner = fields.Char('Owner')
    commercial_amount = fields.Float('Commercial Amount')

    def consume_json_cron(self):
        print("Ejecutanto CREACION:::::")
        # TODO url podría ser parámetro configurable
        url = "http://172.17.0.2:8069/webservice_stock/static/description/json_event_products.json"
        json_objetc = requests.get(url).json()
        num_events = json_objetc["info"]["num_events"]
        event_data = json_objetc["events"]
        messages = json_objetc["info"]["messages"]
        errors = json_objetc["info"]["errors"]

        if num_events > 0:
            print("HAY EVENTOS NUEVOS ::::")
            for event in event_data:
                if event['type'] == "create":
                    self.create_product(event['product_id'], event['vals'])
                elif event['type'] == 'update':
                    self.update_product(event['product_id'], event['vals'])
                elif event['type'] == 'split':
                    self.split_product(event['product_id'], event['product_childs'])
                elif event['type'] == 'join':
                    self.join_product(event['product_ids'], event['product_result'])
                elif event['type'] == 'delete':
                    self.delete_product(event['product_id'])
        if messages:
            print("PINTAR MENSAJES ::::::")
        if errors:
            print("PINTAR ERRORES ::::::")

    def create_product(self, product_id, product_vals):
        print('Creando un producto')
        new_product = self.env['product.template'].create({
            'name': product_id,
            'detailed_type': 'product',
            'owner': product_vals['owner'],
            'commercial_amount': product_vals['commercial_amount']
        })

    def update_product(self, product_id, product_vals):
        print('Actualizando un producto')
        product = self.env['product.template'].search([('name', '=', product_id)], limit=1)
        if product:
            product.write(product_vals)

    def split_product(self, product_id, prod_childs):
        print('Dividiendo un producto')
        product = self.env['product.template'].search([('name', '=', product_id)], limit=1)
        #Crea los hijos y después archiva al padre
        if product:
            for prod in prod_childs:
                self.create_product(prod['product_id'], prod['vals'])
            product.write({'active':False})

    def join_product(self, product_ids, prod_result):
        print('Uniendo Productos')
        #Crea el producto resultado y después archiva los productos que se unen
        self.create_product(prod_result['product_id'], prod_result['vals'])
        for prod in product_ids:
            product = self.env['product.template'].search([('name', '=', prod)], limit=1)
            if product:
                product.write({'active':False})

    def delete_product(self, product_id):
        print('Eliminando Producto')
        product = self.env['product.template'].search([('name', '=', product_id)], limit=1)
        if product:
            product.unlink()
        