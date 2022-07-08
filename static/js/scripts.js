// For use in Purchases sheet: function for dynamically changing purchase order field values, when sheet amount, pallet count or weight is being changed
function dynamicChange(inputField){
    var article = document.getElementById("article");
    var orderPll = document.getElementById("order_pll");
    var orderSheets = document.getElementById("order_sheets");
    var weight = document.getElementById("weight");
    for (var i = 0; i < papers.length; i++){
        if (article.value == papers[i].article){
            var stdWeight = parseFloat(papers[i].weight);
            var palletAmt = parseInt(papers[i].pallet_amt);
        }
    }
    if (inputField == 'article'){
        orderSheets.value = '';
        orderPll.value = '';
        weight.value = '';
    }
    else if (inputField == 'orderPll'){
        orderSheets.value = orderPll.value * palletAmt;
        weight.value = Math.round(orderSheets.value / 1000 * stdWeight);
    }
    else if (inputField == 'orderSheets'){
        orderPll.value = Math.round(orderSheets.value / palletAmt * 100) / 100;
        weight.value = Math.round(orderSheets.value / 1000 * stdWeight);
    }
};


// Function for adding row in table dynamically (for use in Projects, Purchases and Receive sheets)
function addRow(parameter) {
    var parentTable = document.getElementById("table").getElementsByTagName('tbody')[0];
    var myTd,myInput;
    var myTr = document.createElement('tr');
    myTr.setAttribute('class','unit-table');
    // Classname columns is used to identify all the columns that need new rows
    var myTh = document.getElementsByClassName("columns");
    for (i = 0; i < myTh.length; i++) {
        myTd = document.createElement('td');
        // Creates an array of TH tag class attributes to pass those on to new TD fields (for formatting etc.)
        myTdArray = myTh[i].className.split(' ')
        for (k = 0; k < myTdArray.length; k++){
            myTd.classList.add(myTdArray[k]);
        }
        myInput = document.createElement('input');
        myInput.setAttribute('type','text');
        // Name and ID are needed to be passed for those fields later to be submitted to DB
        myInput.setAttribute('name', myTh[i].getAttribute("name"));
        myInput.setAttribute('id', myTh[i].getAttribute("name"));
        myInput.setAttribute('autocomplete','off');
        myInput.setAttribute('required','');
        if (myTh[i].getAttribute("value")) {
            myInput.setAttribute('value', myTh[i].getAttribute("value"))
        }
        myInput.classList.add('form-control')
        // Custom html attributes from TH are passed to input fields (for formatting etc.)
        myCustomAttrs = myTh[i].getAttribute("customattr")
        if (myCustomAttrs) {
            myAttrArray = myTh[i].getAttribute("customattr").split(' ')
            for (j = 0; j < myAttrArray.length; j++) {
            myInput.classList.add(myAttrArray[j])
            }
        }
        myTd.appendChild(myInput);
        myTr.appendChild(myTd);
    }
    parentTable.appendChild(myTr);
    // Buttons are shown/hidden depending on available actions
    document.getElementById("addButton").style.display = 'none';
    document.getElementById("submitButton").style.display = 'block';

    if (parameter == 'purchases') {
    // For dynamic changing of values between pll/sheet amount/weight
    var articleObject = document.getElementById("article");
    articleObject.setAttribute('onchange','dynamicChange("article")');

    var pllObject = document.getElementById("order_pll");
    pllObject.setAttribute('onkeyup','dynamicChange("orderPll")');

    var sheetObject = document.getElementById("order_sheets");
    sheetObject.setAttribute('onkeyup','dynamicChange("orderSheets")');

    var weightObject = document.getElementById("weight");
    weightObject.setAttribute('readonly','');

    autocomplete(document.getElementById("article"), articleList);
    autocomplete(document.getElementById("supplier"), supplierList);
    autocomplete(document.getElementById("project"), projectList);

    }

    if (parameter == 'receive') {
        receiveOrder()
        }

    if (parameter == 'projects') {
        var article2Object = document.getElementById("article2");
        article2Object.removeAttribute('required');
        var sizediffObject = document.getElementById("sizediff");
        sizediffObject.removeAttribute('required');
        var statusObject = document.getElementById("status");
        statusObject.setAttribute('readonly','');
        statusObject.setAttribute('value','OPEN');
        autocomplete(document.getElementById("article"), articleList);
        autocomplete(document.getElementById("article2"), articleList);
        }

};

// ----- MEGA AUTO-COMPLETE FUNCTION -----

function autocomplete(inp, arr) {
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val) { return false;}
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        /*for each item in the array...*/
        for (i = 0; i < arr.length; i++) {
            /*check if the item starts with the same letters as the text field value:*/
            if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
            /*create a DIV element for each matching element:*/
            b = document.createElement("DIV");
            /*make the matching letters bold:*/
            b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
            b.innerHTML += arr[i].substr(val.length);
            /*insert a input field that will hold the current array item's value:*/
            b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
            /*execute a function when someone clicks on the item value (DIV element):*/
            b.addEventListener("click", function(e) {
                /*insert the value for the autocomplete text field:*/
                inp.value = this.getElementsByTagName("input")[0].value;
                /*close the list of autocompleted values,
                (or any other open lists of autocompleted values:*/
                closeAllLists();
            });
            a.appendChild(b);
            }
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 38) { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
            /*and simulate a click on the "active" item:*/
            if (x) x[currentFocus].click();
            }
        }
    });
    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
        x[i].classList.remove("autocomplete-active");
        }
    }
    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
        if (elmnt != x[i] && elmnt != inp) {
            x[i].parentNode.removeChild(x[i]);
        }
        }
    }
    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
    }

 
    // ----- END OF MEGA AUTO-COMPLETE FUNCTION -----
    
      
// Function for custom formatting negative stock values in backlog page
function dynamicBold() {
    var backlog = document.getElementsByClassName("backlog");
    var tablerow = document.getElementsByClassName("tablerow");
    for (i = 0; i < backlog.length; i++) {
        if (parseInt(backlog[i].innerText) < 0) {
            tablerow[i].classList.add('very-bold-text')
        }
    }    
};

function isLinked() {
    if (new URLSearchParams(window.location.search).get("source") == "backlog") {
        addRow('purchases')
        let articleName = new URLSearchParams(window.location.search).get("article");
        let orderAmount = new URLSearchParams(window.location.search).get("amount");
        document.getElementById("article").value = articleName;
        document.getElementById("order_sheets").value = orderAmount;
        calcFields()
    }
};

// this function calculates pallet and weight fields initially, when purchase order is generated from backlog page
function calcFields(){
    var orderSheets = parseInt(document.getElementById("order_sheets").value);
    var article = document.getElementById("article").value;
    for (var i = 0; i < papers.length; i++){
        if (article == papers[i].article){
            var stdWeight = parseFloat(papers[i].weight);
            var palletAmt = parseInt(papers[i].pallet_amt);
        }
    }
    document.getElementById("weight").value = Math.round(orderSheets / 1000 * stdWeight);
    document.getElementById("order_pll").value = Math.round(orderSheets / palletAmt * 100) / 100;
};
