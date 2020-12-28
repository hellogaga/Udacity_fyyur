# Fyyur
-----

## Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

## Table of contents
  - [Overview](#Overview)
  - [Table of contents](#table-of-contents)
  - [Teck Stack](#Tech-Stack-(Dependencies))
  - [Project Structure](#project-structure)
  - [How to use the application](#how-to-use-the-application)
  - [Screenshot of the application](#screenshot-of-the-application)
  - [Licensing, Authors, Acknowledgements](#licensing-authors-acknowledgements)

## Overview

The application use PostgreSQL database in the backend. The application is capable of:
* creating new venues, artists, and creating new shows.
* searching for venues and artists.
* learning more about a specific artist or venue.

We want Fyyur to be the next new platform that artists and musical venues can use to find each other, and discover new music shows.

## Tech Stack (Dependencies)

### 1. Backend Dependencies
Our tech stack will include the following:
 * **virtualenv** as a tool to create isolated Python environments
 * **SQLAlchemy ORM** to be our ORM library of choice
 * **PostgreSQL** as our database of choice
 * **Python3** and **Flask** as our server language and server framework
 * **Flask-Migrate** for creating and running schema migrations
You can download and install the dependencies mentioned above using `pip` or `conda` as:
```
pip install virtualenv
pip install SQLAlchemy
pip install postgres
pip install Flask
pip install Flask-Migrate
```

### 2. Frontend Dependencies
You must have the **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/) for our website's frontend. Bootstrap can only be installed by Node Package Manager (NPM). Therefore, if not already, download and install the [Node.js](https://nodejs.org/en/download/). Windows users must run the executable as an Administrator, and restart the computer after installation. After successfully installing the Node, verify the installation as shown below.
```
node -v
npm -v
```
Install [Bootstrap 3](https://getbootstrap.com/docs/3.3/getting-started/) for the website's frontend:
```
npm init -y
npm install bootstrap@3
```

## Project Structure

  ```sh
  ├── README.md
  ├── app.py *** the main driver of the app. Includes your SQLAlchemy models.
                    "python app.py" to run after installing dependences
  ├── config.py *** Database URLs, CSRF generation, etc
  ├── error.log
  ├── forms.py *** Your forms
  ├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
  ├── static
  │   ├── css 
  │   ├── font
  │   ├── ico
  │   ├── img
  │   └── js
  └── templates
      ├── errors
      ├── forms
      ├── layouts
      └── pages
  ```

Overall:
* Models are located in the `MODELS` section of `app.py`.
* Controllers are also located in `app.py`.
* The web frontend is located in `templates/`, which builds static assets deployed to the web server at `static/`.
* Web forms for creating data are located in `form.py`

Highlight folders:
* `templates/pages` --  Defines the pages that are rendered to the site. These templates render views based on data passed into the template’s view, in the controllers defined in `app.py`. These pages successfully represent the data to the user, and are already defined for you.
* `templates/layouts` -- Defines the layout that a page can be contained in to define footer and header code for a given page.
* `templates/forms` --  Defines the forms used to create new artists, shows, and venues.
* `app.py` --  Defines routes that match the user’s URL, and controllers which handle data and renders views to the user. This is the main file you will be working on to connect to and manipulate the database and render views with data to the user, based on the URL.
* Models in `app.py` --  Defines the data models that set up the database tables.
* `config.py` --  Stores configuration variables and instructions, separate from the main application code. This is where you will need to connect to the database.


## How to use the application
1. Understand the Project Structure (explained above) and where important files are located.
2. Install all the dependencies according to the instructions before. 
3. git clone this repo to your local folder using `https://github.com/hellogaga/Udacity_fyyur.git`
4. Navigate to **config.py** and revise the line `SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost:5432/fyyur'` with your own PostgreSQL username and password. 
5. Login to your PostgreSQL through `psql -U yourusername` and build a local database named 'fyyur' through the following in the computer console `CREATE DATABASE fyyur;`
6. Navigate to the local folder and run the following commands. They will initiate the required tables in the application. 
```
flask db init
flask db migrate
flask db upgrade
```  
7. Run `python app.py`  
8. Navigate to project homepage [http://127.0.0.1:5000/](http://127.0.0.1:5000/) or [http://localhost:5000](http://localhost:5000) 
9. Enjoy the application.

## Screenshot of the application
index page <br>
![](pics/index.png =500x) 

add a new venue<br>
![](pics/addvenue.png =500x) 

## Licensing, Authors, Acknowledgements
The code released subjects to the MIT license. The author appreciates the code structure from [Udacity](www.udacity.com).