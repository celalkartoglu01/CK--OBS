from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps



#Kullanıcı Giriş Decoratoru
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if "logged_in" in session:
            return f(*args,**kwargs)
        else:
            flash("Bu Sayfayı Görüntülemek İçin Lütfen Giriş Yapın !","danger")
            return redirect(url_for("login"))
        return decorated_function


#Not Ekleme Formu
class NotesForm(Form):
    student = StringField("Öğrenci")
    lesson = StringField("Ders")
    exam1 = StringField("Vize Notu")
    exam2 = StringField("Final Notu")

#Devamsızlık Ekleme Formu
class DiscontinuityForm(Form):
    student = StringField("Öğrenci")
    lesson = StringField("Ders")
    days = StringField("Devamsız Gün Sayısı")

#Duyuru Form
class AnnouncementForm(Form):
    title = StringField("Duyuru Başlığı",validators= [validators.Length(min=5,max=100)])
    content = TextAreaField("Duyuru İçeriği",validators= [validators.Length(min=10)])


#Kullanıcı Kayıt Formu
class RegisterForm(Form):
    name = StringField("İsim",validators = [validators.Length(min=4,max=50)])
    surname = StringField("Soyisim",validators = [validators.Length(min=4,max=100)])
    number = StringField("Öğrenci Numarası",validators = [validators.Length(min=11,max=11)])
    username = StringField("Kullanıcı Adı",validators = [validators.Length(min=5,max=50)])
    password = PasswordField("Şifre Belirle",validators = [validators.DataRequired(message="Lütfen Bir Şifre Belirleyin !"),validators.EqualTo(fieldname="confirm",message="Şifreleriniz Uyuşmuyor !")])
    confirm = PasswordField("Şifreyi Doğrula")


#Giriş Formu
class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Şifre ",validators = [validators.DataRequired(message="Şifrenizi Girin !")])
    
#Yönetici Giriş Formu
class Login2Form(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Şifre",validators= [validators.DataRequired(message="Şifrenizi Girin !")])


#Akademik Kadro Formu
class StaffForm(Form):
    name = StringField("İsim",validators= [validators.Length(min=4,max=50)])
    surname = StringField("Soyisim",validators = [validators.Length(min=4,max=100)])
    section = StringField("Bölüm",validators= [validators.Length(min=4,max=50)])
    title = StringField("Ünvan",validators= [validators.Length(min=4,max=50)])



app = Flask (__name__)

#Database Bağlantısı
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "obs"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql =  MySQL(app)


#Hakkımızda Sayfasına Gönderen Fonksiyon
@app.route("/about")
def about():
    return render_template("about.html")



#Ana Sayfa Fonksiyonu
@app.route("/")
def index():
    return render_template("index.html")



#Kayıt Sayfasına Gönderen Fonksiyon
@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST":
        name = form.name.data
        surname = form.surname.data
        number = form.number.data
        username = form.username.data
        password = sha256_crypt.encrypt(form.password.data)
        cursor = mysql.connection.cursor()
        sorgu = "Insert Into students(name,surname,number,username,password) VALUES(%s,%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,surname,number,username,password))
        mysql.connection.commit()
        cursor.close()
        flash("Başarıyla Kayıt Oldunuz.","success")
        return redirect(url_for("login"))
        
    else:
        return render_template("register.html",form = form)

#Yönetici Akademik Kadro
@app.route("/staff2")
def staff2():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From staff"
    result = cursor.execute(sorgu)
    if result > 0:
        staff2 = cursor.fetchall()
        return render_template("staff2.html",staff2 = staff2)
    else:
        return render_template("staff2.html")


#Yönetici Notlar
@app.route("/updatenotes")
def updatenotes():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From notes"
    result = cursor.execute(sorgu)
    if result > 0:
        notes = cursor.fetchall()
        return render_template("updatenotes.html",notes = notes)
    else:
        return render_template("updatenotes.html")


#Not Güncelleme
@app.route("/edit/<string:id>",methods = ["GET","POST"])
def update(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        sorgu = "Select * from notes where id = %s"
        result = cursor.execute(sorgu,(id,))
        if result == 0:
            flash("Not Bilgisi Yanlış !","danger")
            return redirect(url_for("update"))
        else:
            note = cursor.fetchone()
            form = NotesForm()
            form.student.data = note["student"]
            form.lesson.data = note["lesson"]
            form.exam1.data = note["exam1"]
            form.exam2.data = note["exam2"]
            return render_template("update.html",form = form)
    else:
        form = NotesForm(request.form)
        newStudent = form.student.data
        newLesson = form.lesson.data
        newExam1 = form.exam1.data
        newExam2 = form.exam2.data
        sorgu2 = "Update notes Set student = %s,lesson = %s,exam1 = %s,exam2 = %s where id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newStudent,newLesson,newExam1,newExam2,id))
        mysql.connection.commit()
        flash("Güncelleme Başarıyla Yapıldı !","success")
        return redirect(url_for("updatenotes"))

    

#Not Ekleme Sayfası
@app.route("/addnotes",methods = ["GET","POST"])
def addnotes():
    form = NotesForm(request.form)
    if request.method == "POST":
         student = form.student.data
         lesson = form.lesson.data
         exam1 = form.exam1.data
         exam2 = form.exam2.data
         cursor = mysql.connection.cursor()
         sorgu = "Insert into notes(student,lesson,exam1,exam2) VALUES(%s,%s,%s,%s)"
         cursor.execute(sorgu,(student,lesson,exam1,exam2))
         mysql.connection.commit()
         cursor.close()
         flash("Not Başarıyla Eklendi !","success")
         return redirect(url_for("addnotes"))
    else:
        return render_template("addnotes.html",form = form)


#Akademik Kadroyu Güncelle (Sil)
@app.route("/delete/<string:id>")
def delete(id):
   cursor = mysql.connection.cursor()
   sorgu = "Delete from staff where id = %s"
   cursor.execute(sorgu,(id,))
   mysql.connection.commit()
   flash("Güncelleme Başarıyla Yapıldı !","success")
   return redirect(url_for("staff2"))


#Akademik Kadroyu Güncelle (Ekle)
@app.route("/updatestaff",methods = ["GET","POST"])
def updatestaff():
    form = StaffForm(request.form)
    if request.method == "POST":
        name = form.name.data
        surname = form.surname.data
        section = form.section.data
        title = form.title.data
        cursor = mysql.connection.cursor()
        sorgu = "Insert into staff(name,surname,section,title) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,surname,section,title))
        mysql.connection.commit()
        cursor.close()
        flash("Güncelleme Başarıyla Yapıldı !","success")
        return redirect(url_for("updatestaff"))
    else:
        return render_template("updatestaff.html",form = form)

#Devamsızlık Ekle
@app.route("/adddiscontinuity",methods = ["GET","POST"])
def adddiscontinuity():
     form = DiscontinuityForm(request.form)
     if request.method == "POST":
         student = form.student.data
         lesson = form.lesson.data
         days = form.days.data
         cursor = mysql.connection.cursor()
         sorgu = "Insert into discontinuty(student,lesson,days) VALUES(%s,%s,%s)"
         cursor.execute(sorgu,(student,lesson,days))
         mysql.connection.commit()
         cursor.close()
         flash("Devamsızlık Başarıyla Eklendi !","success")
         return redirect(url_for("adddiscontinuity"))
     else:
        return render_template("adddiscontinuity.html",form = form)

@login_required
#Not Sayfası
@app.route("/infos")
def infos():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From notes where student = %s"
    result = cursor.execute(sorgu,(session["username"],))
    if result > 0:
        note = cursor.fetchall()
        return render_template("infos.html",note = note)
    return render_template("infos.html")

#Öğrenci Devamsızlık
@app.route("/discontinuity")
def studentdiscont():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From discontinuty where student = %s"
    result = cursor.execute(sorgu,(session["username"],))
    if result > 0:
        discont = cursor.fetchall()
        return render_template("discontinutiy.html",discont = discont)
    return render_template("discontinutiy.html")

#Yönetici Devamsızlık
@app.route("/updatediscontinuty")
def updatediscontinuty():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From discontinuty"
    result = cursor.execute(sorgu)
    if result > 0:
        disconts = cursor.fetchall()
        return render_template("updatediscontinuty.html",disconts = disconts)
    else:
        return render_template("updatediscontinuty.html")



#Devamsızlık Güncelleme
@app.route("/editdiscontinuty",methods = ["GET","POST"])
def editdiscontinuty():
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        sorgu = "Select * from discontinuty"
        result = cursor.execute(sorgu)
        if result == 0:
            flash("Devamsızlık Bilgisi Yanlış !","danger")
            return redirect(url_for("updatediscontinuty"))
        else:
            discont = cursor.fetchone()
            form = DiscontinuityForm()
            form.student.data = discont["student"]
            form.lesson.data = discont["lesson"]
            form.days.data = discont["days"]
            return render_template("update2.html",form = form)
    else:
        form = DiscontinuityForm(request.form)
        newStudent = form.student.data
        newLesson = form.lesson.data
        newDays = form.days.data
        sorgu2 = "Update discontinuty Set student = %s,lesson = %s,days = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newStudent,newLesson,newDays))
        mysql.connection.commit()
        flash("Güncelleme Başarıyla Yapıldı !","success")
        return redirect(url_for("updatediscontinuty"))


#Danışman Sayfası
@app.route("/advisor")
def advisor():
    return render_template("advisor.html")

#Çıkış Fonksiyonu
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

#Akademik Takvim Sayfası
@app.route("/calendar")
def calendar():
    return render_template("calendar.html")

@login_required
#Sınav Takvimi
@app.route("/exams")
def exams():
    return render_template("exams.html")

@login_required
#Ders Programı Sayfası
@app.route("/syllabus")
def syllabus():
    return render_template("syllabus.html")


#İletişim Sayfası
@app.route("/communication")
def communication():
    return render_template("communication.html")


#Akademik Kadro
@app.route("/staff")
def staff():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From staff"
    result = cursor.execute(sorgu)
    if result > 0:
        staff = cursor.fetchall()
        return render_template("staff.html",staff = staff)
    else:
        return render_template("staff.html")


#Duyuru Detay Sayfası
@app.route("/announcement/<string:id>")
def detail(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * from announcements where id = %s"
    result = cursor.execute(sorgu,(id,))
    if result > 0:
        announcement = cursor.fetchone()
        return render_template("announcement.html",announcement = announcement)
    else:
        return render_template("announcement.html")


#Duyuru Sayfası
@app.route("/announcements")
def announcement():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From announcements"
    result = cursor.execute(sorgu)
    if result > 0:
        announcements = cursor.fetchall()

        return render_template("announcements.html",announcements = announcements)
    else:
        return render_template("/announcements.html")


#Duyuru Ekleme Sayfası
@app.route("/addannouncement",methods=["GET","POST"])
def addannouncement():
    form = AnnouncementForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        cursor = mysql.connection.cursor()
        sorgu = "Insert into announcements(title,faculty,content) VALUES(%s,%s,%s)"
        cursor.execute(sorgu,(title,session["username2"],content))
        mysql.connection.commit()
        cursor.close()
        flash("Duyuru Başarıyla Eklendi !","success")
        return redirect(url_for("index"))
    return render_template("addannouncement.html",form = form)


#Yönetici Giriş Fonksiyonu
@app.route("/login2",methods=["GET","POST"])
def login2():
    form = Login2Form(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data
        cursor = mysql.connection.cursor()
        sorgu = "Select * From executives where username = %s"
        result = cursor.execute(sorgu,(username,))
        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if password_entered == real_password:
                flash("Başarıyla Giriş Yapıldı !","success")
                session["logged_in2"] = True
                session["username2"] = username
                return redirect(url_for("index"))
            else:
                flash("Şifre Yanlış !","danger")
                return redirect(url_for("login2"))
        else:
            flash("Böyle Bir Kullanıcı Bulunmamaktadır.","danger")
            return redirect(url_for("login2"))
    else:
        return render_template("login2.html",form = form)
    


#Giriş Fonksiyonu
@app.route("/login",methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data
        cursor = mysql.connection.cursor()
        sorgu = "Select * From students where username = %s"
        result = cursor.execute(sorgu,(username,))
        if result >  0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla Giriş Yapıldı !","success")
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("index"))
            else:
                flash("Şifre Yanlış","danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle Bir Kullanıcı Bulunmamaktadır.","danger")
            return redirect(url_for("login"))
    else:
       return render_template("login.html",form = form)



if __name__ == ("__main__"):
    app.secret_key = 'super secret key'

    app.run(debug=True)
