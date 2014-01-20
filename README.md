Django on OpenShift
===================

This git repository s a Django project template that helps you get up and
running quickly w/ a Django installation on OpenShift.

It configures your settings to autodetect the database type and does a syncdb
on every deploy.

Note that the [Django admin password](#admin-user-name-and-password) is set for
you.


Creating the project
--------------------

We're going to make a project called myproject, based on the openshift project
template. Note that we ask django-admin.py to render application as well. This
is important because this file is called by OpenShift and by default
django-admin only renders .py files.

    django-admin.py startproject -n application --template https://github.com/ekohl/django-project-openshift/archive/master.zip myproject

Since startproject does not handle hidden directories, we need to move our
openshift directory:

    cd myproject
    mv openshift .openshift

Now we're going to commit it in git:

    git init
    git add .
    git commit -m "Initial commit"


Running on OpenShift
--------------------

Create an account at http://openshift.redhat.com/

Install the RHC client tools if you have not already done so:

    sudo gem install rhc

Create a python-2.7 application:

    rhc app create myproject python-2.7 --from-code empty --no-git

Consider adding postgresql (or mysql) and making it scaling:

    rhc app create myproject python-2.7 postgresql-9.2 --scaling --from-code empty --no-git

Now got to the previously created django project:

    cd myproject

Because we skipped the git clone, we need to manually add our remote. Look for
Git URL:

    rhc show-app myproject

Or we can automate it:

    GIT_URL=`rhc show-app myproject | awk '/Git URL/ { print $3 }'`

Add it as a remote named openshift:

    git remote add openshift $GIT_URL

Then we push it to deploy the application. We will also set the upstream so git
will [track the remote branch](http://git-scm.com/book/en/Git-Branching-Remote-Branches#Tracking-Branches):

    git push --set-upstream openshift HEAD

Now the [admin user name and password](#admin-user-name-and-password) will be
displayed, so pay special attention.

That's it. You can now checkout your application at:

    http://myproject-$yournamespace.rhcloud.com


Admin user name and password
----------------------------
As the `git push` output scrolls by, keep an eye out for a line of output that
starts with `Django application credentials: `. This line contains the
generated admin password that you will need to begin administering your Django
app. This is the only time the password will be displayed, so be sure to save
it somewhere. You might want to pipe the output of the git push to a text file
so you can grep for the password later.


Repo layout
-----------
wsgi/ - Externally exposed wsgi code goes
wsgi/static/ - Public static content gets served here
libs/ - Additional libraries
data/ - For not-externally exposed wsgi code
setup.py - Standard setup.py, specify deps here
../data - For persistent data (also env var: OPENSHIFT\_DATA\_DIR)
.openshift/action\_hooks/pre\_build - Script that gets run every git push before the build
.openshift/action\_hooks/build - Script that gets run every git push as part of the build process (on the CI system if available)
.openshift/action\_hooks/deploy - Script that gets run every git push after build but before the app is restarted
.openshift/action\_hooks/post\_deploy - Script that gets run every git push after the app is restarted


Environment Variables
---------------------

OpenShift provides several environment variables to reference for ease
of use. The following list are some common variables but far from exhaustive:

    os.environ['OPENSHIFT_APP_NAME']  - Application name
    os.environ['OPENSHIFT_DATA_DIR']  - For persistent storage (between pushes)
    os.environ['OPENSHIFT_TMP_DIR']   - Temp storage (unmodified files deleted after 10 days)

When embedding a database using 'rhc cartridge add', you can reference environment
variables for username, host and password:

If you embed MySQL, then:

    os.environ['OPENSHIFT_MYSQL_DB_HOST']      - DB host
    os.environ['OPENSHIFT_MYSQL_DB_PORT']      - DB Port
    os.environ['OPENSHIFT_MYSQL_DB_USERNAME']  - DB Username
    os.environ['OPENSHIFT_MYSQL_DB_PASSWORD']  - DB Password

To get a full list of environment variables, simply add a line in your
.openshift/action\_hooks/build script that says "export" and push.


Notes about layout
------------------
Please leave wsgi, libs and data directories but feel free to create additional
directories if needed.

Note: Every time you push, everything in your remote repo dir gets recreated
please store long term items (like an sqlite database) in ../data which will
persist between pushes of your repo.


Notes about setup.py
--------------------

Adding deps to the install\_requires will have the openshift server actually
install those deps at git push time.
