from flask import Flask, render_template, request
import psycopg2
import pandas as pd
import re
import json
app = Flask(__name__)




#@app.route('/init')
def db(method='GET', data=''):
    customer = ''
    conn = psycopg2.connect(
        host="dpg-cgtv1paut4mcfrnp2b70-a.singapore-postgres.render.com",
        database="saudebazi",
        user="saudebaz",
        password="emJNrMiFX83SRCwFcokOnwhzNJkaU7Fn")
    cur = conn.cursor()
    
    if data:
        if method == 'POST':
            cur.excute('INSERT INTO COMMENTTABLE(entered_number, dialed_number, comment) VALUES(%s,%s,%s)',data['entered_number'],data['dialed_number'],data['comment'] )
            cur.commit()
        elif method == 'PUT':
            print(data)
            number = data['number']
            info = data['info']
            cur.execute("")
            cur.execute('UPDATE CLEANEDTABLE SET VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) where "Mobile 1" LIKE %(number)s',(info[0],info[1],info[3],info[4],info[5],info[6],info[7],info[8],info[9],info[10],info[11],info[12],info[13],info[14],info[15],info[16],info[17],info[18]),{ 'number': '%{}%'.format(number)})
            cur.commit()
            return "Data Updated"
        
        elif method == 'GET':    
            alist = []
            leads = set()
            print(f'this is data {data}')
            cur.execute('SELECT * FROM CLEANEDTABLE WHERE "Mobile 1" LIKE %(name)s', { 'name': '%{}%'.format(data)})
            customer = cur.fetchone()
            print(customer)
            #leads = fetchMatch(cur,customer[13])
            print(customer[13])
            cus = re.sub('[^A-Za-z0-9]+', '-', customer[13])
            print(cus)
            for d in cus.split('-'):
                alist.append(fetchMatch(cur,d))
            
            # print(alist)
            # for a in alist:
            #     templist = []
            #     print(a)
            #     templist.append(fetchMatch(cur,a))
            #     leads = templist
            # print(leads)

    cur.close()
    conn.close()
    return customer, alist





@app.route('/matching', methods=["GET","POST","PUT"])
def match():
    if request.method == 'GET':
        number = request.args.get('number')
        #print (number)
        fetch, leads = db(data=number)
        return render_template('match.html',data = [fetch[1:],leads])
    
    elif request.method == 'POST':
        print('POST is called')
        entered_number = request.form['entered_number']
        dialed_number = request.form['dialed_number']
        comment = request.form['comment']
        data = { 'entered_number':entered_number, 'dialed_number': dialed_number, 'comment':comment }
        return  json.dumps(db('POST', data))
    
    elif request.method == 'PUT':
        data = request.get_json('body')
        res = db(method='PUT',data=data)
        print("PUT is effective")
        return json.dumps(res)


def fetchMatch(cur,commoditiy):
    print(commoditiy)
    cur.execute('SELECT * FROM cleanedtable WHERE "Current Commodity" LIKE %(name)s', { 'name': '%{}%'.format(commoditiy)})
    #cur.execute("SELECT * FROM CLEANEDTABLE WHERE 'Current Commodity' = %s", commoditiy)
    return cur.fetchall()    



@app.route('/')
def index():
    if request.method == 'GET':
        return render_template("index.html")


app.run(port=8000)
