# Blog web application

## Description
This is a blog web application. It is built using Flask, a Python web framework and utilises SQLite/Postgres for database management and Flask-Auth for authentication.

## Stack
- Python (Flask Framework)
- SQL database (SQLAlchemy)
- Bootstrap 5 (CSS Framework)
- Javascript (Basic/Raw)

## Features
- User authentication and registration, Utilisation of Bcrypt
- Create, Read, Update and delete blog posts (CRUD)
- Comment system with timestamps for interaction
- Responsive web design using Bootstrap 5 CSS
- Flash messaging for a positive user experience.
- Object Oriented Programming used to create Database models and user input forms.

## Live Screen Shots

1. **User Registration and Login**: Users can register as new users or log in. This process is secured using Bcrypt for hashing passwords, ensuring enhanced security. <br>

    <img src="images/regSC.png" alt="User Registration and Login Screenshot" width="700" height="600">

2. **Access to Content Feed**: Authorised users access the applications ability to create, update, and delete their own blog posts. Non-authorised users may also read blog posts by others, fostering a community of shared information. <br>

    <img src="images/postSC.png" alt="Content Feed Screenshot" width="700" height="600"> <br>

3. **Creating a Blog Post**: Users can create blog posts using a form which supports advanced formatting options with CKEditor, allowing for rich text editing and versatile content creation. <br>

    <img src="images/createpost.png" alt="Creating a Blog Post Screenshot" width="700" height="600"> <br>

4. **Interactive Comments**: Users, including the original author of a blog post, can comment on posts, adding a layer of interaction. Comments include detailed timestamps, providing context and sequence to discussions. <br>

    <img src="images/commentsSC.png" alt="Interactive Comments Screenshot" width="700" height="600"> <br>



## Installation
To set up the application on your local machine, follow these steps:
1. Clone the repository: `git clone https://github.com/chapmanic/Blogga-app.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize the database: `python init_db.py`
4. Run the application: `python app.py`

