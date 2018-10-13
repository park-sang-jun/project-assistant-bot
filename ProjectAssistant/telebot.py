#telegram modules
import telegram
from telegram.ext import Updater,CommandHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
import logging 
#other modules
from googlesearch import search #pip install google
from newsplease import NewsPlease #pip install news-please
import requests
from urllib.parse import urlparse
import nltk
from nltk.corpus import wordnet
from gensim.summarization.summarizer import summarize

#########################telegram#########################
bot_token = '622777049:AAEmGczXqFjMD1Jkr0n9WOdRydfWIcj_slI'
bot = telegram.Bot(token=bot_token)
#bot credential
#print(bot.get_me())
#setting up updater & dispatcher
updater = Updater(token=bot_token)
dispatcher = updater.dispatcher
#debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#init cmd
def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

#return /"unknown" is queried
def unknown(bot, update):
    	bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")
'''
functions requiring googling is abandoned
reasons: 
1. Permisson of from Google is required
2. Google may be unhappy even if it is possible implement the function below by trying to bypass Google restraint
#google links
def google(bot, update, args):
	query_list=[]
	query = ' '.join(args)
	number = 10 #no. of trying queries 
	retrieve_url(query, number,query_list)
	filtered_list = urlFilter(query_list)
	bot.send_message(chat_id=update.message.chat_id, text=filtered_list)
	print(query)
'''
#return defintion ***implement check word ==1
def define(bot, update, args):
	word = ' '.join(args)
	text_def = define_word(word)
	bot.send_message(chat_id=update.message.chat_id, text=text_def)

#print raw content in the url ***optional
def rdisplay(bot, update, args):
	url_link =  ' '.join(args)
	raw_content = print_article(url_link)
	bot.send_message(chat_id=update.message.chat_id, text=raw_content)

#return available functions
def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Here are the commands you can use: "
								"\n /start to start the bot \n "
								"/google to google things \n"
								"/define to get the definition of a word \n"
								"/help to display all commands")

#return summary of the text
def summary(bot, update, args):
	text = ' '.join(args)
	summary = "Summary:\n" + summarize(text)
	bot.send_message(chat_id=update.message.chat_id, text=summary)

#########################others#########################
'''
Define function requires wordnet
If you are missing the wordnet,
1. run python3 console
2. import nltk
3. nltk.download()
'''
'''
#retrieve_url from google
def retrieve_url(query, number,query_list):
	for url in search(query, stop=number):
		query_list.append(url)
'''
#filter url + remove http to reduce biasness
def urlFilter(lst):
    existingDomains = [];
    newList = []
    for url in lst:
        #print("looking at" + url)
        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        scheme = urlparse(url).scheme
        #print(domain)

        if domain not in existingDomains and scheme != "http":            
            existingDomains.append(domain) 
            newList.append(url)
    return newList

#return definition of words
def define_word(word):
	definitions=""
	meanings=wordnet.synsets(word)
	index=0
	for i in meanings:
		index += 1
		message=str(index)+'. '+i.definition()+'\n'
		definitions=definitions+message

	if not index:
		definitions = "Undefined word: " + word
	return definitions

#print article through url if can request
def print_article(url):
	request = requests.get(url)
	if request.status_code < 400:
		article = NewsPlease.from_url(url)
		if article.title == None and article.text == None:
			return "0"
		else:
		   	#print(article.title)
		   	#print(article.text)
			text = article.tite + "\n" + article.text
			return text
	elif request.status_code == 403 or request.status_code == 401:
		print("The website is not allowing us to access it. . .")
		return "0"
	else:
		print("URL is invalid!")
		return "0"

#########################main#########################
def main():
	# cmd: /start
	start_handler = CommandHandler('start', start)
	dispatcher.add_handler(start_handler)

	#cmd: /google | google
	#google_handler = CommandHandler('google', google, pass_args=True)
	#dispatcher.add_handler(google_handler)

	#cmd: /define | definitions
	define_handler = CommandHandler('define', define, pass_args=True)
	dispatcher.add_handler(define_handler)

	#cmd: /rdisplay | display raw content
	rdisplay_handler = CommandHandler('rdisplay', rdisplay, pass_args=True)
	dispatcher.add_handler(rdisplay_handler)

	#cmd: /sum | summarize 
	summary_handler = CommandHandler('summary', summary, pass_args=True)
	dispatcher.add_handler(summary_handler)

	#cmd: /help | return available functions
	#help_handler = CommandHandler('help', help)
	#dispatcher.add_handler(help_handler)

	#unregistered cmd handler
	unknown_handler = MessageHandler(Filters.command, unknown)
	dispatcher.add_handler(unknown_handler)

	#start bot to receive updates
	updater.start_polling()

if __name__ == '__main__':
    main()
