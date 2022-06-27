from flask import Flask, render_template, redirect, session, request
from flask_session import Session
import hashlib
import json
import time

from lib import db
from lib import api

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
database = db.DB()
global Api
def get_secert():
    return database.get_secret(session.get('email'))

def get_admin():
    return database.get_user_admin(session.get('email'))

@app.route('/')
def home():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    secret = get_secert()
    global Api
    Api = api.CoinexPerpetualApi(secret[0], secret[1])
    markets = Api.get_market_info()['data']
    market_to = []
    for market in markets:
        if 'USDT' in market['name']:
            market_to.append(market['name'])
    return render_template('index.html', admin=get_admin(), market_to=market_to)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')
        if email == '' or password == '': 
            return redirect('/login')
        else:
            if database.get_login(email, password):
                session['email'] = email
                return redirect('/')
            else:
                return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['email'] = None
    return redirect('/')

@app.route('/ban')
def baned():
    return render_template('ban.html')

@app.route('/account', methods=['GET', 'POST'])
def account():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    data = database.get_account(session.get('email'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        access_id = request.form.get('access_id')
        secret_key = request.form.get('secret_key')
        old_pass = request.form.get('old_pass')
        new_pass = request.form.get('new_pass')
        new_pass_again = request.form.get('new_pass_again')
        if old_pass == '' or new_pass == '' or new_pass_again == '':
            database.update_account(data['id'], name, email, access_id, secret_key)
        else:
            if new_pass == new_pass_again:
                if  hashlib.sha256(old_pass.encode()).hexdigest() == data['pass']:
                    new_pass = hashlib.sha256(new_pass.encode()).hexdigest()
                    database.update_account_pass(data['id'], name, email, access_id, secret_key, new_pass)
                    return redirect('/logout')
    return render_template('account.html', data=data, admin=get_admin())

@app.route('/user', methods=['GET', 'POST'])
def user():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if not get_admin():
        return redirect('/')
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('pass')
        status = request.form.get('status')
        baned = request.form.get('baned')
        database.add_new_user(name, email, password, status, baned)
        return redirect('/user')
    users = database.get_user(session.get('email'))
    return render_template('user.html', admin=get_admin(), users=users)

@app.route('/change-status', methods=['GET'])
def change_status():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if not get_admin():
        return redirect('/')
    if request.method == 'GET':
        id = request.args.get("id")
        status = request.args.get("status")
        database.change_status(id, status)
        return redirect('/user')
    return redirect('/user')

@app.route('/change-baned', methods=['GET'])
def change_baned():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if not get_admin():
        return redirect('/')
    if request.method == 'GET':
        id = request.args.get("id")
        status = request.args.get("status")
        database.change_baned(id, status)
        return redirect('/user')
    return redirect('/user')

@app.route('/delete-user', methods=['GET'])
def delete_user():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if not get_admin():
        return redirect('/')
    if request.method == 'GET':
        id = request.args.get("id")
        database.delete_user(id)
        return redirect('/user')
    return redirect('/user')

@app.route('/get-coin-price', methods=['GET'])
def get_coin_price():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        market = request.args.get("market")
        out = Api.kline(market=market, limit=1, kline_type='1min')
        return out
    
@app.route('/open-pos', methods=['GET'])
def open_pos():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        type = request.args.get("type")
        market = request.args.get("market")
        leverage = request.args.get("leverage")
        leverage_t = request.args.get("leverage_t")
        amount = request.args.get("amount")
        price = request.args.get("price")
        pos = request.args.get("pos")
        if pos == 'long':
            pos = 1
        else:
            pos = 2
        Api.adjust_leverage(market, leverage_t, str(leverage))
        if type == 'limit':
            Api.put_limit_order(market, pos, str(amount), str(price))
        if type == 'market':
            Api.put_market_order(market, pos, str(amount))
    
@app.route('/get-asset', methods=['GET'])
def get_asset():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        out = Api.query_account()
        return out
    
@app.route('/get-pending', methods=['GET'])
def get_pending():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        out = Api.query_order_pending('null', 0, 0)
        return out
    
@app.route('/cancel-order', methods=['GET'])
def cancel_order():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        id = request.args.get("id")
        market = request.args.get("market")
        out = Api.cancel_order(market, id)
        return out

@app.route('/update', methods=['GET'])
def update():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        result = {}
        market = request.args.get("market")
        out = Api.kline(market=market, limit=1, kline_type='1min')
        result['price'] = out
        time.sleep(1)
        out = Api.query_account()
        result['asset'] = out
        time.sleep(1)
        out = Api.query_order_pending(market, 0, 0)
        result['pending'] = out
        time.sleep(1)
        out = Api.query_position_pending(market)
        result['pos'] = out
        return json.dumps(result)

@app.route('/deposit', methods=['GET'])
def deposit():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    secret = get_secert()
    global Api
    Api = api.CoinexPerpetualApi(secret[0], secret[1])
    return render_template('deposit.html', admin=get_admin())
    
@app.route('/get-deposit', methods=['GET'])
def get_deposit():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        market = request.args.get("market")
        chain = request.args.get("chain")
        out = Api.get_deposite_address(market, chain)
        return out
    
@app.route('/set-withdraw', methods=['GET'])
def set_withdraw():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        market = request.args.get("market")
        chain = request.args.get("chain")
        target = request.args.get("target")
        amount = request.args.get("amount")
        out = Api.submit_withdraw(market, chain, target, amount)
        return out
    
@app.route('/getall_asset', methods=['GET'])
def getall_asset():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        result = {}
        out = Api.query_account()
        result['asset_f'] = out
        time.sleep(1)
        out = Api.asset_s()
        result['asset_s'] = out
        return result

@app.route('/trasfer', methods=['GET'])
def trasfer():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        market = request.args.get("market")
        status = request.args.get("status")
        amount = request.args.get("amount")
        out = Api.transfer(market, status, amount)
        return out
    
@app.route('/settpsl', methods=['GET'])
def settpsl():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        market = request.args.get("market")
        tp = request.args.get("tp")
        tp_t = request.args.get("tp_t")
        sl = request.args.get("sl")
        sl_t = request.args.get("sl_t")
        out = Api.query_position_pending(market)['data']
        if len(out != 0):
            id = out[0]['position_id']
            if sl != '':
                if tp == '':
                    Api.setsl(market, id, sl_t, sl)
                else:
                    Api.setsl(market, id, sl_t, sl)
                    time.sleep(1)
                    Api.settp(market, id, tp_t, tp)
        return 0
    
@app.route('/closepos', methods=['GET'])
def closepos():
    if not session.get('email'):
        return redirect('/login')
    else:
        if database.get_ban(session.get('email')):
            return redirect('/ban')
    if request.method == 'GET':
        market = request.args.get("market")
        out = Api.query_position_pending(market)['data']
        if len(out != 0):
            id = out[0]['position_id']
            Api.close_pos(market, id)
        return 0
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')