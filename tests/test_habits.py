from app import Habit, app, User, db
from datetime import date, timedelta


### Test basic habit creation ###
def test_add_habit(client, auth):
    # Log in dummy tester
    auth.login('tester', '12345678')

    # Create a habit
    client.post('/', data={'new_habit': 'Gym'})

    # Confirm habit is in database
    assert Habit.query.filter_by(name= 'Gym').count() == 1


### Test basic habit deletion ###
def test_delete_habit(client, auth):
    # Log in dummy tester
    auth.login('tester', '12345678')

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


### Test malicious habit deletion ###
def test_delete_other_users_habit(client):
    with app.app_context():
        # Create 2 Users and add them to database
        attacker = User(username= 'attacker', password= '12345678')
        victim = User(username= 'victim', password= '12345678')
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
    

### Test empty habit creation ###
def test_habit_empty_name(client, auth):
    # Log in dummy tester
    auth.login('tester', '12345678')

    # Attempt to create empty habit
    response = client.post('/', data={'new_habit': ' '}, follow_redirects=True)
    assert b'Habit cannot be empty' in response.data
    assert Habit.query.count() == 0


### Test habit name over 30 characters ###
def test_habit_long_name(client, auth):
    # Log in dummy tester
    auth.login('tester', '12345678')

    # Attempt to create habit with name > 30 characters
    response = client.post('/', data={'new_habit': "a" * 120}, follow_redirects= True)
    assert b'Habit cannot be more than 30 characters' in response.data
    assert Habit.query.count() == 0


### Test habit with special characters ###
def test_habit_special_char(client, auth):
    # Log in dummy tester
    auth.login('tester', '12345678')

    # Attempt to create habit with special characters
    client.post('/', data={'new_habit': 'Gym @ 7'})
    assert Habit.query.filter_by(name= 'Gym @ 7').count() == 1

    # Attempt to create habit with html input
    response = client.post('/', data={'new_habit': '<script>alert(1)</script>'}, follow_redirects= True)
    assert Habit.query.filter_by(name= '<script>alert(1)</script>').count() == 1
    # Verify safe version is still visible
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in response.get_data(as_text=True)


### Test attempt to delete a non-existent habit ###
def test_delete_ghost_habit(auth, client):
    # Log in dummy tester
    auth.login('tester', '12345678')

    # Attempt to delete habit that does not exist in db
    response = client.post('/delete/99', follow_redirects= True)
    assert b'Welcome' in response.data


### Test repeat habit marked done ###
def test_repeat_habit_completion(auth, client):
    # Log in tester
    auth.login('tester', '12345678')

    with app.app_context():
        tester = User.query.filter_by(username= 'tester').first()
        tester_id = tester.id
        # Add test habit to database
        test_habit = Habit(name= 'gym', user_id= tester_id, date_created= date.today())
        db.session.add(test_habit)
        db.session.commit()

        habit_id = test_habit.id

    # Tester logs habit
    client.post(f'/done/{habit_id}')
    with app.app_context():
        habit =  Habit.query.filter_by(name= 'gym').first()
        assert habit.streak == 1


    # Tester logs habit again (same day)
    client.post(f'/done/{habit_id}')
    with app.app_context():
        habit =  Habit.query.filter_by(name= 'gym').first()
        assert habit.streak == 1


### Test streak reset logic ###
def test_streak_reset(client, auth):
    # Log in tester
    auth.login('tester', '12345678')

    today = date.today()
    # Define number of days to subtract
    days_to_subtract = 2
    time_change = timedelta(days= days_to_subtract)

    with app.app_context():
        tester= User.query.filter_by(username= 'tester').first()
        tester_id = tester.id
        # Add test habit to database (2 days ago) with fake streak
        test_habit = Habit(name='gym', user_id= tester_id, date_created= today - time_change, streak= 3)
        db.session.add(test_habit)
        db.session.commit()
        habit_id = test_habit.id

    # Tester logs habit today
    client.post(f'/done/{habit_id}')
    with app.app_context():
        habit = Habit.query.filter_by(name= 'gym').first()
        assert habit.streak == 1


### Test streak increment logic ###
def test_streak_increment(client, auth):
    # Log in tester
    auth.login('tester', '12345678')

    today = date.today()
    # Define number of days to subtract
    days_to_subtract = 1
    time_change = timedelta(days= days_to_subtract)

    with app.app_context():
        tester = User.query.filter_by(username= 'tester').first()
        tester_id = tester.id
        # Add habit to database--> last_done set to yesterday, streak set to 1
        test_habit = Habit(name='gym', user_id= tester_id, date_created= today - time_change,
                           last_done= today - time_change, streak= 1)
        db.session.add(test_habit)
        db.session.commit()
        habit_id = test_habit.id

    # Tester logs habit today
    client.post(f'done/{habit_id}')
    with app.app_context():
        habit = Habit.query.filter_by(name= 'gym').first()
        assert habit.streak == 2


### Test first habit log increments streak ###
def test_null_habit_last_done(auth, client):
    auth.login('tester', '12345678')

    with app.app_context():
        tester = User.query.filter_by(username= 'tester').first()
        tester_id = tester.id
        test_habit = Habit(name= 'gym', date_created= date.today(), user_id= tester_id)
        db.session.add(test_habit)
        db.session.commit()
        test_habit_id = test_habit.id

        # confirm habit last_done is currently Null and streak is 0
        assert test_habit.last_done is None
        assert test_habit.streak == 0

    # User logs habit
    client.post(f'/done/{test_habit_id}')
    with app.app_context():
        habit = Habit.query.filter_by(name= 'gym').first()
        assert habit.streak == 1




