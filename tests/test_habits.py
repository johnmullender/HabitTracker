from app import Habit, app, User, db
from datetime import date

def test_add_habit(client, auth):
    # Log in dummy tester
    auth.login('tester', '123')

    # Create a habit
    client.post('/', data={'new_habit': 'Gym'})

    # Confirm habit is in database
    assert Habit.query.filter_by(name= 'Gym').count() == 1


def test_delete_habit(client, auth):
    # Log in dummy tester
    auth.login('tester', '123')

    # Create a habit
    client.post('/', data={'new_habit': 'Gym'})
    # Confirm habit is in database
    assert Habit.query.filter_by(name= 'Gym').count() == 1

    # Fetch test habit
    habit = Habit.query.first()

    # Delete test habit
    client.post(f'/delete/{habit.id}')
    # Confirm habit is removed from database
    assert Habit.query.count() == 0


def test_delete_other_users_habit(client):
    with app.app_context():
        # Create 2 Users and add them to database
        attacker = User(username= 'attacker', password= '123')
        victim = User(username= 'victim', password= '123')
        db.session.add(attacker)
        db.session.add(victim)
        db.session.commit()

        # Create a habit owned by victim
        test_habit = Habit(name='test', user_id= victim.id, date_created= date.today())
        db.session.add(test_habit)
        db.session.commit()

        victim_habit_id = test_habit.id
        attacker_username = attacker.username

    # Attacker attempts to delete victims habit
    client.post('/login', data={'username': attacker_username, 'password': '123'})
    client.post(f'/delete/{victim_habit_id}')

    with app.app_context():
        # Make sure victims habit still exists
        assert Habit.query.filter_by(id= victim_habit_id).first() is not None
    

