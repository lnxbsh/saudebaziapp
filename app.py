from flask import Flask, render_template, request
import psycopg2
import re
import json
import os
from psycopg2 import sql
import requests as r
from random import shuffle,choice
app = Flask(__name__)

user = "saudebaz"
password = "emJNrMiFX83SRCwFcokOnwhzNJkaU7Fn"
# user = os.getenv('username')
# password = os.getenv('password')
#@app.route('/init')
def db(method='GET', data=''):
    customer = ''
    conn = psycopg2.connect(
        host="dpg-cgtv1paut4mcfrnp2b70-a.singapore-postgres.render.com",
        database="saudebazi",
        user=user,
        password=password)
    cur = conn.cursor() 
    
    if data:
        if method == 'POST':
            cur.execute('INSERT INTO comment_data(number_entered_seeker, number_dialed_provided, comment, timestamp) VALUES(%s,%s,%s,%s)',(data['number_entered_seeker'],data['number_dialed_provided'],data['comment'],data['timestamp']), )
            conn.commit()
            cur.execute('SELECT * FROM comment_data')
            return cur.fetchall()
        
        elif method == 'PUT':
            print(data)

            for key, value in data.items():
                cur.execute(f'UPDATE CLEANEDTABLE SET "{key}" =' +  ' %(val)s WHERE "Mobile 1" LIKE %(number)s',({"val":value,"number":'%{}%'.format(data["Mobile 1"])}))
 #               cur.execute('UPDATE CLEANEDTABLE SET "%(col)s = %(val)s" WHERE "Mobile 1" LIKE %(number)s',({  "col": key,"val": value,'number': '%{}%'.format(data["Mobile 1"])}))
            conn.commit()
            return "Data Updated"
        
        elif method == 'GET':
            inx = 0
            table_coloumn = ["index","Type of customer","Source","Status of calling","Date","Company Name","Location","Mobile 1","Mobile 2","Call disposition","Comments","Call back comments","Customer Name","Current Commodity","Whatsapp Number","Company brochure","Business card","Target customers","2nd call Comments"]    
            alist = []
            #leads = dict()
            print(f'this is data {data}')
            cur.execute('SELECT * FROM CLEANEDTABLE WHERE "Mobile 1" LIKE %(number)s', { 'number': '%{}%'.format(data)})
            customer = cur.fetchone()
            
            print(customer)
            
            #leads = fetchMatch(cur,customer[13])
            # print(customer[13])
            # if customer[13]:
            #     cus = re.sub('[^A-Za-z0-9]+', '-', customer[13])
            # else: 
            #     cus = 'None' 
            # print(cus)

            # if cus != 'None':
            #     for d in cus.split('-'):
            #         temp = fetchMatch(cur,d)
            #         for t in temp:
            #             leads = {}
            #             for i in range(len(t)):
            #                 leads[table_coloumn[i]] = t[i]
            #         alist.append(leads)
                
            # else:
            #     temp = fetchMatch(cur,'spices')
            #     for t in temp:
            #         leads = {}
            #         for i in range(len(t)):
            #             leads[table_coloumn[i]] = t[i]
            #         alist.append(leads)
            
            allNumbers = getNumbers(customer[13])
            
            numbers = set()
            while len(numbers) <= 2:
                shuffle(allNumbers)
                numbers.add(choice(allNumbers)["number"])

            print(numbers)

            
            temp = fetchMatchByNumber(cur,numbers)
            print(temp)
            for t in temp:
                leads = {}
                for i in range(len(t)):
                    leads[table_coloumn[i]] = t[i]
                alist.append(leads)
             
            mobilesNums = getConnectedUser(cur,data)
            mobilesNums.append("9829239542")



            print(alist)
            return customer, alist,mobilesNums
            # print(alist)
            # for a in alist:
            #     templist = []
            #     print(a)
            #     templist.append(fetchMatch(cur,a))
            #     leads = templist
            # print(leads)

    cur.close()
    conn.close()
    

def getNumbers(cus):
    if cus:
        dataJSON =  r.get("https://spice-matcher.onrender.com/p/" + cus)
    else:
        dataJSON = r.get("https://spice-matcher.onrender.com/p/" + "spices")
    print(dataJSON.text)
    dataJSON = json.loads(dataJSON.text)
    return dataJSON

@app.route('/broker_ref',methods=["POST","PUT","GET"])
def addBroker():
    if request.method == "POST":
        data = request.get_json("body")
        print(data)
        broker_mobile = data["broker_mobile"]
        broker_name = data["broker_name"]
        number_entered_seeker = data["number_entered_seeker"]
        number_dialed_provided = data["number_dialed_provided"]
        #string = f"INSERT INTO broker_ref (broker_name,broker_mobile,number_entered_seeker,number_dialed_provided) values ( '%({broker_name})s',{broker_mobile},{number_entered_seeker},{number_dialed_provided})"
        string = "INSERT INTO broker_ref (broker_name,broker_mobile,number_entered_seeker,number_dialed_provided) VALUES ('{}','{}','{}','{}' )".format(broker_name,broker_mobile,number_entered_seeker,number_dialed_provided)
        broker_db(string)
        dic = {}
        dic["status"] = "yo yo"
        return json.dumps(dic)

@app.route('/matching', methods=["GET",'POST',"PUT"])
def match():
    if request.method == 'GET':
        number = request.args.get('number')
        #print (number)
        fetch, leads, mobileNums = db(data=number)
        return render_template('match.html',data = {"fetch":fetch[1:],"leads":leads,"mobileNums":mobileNums})
        #return  json.dumps(db('POST', data))

    elif request.method == 'POST':
        print('POST is called')
        formData = request.get_json("body")
        number_dialed_provided = formData['number_dialed_provided']
        number_entered_seeker = formData['number_entered_seeker']
        comment = formData['comment']
        timestamp = formData['timestamp']
        data = { 'number_entered_seeker':number_entered_seeker, 'number_dialed_provided': number_dialed_provided, 'comment':comment, 'timestamp':timestamp }
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

def fetchMatchByNumber(cur,numbers):
    customers = []
    for num in numbers:
        print(num)
        cur.execute('SELECT * FROM customer_table WHERE "Mobile 1" LIKE %(number)s ', { 'number': '%{}%'.format(num)})
        val = cur.fetchone()
        customers.append(val)
    return customers

def getConnectedUser(cur,num):
    numbers = []
    cur.execute('SELECT number_dialed_provided FROM connected_status WHERE "number_entered_seeker" LIKE %(number)s ', { 'number': '%{}%'.format(num)})
    numbers = cur.fetchall()
    return numbers
    


    
@app.route('/handleCustomer', methods=['POST'])
def handleCustomer():
        status = dbHelper(request.get_json("body")["number"])
        dic = {}
        dic["status"] = status
        return json.dumps(dic)
    


@app.route('/createCustomer', methods= ["POST","PUT"])
def createCustomer():
    dic ={}
    
    if request.method == "POST":
        status = addCustomer(request.get_json("body"))
        dic["status"] = status
        return json.dumps(dic)
    elif request.method == 'PUT':
        status = updateCustomer(request.get_json("body"))
        
        return json.dumps(status)

def updateCustomer(data):
    conn = psycopg2.connect(
        host="dpg-cgtv1paut4mcfrnp2b70-a.singapore-postgres.render.com",
        database="saudebazi",
        user='saudebaz',
        password=password)
    cur = conn.cursor()
    dic = {}
    del(data["broker_name"])
    del(data["broker_mobile"])
    
    for key, value in data.items():
                cur.execute(f'UPDATE company_details SET "{key}" =' +  ' %(val)s WHERE "number" LIKE %(number)s',({"val":value,"number":'%{}%'.format(data["number"])}))
 #               cur.execute('UPDATE CLEANEDTABLE SET "%(col)s = %(val)s" WHERE "Mobile 1" LIKE %(number)s',({  "col": key,"val": value,'number': '%{}%'.format(data["Mobile 1"])}))
                conn.commit()
    dic["status"] = "Updated" 
    return dic


def addCustomer(data):
    conn = psycopg2.connect(
        host="dpg-cgtv1paut4mcfrnp2b70-a.singapore-postgres.render.com",
        database="saudebazi",
        user='saudebaz',
        password=password)
    cur = conn.cursor()

    broker_name = data["broker_name"]
    broker_number = data["broker_mobile"]
    del(data["broker_name"])
    del(data["broker_mobile"])
    k = list()
    for key in data.keys():
        k.append(key)
    
    k = ",".join(k)

    k = "(" + k +  ")"
    
    v = list()
    for val in data.values():
        val = "'" + val + "'"
        v.append(val)
    v = ",".join(v)
    v = "(" + v +  ")" 
        
    #cur.execute(f'UPDATE CLEANEDTABLE SET "{key}" =' +  ' %(val)s WHERE "Mobile 1" LIKE %(number)s',({"val":value,"number":'%{}%'.format(data["Mobile 1"])}))
    print(f"{k} = {v}")
    cur.execute("INSERT INTO company_details {0} VALUES{1}".format(k,v))
    conn.commit()
    return "Created"


def broker_db(query):
    conn = psycopg2.connect(
        host="dpg-cgtv1paut4mcfrnp2b70-a.singapore-postgres.render.com",
        database="saudebazi",
        user='saudebaz',
        password=password)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()
    print("done")

@app.route('/connectedStatus',methods = ['POST'])
def statusCheckDBHelper():
    if request.method == "POST":
        data = request.get_json("body")
        dic = checkExistDB(data)
    return json.dumps(dic)



def checkExistDB(data):
    conn = psycopg2.connect(
        host="dpg-cgtv1paut4mcfrnp2b70-a.singapore-postgres.render.com",
        database="saudebazi",
        user='saudebaz',
        password=password)
    cur = conn.cursor()
    dic = {}
    number1,number2,connected,timestamp = data['number_entered_seeker'],data['number_dialed_provided'],data['connected'],data['timestamp']
   
    #cur.execute(f"select count(*) from connected_status where number_entered_seeker LIKE '%{number1}%' AND  number_dialed_provided LIKE '%{number2}%'")
    #print(cur.fetchall())
    cur.execute("select count(*) from connected_status where number_dialed_provided LIKE %(number2)s AND  number_entered_seeker LIKE %(number1)s",{"number1":'%{}%'.format(number1),"number2":'%{}%'.format(number2)})
    # query = sql.SQL("select count(*) from {table} where {pkey} = %s AND {skey} = %s").format(
    
    # table=sql.Identifier('connected_status'),
    # pkey=sql.Identifier('number_dialed_provided'),
    # skey = sql.Identifier('number_entered_seeker'))
    # cur.execute(query,(number2,number1,))
    val = cur.fetchall()
    print(val[0])
    if  val[0][0] == 0:
        cur.execute(f"INSERT INTO connected_status(number_dialed_provided,number_entered_seeker,connected,timestamp) values('{number2}','{number1}','{connected}','{timestamp}')")
        conn.commit()
        dic["status"] = "Connected"
        return dic
    
    else:
        dic["status"] = "Already Connected"
        return dic
    
        

def dbHelper(number):
    conn = psycopg2.connect(
        host="dpg-cgtv1paut4mcfrnp2b70-a.singapore-postgres.render.com",
        database="saudebazi",
        user='saudebaz',
        password=password)
    cur = conn.cursor()

    # broker_name = data["broker_name"]
    # broker_number = data["broker_number"]
    # del(data["broker_name"])
    # del(data["broker_number"])
    # keys = set(data.keys())
    # keys.remove("broker_name","broker_number")
    # values = set(data.values())
    # values.remove()
    # cur.execute(f'INSERT INTO company_details {keys} values({values})')
    # conn.commit()
    
    cur.execute(f"select count(*) from company_details where number like '%{number}%' " )
    val = cur.fetchall()
    print(val)
    cur.close()
    conn.close()
    return val[0]
    


@app.route('/')
def index():
    if request.method == 'GET':
        return render_template("index.html")

if __name__ == "__main__":
    app.run(port=8000,debug=True)
