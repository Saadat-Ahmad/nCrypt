import os
import random
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from main import caesar_encryption, caesar_decryption, morse_encryption, morse_decryption, binary_encryption, binary_decryption, base16_encryption, base16_decryption, base32_encryption, base32_decryption, base64_encryption, base64_decryption, base85_encryption, base85_decryption, nato_spelling_alphabet_encoder, nato_spelling_alphabet_decoder, login_required

app = Flask(__name__)
app.secret_key = '12345'

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
Session(app)

# db = SQL("sqlite:///database.db")

conn = sqlite3.connect('database.db', check_same_thread=False)
db = conn.cursor()
table = "CREATE TABLE IF NOT EXISTS 'encryption_methods' (id INTEGER PRIMARY KEY AUTOINCREMENT, encryption_name TEXT UNIQUE NOT NULL, hashed_password TEXT NOT NULL, encryption_list TEXT, 'length'  INTEGER , type TEXT, hashed_admin_key TEXT);"
db.execute(table)

def generate_padded_encryption(length, encryption_list, i):
    for j in range(int(length) - 1):
        i = i + chr(random.randint(33, 126))
    if i not in encryption_list:
        return i
    else:
        generate_padded_encryption(length, encryption_list, i)

def checkAdmin():
    key = request.form.get("adminKey")
    key = generate_password_hash(key)
    rows = db.execute("SELECT hashed_admin_key FROM encryption_methods WHERE encryption_name = ?", int(session["user_id"])).fetchall()
    keyHash = rows[0][0]
    if check_password_hash(key, keyHash):
        return True
    else:
        return False

def save_encryption(inpt):
    list_ecryption = []
    length_encrypted_char = 0
    for i in range(65, 91):
        a = request.form.get(str(chr(i)), "")
        if a not in list_ecryption and (len(a) == length_encrypted_char or length_encrypted_char == 0) :
            list_ecryption.append(a)
            length_encrypted_char = len(a)
        else:
            print(list_ecryption, "else")
            return False
    a = request.form.get("Space", "")
    if a not in list_ecryption and (len(a) == length_encrypted_char or length_encrypted_char == 0) :
        list_ecryption.append(a)
        length_encrypted_char = len(a)
    else:
        print(list_ecryption, "else")
        return False
    print(list_ecryption)

    action = request.form.get("submit")
    if action == "submit":
        id = int(session["user_id"])
        joint_list = ""
        for i in list_ecryption:
            joint_list = joint_list + i + ","
        joint_list = joint_list[: -1]
        db.execute("UPDATE encryption_methods SET encryption_list = ?, length = ?, type = ? WHERE id = ?", (joint_list, length_encrypted_char, inpt,id))
        conn.commit()
        print("database updated....\n going for redirection")
        return True

def save_language(inpt):
    list_ecryption = []
    for i in range(65, 91):
        a = request.form.get(str(chr(i)), "")
        if " " in a:
            return False
        list_ecryption.append(a)
        
    a = request.form.get("Space", "")
    if " " in a:
        return False
    list_ecryption.append(a)
    
    print(list_ecryption)

    action = request.form.get("submit")
    if action == "submit":
        id = int(session["user_id"])
        joint_list = ""
        for i in list_ecryption:
            joint_list = joint_list + i + ","
        joint_list = joint_list[: -1]
        db.execute("UPDATE encryption_methods SET encryption_list = ?, length = ?, type = ? WHERE id = ?", (joint_list, 0, inpt,id))
        conn.commit()
        print("database updated....\n going for redirection")
        return True

def languageEncryption(text, encryption_list):
    encryption_list = encryption_list.split(",")
    text =  text.upper()
    encrypted = ""
    for char in text:
        if char.isalpha():
            i = ord(char) - ord("A")
            encrypted =  encrypted + encryption_list[i] + " " 
        elif char == " ":
            encrypted = encrypted + encryption_list[26] + " " 
        else:
            encrypted = encrypted + char + " "

    return encrypted

def languageDecryption(text, encryption_list):
    listText = text.split(" ")
    encryption_list = encryption_list.split(",")
    print(listText)
    print(encryption_list)
    decrypted = ""
    for i in listText:
        if i in encryption_list:
            position =  encryption_list.index(i)
            if position == 26:
                decrypted = decrypted + " "
            else:
                x = position + ord("A")
                decrypted = decrypted + chr(x)
        else:
            decrypted = decrypted + i
    return decrypted
    
def custom_encryption(text, encryption_list, length):
    print(encryption_list)
    encryption_list = encryption_list.split(",")
    print(encryption_list)
    text = text.upper()
    encrypted = ""
    for i in text:
        if i.isalpha():
            replacement = ord(i) - ord("A")
            encrypted = encrypted + encryption_list[replacement]
        elif i == " ":
            encrypted = encrypted + encryption_list[26]
        else:
            try:
                encrypted = encrypted + generate_padded_encryption(length, encryption_list, i)
            except:
                return "Unavoidable Collision in your encryption"
    return encrypted

def custom_decryption(text, encryption_list, length):
    decrypted = ""
    encryption_list = encryption_list.split(",")
    char_encrypted = [text[i:i+length] for i in range(0, len(text), length)]
    for i in char_encrypted:
        if i in encryption_list:
            x = encryption_list.index(i)
            if x == 26:
                decrypted = decrypted + " "
            else:
                decrypted = decrypted + chr(x + ord("A"))
        else:
            decrypted = decrypted + i[:1]
    return decrypted

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/caesar', methods=["GET", "POST"])
def caesar():
    if request.method == "POST":
        text_input = request.form.get("text_input", "")
        key = request.form.get("shift", "")
        action = request.form.get("action")
        result = ""

        if action == "encrypt":
            result = "Encrypted: " + caesar_encryption(text_input, key)
        elif action == "decrypt":
            result = "Decrypted: " + caesar_decryption(text_input, key)
        return render_template("caesar.html", result=result)
    return render_template("caesar.html")

@app.route("/morse", methods=["GET", "POST"])
def morse_code():
    if request.method == "POST":
        text_input = request.form.get("text_input", "")
        action = request.form.get("action")
        result = ""
        if action == "encrypt":
            result = "Encrypted: " + morse_encryption(text_input)
        elif action == "decrypt":
            result = "Decrypted: " + morse_decryption(text_input)
        return render_template("morse.html", result=result)
    return render_template("morse.html")

@app.route('/binary', methods=["GET", "POST"])
def binary():
    if request.method == "POST":
        text_input = request.form.get("text_input", "")
        action = request.form.get("action")
        result = ""
        if action == "encrypt":
            result = "Encrypted: " + binary_encryption(text_input)
        elif action == "decrypt":
            result = "Decrypted: " + binary_decryption(text_input)
        return render_template("binary.html", result=result)
    return render_template("binary.html")

@app.route('/base16', methods=["GET", "POST"])
def base16():
    if request.method == "POST":
        text_input = request.form.get("text_input", "")
        action = request.form.get("action")
        result = ""
        if action == "encrypt":
            result = "Encrypted: " + base16_encryption(text_input)
        elif action == "decrypt":
            result = "Decrypted: " + base16_decryption(text_input)
        return render_template("base16.html", result=result)
    return render_template("base16.html")

@app.route('/base32', methods=["GET", "POST"])
def base32():
    if request.method == "POST":
        text_input = request.form.get("text_input", "")
        action = request.form.get("action")
        result = ""
        if action == "encrypt":
            result = "Encrypted: " + base32_encryption(text_input)
        elif action == "decrypt":
            result = "Decrypted: " + base32_decryption(text_input)
        return render_template("base32.html", result=result)
    return render_template("base32.html")

@app.route('/base64', methods=["GET", "POST"])
def base64():
    if request.method == "POST":
        text_input = request.form.get("text_input", "")
        action = request.form.get("action")
        result = ""
        if action == "encrypt":
            result = "Encrypted: " + base64_encryption(text_input)
        elif action == "decrypt":
            result = "Decrypted: " + base64_decryption(text_input)
        return render_template("base64.html", result=result)
    return render_template("base64.html")

@app.route('/base85', methods=["GET", "POST"])
def base85():
    if request.method == "POST":
        text_input = request.form.get("text_input", "")
        action = request.form.get("action")
        result = ""
        if action == "encrypt":
            result = "Encrypted: " + base85_encryption(text_input)
        elif action == "decrypt":
            result = "Decrypted: " + base85_decryption(text_input)
        return render_template("base85.html", result=result)
    return render_template("base85.html")

@app.route('/rot13', methods=["GET", "POST"])
def rot13():
    if request.method == "POST":
        text_input = request.form.get("text_input", "")
        action = request.form.get("action")
        result = ""
        if action == "encrypt":
            result = "Encrypted: " + caesar_encryption(text_input, 13)
        elif action == "decrypt":
            result = "Decrypted: " + caesar_decryption(text_input, 13)
        return render_template("rot13.html", result=result)
    return render_template("rot13.html")

@app.route('/natospelling', methods=["GET", "POST"])
def nato_alphabet():
    if request.method == "POST":
        text_input = request.form.get("text_input", "")
        action = request.form.get("action")
        result = ""
        if action == "encrypt":
            result = "Encrypted: " + nato_spelling_alphabet_encoder(text_input)
        elif action == "decrypt":
            result = "Decrypted: " + nato_spelling_alphabet_decoder(text_input)
        return render_template("nato.html", result=result)
    return render_template("nato.html")

@app.route("/use", methods=["GET", "POST"])
def use():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("encryption"):
            flash("Must provide the unique encryption name", "error")
            return render_template("use.html")
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password", "error")
            return render_template("use.html")

        # Query database for username
        rows = db.execute("SELECT * FROM encryption_methods WHERE encryption_name = ?", (request.form.get("encryption"), )).fetchall()
        # Ensure username exists and password is correct
        if (not rows) or (not check_password_hash(rows[0][2], request.form.get("password"))):
            flash("invalid encryption name and/or password", "error")
            return render_template("use.html")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        # Redirect user to home page
        return render_template("encrypt.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("use.html")

@app.route("/logout")
def logout():
    """Log encryption out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/create-encryption", methods=["GET", "POST"])
def create():
    """Register encryption"""
    session.clear()
    if request.method == "POST":
        encryption_name = request.form.get("encryption")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        adminKey = request.form.get("adminKey")
        adminKeyConfirmation = request.form.get("adminKeyConfirmation")
        name = db.execute("SELECT * FROM encryption_methods WHERE encryption_name = ?", (encryption_name, )).fetchone()
        if not encryption_name:
            flash("Input unique encryption name", "error")
            return render_template("create.html")
        if not password:
            flash("Input password", "error")
            return render_template("create.html")
        if len(password) < 8:
            flash("Password should have at least 8 characters", "error")
            return render_template("create.html")
        if not confirmation:
            flash("Please Confirm password", "error")
            return render_template("create.html")
        if password != confirmation:
            flash("Password was not confirmed correctly", "error")
            return render_template("create.html")
        if adminKey != adminKeyConfirmation:
            flash("Admin Key was not confirmed correctly", "error")
            return render_template("create.html")
        if len(adminKey) < 8:
            flash("Admin Key should have at least 8 characters", "error")
            return render_template("create.html")
        elif name:
            flash("encryption name already exists", "error")
            return render_template("create.html")
        else:
            hashed_password = generate_password_hash(password)
            hashed_AdminKey = generate_password_hash(adminKey)
            db.execute("INSERT INTO encryption_methods (encryption_name, hashed_password, encryption_list, length, type, hashed_admin_key) VALUES(?, ?, ?, ?, ?, ?)", (encryption_name, hashed_password, "a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z, ,", 1, "encryption", hashed_AdminKey))
            conn.commit()
            rows = db.execute(
            "SELECT id FROM encryption_methods WHERE encryption_name = ?", (encryption_name,)).fetchall()
            session["user_id"] = rows[0][0]
            return redirect("/make-custom")
    else:
        return render_template("create.html")


@app.route('/route-custom', methods=["GET", "POST"])
@login_required
def routeCustom():
    method = db.execute("SELECT type FROM encryption_methods WHERE id = ?", (session["user_id"],)).fetchone()
    print(method)
    if method[0] == "encryption":
        return redirect("/use-custom")
    if method[0] == "language":
        return redirect("/use-custom-language")



@app.route('/custom', methods=["GET", "POST"])
@login_required
def custom():
    if request.method == "POST":
        encrypted_list = db.execute("SELECT encryption_list FROM encryption_methods WHERE id = ?", (session["user_id"],)).fetchone()
        encrypted_list = encrypted_list.split(", ")
        length = db.execute("SELECT length FROM encryption_methods WHERE id = ?", (session["user_id"],)).fetchone()
        encryption_dict = {chr(i): encrypted_list[i - 65] for i in range(65, 91)}
        text_input = request.form.get("text_input", "")
        action = request.form.get("action")
        result = ""
        if action == "encrypt":
            result = "Encrypted: " + custom_encryption(text_input, encryption_dict, length)
        elif action == "decrypt":
            result = "Decrypted: " + custom_decryption(text_input, encryption_dict, length)
        return render_template("custom.html", result=result)
    return render_template("custom.html")

@app.route('/make-custom', methods=["GET", "POST"])
@login_required
def numeric():
    if request.method == "POST":
        if checkAdmin():
            if save_encryption("encryption(/make-custom)"):
                return redirect("/use-custom")
            else:    
                flash("Unique enryption for each character", "error")
                return render_template("numeric.html")
        else:
            flash("Give Admin key", "error")
            return render_template("admin.html")
    flash("Give Admin key", "error")
    return render_template("admin.html")

@app.route('/use-custom', methods=["GET", "POST"])
@login_required
def useNumeric():
    if request.method == "POST":
        text_input = request.form.get("text_input", "")
        action = request.form.get("action")
        result = ""
        list_encrypt = db.execute("SELECT encryption_list FROM encryption_methods WHERE id = ?", (session["user_id"], )).fetchall()
        list_encrypt = list_encrypt[0][0] # (split on comma ",")
        length = db.execute("SELECT length FROM encryption_methods WHERE id = ?", (session["user_id"],)).fetchall()
        length = length[0][0]
        if action == "encrypt":
            result = "Encrypted: " + custom_encryption(text_input, list_encrypt, length)
        elif action == "decrypt":
            result = "Decrypted: " + custom_decryption(text_input, list_encrypt, length)
        return render_template("encrypt.html", result=result)
    return render_template("encrypt.html")

#lang

@app.route('/choose-custom', methods=["GET", "POST"])
def choose():
    flash("You are not loged in")
    return render_template("choice.html")

@app.route('/use-custom-language', methods=["GET", "POST"])
@login_required
def useLang():
    if request.method == "POST":
        text_input = request.form.get("text_input", "")
        action = request.form.get("action")
        result = ""
        list_encrypt = db.execute("SELECT encryption_list FROM encryption_methods WHERE id = ?", (session["user_id"], )).fetchall()
        list_encrypt = list_encrypt[0][0] # (split on comma ",")
        length = db.execute("SELECT length FROM encryption_methods WHERE id = ?", (session["user_id"],)).fetchall()
        length = length[0][0]
        if action == "encrypt":
            result = "Encrypted: " + languageEncryption(text_input, list_encrypt)
        elif action == "decrypt":
            result = "Decrypted: " + languageDecryption(text_input, list_encrypt)
        return render_template("language.html", result=result)
    return render_template("language.html")

@app.route('/make-custom-language', methods=["GET", "POST"])
@login_required
def language():
    if request.method == "POST":
        if save_language("language"):
            return redirect("/use-custom-language")
        else:    
            flash("No spaces allowed in replacement word", "error")
            return render_template("langStrings.html")
    return render_template("langStrings.html")

@app.route("/create-language", methods=["GET", "POST"])
def createlang():
    """Register encryption"""
    session.clear()
    if request.method == "POST":
        encryption_name = request.form.get("encryption")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        adminKey = request.form.get("adminKey")
        adminKeyConfirmation = request.form.get("adminKeyConfirmation")
        name = db.execute("SELECT * FROM encryption_methods WHERE encryption_name = ?", (encryption_name, )).fetchone()
        if not encryption_name:
            flash("Input unique encryption name", "error")
            return render_template("createLang.html")
        if not password:
            flash("Input password", "error")
            return render_template("createLang.html")
        if len(password) < 8:
            flash("password should have at least 8 characters", "error")
            return render_template("createLang.html")
        if not confirmation:
            flash("Please Confirm password", "error")
            return render_template("createLang.html")
        if password != confirmation:
            flash("Password was not confirmed correctly", "error")
            return render_template("createLang.html")
        if adminKey != adminKeyConfirmation:
            flash("Admin Key was not confirmed correctly", "error")
            return render_template("createLang.html")
        if len(adminKey) < 8:
            flash("Admin Key should have at least 8 characters", "error")
            return render_template("createLang.html")
        elif name:
            flash("encryption name already exists", "error")
            return render_template("createLang.html")
        else:
            hashed_password = generate_password_hash(password)
            hashed_AdminKey = generate_password_hash(adminKey)
            db.execute("INSERT INTO encryption_methods (encryption_name, hashed_password, encryption_list, length, type, hashed_admin_key) VALUES(?, ?, ?, ?, ?, ?)", (encryption_name, hashed_password, "a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z, ,", 1, "encryption", hashed_AdminKey))
            conn.commit()
            rows = db.execute(
            "SELECT id FROM encryption_methods WHERE encryption_name = ?", (encryption_name,)).fetchall()
            session["user_id"] = rows[0][0]
            return redirect("/make-custom-language")
    else:
        return render_template("createLang.html")

if __name__ == "__main__":
    app.run(debug=True)