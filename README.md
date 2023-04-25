# Deploy a Flask App on Apache Shared Hosting with MySql

## Preparing the Application Before Deployment

Flask provides a run command to run the application with a development server. In production we will substitute it with a FastCGI server. In our case We will use flup, it is one of the most popular and also is used in the Flask documentation.

It is usually recommended to use a virtual environment whenever you work on a Python-based project. So the dependencies of every project are isolated from the system and each other. This recommendation is especially important when the app will be uploaded to the internet for production.

Also, consider using SQLAlchemy to create and maintain the app’s database. This option will let you work with SQLite on development and easily migrate to MySql, PostgreSQL, or other relational databases for production.

Make sure that any **app.run()** calls are inside an *if __name__ == ‘__main__’* block.

Remember to delete all printings you used during development because they will break the CGI by writing into the HTTP response.

## Setting up the Environment for Deployment in Production

You can set your environment with an SSH connection or a terminal application online included in the cPanel.

Before deployment to production, it should be verified with the technical staff running the web hosting server if python is installed. It is recommended to use in development the same version of python installed in production.

The following steps are described assuming the app will be installed in the folder deploy_flask/. You may change the name of the folder at your convenience.

### Step 1: Install the Virtual Environment

Sometimes you may substitute $HOME with the path to the root of your installation.

```
python -m venv $HOME/venv/deploy_flask/
```

Then activate the virtual environment:

```
. $HOME/venv/deploy_flask/bin/activate
```

After activation, you should see some new text on the command line to indicate you are using your newly created virtual environment. In my case, it looks like this.

```
(deploy_flask)username@domain.com [~]#
```

### Step 2: Install the Packages

You may install your packages manually, i.e.:

```
pip install flup
pip install flask
⠇
```

Although, it will be more effective to install the packages via a requirements.txt file:
```
pip install -r $HOME/public_html/deploy_flask/requirements.txt
```

Remember to include in the requirements.txt file the flup and mysql-connector packages. You can also install them manually.

Deactivate the virtual environment after you finished installing the packages:

```
(deploy_flask)username@domain.com [~]# deactivate
```

You may face problems when installing your packages with the requirements.txt file. In this case you may try to upload the site-packages/ folder from your development virtual environment instead of the one in the production virtual environment. Pay attention, this will work if you are using the same python version.

## Uploading the App to Production

### Step 1: Create your Database and Update the connector

With the database tools create a database and update the main.py file:

```
from flask_sqlalchemy import SQLAlchemy
⠇
app.config[‘SECRET_KEY’] = “the-secret-key”
app.config[‘SQLALCHEMY_DATABASE_URI’] = ‘mysql+mysqlconnector://user:password@localhost/your_database’
app.config[‘SQLALCHEMY_TRACK_MODIFICATIONS’] = False
db = SQLAlchemy(app)
```

### Step 2: Create .htaccess and fcgi files

Create $HOME/public_html/deploy_flask/ .htaccess

```
Options +ExecCGI
AddHandler fcgid-script .fcgi
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !=/path/to/public_html/deploy_flask/deploy_flask.fcgi
RewriteRule ^(.*)$ deploy_flask.fcgi/$1 [QSA,L]
```

Create $HOME/public_html/deploy_flask/deploy_flask.fcgi

```
#!/path/to/venv/deploy_flask/bin/python
from flup.server.fcgi import WSGIServer
from main import app as application
WSGIServer(application).run()
```

Make the fcgi file executable
```
chmod +x $HOME/public_html/deploy_flask/deploy_flask.fcgi
```

## Upload and Run the Application

Now you can upload your app to the server and run it.

