import xmlrpc.client


# logger = logging.getLogger(name_)
url = "http://hspl:8069"
db = "db_shopify"
username = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(url))
models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(url))
uid = common.authenticate(db, username, password, {})
#
brands = models.execute_kw(
    db,
    uid,
    password,
    "product.brand",
    "search",
    [[
        ("name", "=", "Samsung")
    ]]
)
if brands:
    result = models.execute_kw(
        db,
        uid,
        password,
        "product.brand",
        "unlink",
        [brands]
    )

    print("Records deleted successfully.")
    print(brands)
else:
    print("No records found with the given name.")