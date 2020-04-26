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

    url = 'https://www.worldometers.info/coronavirus/'
    doc = get_document(url)

    country_relative_paths = doc.xpath(
        '//table[@id="main_table_countries_today"]/tbody/tr/td[1]/a[contains(@href, "country/")]/@href')

    country_absolute_paths = ['https://www.worldometers.info/coronavirus/' + each for each in country_relative_paths]
    country_absolute_paths.append(url)

    country_names = doc.xpath(
        '//table[@id="main_table_countries_today"]/tbody/tr/td[1]/a[contains(@href, "country/")]/text()')
    country_names = [each.lower() for each in country_names]
    country_names.append('world')

    welcome_message = f'''
            Hi there! I am a bot that gives you the latest stats on Covid-19 cases from around the world.
-Type *world* to get the latest global Covid-19 stats.
-Type the name of a country to get it's latest Covid-19 stats.
-Type *help* to to learn how to interact with me.
'''

    help_message = f'''
                Say *hi* to begin an interaction with me anytime.
-Type *world* to get the latest global Covid-19 stats.
-Type the name of a country to get it's latest Covid-19 stats.
'''

    fallback_message = 'Sorry, I did not quite get that. Type *help* to learn how to interact with me.'

    greeting_tokens = ['hi', 'hello', 'hey']
    if incoming_msg in greeting_tokens:
        msg.body(welcome_message)
        responded = True

    if incoming_msg in country_names:
        # return cases
        country = incoming_msg
        i = country_names.index(country)
        url = country_absolute_paths[i]
        doc = get_document(url)
        data_message = get_data_message(country, url, doc)
        msg.body(data_message)
        responded = True

    if 'help' in incoming_msg:
        # return help message
        msg.body(help_message)
        responded = True

    if not responded:
        msg.body('Sorry, I did not quite get that. Type *help* to learn how to interact with me.')

    return str(resp)


def get_document(url):
    response = requests.get(url)
    doc = html.fromstring(response.content)
    return doc


def get_data_message(country, url, doc):
    total, deaths, recovered = doc.xpath('//div[@class="maincounter-number"]/span/text()')
    data_message = f'''
                    *Latest Covid-19 cases from {country.title()}*
Total cases: {total}
Recovered: {recovered}
Deaths: {deaths}

View more: {url}
'''
    return data_message


if __name__ == '__main__':
    app.run()
