import datetime

from py4web import URL, action, redirect, request
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
from yatl.helpers import A

from .common import (T, auth, authenticated, cache, db, flash, logger, session,
                     unauthenticated)
from .models import get_user_id, get_user_firstname

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
        r['timeleft'] =  r['deadline'].isoformat()
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
    assigned = request.json.get('assigned')
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
    print(assigned)
    # [[current], [past]]
    add = list(set(assigned[0]) - (set(assigned[0]) & set(assigned[1])))
    remove = list(set(assigned[1]) - (set(assigned[0]) & set(assigned[1])))
    
    for user in add:
        db.assigned.insert(
            asignee = user,
            task_id = id
        )
    for user in remove:
        db((db.assigned.task_id == id) & (db.assigned.asignee == user)).delete()

    return "ok"

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
    #assignees_names = [db.auth_user[a['asignee']].first_name for a in assignees_ids if 'asignee' in a]
    assignees_names = []

    for user in assignees_ids:
        if 'asignee' in user:
            if db.auth_user[user['asignee']].first_name == get_user_firstname():
                assignees_names.append("You")
            else:
                assignees_names.append(db.auth_user[user['asignee']].first_name)

    return assignees_names