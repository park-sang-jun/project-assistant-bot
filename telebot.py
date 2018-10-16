# telegram modules
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
import logging

# other modules
#from googlesearch import search  # pip3 install google
from newsplease import NewsPlease  # pip3 install news-please
import requests
from urllib.parse import urlparse
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import wordnet
from gensim.summarization.summarizer import summarize
import time
import re
import spacy # pip3 install -U spacy | python -m spacy download en
import datetime
import fbchat 

#########################telegram#########################
#bot_token = '622777049:AAEmGczXqFjMD1Jkr0n9WOdRydfWIcj_slI'
#bot_token = '662193904:AAHa_jprKD5GI1xU3K5Eqzs2GOYpf4GzHBI'
bot_token = '662878959:AAFSf5bx_bbKH99Bbz-x7SuYPu59R4FY_wA'
bot = telegram.Bot(token=bot_token)
#bot credential
print(bot.get_me())

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
    	bot.send_message(chat_id=update.message.chat_id, text="I didn't understand that command. Try /help for commands")
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
###reminder


#return defintion ***need to implement check word ==1
def define(bot, update, args):
	word = ' '.join(args)
	text_def = define_word(word)
	bot.send_message(chat_id=update.message.chat_id, text=text_def)

#print raw content in the url ***optional
def rdisplay(bot, update, args):
	url_link =  ' '.join(args)
	title, raw_content = extract_article(url_link)
	if(title == "0" and raw_content == "0"):
		bot.send_message(chat_id=update.message.chat_id, text="Unable to access the URL")
	elif(raw_content == "0"):	
		bot.send_message(chat_id=update.message.chat_id, text="No content is read")
	elif(raw_content == None or raw_content == ""):	
		bot.send_message(chat_id=update.message.chat_id, text="Unable to retrive content: Perhaps it's too long")
	else:
		if(title == "0"):
			content = raw_content
		else:
			content = title + "\n" + raw_content
		text_splitter(bot, update, content)

#return available functions
def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Here are the commands you can use: "
								"\n /start: Greetings \n "
								"/define 'word': Get the definition of a word \n"
								"/display 'link': Display the content of the link\n"
								"/mla 'links': Display the APA citation of the links\n"
								"/apa 'links': Display the APA citation of the links\n"
								"/sum 'link': Summarize the content of the link"
								"/csum 'integer' 'link': Summarize the content of the link as near to the interger given\n"
								"/cross 'links': Try cross-referencing links to check potential reliabilty\n"
								"/help to display all commands")


###raw text from url summary
#return summary of the raw text from the link
def summary(bot, update, args):
	url_link =  ' '.join(args)
	title, raw_content = extract_article(url_link)
	if(title == "0" and raw_content == "0"):
		bot.send_message(chat_id=update.message.chat_id, text="Unable to access the URL")
	elif(raw_content == "0"):	
		bot.send_message(chat_id=update.message.chat_id, text="No content is read")
	elif(raw_content == None):	
		bot.send_message(chat_id=update.message.chat_id, text="Unable to retrive content: Perhaps it's too long")
	else:	
		summary = summarize(raw_content)
		analysed_text = "Title: " + title + "\nSummary:\n" + summary
		original_len = count_words(raw_content)
		summarised_len = count_words(summary)
		if(summarised_len>=original_len):
			bot.send_message(chat_id=update.message.chat_id, text="Fail to summarize: Perhaps your content is too short or using too big chunk sentence(s)")
		else:
			#prevent overflooding
			#text_splitter(bot, update, analysed_text)
			bot.send_message(chat_id=update.message.chat_id, text=analysed_text)
			data_text = "\nOriginal Length: " + str(original_len) + "words\nSummary length: " + str(summarised_len) + "words\nProportion from original length:" + str(summarised_len/original_len)
			bot.send_message(chat_id=update.message.chat_id, text=data_text)

#return customised summary of the raw text from the link **first arg as input nearest word limit
def csummary(bot, update, args):
	url_link =  ' '.join(args[1:])
	title, raw_content = extract_article(url_link)
	if(title == "0" and raw_content == "0"):
		bot.send_message(chat_id=update.message.chat_id, text="Unable to access the URL")
	elif(raw_content == "0"):	
		bot.send_message(chat_id=update.message.chat_id, text="No content is read")
	elif(raw_content == None):	
		bot.send_message(chat_id=update.message.chat_id, text="Unable to retrive content: Perhaps it's too long")
	else:	
		summary = summarize(raw_content,0.5,int(args[0]))		
		analysed_text = "Title: " + title + "\nSummary:\n" + summary
		original_len = count_words(raw_content)
		summarised_len = count_words(summary)
		if(summarised_len>=original_len):
			bot.send_message(chat_id=update.message.chat_id, text="Fail to summarize: Perhaps your content is too short or using too big chunk sentence(s)")
		else:
			#prevent overflooding
			#text_splitter(bot, update, analysed_text)
			bot.send_message(chat_id=update.message.chat_id, text=analysed_text)
			data_text = "\nOriginal Length: " + str(original_len) + " words\nSummary length: " + str(summarised_len) + " words\nProportion from original length:" + str(summarised_len/original_len)
			bot.send_message(chat_id=update.message.chat_id, text=data_text)

###citation handling
#return APA style citation
def apa_citation(bot, update, args):
	url_links =  ''.join(args)
	citation_list = apacitationforlist(url_links)
	try:
		bot.send_message(chat_id=update.message.chat_id, text=citation_list)
	except:
		bot.send_message(chat_id=update.message.chat_id, text="Pls try feeding less URL links")	

#return MLA style citation
def mla_citation(bot, update, args):
	url_links =  ''.join(args)
	citation_list = mlacitationforlist(url_links)
	try:
		bot.send_message(chat_id=update.message.chat_id, text=citation_list)
	except:
		bot.send_message(chat_id=update.message.chat_id, text="Pls try feeding less URL links")	

#test and return potential reliable resources and test unreliable sources
def cross(bot, update, args):
	url_links =  ''.join(args)
	url_links = url_links.split(",")
	print(url_links)
	result = analyse_similarity(url_links)
	bot.send_message(chat_id=update.message.chat_id, text=result)

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
def extract_article(url):
	request = requests.get(url)
	if request.status_code < 400:
		article = NewsPlease.from_url(url)
		if article.title == None and article.text == None:
			return "0", "0"
		else:
		   	#print(article.title)
		   	#print(article.text)
			return article.title, article.text
	elif request.status_code == 403 or request.status_code == 401:
		print("The website is not allowing us to access it. . .")
		return "0", "0"
	else:
		print("URL is invalid!")
		return "0", "0"

#return the number of words 
def count_words(words):
	return len(re.findall(r'\w+', words))
###citation
#input and output list of MLA format citations
def mlacitationforlist(multipleurls):
	mylist = multipleurls.split(",")
	length = len(mylist)
	message = ""

	for x in range(length):
		message = message + str(x + 1) + ". "
		myurl = mylist[x]
		request = requests.get(myurl)
		if request.status_code < 400:
			article = NewsPlease.from_url(mylist[x])
			if article.authors == None or article.title == None:
				message += "There is not enough information to make a citation."
				message += "\n"
			else:
				if len(article.authors) != 0:
					message += mlacitation(article.authors[0], article.title, myurl)
					message += "\n"
				else:
					message += "We could not find an author."
					message += "\n"
		else:
			message += "The website you requested is not available or does not exist."
			message += "\n"
	print(message)
	return message


def mlacitation(author, title, url):
    now = datetime.datetime.now()
    today = now.strftime("%d %B %Y")
    name = getmlaname(author)
    return name + '"' + title + '."' + " Web. " + today + ". "

def getmlaname(name):
	words = name.split(" ")
	length = len(words)
	mlaname = words[length - 1] + " "

	for x in range(length - 1):
		mlaname += words[x]
		mlaname += " "
	return(mlaname)

#input and output list of APA format citations
def apacitationforlist(multipleurls):
	mylist = multipleurls.split(",")
	length = len(mylist)
	message = ""

	for x in range(length):
		message = message + str(x + 1) + ". "
		myurl = mylist[x]
		request = requests.get(myurl)
		if request.status_code < 400:
			article = NewsPlease.from_url(mylist[x])
			if article.authors == None or article.title == None:
				message += "There is not enough information to make a citation."
				message += "\n"
			else:
				if len(article.authors) != 0:
					message += apacitation(article.authors[0], article.title, myurl)
					message += "\n"
				else:
					message += "We could not find an author."
					message += "\n"
		else:
			message += "The website you requested is not available or does not exist."
			message += "\n"
	print(message)
	return message


def apacitation(author, title, url):
    now = datetime.datetime.now()
    today = now.strftime("%B %d, %Y")
    name = getapaname(author)
    return name + title + ". Retrieved " + today + ", from " + url


def getapaname(name):
	words = name.split(" ")
	length = len(words)
	mlaname = words[length - 1] + ", "
	for x in range(length - 1):
		mlaname += words[x][0]
		mlaname += ". "

	return(mlaname)

###document comparision
#Jaccard similarity: duplication does not matter
def jaccard_sim(str1, str2): 
	a = set(str1.split()) 
	b = set(str2.split())
	c = a.intersection(b)
	return float(len(c)) / (len(a) + len(b) - len(c))

#cosine similarity: duplication matters | utilizing spacy
def cosine_sim(str1,str2):
	nlp = spacy.load('en')
	doc1 = nlp(str1)
	doc2 = nlp(str2)
	return doc1.similarity(doc2)

#combine jaccard_sim and cosine_sim
def combined_sim(str1, str2):
	#more weight on cosine similarity
	threshold = 0.27
	return threshold*jaccard_sim(str1, str2) + (1-threshold)*cosine_sim(str1,str2)

#algorithm to analyse similarity  
def analyse_similarity(url_links):
	counter = 0
	message = ""
	maximum_no = len(url_links)
	#initialize data list
	data_list = [0 for x in range(maximum_no)] 
	for url in url_links:	
		title, content = extract_article(url)
		if content == "0":
			message = message + "Unable to access: " + url + "\n"
		else:
			data_list[counter] = content
			counter+=1
	#initialize 2d array
	score_list = [[0 for x in range(maximum_no)] for y in range(maximum_no)]
	maximum_score = 0
	for x in range(counter):
		for y in range(counter):
			if score_list[y][x]==0 and x!=y:
 				score_list[x][y] = combined_sim(data_list[x],data_list[y])
			else:
				score_list[x][y] = score_list[y][x]
			#replace max
			if maximum_score < score_list[x][y]:
				maximum_score = score_list[x][y]
	print(score_list)
	
	###store satisfied data for final evaluations
	satisfied_list = [0 for x in range(counter)]
	#configure number to modify if needed	
	min_threshold = 0.8
	max_diff_threshold = 0.3
	tolerable = 0.02
	danger_set = set()
	#in case min is too high	
	if maximum_score < min_threshold:
		min_threshold = maximum_score - tolerable
	for x in range(counter):
		for y in range(counter):
			#keep track of satified_pairs
			if score_list[x][y] > min_threshold:
					satisfied_list[x] += 1

	#considering the idea of maping many to many: multiple complete graphs  
	winner_index = 0
	for x in range(counter):
		if satisfied_list[winner_index] < satisfied_list[x]:
				winner_index = x
	#run through winner array
	message = message + "Threshold used: " + str(min_threshold) + "\nArticles with potential reliability:\n"
	i = 1
	for y in range(counter):
		if score_list[winner_index][y] > min_threshold:
			message = message + "[" +str(i) + "] " +url_links[y] + "\n"
			i+=1
		elif score_list[winner_index][y] < max_diff_threshold:
			danger_set.add(y)

	if len(danger_set) > 0:
		message = message + "!Potentially unreliable source:\n"
		for x in danger_set:
			message = message +  "[" +str(i) + "] " +url_links[x] + "\n"

	return message

###to prevent overflooding to telegram
#split text 
def text_splitter(bot, update, text):
	# Counter to keep track of messages being sent.
	# This is necessary to prevent flooding.
	counter = 0

	# The character limit of a telegram message.
	limit = 4080
	limit_send = 25
	length = len(text)
	div = length / limit + 1

	segment = divide_string(text, limit)

	for i in segment:
		bot.send_message(chat_id=update.message.chat_id, text=i)
		counter += 1
	if counter == limit_send:
		counter = 0
		time.sleep(1)

# Put divideString function here
def divide_string(text, limit):
	lst = []
	sentencelist = sent_tokenize(text)
	counter = 0
	messagetray = ""
	for sentence in sentencelist:
		counter += len(sentence)
	if counter < limit:
		messagetray += sentence
	else:
		lst.append(messagetray)
		messagetray = sentence
		counter = len(sentence)
	lst.append(messagetray)
	return lst

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

	#cmd: /display | display raw content
	rdisplay_handler = CommandHandler('display', rdisplay, pass_args=True)
	dispatcher.add_handler(rdisplay_handler)
	
	#cmd: /sum | summarize raw content from url
	summary_handler = CommandHandler('sum', summary, pass_args=True)
	dispatcher.add_handler(summary_handler)

	#cmd: /csum | summarize raw content from url with nearest word limit as first input
	csummary_handler = CommandHandler('csum', csummary, pass_args=True)
	dispatcher.add_handler(csummary_handler)
	
	#cmd: /apa | construct APA citation style
	apa_handler = CommandHandler('apa', apa_citation, pass_args=True)
	dispatcher.add_handler(apa_handler)

	#cmd: /mla | construct MLA citation style
	mla_handler = CommandHandler('mla', mla_citation, pass_args=True)
	dispatcher.add_handler(mla_handler)
	
	#cmd: /cross | apply cross check using customized combination of algorithms 
	cross_handler = CommandHandler('cross', cross, pass_args=True)
	dispatcher.add_handler(cross_handler)


	#cmd: /help | return available functions
	help_handler = CommandHandler('help', help)
	dispatcher.add_handler(help_handler)

	#unregistered cmd handler
	unknown_handler = MessageHandler(Filters.command, unknown)
	dispatcher.add_handler(unknown_handler)

	#start bot to receive updates
	updater.start_polling()

if __name__ == '__main__':
    main()

