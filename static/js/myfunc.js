//Financial Management
function fm_cal () {
    if(document.getElementById("fund").value.length == 0 || document.getElementById("my_d").value.length == 0 || document.getElementById("ch_d").value.length == 0){
        document.getElementById("fm_result").innerHTML = "Please enter information.";
        document.getElementById("fm_result").classList.add("bg-danger");
        document.getElementById("fm_result").classList.remove("bg-info");
    }else{
        let fund = parseFloat(document.getElementById("fund").value);
        let my_d = parseFloat(document.getElementById("my_d").value);
        my_d = my_d / 100;
        let ch_d = parseFloat(document.getElementById("ch_d").value);
        ch_d = ch_d / 100;
        let leverage = parseFloat(document.getElementById("leverage").value);
        let x = (my_d * fund) / (ch_d * leverage);
        document.getElementById("fm_result").innerHTML = "You must enter the position with : <br/><b>" + x.toFixed(2) + "</b> USDT";
        document.getElementById("fm_result").classList.add("bg-info");
        document.getElementById("fm_result").classList.remove("bg-danger");
    }
}

//Cancel Order
function cancel_order (id, market) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "/cancel-order?id=" + id + "&market=" + market, false ); // false for synchronous request
    //let result = JSON.parse(xmlHttp.responseText).data[0][2];
    xmlHttp.send( null );
}

function change_order_type(){
    let order_type = document.getElementById("order_type").value;
    if (order_type == 'market'){
        document.getElementById("price").value = '';
        document.getElementById("price").disabled = true;
    }
    else{
        document.getElementById("price").disabled = false;
    }
}
function print_can(){
    let price = parseFloat(document.getElementById("price").value);
    let amount = parseFloat(document.getElementById("amount").value);
    let leverage = parseFloat(document.getElementById("leverage_p").value);
    if (document.getElementById("amount").value.length != 0){
        document.getElementById("print_can_p").innerHTML = "You can open position with " + ((amount * leverage) / price) + " of " + document.getElementById("market").value;
    }
}

function open_pos_api(){
    let market = document.getElementById("market").value;
    let leverage = document.getElementById("leverage_p").value;
    let leverage_t = document.getElementById("leverage_pt").value;
    let order_type = document.getElementById("order_type").value;
    let amount = document.getElementById("amount").value;
    let price = document.getElementById("price").value;
    let pos = '';
    if(document.getElementById("type_long").checked){
        pos = 'long'
    }
    if(document.getElementById("type_short").checked){
        pos = 'short'
    }
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "/open_pos?type=" + order_type + "&market=" + market + "&leverage=" + leverage + "&amount=" + amount + "&price=" + price + "&pos=" + pos + "&leverage_t=" + leverage_t, false ); // false for synchronous request
    //let result = JSON.parse(xmlHttp.responseText).data[0][2];
    xmlHttp.send( null );
}

function close_pos_api(){
    let market = document.getElementById("market").value;
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "/closepos?" + "market=" + market, false ); // false for synchronous request
    //let result = JSON.parse(xmlHttp.responseText).data[0][2];
    xmlHttp.send( null );
}

function settpsl(){
    let market = document.getElementById("market").value;
    let tp = document.getElementById("tp").value;
    let sl = document.getElementById("sl").value;
    let tp_t = document.getElementById("tp_t").value;
    let sl_t = document.getElementById("sl_t").value;
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "/setstpsl?market=" + market + "&tp=" + tp + "&sl=" + sl + "&sl_t=" + sl_t + "&tp_t=" + tp_t, false ); // false for synchronous request
    //let result = JSON.parse(xmlHttp.responseText).data[0][2];
    xmlHttp.send( null );
}

setInterval(
    async function (){
        let market = document.getElementById("market").value;
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", "/update?market=" + market, true ); // false for synchronous request
        xmlHttp.onload = function (e) {
            if (xmlHttp.readyState === 4) {
                if (xmlHttp.status === 200) {
                    let price = JSON.parse(xmlHttp.responseText).price.data[0][2];
                    document.getElementById("price_now").innerHTML = price;

                    let asset = JSON.parse(xmlHttp.responseText).asset.data;
                    out = ''
                    for (var key in asset){
                        let avail = asset[key]['available']
                        if (avail == 0){
                            avail = 0;
                        }
                        let frozen = asset[key]['frozen']
                        if (frozen == 0){
                            frozen = 0;
                        }
                        out += "<tr><td>" + key + "</td><td>" + avail + "</td><td>" + frozen + "</td></tr>"
                    }
                    document.getElementById("asset_table").innerHTML = out

                    let pending = JSON.parse(xmlHttp.responseText).pending.data;
                    out = ''
                    for (var record in pending['records']){
                        if(record['side'] == 1){
                            let side = 'SHORT';
                        }else{
                            let side = 'LONG';
                        }
                        out += "<tr><td>" + pending['market'] + "</td><td>" + side + "</td><td>" + pending['price'] + "</td><td>" + pending['leverage'] + "</td><td>" + pending['amount'] + "</td><td><button class='btn btn-danger' onclick='show_order(" + parseInt(pending['order_id']) + "," + pending['market'] + ")''>Cancel</button></td></tr>";
                    }
                    document.getElementById("pending_table").innerHTML = out

                    let pos = JSON.parse(xmlHttp.responseText).pos.data;
                    if (pos.length == 0){
                        document.getElementById("pos_status").innerHTML = '<h3 class="text-center">You don\'t have open position.</h3>';
                    }else{
                        let pos = JSON.parse(xmlHttp.responseText).pos.data[0];
                        let side = pos['side']
                        if(side == 1){
                            side = 'Short'
                        }else{
                            side = 'Long'
                        }
                        out = '<div class="row hove-status"> \
                                <div class="col"> \
                                    <p>Side</p> \
                                </div> \
                                <div class="col d-flex flex-row-reverse"> \
                                    <p>' + side + '</p> \
                                </div> \
                                </div><hr/> \
                                <div class="row hove-status"> \
                                    <div class="col"> \
                                        <p>Entry Price</p> \
                                    </div> \
                                    <div class="col d-flex flex-row-reverse"> \
                                        <p>' + pos['open_price'] + '</p> \
                                    </div> \
                                </div><hr/> \
                                <div class="row hove-status"> \
                                    <div class="col"> \
                                        <p>Leverage</p> \
                                    </div> \
                                    <div class="col d-flex flex-row-reverse"> \
                                        <p>' + pos['leverage'] + '</p> \
                                    </div> \
                                </div><hr/> \
                                <div class="row hove-status"> \
                                    <div class="col"> \
                                        <p>Liquid Price</p> \
                                    </div> \
                                    <div class="col d-flex flex-row-reverse"> \
                                        <p>' + pos['liq_price'] + '</p> \
                                    </div> \
                                </div><hr/> \
                                <div class="row hove-status"> \
                                    <div class="col"> \
                                        <p>Take Profit</p> \
                                    </div> \
                                    <div class="col d-flex flex-row-reverse"> \
                                        <p>' + pos['take_profit_price'] + '</p> \
                                    </div> \
                                </div><hr/> \
                                <div class="row hove-status"> \
                                    <div class="col"> \
                                        <p>Stop Loss</p> \
                                    </div> \
                                    <div class="col d-flex flex-row-reverse"> \
                                        <p>' + pos['stop_loss_price'] + '</p> \
                                    </div> \
                                </div><hr/> \
                                <div class="row hove-status"> \
                                    <div class="col"> \
                                        <p>Percent</p> \
                                    </div> \
                                    <div class="col d-flex flex-row-reverse"> \
                                        <p>' + (((price - pos['open_price']) / pos['open_price']) * 100 * pos['leverage']) + '</p> \
                                    </div> \
                                </div><hr/>';
                        document.getElementById("pos_status").innerHTML = out;
                    }
                } else {
                    console.error(xmlHttp.statusText);
                }
            }
        };
        xmlHttp.send( null );
    },
5000);