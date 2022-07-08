function receiveOrder() {
    // For changing values when receiving order

    var orderDateObject = document.getElementById("order_date");
    orderDateObject.setAttribute('readonly','')
    orderDateObject.setAttribute('value','{{ order[0]["order_date"] }}');

    var articleObject = document.getElementById("article");
    articleObject.setAttribute('readonly','');
    articleObject.setAttribute('value','{{ order[0]["article"] }}');

    var pllObject = document.getElementById("order_pll");
    pllObject.setAttribute('onkeyup','dynamicChange("orderPll")');
    pllObject.setAttribute('value','{{ order[0]["order_pll"] }}');

    var sheetObject = document.getElementById("order_sheets");
    sheetObject.setAttribute('onkeyup','dynamicChange("orderSheets")');
    sheetObject.setAttribute('value','{{ order[0]["order_sheets"] }}');

    var sheetObject = document.getElementById("act_height");
    sheetObject.setAttribute('hidden','');
    sheetObject.removeAttribute('required','');

    var supplierObject = document.getElementById("supplier");
    supplierObject.setAttribute('readonly','');
    supplierObject.setAttribute('value','{{ order[0]["supplier"] }}');

    var pllObject = document.getElementById("eta_date");
    pllObject.setAttribute('value','{{ today }}');

    var projectObject = document.getElementById("project");
    projectObject.setAttribute('readonly','');
    projectObject.setAttribute('value','{{ order[0]["project"] }}');

    var weightObject = document.getElementById("weight");
    weightObject.setAttribute('readonly','');
    weightObject.setAttribute('value','{{ order[0]["weight"] }}');

    var priceObject = document.getElementById("price");
    priceObject.setAttribute('value','{{ order[0]["price"] }}');

    var buttonObject = document.getElementById("submitButton");
    buttonObject.setAttribute('value', 'changed');
}