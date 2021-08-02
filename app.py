from flask import Flask ,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['WHOOSE_BASE']='whoosh'
db=SQLAlchemy(app)
auth = HTTPBasicAuth()

users = {
    "john": generate_password_hash("hello"),
    "susan": generate_password_hash("bye")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username



class Todo(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100))
    complete=db.Column(db.Boolean)

@app.route('/')
@auth.login_required
def index():
    # show all todos
    todo_list=Todo.query.all()
    print(todo_list)
    q = request.args.get('q') 
    if q:
        todo_list=Todo.query.filter(Todo.id.contains(q) | Todo.title.contains(q))
    else:
        todo_list=Todo.query.all()
    return render_template('base.html',todo_list=todo_list)
    return "Hello, {}!".format(auth.username())


@app.route("/add",methods=['POST'])
def add():
    # add new item 
    title=request.form.get("title")
    new_todo=Todo(title=title,complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo=Todo.query.filter_by(id=todo_id).first()
    todo.complete=not todo.complete
    try:
        db.session.commit()
        return redirect(url_for("index"))
    except:
        return "there was a problem updating your task..."

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo=Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    try:
        db.session.commit()
        return redirect(url_for("index"))
    except:
        return "there was a problem deleting your task..."


if __name__=="__main__":
    db.init_app(app)
    db.create_all()
    new_todo=Todo(title="todo 1",complete=False)
    db.session.add(new_todo)
    db.session.commit()
    app.run(debug=True)

