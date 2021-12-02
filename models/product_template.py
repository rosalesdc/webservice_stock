# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    owner = fields.Char('Owner')
    commercial_amount = fields.Float('Commercial Amount')

    def consume_json_cron(self):
        print("Ejecutanto CREACION:::::")
        # TODO url podría ser parámetro configurable
        url = "http://172.17.0.2:8069/webservice_stock/static/description/json_create_products.json"
        json_objetc = requests.get(url).json()
        num_products = json_objetc["info"]["num_products"]
        product_data = json_objetc["products"]
        messages = json_objetc["info"]["messages"]
        errors = json_objetc["info"]["errors"]

        if num_products > 0:
            print("HAY PRODUCTOS NUEVOS ::::")
            for product in product_data:
                print("CREANDO UN PRODUCTO")
                self.create_product(product)
        if messages:
            print("PINTAR MENSAJES ::::::")
        if errors:
            print("PINTAR ERRORES ::::::")

    def create_product(self, product_dict):
        print('Creando un producto')
        new_product = self.env['product.template'].create({
            'name': product_dict['name'],
            'detailed_type': 'product',
            'owner': product_dict['owner'],
            'commercial_amount' : product_dict['commercial_amount']
        })
