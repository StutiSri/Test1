# -*- coding: utf-8 -*-
if db(db.tbl_categories.id > 0).count() == 0:
    db.tbl_categories.insert(category_field_name='clothing', category_name='Clothing')
    db.tbl_categories.insert(category_field_name='food_outlets',category_name='Food Outlets')
    db.tbl_categories.insert(category_field_name='general_store',category_name='General Store')
    db.tbl_categories.insert(category_field_name='stationary',category_name='Stationary')
    db.tbl_categories.insert(category_field_name='medical',category_name='Medical')
