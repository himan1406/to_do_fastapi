from sqlalchemy.orm import Session as DBSession
from sqlalchemy import delete
from datetime import datetime, timezone
from models import Todo, User, Session
from schemas import TodoCreate, TodoUpdate, TodoReplace, UserCreate
from auth_utils import hash_password


# ── User operations ──────────────────────────────────────────────────────────

def get_user_by_id(db: DBSession, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: DBSession, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone(db: DBSession, phone: str):
    return db.query(User).filter(User.phone == phone).first()

def create_user(db: DBSession, user: UserCreate) -> User:
    hashed_pwd = hash_password(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_pwd
    )
    db.add(db_user)
    db.flush()
    db.refresh(db_user)
    return db_user

def update_user_password(db: DBSession, db_user: User, new_hashed_password: str) -> User:
    db_user.hashed_password = new_hashed_password
    db.flush()
    db.refresh(db_user)
    return db_user


# ── Session operations ───────────────────────────────────────────────────────

def create_session(
    db: DBSession,
    user_id: int,
    token: str,
    expires_at: datetime,
    user_agent: str | None = None,
) -> Session:
    db_session = Session(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        user_agent=user_agent,
    )
    db.add(db_session)
    db.flush()
    db.refresh(db_session)
    return db_session

def get_session_by_token(db: DBSession, token: str) -> Session | None:
    return db.query(Session).filter(Session.token == token).first()

def delete_session(db: DBSession, token: str) -> None:
    db.query(Session).filter(Session.token == token).delete()
    db.flush()

def delete_expired_sessions(db: DBSession) -> None:
    db.execute(
        delete(Session).where(Session.expires_at < datetime.now(timezone.utc))
    )
    db.flush()


# ── Todo operations ──────────────────────────────────────────────────────────

def get_todos(db: DBSession, user_id: int):
    return db.query(Todo).filter(Todo.user_id == user_id).order_by(Todo.id).all()

def get_todo_by_id(db: DBSession, todo_id: int, user_id: int):
    return db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user_id).first()

def get_todo_by_title(db: DBSession, title: str, user_id: int):
    return db.query(Todo).filter(
        Todo.title == title, Todo.user_id == user_id, Todo.completed == False
    ).first()

def get_todo_by_title_exclude(db: DBSession, title: str, todo_id: int, user_id: int):
    return db.query(Todo).filter(
        Todo.title == title, Todo.id != todo_id,
        Todo.user_id == user_id, Todo.completed == False
    ).first()

def create_todo(db: DBSession, todo: TodoCreate, user_id: int) -> Todo:
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        priority=todo.priority,
        completed=False,
        due_date=todo.due_date,
        user_id=user_id,
    )
    db.add(db_todo)
    db.flush()
    db.refresh(db_todo)
    return db_todo

def replace_todo(db: DBSession, db_todo: Todo, todo: TodoReplace) -> Todo:
    db_todo.title = todo.title
    db_todo.description = todo.description
    db_todo.priority = todo.priority
    db_todo.completed = todo.completed
    db_todo.due_date = todo.due_date
    db.flush()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: DBSession, db_todo: Todo, todo: TodoUpdate) -> Todo:
    if todo.title is not None:
        db_todo.title = todo.title
    if todo.description is not None:
        db_todo.description = todo.description
    if todo.priority is not None:
        db_todo.priority = todo.priority
    if todo.completed is not None:
        db_todo.completed = todo.completed
    if todo.due_date is not None:
        db_todo.due_date = todo.due_date
    db.flush()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: DBSession, db_todo: Todo) -> None:
    db.delete(db_todo)