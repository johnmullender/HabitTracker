# HabitTracker: Social Accountability Platform

A full-stack web application designed to gamify habit formation through peer accountability. Unlike isolated tracking tools, this platform allows users to share their progress with friends, leveraging social motivation to drive consistency.

**Project Status:** 🚧 Active Development (January 2026)

## 🎯 Project Overview
The core philosophy of this project is that **accountability drives results**. I built this application to allow users not just to track their own data, but to expose that data to a trusted circle of friends.

As an MIS student, my goal was to architect a system that balances **transparency** (for accountability) with **privacy** (security controls), ensuring users can safely share their wins and streaks with their network.

## 🛠️ Technical Stack
* **Backend:** Python, Flask (MVC Architecture)
* **Database:** PostgreSQL, SQLAlchemy ORM
* **Testing:** Pytest (Unit & Integration Testing)
* **Frontend:** HTML5, CSS3, Jinja2 Templating
* **Tools:** IntelliJ IDEA, Git/GitHub

## 🚀 Key Features

### 🤝 Social Accountability (The Core)
* **Friend Network:** Users can connect with friends to create an accountability circle.
* **Shared Visibility:** Friends can view each other’s habit logs and streaks (read-only access), creating positive social pressure to stay consistent.
* **Privacy Controls:** While friends can view progress, strict backend security prevents unauthorized modification of peer data.

### 🛡️ Engineering & Security
* **Role-Based Access Control (RBAC):** Implemented strict ownership checks. While a friend can *Read* your logs (GET), the system strictly blocks them from *Writing* or *Deleting* your data (POST/DELETE).
* **Referential Integrity:** Configured SQLAlchemy Cascade Deletes to manage the complex web of relationships between Users, Habits, and Logs without creating orphaned data.
* **Automated Testing:** Comprehensive regression testing suite (Pytest) to ensure new social features do not break existing privacy barriers.

### 📊 Data Management
* **Habit Tracking:** Full CRUD capabilities for custom habits.
* **Activity Logging:** precise timestamping for every activity to track consistency patterns.

## 🔮 Future Roadmap
* **Leaderboards:** Gamifying the experience by ranking friends based on consistency streaks.
* **"Nudge" System:** Allowing friends to send reminders if a user hasn't logged a habit in 24 hours.
* **API Development:** Exposing endpoints to allow mobile notifications.

## 💻 How to Run Locally
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/](https://github.com/)[YOUR-USERNAME]/HabitTracker.git
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment:**
    Create a `.env` file with your database credentials.
4.  **Run the application:**
    ```bash
    flask run
    ```