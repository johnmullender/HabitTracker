from app import User, app, db, Habit
import pytest
from datetime import date

def test_follow_unfollow(client, auth):
    # Log in tester
    auth.login('tester', '12345678')

    with app.app_context():
        bill = User(username= 'bill', password= '12345678')
        db.session.add(bill)
        db.session.commit()

    # Tester follows bill
    client.post('/follow/bill')

    # Does follow relationship exist in db
    with app.app_context():
        tester = User.query.filter_by(username= 'tester').first()
        bill = User.query.filter_by(username= 'bill').first()
        assert bill in tester.followed

    # Tester unfollows bill
    client.post('/unfollow/bill')

    # Is follow relationship gone from db
    with app.app_context():
        tester = User.query.filter_by(username= 'tester').first()
        bill = User.query.filter_by(username= 'bill').first()
        assert bill not in tester.followed


@pytest.mark.parametrize(('username', 'expected_response'), [('tester', b"That username is associated with your account"),
                                                    ('fake', b"The username you are trying to follow does not exist"),
                                                    ('bill', b"You already follow this user")])
def test_invalid_follow_attempts(client, auth, username, expected_response):
    auth.login('tester', '12345678')

    with app.app_context():
        bill = User(username= 'bill', password= '12345678')
        db.session.add(bill)
        db.session.commit()

    # Tester follows bill for double follow test
    client.post('/follow/bill')

    # Tester makes invalid follow request
    response = client.post(f'follow/{username}', follow_redirects= True)
    assert expected_response in response.data


@pytest.mark.parametrize(('username', 'expected_response'), [('tester', b"That username is associated with your account"),
                                                             ('bill', b"You do not follow this user"),
                                                             ('fake', b"The user you are trying to unfollow does not exist")])
def test_invalid_unfollow_attempts(client, auth, username, expected_response):
    auth.login('tester', '12345678')

    with app.app_context():
        bill = User(username= 'bill', password= '12345678')
        db.session.add(bill)
        db.session.commit()

    response = client.post(f'/unfollow/{username}', follow_redirects= True)
    assert expected_response in response.data


@pytest.mark.parametrize(('username', 'expected_response'), [('bill', b"Follow bill to see their habits"),
                                                             ('fake', b'That user does not exist')])
def test_invalid_view_profile(client, auth, username, expected_response):
    auth.login('tester', '12345678')

    with app.app_context():
        bill = User(username= 'bill', password= '12345678')
        db.session.add(bill)
        db.session.commit()

    response = client.post(f'/profile/{username}', follow_redirects= True)
    assert expected_response in response.data


def test_valid_view_profile(client, auth):
    auth.login('tester', '12345678')

    with app.app_context():
        bill = User(username= 'bill', password= '12345678')
        db.session.add(bill)
        db.session.commit()
        bill_user = User.query.filter_by(username= 'bill').first()
        bill_id = bill_user.id
        habit = Habit(name='gym', user_id= bill_id, date_created= date.today(), streak= 4)
        db.session.add(habit)
        db.session.commit()

    client.post('follow/bill')
    response = client.post('profile/bill', follow_redirects= True)
    assert b"bill's Habits" in response.data
    assert b'gym' in response.data
    assert b'4 day streak' in response.data


@pytest.mark.parametrize(('search_name', 'expected_response'), [('bill', b'bill'),
                                                             ('BIll', b'bill'),
                                                             (' ', b'No users found'),
                                                             ('curtis', b'No users found'),
                                                             ('bi', b'bill')])
def test_search_functionality(client, auth, search_name, expected_response):
    # Log in tester
    auth.login('tester', '12345678')

    # Add bill to user database
    with app.app_context():
        bill = User(username= 'bill', password= '12345678')
        db.session.add(bill)
        db.session.commit()

    response = client.post('/search', data={'username': search_name}, follow_redirects= True)
    assert expected_response in response.data




