import datetime

from py4web import URL, action, redirect, request
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
from yatl.helpers import A

from .common import (T, auth, authenticated, cache, db, flash, logger, session,
                     unauthenticated)
from .models import get_user_id, get_user_firstname

url_signer = URLSigner(session)

# API for rendering the index page
@action("index")
@action.uses("index.html", auth.user, db, url_signer)
def index():
    # Define URLs for various actions
    return dict(
        get_tasks_url = URL('get_tasks', signer = url_signer),
        get_users_url = URL('get_users', signer = url_signer),
        complete_task_url = URL('complete_task', signer = url_signer),
        edit_url = URL('edit', signer = url_signer),
        add_url = URL('add', signer = url_signer),
        addtag_url = URL('addtag', signer = url_signer),
        get_tags_url = URL('get_tags', signer = url_signer)
    )

# API for getting a list of completed_task and uncompleted_task
@action("get_tasks", method="GET")
@action.uses(db, auth.user)
def get_tasks():
    # Retrieve the user ID of the current user
    user_id = get_user_id()
    user_tasks = db((db.tasks.user_id == user_id)).select(db.tasks.ALL).as_list()
    
    # Retrieve tasks assigned to the user
    assigned_tasks = db((db.assigned.asignee == user_id) & (db.tasks.id == db.assigned.task_id)).select(db.tasks.ALL).as_list()
    # Separate tasks into completed and uncompleted lists
    uncompleted_tasks = [t for t in user_tasks if t['completed'] == False] + [t for t in assigned_tasks if t['completed'] == False]
    completed_tasks = [t for t in user_tasks if t['completed'] == True] + [t for t in assigned_tasks if t['completed'] == True]

    # Add additional information to each task
    for r in uncompleted_tasks:
        r['timeleft'] =  r['deadline'].isoformat()
        r['overdue'] = datetime.datetime.utcnow() > r['deadline'] + datetime.timedelta(hours = 7)
        r['assigned'] = get_assigned_users(r['id'])
    for r in completed_tasks:
        r['assigned'] = get_assigned_users(r['id'])

    return dict(completed=completed_tasks, uncompleted=uncompleted_tasks)

# API for getting a list of tags
@action("get_tags", method="GET")
@action.uses(db, auth.user)
def get_tags():
    """
    API for retrieving a list of tags.

    Returns:
        dict: A dictionary containing the tags.
    """
    user_id = get_user_id()

    # Retrieve tags associated with the user
    user_tags = db(db.tags.user_id == user_id).select()

    return dict(tags=user_tags)

# API for adding a new task
@action('add', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def add():
    # Get all parameters from the request
    name = request.json.get('name')
    description = request.json.get('description')
    deadline_str = request.json.get('deadline')
    assigned = request.json.get('assigned')
    tag_id = request.json.get('tag')
    
    # Check if the provided tag ID is valid
    if tag_id and not db.tags[tag_id]:
        print("recieved no valid tag id")
        tag_id = None

    print("deadline!!!!!", deadline_str)
    
    # Convert deadline string to datetime

    if deadline_str:
        deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
    else:
        deadline = datetime.datetime.now()

    # Insert the new task into the database
    new_task = db.tasks.insert(name = name,
                    description = description,
                    deadline = deadline,
                    tag = tag_id
                    )
    # Assign the task to the specified users
    for user in assigned:
        db.assigned.insert(
            asignee = user,
            task_id = new_task
        )
    
    return "ok"

# API for adding a new tag
@action('addtag', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def addtag():
    # Get all parameters from the request
    name = request.json.get('name')
    color = request.json.get('color').lower()
    colors = ['white', 'black', 'red', 'green', 'blue', 'yellow', 'cyan']

    # Validate the color parameter
    if color not in colors:
        color = 'white'

    # Insert the new tag into the database
    db.tags.insert(name = name, color = color)
    return "ok"

# API for editing an existing task
@action('edit', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def edit():
    # Get all parameters from the request
    id = request.json.get('task_id')
    name = request.json.get('name')
    description = request.json.get('description')
    deadline_str = request.json.get('deadline')
    assigned = request.json.get('assigned')
    tag_id = request.json.get('tag')

    # Check if the provided tag ID is valid
    if not db.tags[tag_id]:
        print("recieved no valid tag id")
        tag_id = None

    print(deadline_str)

    # Convert deadline string to datetime
    if deadline_str:
        try:
            deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
    else:
        deadline = datetime.datetime.now()

    # Create a new task dictionary with updated values
    new_task = {
        'name' : name,
        'description' : description,
        'deadline' : deadline,
        'tag': tag_id
    }

    # Update the task in the database
    db(db.tasks.id == id).update(**new_task)
    print(assigned)
    # Identify users to add and remove from the task assignment
    # based on the provided assigned list
    # [[current], [past]]
    add = list(set(assigned[0]) - (set(assigned[0]) & set(assigned[1])))
    remove = list(set(assigned[1]) - (set(assigned[0]) & set(assigned[1])))

    # Add new assignees to the task
    for user in add:
        db.assigned.insert(
            asignee = user,
            task_id = id
        )
    # Remove assignees from the task
    for user in remove:
        db((db.assigned.task_id == id) & (db.assigned.asignee == user)).delete()

    return "ok"

# API for changing the 'completed' boolean of a task
@action("complete_task", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def complete_task():
    """
    API for changing the completed status of a task.

    Returns:
        str: A string indicating the status of the operation.
    """
    id = request.json.get('task_id')
    t = db.tasks[id]

    # Retrieve assignees of the task
    assginees = db((db.assigned.task_id == t)).select(db.assigned.asignee).as_list()
    assginee_ids = [a['asignee'] for a in assginees if 'asignee' in a]
    assginee_ids.append(t.user_id)

    # Only allow the update to occur if the current user is assigned to the task
    if get_user_id() in assginee_ids:
        # Toggle the 'completed' status of the task
        status = db(db.tasks.id == t.id).select()[0]
        db(db.tasks.id == t.id).update(completed= not status.completed)
    return "ok"

# API for getting a list of users
@action("get_users", method="GET")
@action.uses(db, auth.user)
def get_users():
    # Retrieve all users except the current user
    users = db(db.auth_user.id != get_user_id()).select().as_list()
    return dict(users=users)

def get_assigned_users(task_id):
    # Retrieve assignees of a task
    assignees_ids = db((db.assigned.task_id == task_id)).select(db.assigned.asignee).as_list()
    #assignees_names = [db.auth_user[a['asignee']].first_name for a in assignees_ids if 'asignee' in a]
    assignees_names = []

    # Retrieve the names of the assignees
    for user in assignees_ids:
        if 'asignee' in user:
            # Retrieve the first name of the assignee from the auth_user table
            if db.auth_user[user['asignee']].first_name == get_user_firstname():
                # If the assignee is the current user, add "You" to the list
                assignees_names.append("You")
            else:
                # Add the first name of the assignee to the list
                assignees_names.append(db.auth_user[user['asignee']].first_name)

    return assignees_names