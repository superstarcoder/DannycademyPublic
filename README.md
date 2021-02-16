This is a public repo for Dannycademy's website. Dannycademy is an organizaton that teaches coding interactively for free!
check out our website: https://www.dannycademy.org/


## Inspiration

After many years of coding, I realized that the best way to learn programming is to work on coding projects that you find the most interesting. This way you will not only learn more, but also have an enjoyable learning experience. I did not find many interactive/project based coding websites or tutorials online, so I decided to create my own organization called Dannycademy where I could help students learn various coding concepts the smart way. The first step I took was creating an interactive website for the organization.

## What it does

On the course section of our website, all the available courses from various topics are displayed. After the user clicks on the course, the user is taken to the course page where all the chapters/exercises of the course are listed. There is a separate page for each chapter and exercise. There is also an online editor section on the website where users can run python code online. Users can register on our website with an email, username, and password. Then, the user must sign in using their username and password. If the user forgets their password, the website sends the user an email with instructions on how to reset their password.

## How I built it

For running the website I used Flask which is a lightweight WSGI (Web Server Gateway Interface) web application framework for python. I used python as the backend programming language and sqlite3 for my database to store encrypted user data. For the online editor tab, I used docker, a popular virtualization software, to run the user’s code securely in containers, without giving any access to the server files. If the code uses too much cpu or takes more than a specific time to run, the docker automatically stops running the program. I hosted my website on linode, a platform for linux cloud computing. To run my flask server for production, I used gunicorn and nginx.

## What I learned

I learned how to use docker and sqlite3 and improved my knowledge in using flask, which is a lightweight WSGI (Web Server Gateway Interface) web application framework for python. I learned how to use Flask’s jija2 template engine to help me avoid the repetition of my html code. I enhanced my html, css and bootstrap knowledge. I also learned how to host my website on a linux server from scratch and convert my development flask server to a production server using gunicorn and nginx.

![info1](https://cdn.discordapp.com/attachments/573324187943305223/811091656106835988/Screenshot_20210215_202827.png)
![info2](https://cdn.discordapp.com/attachments/573324187943305223/811091731902365696/Screenshot_20210215_202854.png)
