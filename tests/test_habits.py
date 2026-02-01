from app import Habit, app, User, db
from datetime import date, timedelta


### Test basic habit creation ###
def test_add_habit(client, auth):
    # Log in dummy tester
    auth.login('tester', '12345678')

    # Create a habit
    client.post('/', data={'new_habit': 'Gym'})

 