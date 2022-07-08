from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from helpers import apology, flt0, flt1, flt2, flt3, today, login_required
from datetime import date, datetime, timedelta

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Custom filter
app.jinja_env.filters["flt0"] = flt0
app.jinja_env.filters["flt1"] = flt1
app.jinja_env.filters["flt2"] = flt2
app.jinja_env.filters["flt3"] = flt3

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///db/warehouse.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Set global constants
projectList = ['noliktavas papildinājums']

# Default index page, shows all articles
# shows index page with all stock summary
@app.route("/")
@login_required
def overview():
    articles = db.execute('''
                        SELECT article, SUM(IFNULL(trx_sheets,0)) AS stock, gsm, name, size, size_fiber, thickness, a.weight, pallet_amt, price_per_tonne, price_per_1000_sheets, assortment_stock_pll, assortment_stock_sheets, is_fsc, ROUND(SUM(IFNULL(trx_sheets,0))/1000*price_per_1000_sheets) AS stock_value 
                        FROM articles a 
                        JOIN article_prices ap ON a.article_id = ap.article_id 
                        LEFT OUTER JOIN transactions trx on a.article_id = trx.article_id AND trx_type != 'Writeoff'
                        WHERE DATE() BETWEEN date_from AND date_to 
                        GROUP BY article, gsm, name, size, size_fiber, thickness, a.weight, pallet_amt, price_per_tonne, price_per_1000_sheets, assortment_stock_pll, assortment_stock_sheets, is_fsc 
                        ORDER BY stock DESC, article, gsm
                        ''')
    totalValue = 0
    for article in range(len(articles)):
        totalValue += round(articles[article]['stock_value'])
    return render_template("overview.html", articles=articles, totalValue = totalValue)


# Add articles page -> to add new paper types
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        # get all inputs, calculate some fields
        gsm = request.form.get("gsm")
        name = request.form.get("name")
        size = request.form.get("size")
        size_fiber = request.form.get("size_fiber")
        FSC = request.form.get("fsc")
        # unique key and article name is generated from a number of attributes and depends on whether paper is FSC certified or not
        # also, replace spaces with dashes for unique key + lower all letters
        if FSC == "Y":
            article_id = (f'''{gsm}-{name.replace(' ', '-').lower()}-{size}x{size_fiber}-fsc''')
            article = (f'{gsm} {name} {size}x{size_fiber} FSC')
        else: 
            article_id = (f'''{gsm}-{name.replace(' ', '-').lower()}-{size}x{size_fiber}''')
            article = (f'{gsm} {name} {size}x{size_fiber}')
        stock = int(request.form.get("stock"))
        thickness = request.form.get("thickness")
        weight_per_1000_sheets = int(size) * int(size_fiber) / 1000000 * int(gsm)
        pallet_amt = int(request.form.get("pallet_amt"))
        stock_pll = round((stock / pallet_amt), 2)
        price_per_tonne = int(request.form.get("price_per_tonne"))
        price_per_1000_sheets = round((price_per_tonne / 1000 * float(weight_per_1000_sheets)),2)
        assortment_stock_pll = int(request.form.get("assortment_stock_pll"))
        assortment_stock_sheets = assortment_stock_pll * pallet_amt
        total_weight = round(weight_per_1000_sheets*stock/1000)
        total_price = round(weight_per_1000_sheets*stock/1000000*price_per_tonne)
        # add exception for duplicate article ids
        try: 
            db.execute("INSERT INTO articles (article_id, article, gsm, name, size, size_fiber, thickness, weight, pallet_amt, assortment_stock_pll, assortment_stock_sheets) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    article_id, article, gsm, name, size, size_fiber, thickness, weight_per_1000_sheets, pallet_amt, assortment_stock_pll, assortment_stock_sheets)
            db.execute("INSERT INTO article_prices (article_id, date_from, date_to, price_per_tonne, price_per_1000_sheets) VALUES(?, ?, '2999-12-31', ?, ?)", article_id, today(), price_per_tonne, price_per_1000_sheets)
            db.execute("INSERT INTO transactions (article_id, trx_date, trx_pll, trx_sheets, project, weight, price, trx_type) VALUES(?, ?, ?, ?, 'sākotnējais noliktavas atlikums', ?, ?, 'Initial Stock')", 
                       article_id, today(), stock_pll, stock, total_weight, total_price)
        except ValueError:
            return apology("Duplicate article entered")
        # if all ok
        flash('Article added!', 'message')
        return redirect('/')
    else:
        return render_template("add.html")


# Upcoming projects page with paper reservations
@app.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    # handles case where new projects are being added
    if request.method == "POST":
        article = request.form.get("article")
        article_id = article.replace(' ', '-').lower()
        article2 = request.form.get("article2")
        article2_id = article2.replace(' ', '-').lower()
        project_num = request.form.get("project_num")
        project_paper_sheets = request.form.get("project_paper_sheets")
        sizediff = request.form.get("sizediff")
        all_articles = db.execute("SELECT distinct article_id FROM articles")
        # checks if entered article exists in articles table (to not be able to plan a project with paper that doesn't exist in the warehouse)
        if not any(id['article_id'] == article_id for id in all_articles):
            return apology("This article doesn't exist!")
        elif article2 and not any(id['article_id'] == article2_id for id in all_articles):
            return apology("This article doesn't exist!")
        elif article2:
            db.execute("INSERT INTO project_papers (order_article_id, project_article_id, project_num, project_paper_sheets, size_diff, project_status) VALUES(?, ?, ?, ?, ?, 'OPEN')", article_id, article2_id, project_num, project_paper_sheets, sizediff)
        else:
            db.execute("INSERT INTO project_papers (order_article_id, project_num, project_paper_sheets, project_status) VALUES(?, ?, ?, 'OPEN')", article_id, project_num, project_paper_sheets)
        flash('Project paper added!', 'message')
        return redirect('/projects')
    # shows page in general
    else:
        projects = db.execute('''
                            SELECT oa.article as article1, project_num, project_paper_sheets, pa.article as article2, size_diff, project_status 
                            FROM project_papers pp 
                            LEFT JOIN articles oa ON pp.order_article_id = oa.article_id 
                            LEFT OUTER JOIN articles pa ON pp.project_article_id = pa.article_id 
                            WHERE project_status != 'INVOICED'
                            ORDER BY project_num ASC
                            ''')
        papers = db.execute("SELECT DISTINCT article FROM articles")
        articleList = []
        for paper in papers:
            articleList.append(paper['article'])
        return render_template("projects.html", projects = projects, articleList = articleList)
    
# Invoicing removes written off paper from stock. This is needed because invoicing happens at a different date when writeoffs.
@app.route("/invoicing", methods=["GET", "POST"])
@login_required
def invoicing():
    # handles case where new projects are being added
    if request.method == "POST":
        invoiced = request.form.getlist("invoicing")
        print(invoiced)
        for i in range(len(invoiced)):
            project = db.execute('''
                            SELECT * 
                            FROM transactions 
                            WHERE project_paper_id = ?
                            AND trx_type = 'Writeoff'
                            ''',
                            invoiced[i])
            db.execute("INSERT INTO transactions (article_id, project_paper_id, trx_date, trx_pll, trx_sheets, project, weight, price, trx_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?, 'Invoicing')", 
                       project[0]["article_id"], invoiced[i], today(), project[0]["trx_pll"], project[0]["trx_sheets"], project[0]["project"], project[0]["weight"], project[0]["price"])
            db.execute("UPDATE project_papers SET project_status = 'INVOICED' WHERE id = ?", invoiced[i])
        flash('Paper invoiced!', 'message')
        return redirect('/invoicing')
    # shows page in general
    else:
        projects = db.execute('''
                            SELECT pp.id, project_num, IFNULL(pa.article, oa.article) AS article, project_paper_sheets*IFNULL(size_diff, 1) AS planned_sheets, trx_sheets AS written_off_sheets, project_paper_sheets*IFNULL(size_diff, 1) + trx_sheets AS delta
                            FROM project_papers pp 
                            LEFT JOIN articles oa ON pp.order_article_id = oa.article_id 
                            LEFT OUTER JOIN articles pa ON pp.project_article_id = pa.article_id 
                            LEFT JOIN transactions trx ON pp.id = trx.project_paper_id
                            WHERE project_status = 'WRITTEN OFF'
                            AND trx_type = 'Writeoff'
                            ORDER BY project_num ASC
                            ''')
        return render_template("invoicing.html", projects = projects)
    
# Show projects archive page
@app.route("/archive", methods=["GET", "POST"])
@login_required
def archive():
    objects = {}
    if request.method == "POST":
        # generate fields with values for SQL search. In case of empty - use %
        for i in request.form:
            if request.form.get(i):
                objects[i] = str(request.form.get(i)).lower()
            else:
                objects[i] = '%'
        projects = db.execute('''SELECT project_num, IFNULL(pa.article, oa.article) AS article, IFNULL(pa.article_id, oa.article_id) AS article_id, SUM(project_paper_sheets*IFNULL(size_diff, 1)) AS planned_sheets, 0 AS writeoffs, 0 AS delta 
                              FROM project_papers pp 
                              LEFT JOIN articles oa ON pp.order_article_id = oa.article_id 
                              LEFT OUTER JOIN articles pa ON pp.project_article_id = pa.article_id 
                              WHERE pp.project_status = 'INVOICED'
                              AND lower(project_num) LIKE ? 
                              AND lower(IFNULL(pa.article, oa.article)) LIKE ? 
                              GROUP BY project_num, IFNULL(pa.article, oa.article), IFNULL(pa.article_id, oa.article_id) 
                              ORDER BY project_num DESC LIMIT 200''',
                              objects['project'], objects['article'])
        writeoffs = db.execute("SELECT project, article_id, SUM(trx_sheets) as writeoffs FROM transactions trx WHERE trx.trx_type = 'Writeoff' GROUP BY project, article_id ORDER BY project")
        #combine data from planned projects and writeoffs tables
        for i in range(len(projects)):
            for j in range(len(writeoffs)):
                if projects[i]['article_id'] == writeoffs[j]['article_id'] and str(projects[i]['project_num']) == str(writeoffs[j]['project']):
                    projects[i]['writeoffs'] = writeoffs[j]['writeoffs']
            projects[i]['delta'] = int(projects[i]['planned_sheets']) + int(projects[i]['writeoffs'])
        return render_template("archive.html", projects = projects)
    else:
        projects = db.execute('''SELECT project_num, IFNULL(pa.article, oa.article) AS article, IFNULL(pa.article_id, oa.article_id) AS article_id, SUM(project_paper_sheets*IFNULL(size_diff, 1)) AS planned_sheets, 0 AS writeoffs, 0 AS delta 
                              FROM project_papers pp 
                              LEFT JOIN articles oa ON pp.order_article_id = oa.article_id 
                              LEFT OUTER JOIN articles pa ON pp.project_article_id = pa.article_id 
                              WHERE pp.project_status = 'INVOICED' 
                              GROUP BY project_num, IFNULL(pa.article, oa.article), IFNULL(pa.article_id, oa.article_id) 
                              ORDER BY project_num DESC LIMIT 200''')
        writeoffs = db.execute("SELECT project, article_id, SUM(trx_sheets) as writeoffs FROM transactions trx WHERE trx.trx_type = 'Writeoff' GROUP BY project, article_id ORDER BY project")
        #combine data from planned projects and writeoffs tables
        for i in range(len(projects)):
            for j in range(len(writeoffs)):
                if projects[i]['article_id'] == writeoffs[j]['article_id'] and str(projects[i]['project_num']) == str(writeoffs[j]['project']):
                    projects[i]['writeoffs'] = writeoffs[j]['writeoffs']
            projects[i]['delta'] = int(projects[i]['planned_sheets']) + int(projects[i]['writeoffs'])
        return render_template("archive.html", projects = projects)



# Shows the warehouse stock minus the backlog + reserves for each article
@app.route("/backlog")
@login_required
def backlog():
    projects = db.execute('''
                        SELECT
                            CASE 
                                WHEN pp.project_status = 'OPEN' THEN oa.article
                                WHEN pp.project_status IN ('PAPER PREPARED', 'WRITTEN OFF') THEN pa.article
                            END article,
                            CASE
                                WHEN pp.project_status = 'OPEN' THEN SUM(IFNULL(pp.project_paper_sheets, 0))
                                WHEN pp.project_status IN ('PAPER PREPARED', 'WRITTEN OFF') THEN SUM(IFNULL(pp.project_paper_sheets, 0)*IFNULL(pp.size_diff, 1))
                            END project_paper_sheets
                        FROM project_papers pp
                        LEFT JOIN articles oa ON oa.article_id = pp.order_article_id
                        LEFT JOIN articles pa ON pa.article_id = IFNULL(pp.project_article_id, pp.order_article_id)
                        WHERE pp.project_status IN ('OPEN', 'PAPER PREPARED', 'WRITTEN OFF')
                        GROUP BY 
                            CASE 
                                WHEN pp.project_status = 'OPEN' THEN oa.article
                                WHEN pp.project_status IN ('PAPER PREPARED', 'WRITTEN OFF') THEN pa.article
                            END;
                          ''')
    print(projects)
    orders = db.execute('''
                        SELECT article, SUM(IFNULL(order_sheets, 0)) AS ordered_sheets 
                        FROM articles 
                        LEFT JOIN purchase_orders po ON articles.article_id = po.article_id 
                        WHERE po.order_status = 'OPEN' 
                        GROUP BY article
                        ''')
    backlog = db.execute('''
                         SELECT name, gsm, article, SUM(IFNULL(trx_sheets,0)) AS stock, assortment_stock_sheets, 0 as ordered_sheets, 0 AS project_paper_sheets, SUM(IFNULL(trx_sheets,0))-assortment_stock_sheets AS backlog 
                         FROM articles 
                         LEFT JOIN transactions trx on articles.article_id = trx.article_id AND trx_type != 'Writeoff'
                         GROUP BY name, gsm, article, assortment_stock_sheets ORDER BY name, gsm, article
                         ''')
    for i in range(len(backlog)):
        for j in range(len(projects)):
            if backlog[i]['article'] == projects[j]['article']:
                backlog[i]['project_paper_sheets'] = projects[j]['project_paper_sheets']
        for k in range(len(orders)):
            if backlog[i]['article'] == orders[k]['article']:
                backlog[i]['ordered_sheets'] = orders[k]['ordered_sheets']
        backlog[i]['backlog'] = backlog[i]['stock'] + backlog[i]['ordered_sheets'] - backlog[i]['project_paper_sheets'] - backlog[i]['assortment_stock_sheets']
    return render_template("backlog.html", backlog=backlog)


# Purchase order overview page with the option to make more orders
@app.route("/purchases", methods=["GET", "POST"])
@login_required
def purchases():
    # handles case where new orders are being added
    if request.method == "POST" and request.form['action'] != 'purchase':
        session['purchaseOrderId'] = request.form.get("action")
        return redirect("/receive")
    elif request.method == "POST" and request.form['action'] == 'purchase':
        article = request.form.get("article")
        article_id = article.replace(' ', '-').lower()
        order_date = request.form.get("order_date")
        order_pll = request.form.get("order_pll")
        order_sheets = request.form.get("order_sheets")
        supplier = request.form.get("supplier")
        eta_date = request.form.get("eta_date")
        project = request.form.get("project")
        weight = request.form.get("weight")
        price = request.form.get("price")
        # print(f'{article} - {article_id} - {order_date} - {order_pll} - {order_sheets} - {supplier} - {eta_date} - {project} - {weight} - {price}')
        all_articles = db.execute("SELECT distinct article_id FROM articles")
        # checks if entered article exists in articles table (to not be able to order paper that doesn't exist in the warehouse)
        if not any(id['article_id'] == article_id for id in all_articles):
            return apology("This article doesn't exist!")
        else:
            db.execute("INSERT INTO purchase_orders (article_id, order_date, order_status, order_pll, order_sheets, supplier, eta_date, project, weight, price) VALUES(?, ?, 'OPEN', ?, ?, ?, ?, ?, ?, ?)", 
                       article_id, order_date, order_pll, order_sheets, supplier, eta_date, project, weight, price)
        flash('Purchase order added', 'message')
        return redirect('/purchases')
    # shows PO page
    else:
        purchases = db.execute('''
                                SELECT po.id, order_date, order_status, article, order_pll, order_sheets, supplier, eta_date, project, po.weight AS weight, po.price AS price 
                                FROM purchase_orders po 
                                LEFT JOIN articles ON po.article_id = articles.article_id 
                                WHERE order_status != 'CLOSED'
                                ''')
        papers = db.execute("SELECT DISTINCT article_id, article, weight, pallet_amt FROM articles")
        articleList = []
        for paper in papers:
            articleList.append(paper['article'])
        suppliers = db.execute("SELECT DISTINCT supplier FROM purchase_orders")
        supplierList = []
        for supplier in suppliers:
            supplierList.append(supplier['supplier'])
        return render_template("purchases.html", purchases=purchases, articleList=articleList, supplierList=supplierList, today=today(), papers=papers, projectList=projectList)

# purchase order receipt functionality
@app.route("/receive", methods=["GET", "POST"])
@login_required
def receive():
    purchaseOrderId = session['purchaseOrderId']
    order = db.execute('''SELECT po.id, order_date, article, articles.article_id, order_pll, order_sheets, round(order_sheets*thickness/10,1) AS height, supplier, eta_date, project, po.weight AS weight, po.price AS price, thickness 
                       FROM purchase_orders po 
                       LEFT JOIN articles ON po.article_id = articles.article_id 
                       WHERE po.id = ?''', 
                       purchaseOrderId)
    papers = db.execute("SELECT DISTINCT article_id, article, weight, pallet_amt FROM articles")
    # functionality for receiving purchase order unchanged (if all data matches to order data)
    if request.method == "POST" and request.form['action'] == "original":
        act_height = float(request.form.get("act_height"))
        db.execute("INSERT INTO transactions (article_id, purchase_order_id, trx_date, trx_pll, trx_sheets, supplier, project, weight, price, exp_height, act_height, trx_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Purchase Receipt')", 
                       order[0]["article_id"], purchaseOrderId, today(), order[0]["order_pll"], order[0]["order_sheets"], order[0]["supplier"], order[0]["project"], order[0]["weight"], order[0]["price"], order[0]["height"], act_height)
        db.execute("UPDATE purchase_orders SET order_status = 'CLOSED' WHERE id = ?", purchaseOrderId)
        exp_height = float(order[0]["height"])
        # flashing message in case paper height deviates from expected height
        if act_height < round(exp_height - exp_height*0.05, 1) or act_height > round(exp_height + exp_height*0.05, 1):
            flash('! Order changed & received, but height deviation from norm is higher than 5% !', 'warning')
        else:
            flash('Order changed & received!', 'message')
        return redirect('/purchases')
    # functionality for receiving purchase order with some changed values (e.g. received quantity or prices change)
    elif request.method == "POST" and request.form['action'] == "changed":
        order_pll = request.form.get("order_pll")
        order_sheets = int(request.form.get("order_sheets"))
        receipt_date = request.form.get("eta_date")
        price = request.form.get("price")
        height = round(float(request.form.get("height")),1)
        expected_height = round(float(order_sheets * order[0]["thickness"] / 10),1)
        db.execute("INSERT INTO transactions (article_id, purchase_order_id, trx_date, trx_pll, trx_sheets, supplier, project, weight, price, exp_height, act_height, trx_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Purchase Receipt')", 
                        order[0]["article_id"], purchaseOrderId, receipt_date, order_pll, order_sheets, order[0]["supplier"], order[0]["project"], order[0]["weight"], price, expected_height, height)
        db.execute("UPDATE purchase_orders SET order_status = 'CLOSED' WHERE id = ?", purchaseOrderId)
        # flashing message in case paper height deviates from expected height
        if height < round(expected_height - expected_height*0.05, 1) or height > round(expected_height + expected_height*0.05, 1):
            flash('! Order changed & received, but height deviation from norm is higher than 5% !', 'warning')
        else: 
            flash('Order changed & received!', 'message')
        return redirect('/purchases')
    else:
        return render_template("receive.html", order=order, today=today(), papers=papers)

# functionality for updating the prices of paper from suppliers
@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    if request.method == "POST":
        name = request.form.get("name")
        date_from = request.form.get("date")
        price_per_tonne = request.form.get("price")
        date_to = (datetime.strptime(date_from, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        db.execute("UPDATE article_prices SET date_to = ? WHERE date_to = '2999-12-31' AND article_id IN (SELECT DISTINCT article_id FROM articles WHERE name = ?)", date_to, name)
        articles = db.execute("SELECT DISTINCT article_id, weight FROM articles WHERE name = ?", name)
        for i in range(len(articles)):
            article = articles[i]["article_id"]
            price_per_1000_sheets = round(int(price_per_tonne) / 1000 * float(articles[i]["weight"]),2)
            db.execute("INSERT INTO article_prices (article_id, date_from, date_to, price_per_tonne, price_per_1000_sheets) VALUES(?, ?, '2999-12-31', ?, ?)", 
                       article, date_from, price_per_tonne, price_per_1000_sheets)
        flash('Price updated!', 'message')
        return redirect('/update')
    else:
        articleNames = db.execute("SELECT DISTINCT name FROM articles ORDER BY name")
        allPrices = db.execute("SELECT DISTINCT name, price_per_tonne, date_from FROM articles a JOIN article_prices ap ON a.article_id = ap.article_id WHERE DATE() <= date_to ORDER BY name, date_from")
        return render_template("update.html", today=today(), articleNames=articleNames, allPrices=allPrices)
    

# Transactions page: shows all incoming/outgoing(used) paper transactions
@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    objects = {}
    if request.method == "POST":
        for i in request.form:
            if request.form.get(i):
                objects[i] = str(request.form.get(i)).lower()
            else:
                objects[i] = '%'
        transactions = db.execute('''
                                  SELECT trx.id, article, trx_date, trx_pll, trx_sheets, trx.supplier, trx.project, trx.weight, trx.price, trx.exp_height, trx.act_height, round((trx.act_height*1.0/trx.exp_height-1)*100,2) AS deviation, trx_type 
                                  FROM transactions trx 
                                  LEFT JOIN articles ON articles.article_id = trx.article_id 
                                  WHERE lower(articles.article) LIKE ? 
                                  AND lower(trx_type) LIKE ? 
                                  AND lower(ifnull(trx.supplier, 'None')) LIKE ? 
                                  AND lower(ifnull(trx.project, 'None')) LIKE ? 
                                  AND trx_date LIKE ? 
                                  ORDER BY trx.id DESC 
                                  LIMIT 200
                                  ''',
                              objects['article'], objects['trx_type'], objects['supplier'], objects['project'], objects['date'])
        return render_template("transactions.html", transactions=transactions)
    else:
        transactions = db.execute('''
                                  SELECT trx.id, article, trx_date, trx_pll, trx_sheets, trx.supplier, trx.project, trx.weight, trx.price, trx.exp_height, trx.act_height, round((trx.act_height*1.0/trx.exp_height-1)*100,2) AS deviation, trx_type 
                                  FROM transactions trx 
                                  LEFT JOIN articles ON articles.article_id = trx.article_id 
                                  ORDER BY trx.id DESC 
                                  LIMIT 200
                                  ''')
        return render_template("transactions.html", transactions=transactions)


# functionality for showing tasks of preparing paper for printing, including the possibility to cut it in multiple equal parts.
@app.route("/cut", methods=["GET", "POST"])
def cut(): 
    if request.method == "POST":
        workId = request.form.get("submit")
        work = db.execute('''
                          SELECT pp.id, oa.article AS article1, oa.article_id AS article1_id, project_num, project_paper_sheets, IFNULL(pa.article, oa.article) AS article2, IFNULL(pa.article_id, oa.article_id) AS article2_id, 
                          project_paper_sheets*IFNULL(size_diff, 1) AS output_sheets, oa.pallet_amt AS pallet_amt_oa, IFNULL(pa.pallet_amt, oa.pallet_amt) AS pallet_amt_pa, oa.weight, ap.price_per_tonne 
                          FROM project_papers pp 
                          LEFT JOIN articles oa ON pp.order_article_id = oa.article_id 
                          LEFT OUTER JOIN articles pa ON pp.project_article_id = pa.article_id 
                          LEFT JOIN article_prices ap on ap.article_id = pp.order_article_id 
                          WHERE pp.id = ? 
                          AND DATE() BETWEEN ap.date_from AND ap.date_to
                          ''',
                          workId)
        trx_pll_oa = round(work[0]['project_paper_sheets'] / work[0]['pallet_amt_oa'], 2)
        trx_weight = round(work[0]['project_paper_sheets'] / 1000 * work[0]['weight'])
        trx_price = round(work[0]['weight'] * work[0]['project_paper_sheets'] / 1000000 * work[0]['price_per_tonne'])
        trx_pll_pa = round(work[0]['output_sheets'] / work[0]['pallet_amt_pa'], 2)
        if work[0]['article1_id'] == work[0]['article2_id']:
            db.execute("UPDATE project_papers SET project_status = 'PAPER PREPARED' WHERE id = ?", workId)
        else: 
            db.execute("INSERT INTO transactions (article_id, project_paper_id, trx_date, trx_pll, trx_sheets, project, weight, price, trx_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?, 'Cutting')", 
                       work[0]["article1_id"], work[0]["id"], today(), trx_pll_oa*-1, work[0]['project_paper_sheets']*-1, work[0]["project_num"], trx_weight*-1, trx_price*-1)
            db.execute("INSERT INTO transactions (article_id, project_paper_id, trx_date, trx_pll, trx_sheets, project, weight, price, trx_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?, 'Cutting')", 
                       work[0]["article2_id"], work[0]["id"], today(), trx_pll_pa, work[0]['output_sheets'], work[0]["project_num"], trx_weight, trx_price)
            db.execute("UPDATE project_papers SET project_status = 'PAPER PREPARED' WHERE id = ?", workId)
        flash('Paper prepared!', 'message')
        return redirect('/cut')
    else:
        projects = db.execute('''
                              SELECT pp.id, oa.article AS article1, project_num, project_paper_sheets, round(project_paper_sheets*oa.thickness/10,1) AS oa_height, IFNULL(pa.article, oa.article) AS article2, 
                              project_paper_sheets*IFNULL(size_diff, 1) AS output_sheets, round(project_paper_sheets*IFNULL(size_diff, 1)*oa.thickness/10,1) AS pa_height 
                              FROM project_papers pp 
                              LEFT JOIN articles oa ON pp.order_article_id = oa.article_id 
                              LEFT OUTER JOIN articles pa ON pp.project_article_id = pa.article_id 
                              WHERE pp.project_status = 'OPEN'
                              ''')
        return render_template("cut.html", projects = projects)


# functionality for writing off paper that has been used in the printing process
@app.route("/writeoff",  methods=["GET", "POST"])
def writeoff():
    if request.method == "POST":
        workId = request.form.get("submit")
        try: 
            used_sheets = int(request.form.get(workId))
        except ValueError:
            return apology("Invalid writeoff amount!")
        work = db.execute('''
                          SELECT pp.id, project_num, IFNULL(pa.article, oa.article) AS article, IFNULL(pa.article_id, oa.article_id) AS article_id, project_paper_sheets*IFNULL(size_diff, 1) AS planned_sheets, 
                          IFNULL(pa.pallet_amt, oa.pallet_amt) AS pallet_amt, oa.weight, ap.price_per_tonne 
                          FROM project_papers pp 
                          LEFT JOIN articles oa ON pp.order_article_id = oa.article_id 
                          LEFT OUTER JOIN articles pa ON pp.project_article_id = pa.article_id 
                          LEFT JOIN article_prices ap on ap.article_id = pp.order_article_id 
                          WHERE pp.id = ? 
                          AND DATE() BETWEEN ap.date_from AND ap.date_to
                          ''',
                          workId)
        trx_pll = round(used_sheets / work[0]['pallet_amt'], 2)
        trx_weight = round(used_sheets / 1000 * work[0]['weight'])
        trx_price = round(work[0]['weight'] * used_sheets / 1000000 * work[0]['price_per_tonne'])
        db.execute("INSERT INTO transactions (article_id, project_paper_id, trx_date, trx_pll, trx_sheets, project, weight, price, trx_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?, 'Writeoff')", 
                       work[0]["article_id"], work[0]["id"], today(), trx_pll*-1, used_sheets*-1, work[0]["project_num"], trx_weight*-1, trx_price*-1)
        db.execute("UPDATE project_papers SET project_status = 'WRITTEN OFF' WHERE id = ?", workId)
        flash('Paper written off', 'message')
        return redirect('/writeoff')
    else:
        projects = db.execute('''SELECT pp.id, project_num, IFNULL(pa.article, oa.article) AS article, project_paper_sheets*IFNULL(size_diff, 1) AS planned_sheets 
                              FROM project_papers pp 
                              LEFT JOIN articles oa ON pp.order_article_id = oa.article_id 
                              LEFT OUTER JOIN articles pa ON pp.project_article_id = pa.article_id 
                              WHERE pp.project_status = 'PAPER PREPARED'
                              ''')
        return render_template("writeoff.html", projects=projects)

@app.route("/generate")
def generate():
    session["user"] = 'admin'
    return redirect("/")