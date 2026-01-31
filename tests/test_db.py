from app import db, User, Habit
from datetime import date

def test_habit_creation(client):
    print(db.engine.url)
    user = User(username='Tim', password= 'password')
    db.session.add(user)
    db.session.commit()
    habit = Habit(name= 'gym', user_id= user.id, date_created= date.today())
    db.session.add(habit)
    db.session.commit()
    assert Habit.query.count() == 1

