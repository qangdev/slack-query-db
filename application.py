import re
import os
import logging
import requests

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.DEBUG)

'''
SLACK BOT
'''
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from prettytable import PrettyTable


app = App()


@app.middleware
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.message(re.compile("(get -)(fname|lname)([\w\d\s]+)"))
def reply_to(say, context):
    try:
        field, value = context.matches[1], context.matches[2]
        field, value = field.strip().lower(), value.strip().lower()
        payload = {
            f"{field}": f"eq.{value}"
        }
        r = requests.get(f"{os.getenv('POSTGREST_API_ENDPOINT')}/{os.getenv('TABLE_DATA_SOURCE')}", params=payload)
        
        result = r.json()
        
        # Define a table to display
        ptable = PrettyTable()
        ptable.align = "l"
        
        # If there is nothing then display "no data"
        if len(result) == 0:
            ptable.field_names = ["Result"]
            ptable.add_row(["No data"]) 
        
        # If there is data then add row to table 
        for idx, item in enumerate(result):
            if idx == 0:
                ptable.field_names = item.keys()
            ptable.add_row(item.values())

        # Finally print the table on Slack
        say(f"```{ptable.get_string()}```")
    except Exception as e:
        say("Sorry.. Something went wrong :(")
        raise e
'''
END SLACK BOT
'''

'''
FLASk APP
'''
from flask import Flask, request, jsonify

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

'''
END FLASK APP
'''

if __name__ == "__main__":
    flask_app.run(port=os.getenv("APP_PORT"))
