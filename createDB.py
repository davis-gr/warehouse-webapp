import sqlite3
from sqlite3 import Error
from cs50 import SQL


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    create_connection(r"db/warehouse.db")
db = SQL("sqlite:///db/warehouse.db")

# Create tables
db.execute("CREATE TABLE articles (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, article_id TEXT NOT NULL UNIQUE, article TEXT NOT NULL, gsm INTEGER NOT NULL, name TEXT NOT NULL, size INTEGER NOT NULL, size_fiber INTEGER NOT NULL, thickness NUMERIC NOT NULL, weight NUMERIC NOT NULL, pallet_amt INTEGER NOT NULL, assortment_stock_pll NUMERIC NOT NULL, assortment_stock_sheets INTEGER NOT NULL, is_fsc TEXT);")
db.execute("CREATE TABLE project_papers (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, order_article_id TEXT NOT NULL, project_article_id TEXT, project_num INTEGER NOT NULL, project_paper_sheets INTEGER NOT NULL, size_diff INTEGER, project_status TEXT NOT NULL, FOREIGN KEY(order_article_id) REFERENCES articles(article_id), FOREIGN KEY(project_article_id) REFERENCES articles(article_id));")
db.execute("CREATE TABLE purchase_orders (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, article_id TEXT NOT NULL, order_date TEXT NOT NULL, order_status TEXT NOT NULL, order_pll NUMERIC NOT NULL, order_sheets INTEGER NOT NULL, supplier TEXT NOT NULL, eta_date TEXT NOT NULL, project TEXT NOT NULL, weight NUMERIC NOT NULL, price NUMERIC NOT NULL, FOREIGN KEY(article_id) REFERENCES articles(article_id));")
db.execute("CREATE TABLE transactions (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, article_id TEXT NOT NULL, purchase_order_id INTEGER, project_paper_id INTEGER, trx_date TEXT NOT NULL, trx_pll NUMERIC NOT NULL, trx_sheets INTEGER NOT NULL, supplier TEXT, project TEXT NOT NULL, weight NUMERIC NOT NULL, price NUMERIC NOT NULL, exp_height NUMERIC, act_height NUMERIC, trx_type TEXT NOT NULL, FOREIGN KEY(article_id) REFERENCES articles(article_id), FOREIGN KEY(purchase_order_id) REFERENCES purchase_orders(id), FOREIGN KEY(project_paper_id) REFERENCES project_papers(id));")
db.execute("CREATE TABLE article_prices (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, article_id TEXT NOT NULL, date_from TEXT NOT NULL, date_to TEXT NOT NULL, price_per_tonne INTEGER NOT NULL, price_per_1000_sheets NUMERIC NOT NULL, FOREIGN KEY(article_id) REFERENCES articles(article_id));")

# Create indices
db.execute("CREATE INDEX 'article_index' ON 'articles' ('article')")
db.execute("CREATE INDEX 'name_index' ON 'articles' ('name')")
db.execute("CREATE INDEX 'project_index' ON 'project_papers' ('project_num')")
db.execute("CREATE INDEX 'po_project_index' ON 'purchase_orders' ('project')")
db.execute("CREATE INDEX 'trx_project_index' ON 'transactions' ('project')")

# These are inserts for testing, can be deleted later
db.execute("INSERT INTO articles (article_id, article, gsm, name, size, size_fiber, thickness, weight, pallet_amt, assortment_stock_pll, assortment_stock_sheets, is_fsc) VALUES('100-amber-graphic-720x1020-fsc', '100 Amber Graphic 720x1020 FSC', 100, 'Amber Graphic', 720, 1020, '0.122', '73.4', 8000, 4, 32000, 'Y')")
db.execute("INSERT INTO articles (article_id, article, gsm, name, size, size_fiber, thickness, weight, pallet_amt, assortment_stock_pll, assortment_stock_sheets, is_fsc) VALUES('100-munken-print-cream-640x900-fsc', '100 Munken Print Cream 640x900 FSC', 100, 'Munken Print Cream', 640, 900, '0.150', '57.6', 6000, 3, 18000, 'Y')")
db.execute("INSERT INTO articles (article_id, article, gsm, name, size, size_fiber, thickness, weight, pallet_amt, assortment_stock_pll, assortment_stock_sheets, is_fsc) VALUES('80-amber-graphic-640x900-fsc', '80 Amber Graphic 640x900 FSC', 80, 'Amber Graphic', 640, 900, '0.099', '46.1', 10000, 2, 20000, 'Y')")
db.execute("INSERT INTO articles (article_id, article, gsm, name, size, size_fiber, thickness, weight, pallet_amt, assortment_stock_pll, assortment_stock_sheets, is_fsc) VALUES('115-munken-print-cream-720x1020-fsc', '115 Munken Print Cream 720x1020 FSC', 115, 'Munken Print Cream', 720, 1020, '0.172', '84.5', 5500, 0, 0, 'Y')")
db.execute("INSERT INTO articles (article_id, article, gsm, name, size, size_fiber, thickness, weight, pallet_amt, assortment_stock_pll, assortment_stock_sheets, is_fsc) VALUES('235-metsäboard-prime-fbb-bright-720x1020-fsc', '235 MetsäBoard Prime FBB Bright 720x1020 FSC', 235, 'MetsäBoard Prime FBB Bright', 720, 1020, '0.360', '172.6', 3200, 3, 9600, 'Y')")
db.execute("INSERT INTO articles (article_id, article, gsm, name, size, size_fiber, thickness, weight, pallet_amt, assortment_stock_pll, assortment_stock_sheets, is_fsc) VALUES('100-amber-graphic-720x510-fsc', '100 Amber Graphic 720x510 FSC', 100, 'Amber Graphic', 720, 510, '0.122', '36.7', 16000, 0, 0, 'Y')")
db.execute("INSERT INTO project_papers (order_article_id, project_article_id, project_num, project_paper_sheets, size_diff, project_status) VALUES('100-amber-graphic-720x1020-fsc', '100-amber-graphic-720x510-fsc', 20121, 7500, 2, 'OPEN')")
db.execute("INSERT INTO project_papers (order_article_id, project_num, project_paper_sheets, project_status) VALUES('235-metsäboard-prime-fbb-bright-720x1020-fsc', 20121, 300, 'OPEN')")
db.execute("INSERT INTO project_papers (order_article_id, project_num, project_paper_sheets, project_status) VALUES('115-munken-print-cream-720x1020-fsc', 20321, 5000, 'OPEN')")
db.execute("INSERT INTO project_papers (order_article_id, project_num, project_paper_sheets, project_status) VALUES('235-metsäboard-prime-fbb-bright-720x1020-fsc', 20321, 200, 'OPEN')")
db.execute("INSERT INTO purchase_orders (article_id, order_date, order_status, order_pll, order_sheets, supplier, eta_date, project, weight, price) VALUES('100-amber-graphic-720x1020-fsc', '2022-05-20', 'OPEN', 2, 16000, 'Arctic Paper', '2022-06-05', 'noliktavas papildinājums', 1175, 1604)")
db.execute("INSERT INTO purchase_orders (article_id, order_date, order_status, order_pll, order_sheets, supplier, eta_date, project, weight, price) VALUES('115-munken-print-cream-720x1020-fsc', '2022-05-20', 'OPEN', 0.91, 5000, 'Arctic Paper', '2022-06-05', '20321', 422, 695)")
db.execute("INSERT INTO transactions (article_id, purchase_order_id, trx_date, trx_pll, trx_sheets, supplier, project, weight, price, trx_type) VALUES('100-amber-graphic-720x1020-fsc', 1,'2022-06-05', 2, 16000, 'Arctic Paper', 'noliktavas papildinājums', 1175, 1604, 'Purchase Receipt')")
db.execute("INSERT INTO transactions (article_id, purchase_order_id, trx_date, trx_pll, trx_sheets, supplier, project, weight, price, trx_type) VALUES('115-munken-print-cream-720x1020-fsc', 2, '2022-06-05', 0.91, 5000, 'Arctic Paper', '20321', 422, 700, 'Purchase Receipt')")
db.execute("INSERT INTO transactions (article_id, trx_date, trx_pll, trx_sheets, project, weight, price, trx_type) VALUES('100-amber-graphic-720x1020-fsc', DATE(), 2.44, 19500, 'sākotnējais noliktavas atlikums', 1432, 1955, 'Initial Stock')")
db.execute("INSERT INTO transactions (article_id, trx_date, trx_pll, trx_sheets, project, weight, price, trx_type) VALUES('80-amber-graphic-640x900-fsc', DATE(), 2.2, 22000, 'sākotnējais noliktavas atlikums', 1014, 1384, 'Initial Stock')")
db.execute("INSERT INTO transactions (article_id, trx_date, trx_pll, trx_sheets, project, weight, price, trx_type) VALUES('100-munken-print-cream-640x900-fsc', DATE(), 3.03, 18200, 'sākotnējais noliktavas atlikums', 1048, 1724, 'Initial Stock')")
db.execute("INSERT INTO transactions (article_id, trx_date, trx_pll, trx_sheets, project, weight, price, trx_type) VALUES('235-metsäboard-prime-fbb-bright-720x1020-fsc', DATE(), 3.19, 10200, 'sākotnējais noliktavas atlikums', 1760, 3588, 'Initial Stock')")
db.execute("INSERT INTO article_prices (article_id, date_from, date_to, price_per_tonne, price_per_1000_sheets) VALUES('100-amber-graphic-720x1020-fsc', '2022-05-15', '2999-12-31', 1365, '100.25')")
db.execute("INSERT INTO article_prices (article_id, date_from, date_to, price_per_tonne, price_per_1000_sheets) VALUES('80-amber-graphic-640x900-fsc', '2022-05-15', '2999-12-31', 1365, '62.9')")
db.execute("INSERT INTO article_prices (article_id, date_from, date_to, price_per_tonne, price_per_1000_sheets) VALUES('100-munken-print-cream-640x900-fsc', '2022-05-20', '2999-12-31', 1645, '94.76')")
db.execute("INSERT INTO article_prices (article_id, date_from, date_to, price_per_tonne, price_per_1000_sheets) VALUES('115-munken-print-cream-720x1020-fsc', '2022-05-20', '2999-12-31', 1645, '138.94')")
db.execute("INSERT INTO article_prices (article_id, date_from, date_to, price_per_tonne, price_per_1000_sheets) VALUES('235-metsäboard-prime-fbb-bright-720x1020-fsc', '2022-05-25', '2999-12-31', 2038, '351.73')")
db.execute("INSERT INTO article_prices (article_id, date_from, date_to, price_per_tonne, price_per_1000_sheets) VALUES('100-amber-graphic-720x510-fsc', '2022-05-15', '2999-12-31', 1365, '50.12')")
