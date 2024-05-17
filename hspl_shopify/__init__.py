# -*- coding: utf-8 -*-

from . import controllers
from . import models
from . import wizards

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    group_ids = env.env['res.users'].browse(SUPERUSER_ID).group_id

    env.env['res.users'].ref("hspl_shopify.shopify_user_root").write({
        "group_id": [(6, 0, group_ids)]
    })
