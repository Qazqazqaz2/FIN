from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, g, jsonify
from flask_login import current_user, LoginManager
import base64
from flask_login import login_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate
import psycopg2
import psycopg2.extensions
from geopy.geocoders import Nominatim
from random import randint
import datetime, time
from flask_redis import FlaskRedis


con = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="XXX")

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


DB_URL = 'postgresql://postgres:XXX@localhost:6432/postgres'
UPLOAD_FOLDER = r'/home/armianin/FIfe/Fin/static'
ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['GOOGLEMAPS_KEY'] = "8JZ7i18MjFuM35dJHq70n3Hx4"
app.config['RECAPTCHA_USE_SSL']= False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeBCfIZAAAAAO39_L4Gd7f6uCM0PfP_N3XjHxkW'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeBCfIZAAAAAJTjq0Xz_ndAW9LByCo1nJJKy-up'
app.config['RECAPTCHA_OPTIONS'] = {'theme':'black'}
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
db_cursor = con.cursor()

class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    isactive = db.Column(db.Boolean, default=True)
    title = db.Column(db.String(100), nullable=False)
    img = db.Column(db.ARRAY(db.TEXT), nullable=False)
    text = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    creator_id = db.Column(db.Integer, nullable=False)
    prew_img = db.Column(db.Text, nullable=False)
    lat = db.Column(db.Text, nullable=False)
    log = db.Column(db.Text, nullable=False)
    ad = db.Column(db.Text, nullable=False)
    def __init__(self, title, price, img, text, prew_img, ad, lat, log, creator_id):
        self.img = img
        self.text = text
        self.title = title
        self.price = price
        self.creator_id = creator_id
        self.prew_img = prew_img
        self.log = log
        self.lat = lat
        self.ad = ad
    def __abs__(self):
        return self.title, self.id, self.text, self.video, self.phone

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100), unique=True)
    main_num = db.Column(db.String(11), unique=True)
    prew_img = db.Column(db.Text, nullable=False)

    def __init__(self, email, name, main_num, password, prew_img):
        self.email = email
        self.main_num = main_num
        self.name = name
        self.prew_img = prew_img
        self.password = password

class Comment(db.Model):
    __tablename__ = 'comment'
    name = db.Column(db.Text, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    mess = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __init__(self, post_id, name, pub_date, mess):
        self.post_id = post_id
        self.name = name
        self.pub_date = pub_date
        self.mess = mess

class Chat(db.Model):
    __tablename__ = 'chat'
    name = db.Column(db.ARRAY(db.TEXT))
    id = db.Column(db.Integer, primary_key=True)
    mess = db.Column(db.ARRAY(db.TEXT))
    us_1 = db.Column(db.Text)
    us_2 = db.Column(db.Text)
    pub_date = db.Column(db.ARRAY(db.DateTime), default=datetime.datetime.utcnow())

    def __init__(self, name, pub_date, mess, us_1, us_2):
        self.name = name
        self.us_1 = us_1
        self.us_2 = us_2
        self.pub_date = pub_date
        self.mess = mess

@app.route('/')
def index():
    s = ""
    s += "SELECT id, img, title, ad, prew_img, creator_id FROM item"

    db_cursor.execute(s)

    array_users = db_cursor.fetchall()

    print(array_users)


    return render_template('index.html', array_us=array_users, method='utf-8')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    captcha_response = request.form['g-recaptcha-response']
    print(captcha_response)
    if str(captcha_response)=='':
        print('xxx')
        return redirect('/login')
    user = User.query.filter_by(email=email).first()

    if not user and not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('.login'))

    login_user(user, remember=remember)
    time.sleep(3)
    return redirect(url_for('index'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    main_num = request.form.get('main_num')
    prew_img = request.files['prew_img']
    captcha_response = request.form['g-recaptcha-response']
    print(captcha_response)
    if str(captcha_response)=='':
        print('xxx')
        return redirect('/signup')
    print(prew_img.filename, 111)
    if prew_img.filename == '':
        prew_img.filename = 'Без_названия.png'
    else:
        prew_img.save(os.path.join(app.config['UPLOAD_FOLDER'], prew_img.filename))
    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email address already exists.')



        return redirect(url_for('signup'))

    new_user = User(main_num=main_num, email=email, name=name, password=generate_password_hash(password, method='sha256'), prew_img=prew_img.filename)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/view/<int:id>/post/', methods=['POST', 'GET'])
@login_required
def post(id):
    if request.method == "POST":
        itemss = Item.query.get(id)
        captcha_response = request.form['g-recaptcha-response']
        print(captcha_response)
        if str(captcha_response)=='':
            print('xxx')
            return redirect('/view/' + str(id) + '/post/')
        name = current_user.name
        mess = request.form.get('mess')
        post_id = itemss.id
        pub_date = datetime.datetime.utcnow()
        item = Comment(post_id=post_id, pub_date=pub_date, mess=mess, name=name)
        print(item)
        db.session.add(item)
        print(item)
        db.session.commit()
        return redirect('./')
    else:
        itemss = db.session.query(Comment).all()
        for a in itemss:
            if a.post_id == id:
                print(a.name)
                print(a.post_id)
        print(itemss)
        return render_template('reviews.html', itttt=itemss, id=id)

@app.route('/view/<int:id>', methods=['POST', 'GET'])
def view(id):
   # if 'visits' in session:
    #    session['visits'] = session.get('visits') + 1  # чтение и обновление данных сессии
    #else:
     #   session['visits'] = 1  # настройка данных сессии
    #item = session.get('visits')
    its = Item.query.get(id)
    return render_template('view.html', dt=its)

@app.route("/",methods=["POST"])
def result():
    searchbox = request.form.get("search")
    print(searchbox)
    List1 = []
    results = db.session.query(Item).all()
    for i in results:
        if (searchbox in i.title) is True:
            List1.append([i.title, i.creator_id, i.id, i.prew_img])
    return render_template('result.html', count=len(List1), result=List1)

@app.route('/profile/',  methods=['POST', 'GET'])
@login_required
def profile():
    list_item = db.session.query(Item).filter_by(creator_id=current_user.id).all()
    print(list_item)
    return render_template('prof_ed.html', ma=current_user, main=list_item, mat=len(list_item))

@app.route('/edit/',  methods=['POST'])
@login_required
def edit():
    print('111')
    id = User.query.filter_by(id=current_user.id).first()
    print(request.form.get('delite'))
    if request.form.get('delite') == 'True':
        print('1111')
        db.session.delete(id)
        db.session.commit()
    else:
        name_ed = request.form['name_ed']
        main_num_ed = request.form['main_num_ed']
        email_ed = request.form['email_ed']
        prew_img = request.files['prew_img']

        print(name_ed, email_ed, main_num_ed, prew_img.filename)
        #  prof_img = request.files['prof_img']
        if email_ed == '':
            print('mail none')
        elif email_ed==current_user.email:
            print('its')
        else:
            mail = User.query.filter_by(email=email_ed).first()
            if mail:
                flash('Email address already exists.')
                return redirect(url_for('edit_vi'))
            else:
                current_user.email = email_ed
        if name_ed == '':
            print('name_none')
        elif name_ed==current_user.name:
            print('its')
        else:
            name = User.query.filter_by(name=name_ed).first()
            if name:
                flash('Name already exists.')
                return redirect(url_for('edit_vi'))
            else:
                current_user.name = name_ed
        if main_num_ed == '':
            print('num none')
        elif main_num_ed==current_user.main_num:
            print('its')
        else:
            num = User.query.filter_by(main_num=main_num_ed).first()
            if num:
                flash('Mobile number already exists.')
                return redirect(url_for('profile'))
            else:
                current_user.main_num = main_num_ed

        db.session.commit()

        return redirect(url_for('index'))

@app.route('/edit/',  methods=['GET'])
@login_required
def edit_vi():
    if current_user.is_authenticated:
        return render_template('edit.html', main=current_user)
    else:
        return redirect('/')

@app.route('/chat/<int:id>/', methods=['POST', 'GET'])
@login_required
def chat(id):
    ch = Chat.query.get(id)
    T_ch = ch.us_1==current_user.name
    print(T_ch)
    if T_ch==False:
        T_ch = ch.us_2==current_user.name
        print(T_ch)
    if T_ch == False:
        return redirect('/list/mess/')
    print(ch.us_1)
    if request.method == "POST" and current_user.is_authenticated:
        print('1')
        get_mess = [request.form['mess']]
        ch = db.session.query(Chat).filter(Chat.id==id).first()
        ch.mess = ch.mess + get_mess
        ch.name = ch.name + [current_user.name]
        ch.pub_date = ch.pub_date + [datetime.datetime.utcnow()]
        print(ch.pub_date, ch.name, ch.mess)
        db.session.commit()
        return redirect('./')
    else:
        if ch==None:
            print('111')
            col=0
        else:
            col = len(ch.mess)
            print(col)
        print(ch.mess)
        return render_template('chat.html', ch_h=ch, col=col)

@app.route('/profile/<int:id>/', methods=['POST', 'GET'])
def profile_vi(id):
    pr = User.query.get(id)
    if current_user.is_authenticated and id==current_user.id:
        return redirect(url_for('profile'))
    if request.method == "POST" and current_user.is_authenticated:
        us_1 = current_user.name
        us_2 = pr.name
        check_1 = db.session.query(Chat).filter((Chat.us_2==us_1) and (Chat.us_1==us_2)).first()
        check_2 = db.session.query(Chat).filter((Chat.us_2==us_2) and (Chat.us_1==us_1)).first()
        check = str(str(check_2) + str(check_1))
        print(check)
        if check=='NoneNone':
            print('None')
            us_2 = pr.name
            mess = ['Привет']
            print(mess)
            com_cr = Chat(us_1=current_user.name, us_2=us_2, mess=mess, pub_date=[datetime.datetime.utcnow()], name=[current_user.name])
            print('te')
            db.session.add(com_cr)
            print('1')
            db.session.commit()
            return redirect(url_for('list'))
        else:
            if check_1 == None:
                print('none')
            else:
                check = check_1.id

            if check_2 == None:
                print('none')
            else:
                check = check_2.id

            print(check)
            return redirect('/chat/' + str(check) + '/')
    elif not current_user.is_authenticated:
        return redirect('/login')
    else:
        list_item = db.session.query(Item).filter_by(creator_id=id).all()
        return render_template('prof_vi.html', ma=pr, main=list_item, mat=len(list_item))

@app.route('/list/mess/')
@login_required
def list():
    list = Chat.query.order_by(Chat.us_1==current_user.name or Chat.us_2==current_user.name).all()
    for l in list:
        print(l)
    return render_template('list_mess.html', list=list)

@login_manager.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # next, try to login using Basic
    api_key = request.headers.get('orization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

@app.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    if request.method == "POST" and current_user.is_authenticated:
        title = request.form['title']
        price = request.form['price']
        adr_ul = request.form['ad_ul']
        adr_ci = request.form['ad_ci']
        adr_k = request.form['ad_k']
        adr_hou = request.form['adr_hou']
        index = request.form['index']
        captcha_response = request.form['g-recaptcha-response']
        print(captcha_response)
        if str(captcha_response)=='':
            print('xxx')
            return redirect('/create')
        img = request.files.getlist('img')
        text = request.form['text']
        prew_img = request.files['prew_img']
        print(str(index) + '1')
        if str(index) + '1' != '1':
            print('aaa')
            geolocator = Nominatim(user_agent=str(randint(0, 300)))
            location = geolocator.geocode(str(index))
            print((location.latitude, location.longitude))
            lat = location.latitude
            log = location.longitude
            ad = location.address

        else:
            print('a')
            a=adr_ci
            b=adr_ul
            k=adr_k
            c=adr_hou
            geolocator = Nominatim(user_agent=str(adr_ci + adr_ul + adr_hou).encode('utf-8'))
            location = geolocator.geocode(k +' '+ a+' '+b+' '+c)
            print((location.latitude, location.longitude))
            lat = location.latitude
            log = location.longitude
            ad = location.address
            if str(index) == '' and str(index) == None and str(adr_ul) == '' and str(adr_ul) == None:
                flash('Введите индекс или адрес')
        if ad:
            flash('Проверьте адрес: {{ ad }}')
        fname = []
        print(img)
        for im in img:
            imm = im.filename
            im.save(os.path.join(app.config['UPLOAD_FOLDER'], imm))
            fname.append(imm)
        print(fname)
        prew_img.save(os.path.join(app.config['UPLOAD_FOLDER'], prew_img.filename))
        item = Item(title=str(title), price=price, img=fname, text=text, prew_img=prew_img.filename, ad=str(ad), lat=str(lat), log=str(log), creator_id=current_user.id)
        print(fname)
        db.session.add(item)
        print(item)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('create.html')

app.secret_key = 'some_secret_key'
if __name__ == "__main__":
    app.run(debug=True)
