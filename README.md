# BEFit
#### Video Demo: 
#### Description: BeFit is a Webapp which has been designed to help fitness freaks track their calories.

### Technologies used
Python
Flask - Microframework
sqlite3
flask_session

### How it works?
The idea is to register user using their name, email and password and then he can login with these details.
From the navigation bar all the pages can be accessed.
After logging in user can access their calorie details and BMI related info.
It have databases to store all user details, food_data and calorie tracking information.
Once the user is logged in, all the details are fetched from these databases.

### Routing
There are routes defined for every page.

### Sessions 
The webapp uses session to check if user is logged in or not.

### Database files
There are 3 database files in which user data and food content is stored.
food_data.db - It contains food content of approx. 550 foods
user_info.db - It contains login credentials of the user.
user_stats.db - It contains daily tracked calories and BMI related info.


### app.py
This is the python file which contains all the python code and libraries to manage proper functioning of application.