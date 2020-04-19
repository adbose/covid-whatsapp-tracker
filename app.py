from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
from lxml import html


app = Flask(__name__)


@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False

    for each in ['hi', 'hello', 'hey']:
        if each in incoming_msg:
            msg.body('Hi there! I am a bot that gives you the latest Covid-19 stats from around the world.')
            responded = True
            break

    response = requests.get('https://www.worldometers.info/coronavirus/')
    doc = html.fromstring(response.content)
    total, deaths, recovered = doc.xpath('//div[@class="maincounter-number"]/span/text()')

    body = f'''Coronavirus Latest Updates
            Total cases: {total}
            Recovered: {recovered}
            Deaths: {deaths}
            Source: https://www.worldometers.info/coronavirus/
        '''
    if 'world' in incoming_msg:
        # return global cases  till today
        msg.body(body)
        responded = True
    if 'help' in incoming_msg:
        # return global cases  till today
        msg.body('Type *world* to get the cumulative global cases so far.')
        responded = True
    if not responded:
        msg.body('Sorry, I did not quite get that. Type *help* to learn how to interact with me.')

    return str(resp)


if __name__ == '__main__':
    app.run()
