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
		self.real_links_to_wiki_article_map={}
		self.img_links=[]
		self.wiki_img_links_to_real_map={}
		self.real_links_to_wiki_img_map={}
		self.media_links=[]
		self.wiki_media_links_to_real_map={}
		self.real_links_to_wiki_media_map={}
		# count=1
		# other_count=1
		print soup.find_all('a')
		''' 
		for img_link_tag in soup.find_all('a'):
			img_link=img_link_tag.get('href')

			if  img_link[:6]=="/wiki/" and "/wiki/Special:" not in img_link and "/wiki/Template:" not in img_link and "/wiki/Portal:" not in img_link and "/wiki/Wikipedia:" not in img_link and "/wiki/Help:" not in img_link:  #only extracts links to wikipedia 
				img_link=text_manip.ensure_UTF8(img_link)		
				mapped_link="https://"+self.wiki_domain+img_link
				if img_link[:11]=="/wiki/File:":
					if link[-4:]=='.ogg': #video or audio file
						self.wiki_media_links_to_real_map[link]=mapped_link
						self.media_links.append(mapped_link)
					else: 
						self.wiki_img_links_to_real_map[link]=mapped_link
						self.img_links.append(mapped_link)
		''' 

		for link_tag in article_soup.find_all('a'):
			link=link_tag.get('href')
			# print count,"]",link
			# count+=1
			
			if  link[:6]=="/wiki/" and "/wiki/Special:" not in link and "/wiki/Template:" not in link and "/wiki/Portal:" not in link and "/wiki/Wikipedia:" not in link and "/wiki/Help:" not in link:  #only extracts links to wikipedia article pages
				# print "\t",other_count,"]",link
				# other_count+=1

				link=text_manip.ensure_UTF8(link)		
				mapped_link="https://"+self.wiki_domain+link

				if link[:11] != "/wiki/File:":
					self.wiki_links_to_real_map[link]=mapped_link
					self.real_links_to_wiki_article_map[mapped_link]=link
					self.article_links.append(mapped_link)
				else :
					if link[-4:]=='.ogg': #video or audio file
						self.wiki_media_links_to_real_map[link]=mapped_link
						self.media_links.append(mapped_link)
						self.real_links_to_wiki_media_map[mapped_link]=link
					else: 
						self.wiki_img_links_to_real_map[link]=mapped_link
						self.img_links.append(mapped_link)
						self.real_links_to_wiki_img_map[mapped_link]=link

		



		self.article_links=list(set(self.article_links))
		self.img_links=list(set(self.img_links))
		self.media_links=list(set(self.media_links))
		# print "\n\n\narticle_links:\n\n"
		# for i in self.article_links:
		# 	print i
		# print "\n\n\nimg_links:\n\n"
		# for i in self.img_links:
		# 	print i
		# print "\n\n\nmedia_links:\n\n"
		# for i in self.media_links:
		# 	print i



		
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
			self.saved_filename=self.saved_path.split('/')[-1]
		else:
			print "ERROR in download_smallest_image: The extraction is empty. Downloading main image instead"
			self.download_main_image(folderpath)


	def download_smallest_image(self, folderpath):
		if self.img_px_to_links_map!={}:
			min_index=min(self.img_px_to_links_map)
			min_link=self.img_px_to_links_map[min_index][0]
			self.saved_path=text_manip.get_file( url=min_link, folderpath=folderpath )
			self.saved_filename=self.saved_path.split('/')[-1] 
		else:
			print "ERROR in download_smallest_image: The extraction is empty. Downloading main image instead"
			self.download_main_image(folderpath)



def download_wiki_page(wiki_link, parent_folder_path): 
	#downloads wikipedia pages and images (in a seperate folder), and links the pages to the images

	wiki_obj=Wiki_page_obj(wiki_link)

	imgs_folder_name="imgs_%s"%(wiki_obj.heading)
	imgs_folder_path=text_manip.make_folder_path(parent_folder_path=parent_folder_path, folder_name=imgs_folder_name)

	text_manip.make_directory_if_not_exists(imgs_folder_path, printing=False)

	img_links_to_filenames_map={}

	for img_link in wiki_obj.img_links:
		image=Wikipedia_img_page_object(img_link)
		image.download_smallest_image(imgs_folder_path)

		if image.saved_filename is not None: # maps wiki_links to saved file links
			img_wiki_link=wiki_obj.real_links_to_wiki_img_map[img_link]
			img_links_to_filenames_map[img_wiki_link]=image.saved_filename

	# Linking logic:
	# Here, we edit the .html of the wiki_object directly, since  we aren't going to use it later



	output_wiki_filepath=wiki_obj.write_to_file(parent_folder_path)









def wiki_get_all(root_link, max_depth=1, input_root_folderpath="./", skip_already_downloaded=False):

	'''	
	Given a root link and the input_root_folderpath, it creates a folder, input_root_folderpath/root_<root.heading>, inside which we have the root link, it's associated images, and folders "lvl1", "lvl2", etc. (i.e. as input_root_folderpath/root_<root.heading>/lvl1/, input_root_folderpath/root_<root.heading>/lvl2/, etc.), into which we must download all the links of the closure, upto "lvl<max_depth>". These are organized sequentially because it decreases the overall path length, than if the folders lvl1, lvl2 etc. were nested inside each other.
	This design also allows you to copy or move the folder root_<root.heading> to any place you desire; it will still work so long as you don't move around the files and folders inside. So, basically, this application, given a root link about a certain topic, downloads all the associated articles related to a certain topic. It captures them in a neat little package that you can then send to someone else, so that they can learn about the topic (this was the main incentive for building this application).



	Salient points to be noted while using the application:

	The application essentially is a breadth-first-search, because a depth-first search on the <strong>INTERNET</strong> can lead you anywhere at all and is inadvisabe, espcially when trying to learn about something which first requires you learn from links to other items, such as Wikipedia and other encyclopediac sites.

	The files and folders that are downloaded form a self-contained ecosystem. The hyperlinks in the html have been modified, so that they now point to each other in the filesystem. eg: an html file in input_root_folderpath/root_<root.heading>/lvl1/ which originally had a link in it's article such as "https://en.wikipedia.org/wiki/IBM", might have the link replaced by ../lvl2/IBM.html, if we downloaded IBM.html to /lvl2/. 
	This allows us to start at any link and browse any link that is downloaded (though you'd probably want to start at the root, since that's why you ran this application).
	Obviously, some links are not downloaded, because of max_depth. The non-downloaded links are those not in the closure of depth max_depth; by definition, these will be found, if at all, in the pages in the last level, i.e. /lvl<max_depth>. The application provides hyperlinks for non-downloaded links, so you may connect to the internet and visit them. 

	Suppose you realize that your max_depth specification was not sufficient. No problem, you don't need to download all the links over again. You just set the skip_already_downloaded flag to True, and the function gets all the links from the last level, upto the new max_depth. 
	Note: because this flag is there to reduce data usage, it will necessarily skip over all the /lvl<depth>/ folders, without checking the actual contents (because tracing the links would require downloading all the pages' HTML all over again). The assumption is that they have been downloaded correctly, and the application will start getting fresh links from the files of /lvl<max_depth>/.

	Styling is another issue. Since this application explores article links which are contained to Wikipedia, the styling is assumed to be the same for all the links. Thus, only the styling of the root is downloaded, and all the files are made to link to that style file. It is possible (and fairly easy) to implement a feature that downloads the styles for each file seperately, but for now it is not implemented.
	This in fact brings me to the most important point of this application: swappability and generalization. This application may have been crafted espcially for Wikipedia, but if you have the patience, it can easily be generalized for any website. That makes it a very powerful data and research tool.






	This function works in two passes:
		Pass1: 
			- start with the root, make a seperate folder for it inside the input_root_folderpath, as input_root_folderpath/root_<root.heading>
			- create a folder inside this as input_root_folderpath/root_<root.heading>/img_<root.heading>
			- download its associated images to input_root_folderpath/root_<root.heading>/img_<root.heading>, modify the root's html to link to these images, then write to file the root's modified html (to input_root_folderpath/root_<root.heading>)
			- append the root's filename and level to a dict, where 
				- key is the root's __wiki__ url
				- values are a tuple: (level, filename)
			- create a level-wise dict of all article_links of that level. For the root, that is just the root's article_links.
			- Do the following for every level (root's level is 0):
				- Create a folder called "lvl"+str(current_level+1) in the input_root_folderpath/root_<root.heading>
				- for each link in this level:
					- check the dictionary if the dict[link] is empty, i.e. (level, filename0 does not exist. If it exists, then we already have the file, so skip to the next child article_link.
					- If the link does not exist, download the link & images to input_root_folderpath/root_<root.heading>/lvl1/, (same format as we did the root).
					- append the child article_link's to dict[link]=(level, filename), i.e. to the dictionary of downloaded links, so that it is not downloaded twice in the future.
					- append this link's child article_links, to the level-order child article_links dict (make sure no repeats


		Pass2: 
			- links all the files to one another.

		We keep this as two seperate passes to reduce redundant data usage (by not downloading links that are already there) at the (minimal) cost of time. 
	'''
	
	root_wiki_obj=Wiki_page_obj(root_link)

	root_folder_name="root_%s"%(root_wiki_obj.heading)
	root_folder_path=text_manip.make_folder_path(parent_folder_path=input_root_folderpath, folder_name=root_folder_name)
	
	text_manip.make_directory_if_not_exists(root_folder_path, printing=False)
	
	root_wiki_obj.write_to_file(root_folder_path)

	style_file_path=text_manip.make_file_path(root_folder_path, "wiki_style",".css")
	with open(style_file_path, "w") as style_file:
		style_file.write(text_manip.ensure_ASCII(root_wiki_obj.get_external_styling() ))


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