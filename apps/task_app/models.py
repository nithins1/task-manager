"""
This file defines the database models
"""

from pydal.validators import *

from .common import Field, auth, db

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

def get_user_id():
    return auth.current_user.get('id') if auth.current_user else None

db.define_table(
    "tags",
    Field("name", requires=IS_NOT_EMPTY()),
    Field("user_id", "reference auth_user", default=get_user_id, writable=False,readable=False),
    Field("color")
)

db.define_table(
    "tasks",
    Field("name", requires=IS_NOT_EMPTY()),
    Field("description", "text", requires=IS_NOT_EMPTY()),
    Field("user_id", "reference auth_user", default=get_user_id, writable=False,readable=False),
    Field("deadline", "datetime"),
    Field("completed", "boolean", default=False, writable=False,readable=False)
    Field("tag", "reference tags")
)