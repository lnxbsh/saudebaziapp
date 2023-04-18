from flask import Flask, render_template, request
import psycopg2
import re
import json
import os
app = Flask(__name__)



#@app.route('/init')
def db(method='GET', data=''):
    customer = ''
    conn = psycopg2.connect(
        host="dpg-cgtv1paut4mcfrnp2b70-a",
        database="saudebazi",
        user=os.getenv('username'),
        password=os.getenv('password'))
    cur = conn.cursor()
    
    if data:
        if method == 'POST':
            cur.execute('INSERT INTO COMMENT_DATA(entered_number, dialed_number, comment, timestamp) VALUES(%s,%s,%s,%s)',(data['entered_number'],data['dialed_number'],data['comment'],data['timestamp']), )
            conn.commit()
            cur.execute('SELECT * FROM COMMENT_DATA')
            return cur.fetchall()
        elif method == 'PUT':
            print(data)

            for key, value in data.items():
                cur.execute(f'UPDATE CLEANEDTABLE SET "{key}" =' +  ' %(val)s WHERE "Mobile 1" LIKE %(number)s',({"val":value,"number":'%{}%'.format(data["Mobile 1"])}))
 #               cur.execute('UPDATE CLEANEDTABLE SET "%(col)s = %(val)s" WHERE "Mobile 1" LIKE %(number)s',({  "col": key,"val": value,'number': '%{}%'.format(data["Mobile 1"])}))
            conn.commit()
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
            return customer, alist
            # print(alist)
            # for a in alist:
            #     templist = []
            #     print(a)
            #     templist.append(fetchMatch(cur,a))
            #     leads = templist
            # print(leads)

    cur.close()
    conn.close()
    





@app.route('/matching', methods=["GET",'POST',"PUT"])
def match():
    if request.method == 'GET':
        number = request.args.get('number')
        #print (number)
        fetch, leads = db(data=number)
        return render_template('match.html',data = [fetch[1:],leads])
        #return  json.dumps(db('POST', data))

    elif request.method == 'POST':
        print('POST is called')
        formData = request.get_json("body")
        entered_number = formData['entered_number']
        dialed_number = formData['dialed_number']
        comment = formData['comment']
        timestamp = formData['timestamp']
        data = { 'entered_number':entered_number, 'dialed_number': dialed_number, 'comment':comment, 'timestamp':timestamp }
        comment_data= db('POST',data=data)
        return json.dumps({"message":"Done", "comment_data":comment_data})

    elif request.method == 'PUT':
        data = request.get_json('body')
        print(data)
        res = db(method='PUT',data=data)
        print("PUT is effective")
        return json.dumps(res)
    
# @app.route('/postdata',methods =["POST"])
# def postData():
    #  if request.method == 'POST':
    #     print('POST is called')
    #     formData = request.get_json("body")
    #     entered_number = formData['entered_number']
    #     dialed_number = formData['dialed_number']
    #     comment = formData['comment']
    #     data = { 'entered_number':entered_number, 'dialed_number': dialed_number, 'comment':comment }
    #     db('POST',data=data)
    #     return json.dumps("Done")


def fetchMatch(cur,commoditiy):
    print(commoditiy)
    cur.execute('SELECT * FROM cleanedtable WHERE "Current Commodity" LIKE %(name)s ORDER BY RANDOM() LIMIT 3', { 'name': '%{}%'.format(commoditiy)})
    #cur.execute("SELECT * FROM CLEANEDTABLE WHERE 'Current Commodity' = %s", commoditiy)
    return cur.fetchall()    



@app.route('/')
def index():
    if request.method == 'GET':
        return render_template("index.html")

if __name__ == "__main__":
    app.run(port=8000)
