from flask import Flask, render_template, request
import pymongo
import datetime
import tensorflow as tf
import numpy as np
import cv2


app = Flask(__name__)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

if "bank_database" not in myclient.list_database_names():
    mydb = myclient["bank_database"]
else:
    mydb = myclient["bank_database"]
if "bank_database" not in mydb.list_collection_names():
    mycol = mydb["bank_database"]
else:
    mycol = mydb["bank_database"]



for x in mycol.find():
    print(x)

ml_model = tf.keras.models.load_model("house_predictions.h5")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/creation", methods=['POST'])
def creation():
    global cname, cpin
    if request.method == "POST":
        cname = request.form.get("cname")
        cpin = int(request.form.get("cpin"))
        ccpin = int(request.form.get("ccpin"))
        if cpin != ccpin:
            return render_template("home.html")
        try:
            if cname == mycol.find_one({"name":cname, "pin":cpin})["name"] and cpin == mycol.find_one({"name":cname, "pin":cpin})["pin"]:
                return render_template("home.html")
        except:
            return render_template("account_created.html")


@app.route("/create_account", methods=["POST"])
def create_account():
    global name, pin
    if request.method == "POST":
        name = request.form.get("aname")
        pin = int(request.form.get("apin"))
        cpin = int(request.form.get("acpin"))
        amount = int(request.form.get("aamount"))
        if pin != cpin:
            return render_template("account_created.html")
        date = datetime.datetime.now()
        credit_date = str(date.date().strftime('%d-%m-%Y'))
        data = {"name":name, "pin":pin, "loan":[], "debit":[], "credit":[amount,], "loan_date":[], "credit_date":[credit_date,], "debit_date":[]}
        mycol.insert_one(data)
        total_amount = sum(mycol.find_one({"name": name, "pin": pin})["loan"]) + sum(
            mycol.find_one({"name": name, "pin": pin})["credit"]) - sum(
            mycol.find_one({"name": name, "pin": pin})["debit"])
        loan_money = mycol.find_one({"name": name, "pin": pin})["loan"]
        loan_date = mycol.find_one({"name": name, "pin": pin})["loan_date"]
        credit_money = mycol.find_one({"name": name, "pin": pin})["credit"]
        credit_date = mycol.find_one({"name": name, "pin": pin})["credit_date"]
        debit_money = mycol.find_one({"name": name, "pin": pin})["debit"]
        debit_date = mycol.find_one({"name": name, "pin": pin})["debit_date"]
        return render_template("main_file.html", send_name=name.upper(), total_money=total_amount,
                               len_loan=len(loan_money), len_credit=len(credit_money), len_debit=len(debit_money),
                               loan_money=loan_money, loan_date=loan_date, credit_money=credit_money,
                               debit_money=debit_money, credit_date=credit_date, debit_date=debit_date)



@app.route("/main_file", methods=['POST'])
def main_file():
    global name, pin
    if request.method == "POST":
        name = request.form.get("name")
        pin = int(request.form.get("pin"))
        try:
            if name != mycol.find_one({"name":name, "pin":pin})["name"] and pin != mycol.find_one({"name":name, "pin":pin})["pin"]:
                return render_template("home.html")
        except:
            return render_template("home.html")
        total_amount = sum(mycol.find_one({"name":name, "pin":pin})["loan"]) + sum(mycol.find_one({"name":name, "pin":pin})["credit"]) - sum(mycol.find_one({"name":name, "pin":pin})["debit"])
        loan_money = mycol.find_one({"name":name, "pin":pin})["loan"]
        loan_date = mycol.find_one({"name":name, "pin":pin})["loan_date"]
        credit_money = mycol.find_one({"name":name, "pin":pin})["credit"]
        credit_date = mycol.find_one({"name": name, "pin": pin})["credit_date"]
        debit_money = mycol.find_one({"name": name, "pin": pin})["debit"]
        debit_date = mycol.find_one({"name":name, "pin":pin})["debit_date"]

        return render_template("main_file.html", send_name = name.upper(), total_money = total_amount, len_loan = len(loan_money), len_credit=len(credit_money), len_debit=len(debit_money), loan_money=loan_money, loan_date = loan_date, credit_money = credit_money, debit_money=debit_money, credit_date=credit_date, debit_date = debit_date)


@app.route("/deposit_money", methods=["POST"])
def deposit_money():
    if request.method == "POST":
        credit = int(request.form.get("credit"))
        credit_lst = mycol.find_one({"name":name, "pin":pin})["credit"]
        date_lst = mycol.find_one({"name": name, "pin": pin})["credit_date"]
        date = datetime.datetime.now()
        date_lst.append(str(date.date().strftime('%d-%m-%Y')))
        credit_lst.append(credit)
        mycol.update_one({"name":name, "pin":pin}, {"$set":{"credit":credit_lst}})
        mycol.update_one({"name":name, "pin":pin}, {"$set":{"credit_date":date_lst}})
        total_amount = sum(mycol.find_one({"name": name, "pin": pin})["loan"]) + sum(
            mycol.find_one({"name": name, "pin": pin})["credit"]) - sum(
            mycol.find_one({"name": name, "pin": pin})["debit"])
        loan_money = mycol.find_one({"name": name, "pin": pin})["loan"]
        loan_date = mycol.find_one({"name": name, "pin": pin})["loan_date"]
        credit_money = mycol.find_one({"name": name, "pin": pin})["credit"]
        credit_date = mycol.find_one({"name": name, "pin": pin})["credit_date"]
        debit_money = mycol.find_one({"name": name, "pin": pin})["debit"]
        debit_date = mycol.find_one({"name": name, "pin": pin})["debit_date"]
        return render_template("main_file.html", send_name=name.upper(), total_money=total_amount,
                               len_loan=len(loan_money), len_credit=len(credit_money), len_debit=len(debit_money),
                               loan_money=loan_money, loan_date=loan_date, credit_money=credit_money,
                               debit_money=debit_money, credit_date=credit_date, debit_date=debit_date)


@app.route("/withdrawal_money", methods=["POST"])
def withdrawal_money():
    if request.method == "POST":
        debit = int(request.form.get("debit"))
        debit_lst = mycol.find_one({"name":name, "pin":pin})["debit"]
        date_lst = mycol.find_one({"name": name, "pin": pin})["debit_date"]
        date = datetime.datetime.now()
        date_lst.append(str(date.date().strftime('%d-%m-%Y')))
        debit_lst.append(debit)
        mycol.update_one({"name":name, "pin":pin}, {"$set":{"debit":debit_lst}})
        mycol.update_one({"name":name, "pin":pin}, {"$set":{"debit_date":date_lst}})
        total_amount = sum(mycol.find_one({"name": name, "pin": pin})["loan"]) + sum(
            mycol.find_one({"name": name, "pin": pin})["credit"]) - sum(
            mycol.find_one({"name": name, "pin": pin})["debit"])
        loan_money = mycol.find_one({"name": name, "pin": pin})["loan"]
        loan_date = mycol.find_one({"name": name, "pin": pin})["loan_date"]
        credit_money = mycol.find_one({"name": name, "pin": pin})["credit"]
        credit_date = mycol.find_one({"name": name, "pin": pin})["credit_date"]
        debit_money = mycol.find_one({"name": name, "pin": pin})["debit"]
        debit_date = mycol.find_one({"name": name, "pin": pin})["debit_date"]
        return render_template("main_file.html", send_name=name.upper(), total_money=total_amount,
                               len_loan=len(loan_money), len_credit=len(credit_money), len_debit=len(debit_money),
                               loan_money=loan_money, loan_date=loan_date, credit_money=credit_money,
                               debit_money=debit_money, credit_date=credit_date, debit_date=debit_date)


@app.route("/deposit_loan", methods=['POST'])
def deposit_loan():
    if request.method == "POST":
        loan = -int(request.form.get("loan_negative"))
        loan_lst = mycol.find_one({"name": name, "pin": pin})["loan"]
        date_lst = mycol.find_one({"name": name, "pin": pin})["loan_date"]
        date = datetime.datetime.now()
        date_lst.append(str(date.date().strftime('%d-%m-%Y')))
        loan_lst.append(loan)
        mycol.update_one({"name": name, "pin": pin}, {"$set": {"loan": loan_lst}})
        mycol.update_one({"name": name, "pin": pin}, {"$set": {"loan_date": date_lst}})
        total_amount = sum(mycol.find_one({"name": name, "pin": pin})["loan"]) + sum(
            mycol.find_one({"name": name, "pin": pin})["credit"]) - sum(
            mycol.find_one({"name": name, "pin": pin})["debit"])
        loan_money = mycol.find_one({"name": name, "pin": pin})["loan"]
        loan_date = mycol.find_one({"name": name, "pin": pin})["loan_date"]
        credit_money = mycol.find_one({"name": name, "pin": pin})["credit"]
        credit_date = mycol.find_one({"name": name, "pin": pin})["credit_date"]
        debit_money = mycol.find_one({"name": name, "pin": pin})["debit"]
        debit_date = mycol.find_one({"name": name, "pin": pin})["debit_date"]
        return render_template("main_file.html", send_name=name.upper(), total_money=total_amount,
                               len_loan=len(loan_money), len_credit=len(credit_money), len_debit=len(debit_money),
                               loan_money=loan_money, loan_date=loan_date, credit_money=credit_money,
                               debit_money=debit_money, credit_date=credit_date, debit_date=debit_date)


@app.route("/request_loan", methods=['POST'])
def request_loan():
    if request.method == "POST":
        loan = int(request.form.get("loan_positive"))
        loan_lst = mycol.find_one({"name": name, "pin": pin})["loan"]
        date_lst = mycol.find_one({"name": name, "pin": pin})["loan_date"]
        date = datetime.datetime.now()
        date_lst.append(str(date.date().strftime('%d-%m-%Y')))
        loan_lst.append(loan)
        mycol.update_one({"name": name, "pin": pin}, {"$set": {"loan": loan_lst}})
        mycol.update_one({"name": name, "pin": pin}, {"$set": {"loan_date": date_lst}})
        total_amount = sum(mycol.find_one({"name": name, "pin": pin})["loan"]) + sum(
            mycol.find_one({"name": name, "pin": pin})["credit"]) - sum(
            mycol.find_one({"name": name, "pin": pin})["debit"])
        loan_money = mycol.find_one({"name": name, "pin": pin})["loan"]
        loan_date = mycol.find_one({"name": name, "pin": pin})["loan_date"]
        credit_money = mycol.find_one({"name": name, "pin": pin})["credit"]
        credit_date = mycol.find_one({"name": name, "pin": pin})["credit_date"]
        debit_money = mycol.find_one({"name": name, "pin": pin})["debit"]
        debit_date = mycol.find_one({"name": name, "pin": pin})["debit_date"]
        return render_template("main_file.html", send_name=name.upper(), total_money=total_amount,
                               len_loan=len(loan_money), len_credit=len(credit_money), len_debit=len(debit_money),
                               loan_money=loan_money, loan_date=loan_date, credit_money=credit_money,
                               debit_money=debit_money, credit_date=credit_date, debit_date=debit_date)


@app.route("/transfer_money", methods=["POST"])
def transfer_money():
    if request.method == "POST":
        amount = int(request.form.get("transfer_amount"))
        person_name = request.form.get("person_name")
        person_pin = int(request.form.get("person_pin"))
        debit_lst = mycol.find_one({"name":name, "pin":pin})["debit"]
        date_lst = mycol.find_one({"name": name, "pin": pin})["debit_date"]
        date = datetime.datetime.now()
        date_lst.append(str(date.date().strftime('%d-%m-%Y')))
        debit_lst.append(amount)
        mycol.update_one({"name": name, "pin": pin}, {"$set": {"debit": debit_lst}})
        mycol.update_one({"name": name, "pin": pin}, {"$set": {"debit_date": date_lst}})
        credit_lst = mycol.find_one({"name": person_name, "pin": person_pin})["credit"]
        cdate_lst = mycol.find_one({"name": person_name, "pin": person_pin})["credit_date"]
        date = datetime.datetime.now()
        cdate_lst.append(str(date.date().strftime('%d-%m-%Y')))
        credit_lst.append(amount)
        mycol.update_one({"name": person_name, "pin": person_pin}, {"$set": {"credit": credit_lst}})
        mycol.update_one({"name": person_name, "pin": person_pin}, {"$set": {"credit_date": cdate_lst}})
        total_amount = sum(mycol.find_one({"name": name, "pin": pin})["loan"]) + sum(
            mycol.find_one({"name": name, "pin": pin})["credit"]) - sum(
            mycol.find_one({"name": name, "pin": pin})["debit"])
        loan_money = mycol.find_one({"name": name, "pin": pin})["loan"]
        loan_date = mycol.find_one({"name": name, "pin": pin})["loan_date"]
        credit_money = mycol.find_one({"name": name, "pin": pin})["credit"]
        credit_date = mycol.find_one({"name": name, "pin": pin})["credit_date"]
        debit_money = mycol.find_one({"name": name, "pin": pin})["debit"]
        debit_date = mycol.find_one({"name": name, "pin": pin})["debit_date"]
        return render_template("main_file.html", send_name=name.upper(), total_money=total_amount,
                               len_loan=len(loan_money), len_credit=len(credit_money), len_debit=len(debit_money),
                               loan_money=loan_money, loan_date=loan_date, credit_money=credit_money,
                               debit_money=debit_money, credit_date=credit_date, debit_date=debit_date)


@app.route("/house_loan", methods=["POST"])
def house_loan():
    if request.method == "POST":
        amount = int(request.form.get("amount"))
        file1 = request.files["bathroom"].read()
        file_1 = np.fromstring(file1, np.uint8)
        img_1 = cv2.imdecode(file_1, cv2.IMREAD_COLOR)
        tensor_1 = tf.convert_to_tensor(img_1)
        tensor_1_reshaped = tf.image.resize(tensor_1, (256, 256))
        tensor_1_ex = tf.expand_dims(tensor_1_reshaped, axis=0)
        pred_1 = ml_model.predict(tensor_1_ex/255.0)
        output_1 = tf.nn.softmax(pred_1)
        result_1 = tf.argmax(output_1[0])
        if result_1  == 5:
            total_amount = sum(mycol.find_one({"name": name, "pin": pin})["loan"]) + sum(
                mycol.find_one({"name": name, "pin": pin})["credit"]) - sum(
                mycol.find_one({"name": name, "pin": pin})["debit"])
            loan_money = mycol.find_one({"name": name, "pin": pin})["loan"]
            loan_date = mycol.find_one({"name": name, "pin": pin})["loan_date"]
            credit_money = mycol.find_one({"name": name, "pin": pin})["credit"]
            credit_date = mycol.find_one({"name": name, "pin": pin})["credit_date"]
            debit_money = mycol.find_one({"name": name, "pin": pin})["debit"]
            debit_date = mycol.find_one({"name": name, "pin": pin})["debit_date"]
            return render_template("main_file.html", send_name=name.upper(), total_money=total_amount,
                                   len_loan=len(loan_money), len_credit=len(credit_money), len_debit=len(debit_money),
                                   loan_money=loan_money, loan_date=loan_date, credit_money=credit_money,
                                   debit_money=debit_money, credit_date=credit_date, debit_date=debit_date, loan_status="Loan Not Passed")

        else:
            loan_lst = mycol.find_one({"name": name, "pin": pin})["loan"]
            date_lst = mycol.find_one({"name": name, "pin": pin})["loan_date"]
            date = datetime.datetime.now()
            date_lst.append(str(date.date().strftime('%d-%m-%Y')))
            loan_lst.append(amount)
            mycol.update_one({"name": name, "pin": pin}, {"$set": {"loan": loan_lst}})
            mycol.update_one({"name": name, "pin": pin}, {"$set": {"loan_date": date_lst}})
            total_amount = sum(mycol.find_one({"name": name, "pin": pin})["loan"]) + sum(
                mycol.find_one({"name": name, "pin": pin})["credit"]) - sum(
                mycol.find_one({"name": name, "pin": pin})["debit"])
            loan_money = mycol.find_one({"name": name, "pin": pin})["loan"]
            loan_date = mycol.find_one({"name": name, "pin": pin})["loan_date"]
            credit_money = mycol.find_one({"name": name, "pin": pin})["credit"]
            credit_date = mycol.find_one({"name": name, "pin": pin})["credit_date"]
            debit_money = mycol.find_one({"name": name, "pin": pin})["debit"]
            debit_date = mycol.find_one({"name": name, "pin": pin})["debit_date"]
            return render_template("main_file.html", send_name=name.upper(), total_money=total_amount,
                                   len_loan=len(loan_money), len_credit=len(credit_money), len_debit=len(debit_money),
                                   loan_money=loan_money, loan_date=loan_date, credit_money=credit_money,
                                   debit_money=debit_money, credit_date=credit_date, debit_date=debit_date,
                                   loan_status="Loan Passed")



app.run(debug=True)