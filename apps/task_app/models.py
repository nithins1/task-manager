"""
This file defines the database models
"""

from pydal.validators import *

from .common import Field, auth, db

def get_user_id():
    # Retrieve the ID of the current user if available
    return auth.current_user.get('id') if auth.current_user else None
def get_user_firstname():
    # Retrieve the first name of the current user if available
    return auth.current_user.get('first_name') if auth.current_user else None

# Define the 'tags' table
db.define_table(
    "tags",
    Field("name", requires=IS_NOT_EMPTY()),
    Field("user_id", "reference auth_user", default=get_user_id, writable=False,readable=False),
    Field("color"),
)

# Define the 'tasks' table
db.define_table(
    "tasks",
    Field("name", requires=IS_NOT_EMPTY()),
    Field("description", "text", requires=IS_NOT_EMPTY()),
    Field("user_id", "reference auth_user", default=get_user_id, writable=False,readable=False),
    Field("deadline", "datetime"),
    Field("completed", "boolean", default=False, writable=False,readable=False),
    Field("tag", "reference tags"),
)

# Define the 'assigned' table
db.define_table(
    "assigned",
    Field("asignee", "reference auth_user"),
    Field("task_id", "reference tasks")
)

db.commit()