#hyperlink_fetch
import re
import text_manip
import urllib2
from bs4 import BeautifulSoup
import text_manip
from collections import defaultdict


'''
This code file, given a directory, a wikipedia page link and the depth you want to go, generates a file hierarchy rooted at the provided directory, with the saved webpage as well. You can just open this webpage and keep browsing deeper and deeper (until you hit the max depth which you have assigned). 
'''




class HTML_page_Obj: #uses urllib2
	
	'''	
	class members (usable after constuctor):
		url : the page url
		short_url : a shortened url (if possible to shorten)
		html : the html of the webpage
		charset : the charset used to encode the HTML
		headers : a dictionary of the other miscellaneous headers which might or might not be present.
	
	class functions:
		__init__ : the constructor that sets all the above variables

		all_hyperlinks : returns a dictionary of all hyperlinks in the html code

		html_soup_and_prettify : prettifies the html by using BeautifulSoup.prettify()

		get_response_object : internal method, not meant for external use

	'''

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
					print "\nTried 3 times. Cannot access url: %s. \nHence, cannot make HTML_page_Obj\n"%page_url
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

			self.html = response.read()  #the actual html
			self.html=text_manip.ensure_UTF8(self.html)
			
			self.html_soup=None
			self.link_dict=None
			self.all_style=None


	def get_response_object(self, page_url):
		if 'http://'  in page_url.lower():
			response =urllib2.urlopen(page_url)
		elif 'https://' in page_url.lower():
			response=urllib2.urlopen('https://'+page_url.split("https://")[-1])
		else:
			response =urllib2.urlopen('http://'+page_url)
		return response



	def all_hyperlinks(self):
		article_soup=BeautifulSoup(self.html)
		self.link_dict={}
		for link_tag in article_soup.find_all('a'):
			self.link_dict[link_tag.contents[0].strip()]=link_tag.get('href')
			# this makes a dict of the form {'article_headline':'article_hyperlink'}
		return self.link_dict	

	def html_soup_and_prettify(self):
		if self.html_soup==None:
			self.html_soup=self.make_soup()
		self.html=text_manip.ensure_UTF8(self.html_soup.prettify())
		return self.html_soup

	def make_soup(self):
		if self.html_soup==None:
			self.html_soup= BeautifulSoup(self.html)
		return self.html_soup


	def write_pretty_to_file(self, folderpath):
		file_name = self.url.split('/')[-1]
		self.html_soup_and_prettify()
		with open(text_manip.make_file_path(folderpath , file_name, ".html") ) as output_html_file:
			output_html_file.write(text_manip.ensure_ASCII (self.html) )
	

	def get_external_styling(self):
		css_soup=BeautifulSoup(self.html)
		stylesheet_links=[]
		self.all_style=""
		for head_link_tag in css_soup.find_all('link', rel="stylesheet"):
			stylesheet_links.append(head_link_tag.get('href'))
		#Note: order of links is important, do not comprimise that
		for link in stylesheet_links:
			css_style_page=HTML_page_Obj(link)
			self.all_style+=css_style_page.html +"\n"
		return self.all_style





class Wiki_page_obj:
	def __init__(self, wikipedia_url):
		self._page = HTML_page_Obj(wikipedia_url)	
		self.url=self._page.url
		self.wiki_domain = text_manip.extract_website(self.url)  #gets en.wikipedia.org, etc. in different languages
		soup=self._page.html_soup_and_prettify()
		self.html=self._page.html  #prettified, in UTF-8 format
		self.heading =text_manip.ensure_UTF8(BeautifulSoup('''%s'''%soup.find("h1", id="firstHeading", class_="firstHeading")).get_text().strip())
		
		# soup=BeautifulSoup(self.html)
		article_soup=soup.find("div", id="mw-content-text")  #might come in handy later
		self.article_html=text_manip.ensure_UTF8(article_soup.prettify())

		self.article_links=[]
		self.wiki_links_to_real_map={}   #maps wiki-links to real hyperlinks, that we can extract using urrlib2
		self.img_links=[]
		self.wiki_img_links_to_real_map={}
		self.media_links=[]
		self.wiki_media_links_to_real_map={}
		# count=1
		# other_count=1
		for link_tag in article_soup.find_all('a'):
			link=link_tag.get('href')
			# print count,"]",link
			# count+=1
			
			if  link[:6]=="/wiki/" and "/wiki/Special:" not in link and "/wiki/Template:" not in link and "/wiki/Portal:" not in link:  #only extracts links to wikipedia article pages
				# print "\t",other_count,"]",link
				# other_count+=1

				link=text_manip.ensure_UTF8(link)		
				mapped_link="https://"+self.wiki_domain+link

				if link[:11]=="/wiki/File:":
					if link[-4:]=='.ogg': #video or audio file
						self.wiki_media_links_to_real_map[link]=mapped_link
						self.media_links.append(mapped_link)
					else: 
						self.wiki_img_links_to_real_map[link]=mapped_link
						self.img_links.append(mapped_link)

				else :
					self.wiki_links_to_real_map[link]=mapped_link
					self.article_links.append(mapped_link)

		self.article_links=list(set(self.article_links))
		self.img_links=list(set(self.img_links))
		self.media_links=list(set(self.media_links))

		

		
		# self.replaced_html=self.html
		# for wiki_link in self.wiki_links_to_real_map:
		# 	re.sub(wiki_link, self.wiki_links_to_real_map[wiki_link], self.replaced_html)


	def get_external_styling(self):
		return self._page.get_external_styling()

	def write_to_file(self, folderpath):
		file_path=text_manip.make_file_path(folderpath, filename=self.heading.strip(), extension=".html")
		# print "self.html type: %s"%type(self.html)
		with open(file_path,"w") as output_file:
			output_file.write(text_manip.ensure_ASCII(self.html))
		return file_path




		






		'''this makes a dict of the form {'article_heading':['article_hyperlink1', 'article_hyperlink2', ....]}
			The assumption is that wikipedia article headings are unique, but several links redirect to the same article.
			Eg: "Andrew Grove" and "Andy Grove" redirect to the same article about the Intel co-founder.
			This assumption is justified, because things like https://en.wikipedia.org/wiki/Thread_(computing) 
			have the heading "Thread (computing)", and things like https://en.wikipedia.org/wiki/Threads_(Stargate_SG-1), 
			have the heading "Threads (Stargate SG-1)".
		'''



class Wikipedia_img_page_object:
	#the images on wikipedia pages are their own images
	# the urls are of type:	https://<wiki domain>/wiki/File:<image name>.<extension>
	def __init__(self, wikipedia_image_url):
		img_page=HTML_page_Obj(wikipedia_image_url)
		img_soup=img_page.make_soup()
		# print img_soup.find('div', _class="mw-filepage-resolutioninfo")

		self.main_img_link=img_soup.find('div', class_="fullMedia").find('a', class_="internal").get('href')
		if self.main_img_link[:9]=="//upload.":
			self.main_img_link="https:"+self.main_img_link
		

		img_links_soup=img_soup.find("div", class_="mw-filepage-resolutioninfo")
		self.img_px_to_links_map={} #maps the product of height and width to tuples of pixel dimensions and their links
		for img_link in img_links_soup.find_all('a'):
			actual_link=img_link.get('href')

			if actual_link[:9]=="//upload.":
				actual_link="https:"+actual_link

			img_link_text= text_manip.ensure_UTF8(re.sub(",","", img_link.get_text()) )
			# print text_manip.ensure_ASCII("\n\nimg_link_text: %s"%img_link_text)
			img_dimensions = re.findall('\d+', img_link_text)
			width=int(img_dimensions[0])
			height=int(img_dimensions[1])
			if len(img_dimensions)==2:
				self.img_px_to_links_map[width*height]=( actual_link, width, height ) #does mapping
			else: print "Cannot use image %s, which is at %s with dimensions %s"%(wikipedia_image_url, img_link.get('href'), img_dimensions)

		self.saved_path=None
		self.saved_filename=None


	def download_main_image(self,folderpath):
		self.saved_path=text_manip.get_file( url=self.main_img_link, folderpath=folderpath )
		self.saved_filename=self.saved_path.split('/')[-1]
		print "\n\n\nself.saved_filename:",self.saved_filename

	def download_largest_image(self, folderpath):
		if self.img_px_to_links_map!={}:
			max_index=max(self.img_px_to_links_map)
			max_link=self.img_px_to_links_map[max_index][0]
			self.saved_path=text_manip.get_file( url=max_link, folderpath=folderpath ) #max(dictionary) == max key in dictionary
		else:
			print "ERROR in download_smallest_image: The extraction is empty. Downloading main image instead"
			self.download_main_image(folderpath)


	def download_smallest_image(self, folderpath):
		if self.img_px_to_links_map!={}:
			min_index=min(self.img_px_to_links_map)
			min_link=self.img_px_to_links_map[min_index][0]
			self.saved_path=text_manip.get_file( url=min_link, folderpath=folderpath ) 
		else:
			print "ERROR in download_smallest_image: The extraction is empty. Downloading main image instead"
			self.download_main_image(folderpath)





def wiki_get_all(root_link, max_depth=1, input_root_folderpath="./"):
	
	root_wiki_obj=Wiki_page_obj(root_link)

	root_folder_name="root_%s"%(root_wiki_obj.heading)
	root_folder_path=text_manip.make_folder_path(parent_folder_path=input_root_folderpath, folder_name=root_folder_name)
	
	text_manip.make_directory_if_not_exists(root_folder_path, printing=False)
	
	root_wiki_obj.write_to_file(root_folder_path)

	style_file_path=text_manip.make_file_path(root_folder_path, "wiki_style",".css")
	# with open(style_file_path, "w") as style_file:
	# 	style_file.write(text_manip.ensure_ASCII(root_wiki_obj.get_external_styling() ))


	root_imgs_folder_name="imgs_%s"%(root_wiki_obj.heading)
	root_imgs_folder_path=text_manip.make_folder_path(parent_folder_path=root_folder_path, folder_name=root_imgs_folder_name)

	text_manip.make_directory_if_not_exists(root_imgs_folder_path, printing=False)

	

	for img_link in root_wiki_obj.img_links:
		image=Wikipedia_img_page_object(img_link)
		image.download_smallest_image(root_imgs_folder_path)

	global_pages={}
	# global_pages[link]=(<real url>, <depth>, <filename>) <---we use the depth and filename to link to the file.

	levels_links={} # a dictionary of lists of all /wiki/ links at that level
	levels_links[1]=root_link





		



	










	
	
	

	



	





"""
def fetch_wikipedia_pages(filepath, link, depth=1, is_root=True):

	heading = re.search('''(?<=/wiki/)(?!Portal:)(?!Help:).*''', link, re.I)
	heading=heading.group(0).strip()
	print "\n\n\n\n\n\t\t\tCurrently processing:%s"%heading
	#heading is the file path, gotten from the link, not the html 

	html=text_manip.get_html(link)
	soup = BeautifulSoup(html)
	html = soup.prettify().encode("utf-8",'ignore')
	fileout_path=""
	if is_root==True:
		article_title=re.search('''(?<=<h1 class="firstHeading" id="firstHeading" lang="en">\n).*''', html, re.I)
		article_title=article_title.group(0)
		article_title=article_title.strip()
		fileout_path=filepath+"/%s.html"%article_title
	else:
		fileout_path=filepath+"/%s.html"%heading
	fileout=open(fileout_path, "w+")
	fileout.write(html)
	fileout.close()

	html_replaced_links=html
	if(depth>0):

		article = re.search('''<div class="mw-content-ltr" dir="ltr" id="mw-content-text" lang="en">(\n.*)+((<span class="mw-headline" id="References">)|(<span class="mw-headline" id="External_links">))''', html, re.I)
		if (article==None):
			print "Cannot parse "+link
			exit(0)
		article=article.group(0)
	
		hyperlink_pattern = re.compile(r'(?<=<a href=")/wiki/(?!Portal:)(?!Help:).*?(?=")') 
		#the pattern for recognizing hyperlinks in the article, which we must fetch

		print "\t\t\tQueued for processing:\n"
		hyperlinks=[]
		base_website_url="http://en.wikipedia.org"
		j=1
		for hlink in re.findall(hyperlink_pattern, article):	
			print "\t\t\t"+str(j)+".  "+base_website_url+hlink
			hyperlinks.append(base_website_url+hlink)
			j+=1

		#hyperlinks[] now contains the deeper links which we must fetch recursively
		for i in hyperlinks:
			hyp_heading=fetch_wikipedia_pages(filepath,i, depth=depth-1, is_root=False) 
			#ensures that before we link an article to the file, the file actually exists

			regex='(?<=<a href=")/wiki/(?!Portal:)(?!Help:)%s(?=")'%hyp_heading
			print "\tRegex = "+regex

			fileout_path_hyp=hyp_heading+".html"
			print "\tFile_out_path_hyp = "+fileout_path_hyp
			html_replaced_links= re.sub(regex, fileout_path_hyp, html_replaced_links)
			fileout=open(fileout_path, "w+")
			fileout.write(html_replaced_links)	
			fileout.close()
			#writing to the file multiple times ensures that if we encounter an error, we still get the links we have saved.	
	
	return heading






def fetch_wikipedia_pages_sort_of_working(filepath, link, depth=1):

	html=text_manip.get_html(link)
	soup = BeautifulSoup(html)
	html = soup.prettify().encode("utf-8",'ignore')
	heading=re.search('''(?<=<h1 class="firstHeading" id="firstHeading" lang="en">\n).*''', html, re.I)
	# heading = re.search('''/wiki/(?!Portal:)(?!Help:).*''', link, re.I)
	heading=heading.group(0).strip()

	fileout_path=filepath+"/"+heading+".html"
	fileout=open(fileout_path, "w+")
	fileout.write(html)

	html_replaced_links=html

	article = re.search('''<div class="mw-content-ltr" dir="ltr" id="mw-content-text" lang="en">(\n.*)+((<span class="mw-headline" id="References">)|(<span class="mw-headline" id="External_links">))''', html, re.I)
	if (article==None):
		print "Cannot parse "+link
		exit(0)
	article=article.group(0)
	print "\n\n\n\n\n\t\t\tCurrently processing:%s"%heading
	if(depth>0):
		pattern = re.compile(r'(?<=<a href=")/wiki/(?!Portal:)(?!Help:).*?(?=")')
		hyperlinks=[]
		website="http://en.wikipedia.org"
		print "\t\t\tQueued for processing:\n"
		for hlink in re.findall(pattern, article):	
			print "\t\t\t"+website+hlink
			hyperlinks.append(website+hlink)
		for i in hyperlinks:
			hyp_heading=fetch_wikipedia_pages(filepath,i, depth-1)
			hyp_heading_underscore=re.sub(" ","_",hyp_heading)
			regex='(?<=<a href=")/wiki/(?!Portal:)(?!Help:)%s(?=")'%hyp_heading_underscore
			print "\tRegex = "+regex
			# fileout_path_hyp=filepath+"/"+hyp_heading+".html"
			fileout_path_hyp=hyp_heading+".html"
			print "\tFile_out_path_hyp = "+fileout_path_hyp
			html_replaced_links= re.sub(regex, fileout_path_hyp, html_replaced_links)


	fileout_path=filepath+"/"+heading+".html"
	fileout=open(fileout_path, "w+")
	fileout.write(html_replaced_links)	
		
	return heading











def fetch_wikipedia_pages_working(filepath, link, depth=1):

	html=text_manip.get_html(link)
	soup = BeautifulSoup(html)
	html = soup.prettify().encode("utf-8",'ignore')
	heading=re.search('''(?<=<h1 class="firstHeading" id="firstHeading" lang="en">\n).*''', html, re.I)
	heading=heading.group(0).strip()
	
	fileout_path=filepath+"/"+heading+".html"
	fileout=open(fileout_path, "w+")
	fileout.write(html)
	article = re.search('''<div class="mw-content-ltr" dir="ltr" id="mw-content-text" lang="en">(\n.*)+((<span class="mw-headline" id="References">)|(<span class="mw-headline" id="External_links">))''', html, re.I)
	if (article==None):
		print "Cannot parse "+link
		exit(0)
	article=article.group(0)
	print "\n\n\n\n\n\t\t\tCurrently processing:%s"%heading
	if(depth>0):
		pattern = re.compile(r'(?<=<a href="/wiki/)(?!Portal:)(?!Help:).*?(?=")')
		hyperlinks=[]
		website="http://en.wikipedia.org/wiki/"
		print "\t\t\tQueued for processing:\n"
		j=1
		for hlink in re.findall(pattern, article):	
			print "\t\t\t"+str(j)+".\t"+website+hlink
			hyperlinks.append(website+hlink)
			j+=1
		for i in hyperlinks:
			fetch_wikipedia_pages(filepath,i, depth-1)




fetch_wikipedia_pages(filepath="F:\Workspaces\Python\Wikipedia", link="http://en.wikipedia.org/wiki/Natural_language_processing")
"""