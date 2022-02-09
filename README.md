# Slack Query Database

A POC to demonstrate using Slack text messaging to fetch data in a database and display data as a table.

## Set up Flask web app

Prerequiremnts:
1. `python3` is installed.
2. `docker` and `docker-compose` are installed.
3. `ngrok` is install/available


### Step 0: Virtual environment
This is optional. Do it if you prefer `virtualenv`
1. On the project root and create virtual environment by running `python3 -m venv venv`
2. Activate the new environment by running `source ./venv/bin/activate`

### Step 1: Install requirements
Install all required packages by running `pip install -r requirements.txt`

### Step 2: Create DotEnv file
This program use `python-dotenv` to use environment variables.

In side the project root. Add a new file named `.env` then copy and paste contents from `.env-default` to it.

Your `.env` should look something like this

```
APP_PORT=5000
POSTGREST_API_ENDPOINT=http://0.0.0.0:3000
TABLE_DATA_SOURCE=user_profile
SLACK_BOT_TOKEN=xoxb-<TOKEN>
SLACK_SIGNING_SECRET=<SECRET>
```


### Step 3: Init the project
You can init project by running `make init`

Sample output:

```
docker-compose up -d --build
Creating network "slack-query-db_default" with the default driver
Creating volume "slack-query-db_pgdata" with default driver
Creating slack-query-db_db_1      ... done
Creating slack-query-db_swagger_1 ... done
Creating slack-query-db_postgrest_1 ... done
docker cp ./skel/user_profile.sql slack-query-db_db_1:/
sleep 3
docker exec -it slack-query-db_db_1 bash -c "export PGPASSWORD='nCCGkzg9qs3hPsy7'; psql -U admin -d demodb -q < user_profile.sql"
```

It will build services that are described in `docker-compose.yml` and then import sample data from `user_profile.sql` file for `user_project` table.

To destroy all services and remove data. Run `make destroy`

### Step 4: Ngrok
Run the Flask web app by running `python3 application.py`

The Flask app will be run on port 5000 by default. You can change it in the `.env` file.

Use ngrok to publish your Flask app so that Slack can verify

Use `ngrok` run `ngork http 5000`

Sample output:

```
ngrok by @inconshreveable                                                                                                          (Ctrl+C to quit)
                                                                                                                                                   
Session Status                online                                                                                                               
Account                       qang (Plan: Free)                                                                                                    
Version                       2.3.40                                                                                                               
Region                        United States (us)                                                                                                   
Web Interface                 http://127.0.0.1:4040                                                                                                
Forwarding                    http://<TOKEN>.ngrok.io -> http://localhost:5000                                 
Forwarding                    https://<TOKEN>.ngrok.io -> http://localhost:5000                                
                                                                                                                                                   
Connections                   ttl     opn     rt1     rt5     p50     p90                                                                          
                              0       0       0.00    0.00    0.00    0.00  
```


## Setup Slack
We need a Slack app and tokens to integrate it to our Flask web app

### Step 1: Create a Slack app
1. Visit https://api.slack.com/apps/new and click on `Create New App` button and select `From scratch`
2. Enter an app name (e.g SlackDB) and select one of your workspace
3. Navigate to Basic Information on the left sidebar and scroll down to the App Credentials. Copy your Signing Secret and use it for `SLACK_SIGNING_SECRET` key in `.env` file.

Note: A Slackbot named "SlackDB" will be created after Step 1.

### Step 2: Bot User OAuth Token
1. Navigate to the OAuth & Permissions on the left sidebar and scroll down to the Bot Token Scopes section. Click Add an OAuth Scope.
2. Add `chat:write`. This grants your app the permission to post messages in channels it’s a member of.
3. Scroll up to the top of the OAuth & Permissions page and click Install App to Workspace. You’ll be led through Slack’s OAuth UI, where you should allow your app to be installed to your development workspace.
4. Once you authorize the installation, you’ll land on the OAuth & Permissions page and see a Bot User OAuth Access Token.
5. Copy your Bot User OAuth Access Token and use it for `SLACK_BOT_TOKEN` key in `.env` file.

### Step 3: Event Subcription
1. Navigate to the Event Subcription on the left sidebar and turn it on
2. Enter your ngrok url (either http or https) and then append `/slack/events` to Request URL input(e.g `https://<TOKEN>.ngrok.io/slack/events`)
3. Then click out the input and Slack will verify the link (At this point Flask should be running so Slack can reach)
4. You should get a green tick to indicate it works
5. Scroll down to Subscribe to Bot Events and add `message.channels`, `message.groups`, `message.im`, and `message.mpim`. And then click Save Changes.
6. Slack will ask you to re-install your Slask app to the workspace.

### Step 4: Invite the Slackbot to your channel
Open Slack and login to the workspace that you pick in earlier and pick a channel and invite the Slackbot (SlackDB).

Note: it's name should the same as Slack app name you enter.


## Try it out

Text `get -fname carson` to get all users with first name is carson
```
+-----+--------+------------+---------------------------+
|  id | fname  |   lname    |           email           |
+-----+--------+------------+---------------------------+
|  67 | carson | metterick  | cmetterick1u@redcross.org |
| 340 | carson | kleinzweig |  ckleinzweig9f@diigo.com  |
+-----+--------+------------+---------------------------+
```


Text `get -lname kleinzweig` to get all users with last name is kleinzweig
```
+-----+--------+------------+-------------------------+
|  id | fname  |   lname    |          email          |
+-----+--------+------------+-------------------------+
| 340 | carson | kleinzweig | ckleinzweig9f@diigo.com |
+-----+--------+------------+-------------------------+
```

## Limitation
1. Excatly matching
2. Only can search by first name and last name
3. Can only seach one value at a time

## Table DDL

`user_profile` is the data source for this project.

```sql
create table user_profile (
	id SERIAL PRIMARY KEY,
	fname VARCHAR(50),
	lname VARCHAR(50),
	email VARCHAR(50)
);
```

Set up role and permission for Slackbot
Taken from PostgREST tutorials
[refer: ](https://postgrest.org/en/stable/tutorials/tut0.html)
[refer: ](https://postgrest.org/en/stable/tutorials/tut1.html)

```sql
CREATE ROLE anon nologin;
GRANT USAGE ON SCHEMA public TO anon;
GRANT SELECT ON public.user_profile TO anon;

CREATE ROLE authenticator noinherit login PASSWORD 'password';
GRANT anon TO authenticator;

-- slacknot will be used in PGRST_DB_ANON_ROLE
CREATE ROLE slackbot nologin;
GRANT slackbot TO authenticator;
GRANT USAGE ON SCHEMA public TO slackbot;
GRANT ALL ON public.user_profile TO slackbot;
```

