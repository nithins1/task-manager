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
from py4web.utils.url_signer import URLSigner
from yatl.helpers import A

from .common import (T, auth, authenticated, cache, db, flash, logger, session,
                     unauthenticated)
from .models import get_user_id

url_signer = URLSigner(session)

@action("index")
@action.uses("index.html", auth.user, db, url_signer)
def index():
    return dict(
        get_tasks_url = URL('get_tasks', signer = url_signer),
        get_users_url = URL('get_users', signer = url_signer),
        complete_task_url = URL('complete_task', signer = url_signer),
        edit_url = URL('edit', signer = url_signer),
        add_url = URL('add', signer = url_signer),
        addtag_url = URL('addtag', signer = url_signer),
        get_tags_url = URL('get_tags', signer = url_signer)
    )

#api for getting list of completed_task and uncompleted_task
@action("get_tasks", method="GET")
@action.uses(db, auth.user)
def get_tasks():
    user_id = get_user_id()

    user_tasks = db((db.tasks.user_id == user_id)).select(db.tasks.ALL).as_list()
    assigned_tasks = db((db.assigned.asignee == user_id) & (db.tasks.id == db.assigned.task_id)).select(db.tasks.ALL).as_list()
    
    uncompleted_tasks = [t for t in user_tasks if t['completed'] == False] + [t for t in assigned_tasks if t['completed'] == False]
    completed_tasks = [t for t in user_tasks if t['completed'] == True] + [t for t in assigned_tasks if t['completed'] == True]

    for r in uncompleted_tasks:
        r['timeleft'] =  r['deadline'] - datetime.datetime.utcnow()
        r['overdue'] = datetime.datetime.utcnow() > r['deadline']
        r['assigned'] = get_assigned_users(r['id'])
    for r in completed_tasks:
        r['assigned'] = get_assigned_users(r['id'])

    return dict(completed=completed_tasks, uncompleted=uncompleted_tasks)

@action("get_tags", method="GET")
@action.uses(db, auth.user)
def get_tags():
    user_id = get_user_id()

    user_tags = db(db.tags.user_id == user_id).select()

    return dict(tags=user_tags)

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
    assigned = request.json.get('assigned')
    tag_id = request.json.get('tag')
    if tag_id and not db.tags[tag_id]:
        print("recieved no valid tag id")
        tag_id = None

    print("deadline!!!!!", deadline_str)
    #changing string to datetime
    if deadline_str:
        deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
    else:
        deadline = datetime.datetime.now()

    new_task = db.tasks.insert(name = name,
                    description = description,
                    deadline = deadline,
                    tag = tag_id
                    )
    for user in assigned:
        db.assigned.insert(
            asignee = user,
            task_id = new_task
        )
    
    return "ok"

@action('addtag', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def addtag():
    #get all parameters
    name = request.json.get('name')
    color = request.json.get('color').lower()
    colors = ['white', 'black', 'red', 'green', 'blue', 'yellow', 'cyan']
    if color not in colors:
        color = 'white'

    db.tags.insert(name = name, color = color)
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
    tag_id = request.json.get('tag')
    if not db.tags[tag_id]:
        print("recieved no valid tag id")
        tag_id = None

    print(deadline_str)

    #changing string to datetime
    if deadline_str:
        try:
            deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
    else:
        deadline = datetime.datetime.now()

    new_task = {
        'name' : name,
        'description' : description,
        'deadline' : deadline,
        'tag': tag_id
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
    assginees = db((db.assigned.task_id == t)).select(db.assigned.asignee).as_list()
    assginee_ids = [a['asignee'] for a in assginees if 'asignee' in a]
    assginee_ids.append(t.user_id)

    # Only allow update to occur if row's email matches current user
    if get_user_id() in assginee_ids:
        status = db(db.tasks.id == t.id).select()[0]
        db(db.tasks.id == t.id).update(completed= not status.completed)
    return "ok"

@action("get_users", method="GET")
@action.uses(db, auth.user)
def get_users():
    
    users = db(db.auth_user.id != get_user_id()).select().as_list()

    return dict(users=users)

def get_assigned_users(task_id):

    assignees_ids = db((db.assigned.task_id == task_id)).select(db.assigned.asignee).as_list()
    assignees_names = [db.auth_user[a['asignee']].first_name for a in assignees_ids if 'asignee' in a]

    return assignees_names