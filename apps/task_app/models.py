"""
This file defines the database models.

The models.py file contains the definitions of the database tables and their fields using the PyDAL library. It also includes helper functions to retrieve user information.

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

"""
The models.py file defines three database tables: 'tags', 'tasks', and 'assigned'. Each table is defined using the `db.define_table()` function provided by the PyDAL library.

The 'tags' table contains fields for 'name', 'user_id', and 'color'. The 'user_id' field is a reference to the 'auth_user' table, and its default value is set to the ID of the current user (retrieved using the `get_user_id()` function). The 'color' field is not specified with any validation requirements.

The 'tasks' table contains fields for 'name', 'description', 'user_id', 'deadline', 'completed', and 'tag'. The 'user_id' field is a reference to the 'auth_user' table, and its default value is set to the ID of the current user. The 'deadline' field is of type 'datetime', and the 'completed' field is a boolean with a default value of False. The 'tag' field is a reference to the 'tags' table.

The 'assigned' table contains fields for 'asignee' and 'task_id', both of which are references to other tables.

The helper functions 'get_user_id()' and 'get_user_firstname()' are defined to retrieve the ID and first name of the current user, respectively. These functions rely on the 'auth' object provided by the 'common' module.

Finally, the 'db.commit()' statement is used to ensure that the defined tables are committed to the database.

"""