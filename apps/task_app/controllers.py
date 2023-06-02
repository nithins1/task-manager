"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import datetime

from py4web import URL, action, redirect, request
from py4web.utils.form import Form, FormStyleBulma
from yatl.helpers import A

from .common import (T, auth, authenticated, cache, db, flash, logger, session,
                     unauthenticated)
from .models import get_user_id
from py4web.utils.url_signer import URLSigner



url_signer = URLSigner(session)

@action("index")
@action.uses("index.html", auth.user, db, url_signer)
def index():
    return dict(
        get_tasks_url = URL('get_tasks', signer = url_signer),
        complete_task_url = URL('complete_task', signer = url_signer),
        edit_url = URL('edit', signer = url_signer),
        add_url = URL('add', signer = url_signer)
    )

#api for getting list of completed_task and uncompleted_task
@action("get_tasks", method="GET")
@action.uses(db, auth.user)
def get_tasks():
    user_id = get_user_id()

    user_tasks = (db.tasks.user_id == user_id)
    uncompleted_tasks = db(user_tasks & (db.tasks.completed == False)).select().as_list()
    completed_tasks = db(user_tasks & (db.tasks.completed == True)).select().as_list()
    
    for r in uncompleted_tasks:
        r['timeleft'] =  r['deadline'] - datetime.datetime.utcnow()
        r['overdue'] = datetime.datetime.utcnow() > r['deadline']

    return dict(completed=completed_tasks, uncompleted=uncompleted_tasks)

"""
@action("add", method=['GET', 'POST'])
@action.uses("add.html", auth, db)
def add():
    if not get_user_id:
        redirect(URL('index'))
    form = Form(db.tasks, formstyle=FormStyleBulma, csrf_session=session)
    if form.accepted:
        redirect(URL('index'))

    return dict(form=form)
"""

#api for adding new task
@action('add', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def add():
    #get all parameters
    name = request.json.get('name')
    description = request.json.get('description')
    deadline_str = request.json.get('deadline')

    #changing string to datetime
    if deadline_str:
        deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
    else:
        deadline = datetime.datetime.now()

    db.tasks.insert(name = name,
                    description = description,
                    deadline = deadline)
    return "ok"

#api for edit existing task
@action('edit', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def edit():
    #get all parameters
    id = request.json.get('task_id')
    name = request.json.get('name')
    description = request.json.get('description')
    deadline_str = request.json.get('deadline')

    #changing string to datetime
    if deadline_str:
        deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
    else:
        deadline = datetime.datetime.now()

    new_task = {
        'name' : name,
        'description' : description,
        'deadline' : deadline
    }
    db(db.tasks.id == id).update(**new_task)
    return "ok"

"""
@action('edit/<id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'edit.html')
def edit(id=None):
    
    assert id is not None
    p = db.tasks[id]
    if p is None or p.user_id != get_user_id():
        redirect(URL('index'))
    form = Form(db.tasks, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)
"""

#API for change the completed bool
@action("complete_task", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def complete_task():
    id = request.json.get('task_id')
    t = db.tasks[id]
    # Only allow update to occur if row's email matches current user
    if get_user_id() == t.user_id:
        status = db(db.tasks.id == t.id).select()[0]
        db(db.tasks.id == t.id).update(completed= not status.completed)
    return "ok"