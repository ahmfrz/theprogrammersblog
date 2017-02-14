# The Programmers Blog
 
### What is it?
 It's a multiuser blog where programmers can share their stories. Url: http://theprogrammersblog.appspot.com/
 
### Features
 * Backend is built with python and google app engine
 * Frontend is built with Bootstrap
 * Passwords are hashed before storage
 * Cookie hashing for user security
 * Pagination(5 posts on one page)
 * Users can comment, like/ unlike eachothers posts
 * Users can see all posts by a user and contact them with provided email address
 * Users can edit/ delete their posts
 * Allows raw html to be added in content just for fun
 * About page is a responsive portfolio page of the author, source code is available at - https://github.com/ahmfrz/Portfolio-Site/
 
### Installation steps
 For awesome people who would like to debug the application at their end, following are the steps:
 
 #### Pre-requisites:
 * Python 2.7 - https://www.python.org/downloads/
 * Any text editor for editing the code(Sublime text preferred - https://www.sublimetext.com/download)
 * Google cloud SDK - https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
 
 #### Steps
 1. Download/ Fork all files and folders from theprogrammersblog in a folder
 2. Open command prompt and navigate to the source code folder
 OR Press and hold shift and right click in the empty area and select 'Open command window here' from the menu
 3. Enter the following command:
 'dev_appserver.py .'
 4. Enter Chrome(Or any other browser) and navigate to 'http://localhost:8080/'
 5. Now you can make changes and enjoy the app as much as you like
 
### Known Issues
 * 1000 posts can be accessed from the homepage
 * New post page has an upcoming feature box
 * Little white indicator which shows where you are on the site is fixed at 'Home' nav
