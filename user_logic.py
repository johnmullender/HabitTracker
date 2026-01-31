import datetime as d
import json

class User:
    def __init__(self, name):
        self.name = name
        self.habits = []
        self.friends = []
        self.read_from_file("{0}.json".format(name))

    def add_habit(self, habit):
        new_habit = {"name" : habit, "logs": []}
        self.habits.append(new_habit)
        self.save_to_file("{0}.json".format(self.name))

    def log_entry(self, habit_name, status, note = ""):
        for habit in self.habits:
            if habit["name"] == habit_name:
                log = {"date" : str(d.date.today()), "status" : status, "note" : note}
                habit["logs"].append(log)
                self.save_to_file("{0}.json".format(self.name))

    def add_friend(self, friend_user):
        self.friends.append(friend_user)

    def show_progress(self):
        for habit in self.habits:
            if len(habit["logs"]) > 0:
                last_log = habit["logs"][-1]
                status = last_log["status"]
                print("{0} -- {1}: {2}".format(self.name, habit["name"], status))
            else:
                print("No logs for {0} yet".format(habit["name"]))

    def save_to_file(self, file):
        with open(file, "w") as thefile:
            json.dump(self.habits, thefile)

    def read_from_file(self, file):
        try:
            with open(file, "r") as thefile:
                data = json.load(thefile)
                self.habits = data
        except:
            print("New user created")