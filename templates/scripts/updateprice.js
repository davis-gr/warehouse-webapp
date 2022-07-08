function showPrices(){
    var nameObject = document.getElementById("name").value;
    var paraObject = document.getElementById("paragraph");
    paraObject.innerHTML = '';
    var allPrices = {{ allPrices | tojson}};
    var prices = [];
    var singlePrice = {};
    for (var i = 0; i < allPrices.length; i++) {
        if (allPrices[i]["name"] == nameObject) {
            singlePrice["name"] = allPrices[i]["name"];
            singlePrice["date_from"] = allPrices[i]["date_from"];
            singlePrice["price_per_tonne"] = allPrices[i]["price_per_tonne"];
            let p = document.createElement("p");
            p.innerText = `Price for ${singlePrice["name"]} from ${singlePrice["date_from"]}: ${singlePrice["price_per_tonne"]}€`;
            paraObject.appendChild(p);
        }
    }
    paraObject.removeAttribute('hidden');
};
