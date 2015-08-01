# -*- coding: utf-8 -*-
#text_manip.py
import re
import urllib2
import unicodedata
from bs4 import BeautifulSoup
import nltk
from xgoogle.search import GoogleSearch, SearchError
import os
import random

def ensure_UTF8(string_data, encoding='UTF-8'):
	if type(string_data) is unicode:
		return string_data
	else: 
		return unicode(string_data,'utf-8')

def ensure_ASCII(string_data): #to write to file
	return ensure_UTF8(string_data).encode('ascii', 'replace')
	



# def convert_encoding(data, new_coding = 'UTF-8'):
#   encoding = cchardet.detect(data)['encoding']

#   if new_coding.upper() != encoding.upper():
#     data = data.decode(encoding, data).encode(new_coding)

#   return data


def rectify_folder_path(folderpath):
	if folderpath[-1]!= "\\" and folderpath[-1]!= "/":
		folderpath+="/"
	return folderpath

def make_directory_if_not_exists(folderpath, printing=True):
	folderpath=rectify_folder_path(folderpath)
	if not os.path.exists(folderpath):
		os.makedirs(folderpath)
	else:
		if printing:
			print "\nThe folder %s already exists."%(folderpath)



def get_files_in_folder(folderpath):
	#just returns the filenames
	folderpath=rectify_folder_path(folderpath)
	return [ f for f in os.listdir(folderpath) if os.path.isfile(folderpath+"/"+f) ]  


def make_google_search_query(necessary_topic_list=None, topic_list=None, site_list=None, daterange_from=None, daterange_to=None):
	if necessary_topic_list==None and topic_list==None: 
		return None 

	query=""
	if necessary_topic_list!=None:
		for topic in necessary_topic_list:
			query+='"%s" '%topic
	if topic_list!=None:
		for topic in topic_list:
			query+='"%s" '%topic
	
	if site_list!=None:
		query += " site:"+site_list[0]
		for i in range(1,len(site_list)):
			query+=" | site:"+site_list[i]
	if daterange_from!=None and daterange_to!=None and daterange_from<=daterange_to:
		query+=" daterange:%s-%s"%(daterange_from, daterange_to)
	
	return query	
	# '"Infosys" site:financialexpress.com/article/ | site:business-standard.com/article | site:livemint.com/companies | site:timesofindia.indiatimes.com/business/india-business/ '



def make_file_path(folderpath, filename, extension):
	if folderpath[-1]!= "\\" and folderpath[-1]!= "/":
		folderpath+="/"

	return folderpath+filename[:255-len(folderpath)-len(extension)]+extension # Windows only allows filepaths upto 260 characters. I'm using 255 to be on the safe side.\


def make_folder_path(parent_folder_path, folder_name, char_buffer=30):
	#we make a buffer to allow files with at least this length
	parent_folder_path=rectify_folder_path(parent_folder_path)
	folder_name=rectify_folder_path(folder_name)
	if len(parent_folder_path)-char_buffer>=255: #max filepath length 
		print "\nERROR: cannot make folder, exceeds max OS filepath length.\n"
		return None
	else:
		return (parent_folder_path+folder_name)[:259-char_buffer]



def make_filename(input_line):
	line=re.sub("\:"," -",input_line)
	line=re.sub("\?","",line)
	# line=re.sub("\\\\","-",line)
	line=re.sub("/","-",line)
	line=re.sub('"',"'",line)
	line=re.sub("\|",";",line)
	line=re.sub("<","&lt;",line)
	line=re.sub(">","&gt;",line)
	line=re.sub("\\n","",line)
	return line
	

def to_julian_date(year, month, day): 
	try:
		if(year==int(year)): 
			Y=int(year)
		if(month==int(month)): 
			M=int(month)
		if(day==int(day)): 
			D=int(day)
	except Exception:
		print "Invalid date input."
		return None
	if M<1 or M>12:
		print "Invalid date input."
		return None
	if D<1 or ((M==1 and D>31) or (M==2 and D>29) or (M==3 and D>31) or (M==4and D>30) or (M==5 and D>31) or (M==6 and D>31) or (M==7 and D>31) or (M==8 and D>31) or (M==9 and D>30) or (M==10 and D>31) or (M==11 and D>30) or (M==12 and D>31)):
		print "Invalid date input."
		return None

	C = 2 - (Y/100) + (Y/400)
	E = 365.25*(Y+4716)
	F = 30.6001*(M+1)
	julian_date= int(round(C+D+E+F-1524.5))
	return julian_date


def date_split(input_date): 
	#date must be in YY-MM-DD format
	date=input_date.split('-')
	try:
		Y=int(date[0])
		M=int(date[1])
		D=int(date[2])
	except Exception:
		print "Invalid date input."
		return None
	if M<1 or M>12:
		print "Invalid date input."
		return None
	if D<1 or ((M==1 and D>31) or (M==2 and D>29) or (M==3 and D>31) or (M==4and D>30) or (M==5 and D>31) or (M==6 and D>31) or (M==7 and D>31) or (M==8 and D>31) or (M==9 and D>30) or (M==10 and D>31) or (M==11 and D>30) or (M==12 and D>31)):
		print "Invalid date input."
		return None
	return (Y,M,D)



def useless_function():
	i=0
	while i<10000:
		# time.sleep(0.01)
		print "\r%d"%i,    # \r is the carraige return character.
		# \r moves the cursor to the beginning of the line and then keeps outputting characters as normal.
		i+=1
		if random.randrange(100000) == 0: 
			break
		if i==9999:
			i=0
	return i
	


def num_to_words(num):
	if num>=pow(10,12):
		return str(float(num)/pow(10,12))+" trillion"
	elif num>=pow(10,6):
		return str(float(num)/pow(10,9))+" million"
	elif num>=pow(10,3):
		return str(float(num)/pow(10,3))+" thousand"


def google_search_redirect(random_text): #throws Google off the scent
	print "\tRedirect...."
	try:
		search_query=article_supersplit(random_text)
		search_query=search_query[random.randrange(0, len(search_query))]
		search_query=search_query[random.randrange(0, len(search_query))]
		search_query=remove_empty_from_list(search_query)
		search_query=search_query[:random.randrange(3,4+len(search_query)%6)]
		search_query=' '.join(search_query)
	except Exception: 
		search_query=random_text[:10]
	search_query=re.sub("\.","",search_query)
	search_query=re.sub(",","",search_query)
	search_query=re.sub("`","",search_query)
	google_search_results(search_query=search_query, number_of_results=5)




def google_search_results(search_query, wait=40, number_of_results=10, encode=True):
	''' DO NOT MESS WITH THIS IT IS PERFECT FOR NOW'''
	# gets AT LEAST number_of_results results
	# don't query too fast or Google will ban your IP
	# for this purpose, I have added the variable max_result_size
	print search_query
	try:
		max_result_size=10 #don't change it from this: the standard of 10 seems the least suspicious to google
		gs = GoogleSearch(search_query, random_agent=True) # does not actually search
		gs.results_per_page = max_result_size
		
		gs.page=0
		times_tried=0
		results=[]
		prev=0
		# print "getting results:"	
		while len(results) < number_of_results:
			prev=len(results)
			times_tried+=1
			time.sleep(random.uniform(0.5*wait, 1.5*wait))
			results+=gs.get_results() # Actual search and extraction of results.
			print "\rtimes_tried: %s\tlen(results): %s\tpage_number: %s"%(times_tried, len(results), gs.page),
		print "\n"

		# We now have a list of SearchResult objects, called 'results'.
		# A SearchResult object has three attributes -- "title", "desc", and "url".
		# They are Unicode strings, so do a proper encoding before outputting them. (done below)
		if encode:
			for i in range (0, len(results)):
				results[i].title=results[i].title.encode("utf8", "ignore")
				results[i].desc=results[i].desc.encode("utf8", "ignore")
				results[i].url=results[i].url
		# random.shuffle(results)

	except SearchError, e:
		print "Search failed:\t%s" % e

	return results






def data_structure_similarity(a,b):
	if len(a) < len(b):
		t=a
		a=b
		b=t
	#they must be sets
	percent=len(list(set(a) & set(b)))
	percent=float(percent)/float(len(set(b)))
	percent=percent*100
	print "\n%s elements of B are also in A are: "%percent

def string_list_merge(str_list, merge_with=" "):
	# merges a list of strings into one string
	return merge_with.join(str_list)
	# output_string=str_list[0]
	# if len(str_list)>1:
	# 	for i in range(1,len(str_list)):
	# 		output_string+=(merge_with+str_list[i])
	# return output_string


def try_dict_index(dictionary, index):
	try: 
		return dictionary[index]
	except Exception: 
		print "ERROR on accessing index '%s': No such dictionary index"%(index)
		return None



def remove_empty_from_list(pylist):
	length=len(pylist)
	if length==0:
		return None
	removed=0
	i=0
	while i < length-removed:
		# print "i=%s, pylist[i]=%s, len(pylist)=%s, removed=%s"%(i,pylist[i],len(pylist),removed)
		if pylist[i]==None or pylist[i]=="" or pylist[i]==[] or pylist[i]=={} or pylist[i]==():
			del pylist[i]
			removed+=1
			i-=1
		i+=1

	
	return pylist
			 	#not necessary...reference pylist is a reference to an object. 
				#Since pylist is a mutable object, changes are saved 
				#but I kept doing list=remove_empty_from_list(list)
				


def remove_empty_from_dict(pydict):
	new_dict={}
	for i in pydict:
		if pydict[i]!=None and pydict[i]!="" and pydict[i]!=[] and pydict[i]!={} and pydict[i]!=():
			new_dict[i]=pydict[i]
	return new_dict



def extract_website(url):
	website=""
	if "http://" in url or "https://" in url:
		website= url.split('/')[2]
	else: website= url.split('/')[0] 

	if "www." in website:
		website = website.split("www.")[1]
	return website


def extract_links(article): #extracts links from HTML code
	article_soup=BeautifulSoup(article)
	link_dict={}
	for link_tag in article_soup.find_all('a'):
		link_dict[link_tag.contents[0].strip()]=link_tag.get('href')
		# this makes a dict of the form {'article_heading':'article_hyperlink'}
	return link_dict
	
	

def properly_encode(article, input_encoding="UTF-8"):
	
	article=article.decode(input_encoding)
	article = article.replace(u"\u2022", "*")
	# article = article.replace(u"\u2022", "*")
	# print article.encode('utf-8')
	article=unicodedata.normalize('NFKD', article).encode('ascii','ignore')
	
	# article = article.encode('unicode_escape')
	# article=article.encode('ascii')
	# print article
	return article

def shorten_whitespace(str): 	
	# removes streches of whitespace 
								# appearing before, after and inside a string, 
								# replacing it with two newline characters.
	str=str.strip()
	return re.sub("([ ]*(\\n)+[ ]*)+","\\n\\n",str)

def remove_HTML_tags(str): #removes html tags completely from a string, not their contents
	str=re.sub("<br>","\n", str)
	return re.sub("<.*?>","", str)
	

def remove_HTML(str, tag, attributes=""): #removed everything inside all occurences of that html tag
	regex='''(<%s[ ]*%s.*?>)(\\n*.*?)*?(</%s>)'''%(tag,attributes,tag)
	# print regex
	return re.sub(regex,"",str)

def remove_HTML_except(str, tag): #removed everything inside all html tags, except a particular HTML tag
	return re.sub('''(<%s.*?>)(\\n.*?)*?(</%s>)'''%(tag,tag),"",str)


def remove_php_from_HTML(str): #removes php code completely from a string
	return re.sub("<?php.*?>","", str)



def get_charset(page_url): #gets encoding of the 
	response=None
	if 'http://'  in page_url.lower():
		response =urllib2.urlopen(page_url)
	elif 'https://' in page_url.lower():
		response=urllib2.urlopen('https://'+page_url.split("https://")[-1])
	else:
		response =urllib2.urlopen('http://'+page_url)
	charset = response.headers.getparam('charset')
	return charset


def get_html(page_url):
	#get_html: because typing a few lines of code is way too hard
	response=None
	if 'http://'  in page_url.lower():
		response =urllib2.urlopen(page_url)
	elif 'https://' in page_url.lower():
		response=urllib2.urlopen('https://'+page_url.split("https://")[-1])
	else:
		response =urllib2.urlopen('http://'+page_url)
	
	html = response.read()
	return html


class HTML_page_Obj:
	def __init__(self, page_url):
		response=None
		self.url=None
		try: 
			response=self.get_response_object(page_url)
		except Exception:
			try:
				# time.sleep(1)
				response=self.get_response_object(page_url)
			except Exception:
				try:
					# time.sleep(5)
					response=self.get_response_object(page_url)
				except Exception:
					print "\nTried 3 times. Cannot access url: %s. \nHence, cannot make HTML_page_Obj"%page_url
		if response != None:

			self.url=page_url
			try:
				self.short_url=response.headers.getparam('Link')
			except Exception:
				self.short_url=""
			self.charset = response.headers.getparam('charset')
			self.headers={'charset':self.charset}
			for i in response.headers:
				self.headers[i]=response.headers[i].split(';')[0]

			self.html = response.read()
		

	def all_hyperlinks(self):
		article_soup=BeautifulSoup(self.html)
		self.link_dict={}
		for link_tag in article_soup.find_all('a'):
			self.link_dict[link_tag.contents[0].strip()]=link_tag.get('href')
			# this makes a dict of the form {'article_heading':'article_hyperlink'}
		return self.link_dict	

	def make_soup(self):
		html_soup= BeautifulSoup(self.html)
		self.html=html_soup.prettify(encoding=self.charset)
		return html_soup

	def get_response_object(self, page_url):
		if 'http://'  in page_url.lower():
			response =urllib2.urlopen(page_url)
		elif 'https://' in page_url.lower():
			response=urllib2.urlopen('https://'+page_url.split("https://")[-1])
		else:
			response =urllib2.urlopen('http://'+page_url)
		return response



def bytes_to_other(bytes):
	KB=pow(2,10)
	# print KB
	if bytes < KB:
		return str(bytes)+" Bytes"
	MB = pow(2,20)
	# print MB
	if bytes>KB and bytes<MB:
		return str(bytes/KB)+" KB"
	GB = pow(2,30)
	# print GB
	if bytes>MB and bytes<GB:
		return str(bytes/MB)+" MB"
	if bytes>GB: 
		return str(bytes/GB)+" GB"



def get_file(url, folderpath="./", block_sz=8192, confirm=False): 
	#does not work on html files
	print "Attempting to download from URL : %s"%url
	file_name = url.split('/')[-1] #get the last thing seperated by a '/'
	u = urllib2.urlopen(url)

	folderpath=rectify_folder_path(folderpath)

	fileout_path=ensure_ASCII(folderpath+file_name)
	# print "\n\nfileout_path:  %s\n\n"%fileout_path

	try: 
		meta = u.info()
		file_size = int(meta.getheaders("Content-Length")[0])
		if (confirm):
			print "File size is %s , do you want to continue?"%bytes_to_other(file_size)
			y_or_n= raw_input("\nEnter y or n\n\t>")
			if y_or_n.lower() != 'y':
				exit(0)

		print "Downloading: %s\nBytes: %s" % (file_name, file_size)
		print "Writing to: %s"%fileout_path

		f = open(fileout_path, 'wb')
		file_size_dl = 0
		while True:
		    buffer = u.read(block_sz)
		    if not buffer:
		        break

		    file_size_dl += len(buffer)
		    f.write(buffer)
		    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
		    status = status + chr(8)*(len(status)+1)
		    print status,

		f.close()
	except Exception:
		f = open(fileout_path, 'wb')
		f.write(u.read())
		f.close()
		print "Done downloading : %s"%url
	print ""
	return fileout_path


def properly_format(article):
	
	i=0
	article=article.strip()
	# print article, "\n\n\n\n\n\n\n\n\n\n\n"
	length = len(article)
	output_article = ""#+"\t"
	while i<length:
		if article[i]==";" and article[i+1]=='\n':
			i+=1
			continue
		elif article[i]=='\n':
			if output_article[len(output_article)-1]=='\n':
				i+=1
				continue
			else: output_article+='\n'

		elif article[i]=='\t': #this does not seem to be working
			if output_article[-1]=='\t':
				i+=1; 
				continue
			# elif output_article[-1]=='\n':
				# output_article+='\t'
				# output_article=output_article


		elif article[i]==" ":
			if output_article[len(output_article)-1]=='\n' or output_article[len(output_article)-1]=='\t':
				i+=1
				continue
			else: output_article+=article[i]
		else: output_article+=article[i]

		i+=1
	output_article= re.sub("&amp;","&",output_article)
	output_article= re.sub("&gt;",">",output_article)
	return output_article



def article_supersplit(article):
	article=properly_format(article)
	'''	
	This function splits a "properly_format"ed article, 
	and returns the variable 'text'.

	'text' is structured as:
		a list of paragraphs,
			where each paragraph is a list of sentences,
				where each sentence is a list of words, punctuations as seperate words.
	'''
	text=article.split("\n") #get paragraphs
	text = remove_empty_from_list(text)
	for i in range(0,len(text)):
		text[i]=text[i].split(". ") #get sentences
		text[i]=remove_empty_from_list(text[i])
		for j in range(0,len(text[i])):
			try:
				# print "\ntrying NLTK"
				text[i][j]=nltk.word_tokenize(text[i][j])
				# print "\nNLTK success"
			except Exception:
				# print "\n\nNLTK failed. Going for backup..."
				text[i][j]=text[i][j].split(" ") #get words
				text[i][j]+="."
				for k in range(0,len(text[i][j])):
					text[i][j][k]=re.sub(",", "", text[i][j][k])
					text[i][j][k]=re.sub(";", "", text[i][j][k])
					text[i][j][k]=re.sub("\(", "", text[i][j][k])
					text[i][j][k]=re.sub("\)", "", text[i][j][k])
					text[i][j][k]=re.sub("\[", "", text[i][j][k])
					text[i][j][k]=re.sub("\]", "", text[i][j][k])
					text[i][j][k]=re.sub("\{", "", text[i][j][k])
					text[i][j][k]=re.sub("\}", "", text[i][j][k])

				if text[i][-1][-2][-1] == ".":
					print text[i][-1]
					text[i][-1][-2]=re.sub(".*", text[i][-1][-2][:-1], text[i][-1][-2])
				# print "\nreplaced: %s\n\n\n"%text[i][-1]
			finally:
				text[i][j]=remove_empty_from_list(text[i][j])

	return text
	

