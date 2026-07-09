from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .website import Website  # noqa: E402, F401
from .course import Course  # noqa: E402, F401
from .task import Task  # noqa: E402, F401
from .user_account import UserAccount  # noqa: E402, F401
