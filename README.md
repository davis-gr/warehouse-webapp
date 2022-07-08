# Warehouse Management web-app
### Video Demo:  <URL HERE>
### Description:
#### General intro

This is a web application that is built for warehouse inventory management for a company that is operating in printing business. The back-end is written in Python (using Flask), data is stored in a SQLite database, whereas frontend utilizes HTML (bootstrap) with Jinja templates, CSS and Javascript for additional interactivity on the front-end.

The main app is stored in app.py. There is helpers.py file that stores some additional functions to serve the main app. There is createDB.py file that only needs to be initialized once and which creates the database schema with all the necessary tables and indices. It also contains test data inserts that are not necessary for production environment. 

Currently this app is not prepared for deploying to production, however it will be further adjusted to be hosted on a production environment and thus use a proper web-server, authentication features etc.

#### Main features

The app is comprised of 10 main components:

##### 1. Index page (overview)
This page provides overall overview: what types of paper (articles) are currently stored in the warehouse and what is the stock value of these articles based on the current price. Some additional descriptive parameters are added to help on daily operations.

##### 2. Open projects 
Open projects page shows future printing projects that are currently in the pipeline, but for which paper is not yet prepared. This gives an overview of the projects backlog. There is a possibility to add new projects straight from the page as well. There are validations in place so that it is not possible to plan a project with an article that does not exist in the system. Projects with statuses "OPEN" and "PAPER PREPARED" are shown in this page.

##### 3. Backlog
Backlog page shows the overall status of warehouse taking into account both current stock values of various articles as well as paper reserved for projects planned in future and purchase orders for paper that has been ordered but has not yet been received. In addition, this is checked against the "stock reserve" parameter that is set for each article and shows how much stock should be in the warehouse at all times. There is "Order" button available for each article, which redirects user to "Purchases" page with pre-filled values to create Purchase order in case the Backlog value is negative and additional paper should be ordered.

##### 4. Purchases
Purchases tab shows all outstanding non-received paper purchase orders. It is possible to add new orders from the page. There are validations in place so that it is not possible to order an article that does not exist in the system. It is also possible to mark the ordered paper as received. 

When purchase order "Receive" button is pressed, the user is redirected to "receive" page, where it is possible to receive the order "as is" - without any changes to the original order or to receive order "with changes" i.e. modify the received paper amount/price/receipt date. This functionality can be utilized in case the received values differ from the ordered ones (e.g. the cost was higher or less paper was received due to shortages or it arrived earlier/later than expected). When receiving the order, user must input "height" parameter - this is a measure of how high the paper stack is (in cm). This measurement is an additional indication of whether the received paper amount is correct according to the ordered one. The input height is compared to the expected height that is calculated in the back-end, depending on paper thickness and the amount of ordered sheets. This is done because paper sheets are not counted individually, instead the stack is measured and by knowing thickness of each sheet, it is possible to estimate the amount of sheets in the stack. If the actual height differs from expected height, a flashing message is shown to user to indicate that something might not be accurate.

##### 5. Cutting
This page shows workflow tasks for employee who is doing paper preparation for printing. Tasks for projects with status "OPEN" are shown in this page. The responsible employee looks through the list of tasks and either cuts the paper according to specifications or prepares the correct amount of paper that doesn't need any additional cutting. Once the preparation tasks are completed, the employee presses "DONE" and project status is changed to "PAPER PREPARED".

##### 6. Write-offs
This page shows workflow tasks for employee who is doing printing work. Tasks for projects with status "PAPER PREPARED" are shown in this page. The responsible employee looks through the list of tasks and marks down how many sheets of paper he actually used. He also sees how many sheets were originally planned for this task. Once the tasks are completed, the employee presses "DONE" and project status is changed to "WRITTEN OFF".

##### 7. Transactions
This page provides overview of all transactions that have taken changed the amount of paper in the warehouse. This includes purchase order receipts, paper cutting, paper write-offs and the results of initial stock counting. It is possible to filter the transactions by article/trx dates/trx types/suppliers/projects. Max 200 rows are shown in the page. By default the latest 200 transactions are shown in the page if nothing is filtered.

##### 8. Projects archive
This page provides overview of all historic projects that have the status "WRITTEN OFF". The main focus is to control the planned and actually used sheets of paper for the projects. It is possible to filter the projects by project number and article. Max 200 rows are shown in the page. By default the latest 200 projects are shown in the page if nothing is filtered.

##### 9. Add article
"Add article" tab allows to create new DB records for paper articles that do not yet exist in the warehouse. There are validations in place so that it is not possible to enter an article that already exists in the system.

##### 10. Update prices
This page allows to update prices for paper articles according to the supplier catalogue. It is possible to also note the date from which the new prices are effective. For clarity and to avoid mistakes, all current and future prices are for articles are shown, when user selects an article.

#### Additional notes
Overall this simple web-app provides a clear and easy to use interface for understanding the past, current and future status of a warehouse for a specific company. This web-app is meant to replace excel-based workflow that took a lot of manual work to maintain, wasn't providing real-time data and which historically had a lot of discrepancies. 

There are planned further iterations of the app that will include:
– Admin panel to edit and delete specific transactions in case of mistakes
– Some fine-tuning, input validation and other tweaks to existing functionality
– Automated cross-checks against other systems/workflows to ensure data correctness
– Automated import of planned projects from another system
— Others TBD
