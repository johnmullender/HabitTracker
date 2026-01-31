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

    

