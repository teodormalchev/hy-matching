# hy.com
CS50 Final Project - Here is how to use:

All imports from the python files need to be installed - CS50, flask, flask_session, etc.

Our project is a website that serves as a housing matching platform, where students from Harvard and Yale can register with an account, fill out a form for housing once they have registered, and see their match's information if they have been matched. The user can also view and change their profile, including their password.

To run the website, you have to download all the provided files in a folder and run "flask run" in the terminal in that folder. You may have to activate a virtual environment(venv) on Windows before that. After that, you need to copy the link provided in the terminal and paste it in a browser, where you can use the website. Between now and next year's Harvard-Yale Game, we will actually host the website on a web server. 
For the purpose of demonstration, we  made a few fake accounts which we have matched. You can use those and create new ones too (note that these new ones will not be matched, since the matching algorithm needs to be run manually). Here are their emails and passwords:

1. email: david@college.harvard.edu password: david
2. email: carter@college.harvard.edu password: carter
3. email: yulia@college.harvard.edu password: yulia
4. email: alexandre@college.harvard.edu password: alexandre
5. email: matteo@college.harvard.edu password: matteo
6. email: teodor@college.harvard.edu password: teodor
7. email: yaleduck1@yale.edu password: yaleduck1
8. email: yaleduck2@yale.edu password: yaleduck2
9. email: yaleduck3@yale.edu password: yaleduck3
10. email: yaleduck4@yale.edu password: yaleduck4
11. email: yaleduck5@yale.edu password: yaleduck5

It is important to note that the algorithm.py program needs to be run before you refresh if you want to see the matches for new users that previously did not have an account or had not filled out the form. The idea of the project in real life is that this program will be run only once - one week before The Game, but for testing purposes it can be run multiple times.

Additionally, the variable _matches_done_ on line 30 in app.py can be changed to "False" stop displaying the matches as done

---

The principles of HY.com (what the platform is used for, how users get connected, ...) are explained on the site itself, and you can find a video rundown here:
https://youtu.be/-6r8dPIDVqs

