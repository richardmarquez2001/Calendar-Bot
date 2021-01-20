from __future__ import print_function

import datetime
import pickle
import os.path
import dateutil.parser

import os
from dotenv import load_dotenv, find_dotenv

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import discord

# Read only level
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def start():
    client = discord.Client()

    @client.event
    async def on_message(message):

        if message.author == client.user:
            return
        
        # sends message of next class
        elif message.content == '!nextclass':
            startMsg = getMessage()
            msg =  startMsg + '{0.author.mention}'.format(message)
            await message.channel.send(msg)
        
        # sends photo of current schedule
        elif message.content == '!schedule':
            await message.channel.send('https://media.discordapp.net/attachments/736430075322302536/801489177128337418/unknown.png?width=658&height=676')


    @client.event
    async def on_ready():
        print("Logged in as: ", end="")
        print(client.user.name + " ", end="")
        print(client.user.id)
        print("---------")


    load_dotenv(find_dotenv())
    SECRET_KEY = os.environ.get("SECRET_KEY")
    client.run(SECRET_KEY) #bot token

# method used to get API data
def getMessage():
    creds = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Logs in user if nothing found in token.pickle file

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=2, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    startMsg = ""

    if not events:
        startMsg = "No events were found "
    else:
        for event in events:
            startMsg = ""
            start = event['start'].get('dateTime', event['start'].get('date'))
            dateutil.parser.parse(start)
            dt = dateutil.parser.parse(start)
            
            start = dt.strftime('%A, %B %d. %H:%M %p\t')

            startMsg += "Next class is at " + start + "\n"
            startMsg += "The class is " + event['summary']
            startMsg += "\n"

            da = dateutil.parser.parse(str(datetime.datetime.now()))
            dhour = int(da.strftime('%H'))
            dminute = int(da.strftime('%M'))

            ehour = int(dt.strftime('%H'))
            eminute = int(dt.strftime('%M'))
            
            
            # this case handles if next class is occuring, displays next class
            if dhour < ehour or (dhour == ehour and dminute < eminute):
                print('hit case')
                break
    
    return startMsg

# whatever that means
def main():
    start()
if __name__ == '__main__':
    main()