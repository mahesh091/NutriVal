from flask import Flask, render_template, url_for
from flask import redirect,request, g,request
import sqlite3
from database import connect_db,get_db
from datetime import datetime


app = Flask(__name__)



@app.route("/")
def home():
  return render_template('homem.html')

@app.route("/login")
def login():
    return render_template('login.html')
@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/signup")
def register():
    return render_template('signup.html')
@app.route("/todo")
def todo():
    return render_template('todo.html')
@app.route("/letshop")
def letshop():
    return render_template('letshop.html')

''' todo '''
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
'''-----------------------------------------------------------------'''
@app.route('/add_days', methods=['POST', 'GET'])
#working with add_days(home)
def index():
    db = get_db()

    if request.method == 'POST':
        date = request.form['date'] #assuming the date is in YYYY-MM-DD format
#parse date as a string:if 2017-01-28---->2018,1,28
        dt = datetime.strptime(date, '%Y-%m-%d')
        #formatted as:20170128
        database_date = datetime.strftime(dt, '%Y%m%d')

        db.execute('insert into log_date (entry_date) values (?)', [database_date])
        db.commit()
#returns proteins,..for each day using left join we get
# everything on particular day in order by date
    cur = db.execute('''select log_date.entry_date, sum(food.protein) as protein,
                        sum(food.carbohydrates) as carbohydrates,
                        sum(food.fat) as fat, sum(food.calories) as calories
                        from log_date
                        left join food_date on food_date.log_date_id = log_date.id
                        left join food on food.id = food_date.food_id
                        group by log_date.id order by log_date.entry_date desc''')
    results = cur.fetchall()

    date_results = [] #put all values in this list

    for i in results:
        single_date = {}  #empty dict
#all values in a dictionary
        single_date['entry_date'] = i['entry_date'] #getting date
        single_date['protein'] = i['protein']  #getting proteins
        single_date['carbohydrates'] = i['carbohydrates']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']
#parsing the date to string
        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')
#formatting date to Janauary 26,2020 like that
        single_date['pretty_date'] = datetime.strftime(d, '%B %d, %Y')

        date_results.append(single_date) #takes that date value
#takes dates on homepage
    return render_template('home.html', results=date_results)

'''------------------------------------------------------------------------------------------------------------------'''
#view details day wise food items,etc
@app.route('/view/<date>', methods=['GET', 'POST'])
#date is going to be 20170520 gonna add in log_date table
def view(date):
    db = get_db()

    cur = db.execute('select id, entry_date from log_date where entry_date = ?', [date])
    date_result = cur.fetchone()
#for inserting food on that day
    if request.method == 'POST':
        db.execute('insert into food_date (food_id, log_date_id) values (?, ?)',\
             [request.form['food-select'], date_result['id']])
        db.commit()

    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')
#to display food names in the view dropdown and saves in logtable
    food_cur = db.execute('select id, name from food')

    food_results = food_cur.fetchall()

   #this returns all the foods
    log_cur = db.execute('''select food.name, food.protein, food.carbohydrates,
                            food.fat, food.calories
                            from log_date
                        join food_date on food_date.log_date_id = log_date.id
                        join food on food.id = food_date.food_id where log_date.entry_date = ?''', [date])
    log_results = log_cur.fetchall()
#inside the view dates we set values to be '0' and it adds overall when added to it.!
    totals = {}
    totals['protein'] = 0
    totals['carbohydrates'] = 0
    totals['fat'] = 0
    totals['calories'] = 0

    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']

    return render_template('day.html', entry_date=date_result['entry_date'], pretty_date=pretty_date, \
                            food_results=food_results, log_results=log_results, totals=totals)

'''--------------------------------------------------------------------------------------------------------'''

#adding new food site
@app.route('/food', methods=['GET', 'POST'])  #data from form of ADD FOOD ITEM  get and posts data in URL
def food():   #working with food database
    db = get_db()  #connecting database

    if request.method == 'POST':
        name = request.form['food-name']   #fetching name data in 'name'
        protein = int(request.form['protein'])  #similarly all
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])

        calories = protein * 4 + carbohydrates * 4 + fat * 9  #calculating overall calories of above collected data

        #inserting data into food table
        db.execute('insert into food (name, protein, carbohydrates, fat, calories) values (?, ?, ?, ?, ?)', \
            [name, protein, carbohydrates, fat, calories])
        db.commit()

    cur = db.execute('select name, protein, carbohydrates, fat, calories from food')
    results = cur.fetchall() #fetching the data from food

    return render_template('add_food.html', results=results)




if __name__ == '__main__':
    app.run(debug=True)
