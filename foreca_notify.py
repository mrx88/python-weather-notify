#! python
"""
Fun project to automatically warn user if there is x probability
that it's going to rain. Send automated notification accordingly.

Notification possibilities:
1) MS Teams webhook
2) SMS through Twilio API
"""

import datetime
import logging
import os
import json
import time
import click
import requests
import bs4
from twilio.rest import Client


class Globals:
    """Parse data from Foreca"""
    def __init__(self, url):
        """Init func"""
        self.url = url

    def getdata(self):
        """Get html data"""
        data = requests.get(self.url)
        return bs4.BeautifulSoup(data.text, 'html.parser')

    def gethour(self, urldata):
        """Get hour data"""
        return urldata.findAll("div", {"class": "c0"})[1].getText()

    def getrain(self, urldata):
        """Get rain precentage"""
        details = urldata.findAll("div", {"class": "c3"})[1]
        return details.select('strong')[1].getText()

    def gethumidity(self, urldata):
        """Get humidity percentage"""
        details = urldata.findAll("div", {"class": "c3"})[1]
        return details.select('strong')[2].getText()

    def gettemp(self, urldata):
        """Get temprerature"""
        details = urldata.findAll("div", {"class": "c3"})[1]
        return details.select('strong')[0].getText()

    def converttime(self, gethour):
        """test"""
        eventime = str(time.strftime("%Y-%m-%d")) + gethour
        eventimeformat = datetime.datetime.strptime(eventime, "%Y-%m-%d %H:%M")
        alerttime = (eventimeformat - datetime.timedelta(hours=4))
        return alerttime


def thresholds(getrain, city, gethumidity, gettemp, gethour):
    """Send alerts to user if threshold X is met """
    rain = int(getrain.strip('%'))
    title = "Foreca Weather Information"

    if rain >= 60:
        message1 = "It is going to rain at ({0}), probability {1} ".format(
            gethour, getrain)
        message2 = "Other: Humidity {0}, Temperature {1}, Location {2}".format(
            gethumidity, gettemp, city)
        warn = message1 + message2

        # Send notifications
        send_teams(title, warn)
        send_twilio(warn)
        return warn
    elif rain < 60:
        warn = 'OK:  Raining probability is low in {0} ({1})'.format(city, getrain)
        return warn
    else:
        return 'Something went wrong?'


def send_teams(title, message):
    """Function for sending MS Teams notifications"""
    try:
        alert = """{
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": "SUMMARY",
                "themeColor": "0078D7",
                "title": "TITLE",
                "sections": [ { "text": "LOG" } ]
            }"""

        token = os.getenv('MS_TEAMS_TOKEN')
        alert_json = json.loads(alert)
        alert_json['title'] = "[{0}]".format(title)
        alert_json['sections'][0]['text'] = "[%s], " % (message)
        send_alert = requests.post(
            token, data=json.dumps(alert_json))
        send_alert.raise_for_status()

    except KeyError as error:
        logging.error("Problems with token: %s", error)
    except Exception as error:
        logging.error("Problems with sending webhook: %s", error)


def send_twilio(message):
    """Send SMS through Twilio API"""
    try:
        account_sid = os.getenv('TWILIO_SID')
        auth_token = os.getenv('TWILIO_TOKEN')
        sms_from = os.getenv('TWILIO_SMS_FROM')
        sms_to = os.getenv('TWILIO_SMS_TO')
        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
                body=message,
                from_=sms_from,
                to=sms_to
            )

        print(message.sid)
    except Exception as error:
        logging.error("Problems with Twilio API communication: %s", error)


@click.command()
@click.option("--country", default="Estonia", help="Define Country")
@click.option("--city", default="Viimsi", help="Define City")
def main(city=None, country=None):
    """Main function"""
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        #  Get data from Foreca
        foreca = Globals('http://www.foreca.com/{0}/{1}?details=20160804'.format(country, city))
        urldata = foreca.getdata()
        gethour = foreca.gethour(urldata)
        getrain = foreca.getrain(urldata)
        gethumidity = foreca.gethumidity(urldata)
        gettemp = foreca.gettemp(urldata)
        alerttime = foreca.converttime(gethour)

        # Alert if current time matches before and after time, send out alert
        now = datetime.datetime.utcnow()
        logging.debug('Hour: %s, Rain: %s, Humidity: %s, Temp: %s, Now time: %s, Alerttime: %s',
                      gethour, getrain, gethumidity, gettemp, now, alerttime)
        if now >= alerttime:
            logging.debug('Alert time: %s', str(alerttime))
            logging.info('Alert message: %s', thresholds(
                getrain, city, gethumidity, gettemp, gethour))
    except Exception as error:
        logging.error("Error: %s", error)


if __name__ == '__main__':
    main()
