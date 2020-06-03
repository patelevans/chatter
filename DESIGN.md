# Looking at the implementation of Chatter!

# Chatter uses a SQLite database in conjunction with a Flask App to create a dynamic web app that is effectively a basic social media website.


# At the heart of chatter is the database, "chatter.db".
# chatter.db contains 5 tables: users, profiles, posts, comments, and follows.

The users table contains the id of every user, their username, and a hash of their password. The password is hashed the same way as it was in CS50 Finance.
In the users table, there are unique indices on the user's id and username.

The profiles table contains the user's id, as well as any information about the user, and a link to a picture they can display on their profile.
In the profiles table, there is a unique index on the user's id.

The posts table contains the post's id, the poster's user id, the post's title, the post's contents, and the date and time the post was created.
In the posts table, there is a unique index on the post's id. In addition, there is another index (not unique) on the poster's user id.

The comments table contains the comment's id, the commenter's user id, the post id of the post the comment is on, the contents of the post, and the date and time it was created.
In the comments table, there are indices on the commenter's user id and the post's post id. There is a unique index on the comment's id.

The follows table contains the user id of a follower and the user id of a followee.
In the follows table, there are indices on both columns.

Indices were created on columns that would be searched often or columns that were unique.

"users.txt" is a plaintext file that contains a list of usernames and passwords for testing the application.


# The logic behind the webpage lies in "application.py".

The "/" route shows the home page.
In this route, SQL queries are used to get the username of the logged in user and posts made by the user's followees.
This route renders a home page that welcomes the user and shows them a list of posts by people they follow.
"index.html" is structured to allow users to click on post titles and usernames to view posts' contents and go to users' profiles.

The "/addcomment" route lets a user add a comment to a post.
This route is POST only, because it is accessed from "post.html", which contains a form to add comments.
This route first ensure that the comment box is not empty (or returns an apology as in CS50 Finance), then uses a SQL statement to insert the comment into the database.

The "/discover/people" route shows the user a list of people followed by their followees.
Since this route uses "peoplelist.html" template, which is used by other routes, it first sets the page's title.
Then, a SQL query gets a list of usernames followed by the user's followees. "peoplelist.html" is rendered.
If the user does not have any second degree followees, Jinja templating is used to simply display the word "Empty".

The "/discover/posts" route shows the user the 50 newest posts on Chatter.
This route uses a SQL query to get the 50 newest posts from "chatter.db", regardless of whether the user is following the poster.
This route renders "postlist.html" to list out all of the posts. Again, post titles and usernames are clickable, due to Jinja templating.

The "/editprofile" route lets users edit their profiles.
If the method for the route is GET, it simply renders a form from "editprofile.html".
If the method is POST, a SQL statement is used to update the user's profile entry in "chatter.db" with the contents of the form.
Then, after the database is updated, the user is redirected to their profile.
If any part of the form is empty, the entry column corresponding to that part of the form in "chatter.db" will also be empty.

The "/follow" route lets users follow other people.
The follow button exists on users' profiles, so this route is POST only.
First, the route ensures that the user is already not following the other user, returning an apology message if they are.
Then, the route adds to the follows table in "chatter.db" the user's id as follower id and the other profile's id as followee id.
Lastly, the route redirects to the profile that the user just followed.

The "/followees" route lets users see a list of their followees.
Since it uses "peoplelist.html" as the "/discover/people" route does, the route first sets the page title.
Then, the route uses a SQL query to get the user's followees.
The route renders "peoplelist.html". If the user is not following anyone, Jinja templating is used to display the word "Empty".

The "/followers" route lets users see a list of their followers.
Since it uses "peoplelist.html" as the "/discover/people" and "/followees" routes do, the route first sets the page title.
Then, the route uses a SQL query to get the user's followers.
The route renders "peoplelist.html". If the user has no followers, Jinja templating is used to display the word "Empty".

The "/login" route lets users log into their accounts.
The implementation of this route is exactly the same as the distribution code of login in CS50 Finance.

The "/logout" route lets users log out of their accounts.
This implementation is also the same as it was in CS50 Finance.
The session is cleared, and the user is redirected to the "/" route.

The "/newpost" route lets users make a new post.
If the method is GET, the route renders "newpost.html". The following occurs when the method is POST.
The form ensures that the "title" and "contents" fields are not blank, or else it returns an apology.
In addition, to prevent users from making duplicate posts, the application returns an apology if the user has already made a post with the same title or contents.
If all condiitons are satisfied, the post is added to the "chatter.db" and the user is redirected to the "/" route.

The "/post/post_id" route shows users the contents of the post they clicked on and all comments on that post.
This route takes a post id as an input and queries "chatter.db" for that post.
The route ensures that there is only 1 post with that post_id, or returns an apology.
Then, the route queries the database for comments on the post.
Finally, the route renders the "post.html" template.

The "/profile/user_id" route shows users the profile they clicked on, and shows the profile's post history.
This route takes a user id as an input and queries "chatter.db" for the corresponding profile.
If more than one profile is returned, then an apology is returned.
Then, the route finds out if the profile belongs to the user and saves that information.
If the profile did not belong to the logged in user, the route finds out whether the profile belongs to someone the user follows.
Lastly, the database is queried for the post history associated with the profile, and then "profile.html" is rendered.
Using Jinja, the page shows different action buttons based on whether the profile belongs to the user, belongs to someone the user follows, or belongs to neither.

The "/register" route is largely taken from my implementation of CS50 Finance.
However, there are some modifications. The SQL queries are different, as there is a different database being used in this application.
In addition, the "/register" route creates a blank profile for the user.

The "/search" route lets users search for posts and people.
The route is POST only, due to the search bar being present on every page of the web app (the search bar is in "layout.html").
The route makes sure the search bar is not empty, or else it returns an apology.
The route queries the database for any posts with titles or contents matching the keywords, as well as any usernames matching the keywords.
Lastly, the route renders "search.html", which displays the search results.

The "/unfollow" route lets users unfollow a profile.
The unfollow button exists on users' profiles, so this route is POST only.
First, the route ensures that the user is following the other user, returning an apology message if they are not.
Then, the route removes from the follows table in "chatter.db" the entry containing the user's id as follower id and the profile's id as followee id.
Lastly, the route redirects to the profile that the user just unfollowed.


# A look at the front end of the web app.

"layout.html" is the basic layout of the website. Every other template extends this template.
The website uses Bootstrap for styling, as well as a custom "styles.css" stylesheet in the static folder.
The necessary JavaScript for some Bootstrap elements to work is also imported in, as well as jQuery for a custom script for forms.
This custom script for forms is intended to disable the submit button on certain forms if the fields are left blank.
The script works well for the search bar, but is only partially functional on forms with more than one text entry field.
For that reason, I have still built in the logic in "application.py" to reject inappropriately blank entries on forms.
For all templates that extend "layout.html", I've used Jinja to dynamically fill in the header and body of the webpage.
In addition, Jinja is used to dynamically generate buttons and content, given certain conditions are satisfied.