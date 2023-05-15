"""
This file defines the database models
"""

from .common import db, Field, auth
from pydal.validators import *

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
    "tasks",
    Field("name", requires=IS_NOT_EMPTY()),
    Field("description", "text", requires=IS_NOT_EMPTY()),
    Field("user_id", "reference auth_user", default=get_user_id, writable=False,readable=False),
    Field("deadline", "datetime"),
    Field("completed", "boolean", default=False, writable=False,readable=False)
)