# Introducing Chatter, a basic social media website!

To begin, make sure the terminal is in the directory containing application.py.
Then, in the terminal, execute "flask run".
Click on the link in the terminal, and the application should appear in a new tab or window.

From here, you can do anything you want!
The first page that appears should be the login page. In the users.txt file, I've provided some usernames and passwords; feel free to use them.
Alternatively, you can also register a new account using the register link in the top right. Go ahead and log in after registration.

You should be taken to the home page after logging in. The home page displays all posts by people you follow. If you've created a new account, this page is empty.
In order to first interact with posts of other users on the website, there are two avenues. The first is the Discover Posts page. This lists the 50 most recent posts.
The other option is the search bar. Enter any search term, and if there is a matching post or username, it will be listed. All posts and usernames can be clicked on.

Clicking on a post will take you to the post's individual page, in which its contents are shown along with any comments on the post. On this page, you can add comments.
Clicking on a username will take you to the user's profile page, in which you can see their profile picture (if they have set one),
as well as any other information they have elected to share. The user's profile page will also list all posts by that user below their profile.

On the profile page, you can follow a user, or unfollow them if you are already following them. If you are on your own profile page, you can edit your profile.
Editing your profile entails adding an "About" section, in which you can tell any visitors to your profile page about yourself, and adding a profile picture.
Of note is that when you edit your profile, if any of the fields are left blank, they will be updated to be blank in the database.
In addition, if you are on your own profile page, you can click on "My Followers / My Followees" to see a list of your followers / followees.
After you have followed at least one user, the home page begins to show posts by your followees, and the Discover People page begins showing followees of followees.

There are a few more items on the navbar that should be self-explanatory. Clicking on "Chatter" or "Home" will take you to the home page.
Clicking on "My Profile" will take you to your profile. Clicking on "New Post" will allow you to make a post. Lastly, clicking on "Log Out" will log you out.