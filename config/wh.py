# fmt: off

warehouses = {
    "msk": {
        "wb": "",
        "ymarket": "",
        "ozon": "",
        "name": "Москва",
    }
}
# fmt: on
y_whs = [warehouses[city]["ymarket"] for city in warehouses.keys()]
ozon_whs = [warehouses[city]["ozon"] for city in warehouses.keys()]
wb_whs = [warehouses[city]["wb"] for city in warehouses.keys()]
