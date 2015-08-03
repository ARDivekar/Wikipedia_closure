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
	def __init__(self, wikipedia_url, just_heading=False):
		#	inherit items from the HTML_page_Obj: 
		self._page = HTML_page_Obj(wikipedia_url)	
		self.url=self._page.url

		self.wiki_domain = text_manip.extract_website(self.url)  #gets en.wikipedia.org, etc. in different languages

		#	make the soup of the HTML and get the HTML, prettified:
		soup=self._page.html_soup_and_prettify()
		self.html=self._page.html  #prettified, in UTF-8 format

		#	Get the heading of the Wikipedia page:
		self.heading =text_manip.ensure_UTF8(BeautifulSoup('''%s'''%soup.find("h1", id="firstHeading", class_="firstHeading")).get_text().strip())
		

		if just_heading==False: # prevents a lot of unecessary processing if True

		#	Make a soup of the article html, set the article html:
			article_soup=soup.find("div", id="mw-content-text")  #might come in handy later
			self.article_html=text_manip.ensure_UTF8(article_soup.prettify())
			temp_art_html=self.article_html
			temp_art_html=text_manip.remove_HTML_perfect(html=temp_art_html, tag="div", class_list=["reflist"])
			temp_art_html=text_manip.remove_after(regex='<span.*?id="References"', text=temp_art_html)
			temp_art_html=text_manip.remove_after(regex='<span.*?id="See_also"', text=temp_art_html)
			temp_art_html=text_manip.remove_after(regex='<span.*?id="Further_reading"', text=temp_art_html)
			temp_art_html=text_manip.remove_after(regex='<span.*?id="External_links"', text=temp_art_html)
			article_soup=BeautifulSoup(temp_art_html)

			
		#	Get the links from the article HTML:

			self.article_links=[] # real links, from article
			self.img_links=[] # real direct links, from article
			self.direct_img_to_img_map={}
			self.media_links=[] # real links, from article

			

			
			not_allowed_in_url_from_article=["/wiki/Special:", "/wiki/Template:", "/wiki/Portal:", "/wiki/Wikipedia:", "/wiki/Help:", "redlink=1"]
			
			for link_tag in article_soup.find_all('a'):
				link=link_tag.get('href')

				if link is not None and link[:6]=="/wiki/": #only extracts links to wikipedia 
					allowed_flag=True
					for allowed_test in not_allowed_in_url_from_article:
						if allowed_test in link:
							allowed_flag=False
							break

					if allowed_flag:
						link=text_manip.ensure_UTF8(link)		
						mapped_link="https://"+self.wiki_domain+link

						if link[:11] != "/wiki/File:":
							self.article_links.append(mapped_link)
						else :
							if link[-4:]=='.ogg': #video or audio file
								self.media_links.append(mapped_link)
							else:  # image file
								img_tag=link_tag.img
								# print "\n\n"
								# print "link_tag :",link_tag
								# print "\timg_tag :",img_tag
								if img_tag is not None:
									direct_img_link=img_tag.get('src')
									# print "\t\tdirect_img_link :",direct_img_link
									self.img_links.append(direct_img_link)
									self.direct_img_to_img_map[direct_img_link]=mapped_link


			self.article_links=list(set(self.article_links))
			self.img_links=list(set(self.img_links))
			self.media_links=list(set(self.media_links))


			#	replace the /wiki/ links for actual links. Presetve the old html, and use replaced_html from now on

			self.replaced_html=self.html
			for link_tag in soup.find_all('a'):
				link=link_tag.get('href')
				if link is not None:
				 	if link[:6]=="/wiki/":
						mapped_link="https://"+self.wiki_domain+link
						self.replaced_html=self.replaced_html.replace('href="%s'%link, 'href="%s'%mapped_link)

		
					


	def get_external_styling(self):
		return self._page.get_external_styling()

	def write_to_file(self, folderpath, replaced=True):
		file_path=text_manip.make_file_path(folderpath, filename=self.heading.strip(), extension=".html")
		# print "self.html type: %s"%type(self.html)
		with open(file_path,"w") as output_file:
			if replaced: 
				output_file.write(text_manip.ensure_ASCII(self.replaced_html))
			else: 
				output_file.write(text_manip.ensure_ASCII(self.html))
		return file_path




		


class Wikipedia_img_page_object:
	#the images on wikipedia pages are their own images
	# the urls are of type:	https://<wiki domain>/wiki/File:<image name>.<extension>
	def __init__(self, wikipedia_image_url=None, direct_url=None):
		self.direct_image_link=None
		self.saved_path=None
		self.saved_filename=None

		if direct_url is not None:
			self.direct_image_link=direct_url


		elif wikipedia_image_url is not None:
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


	def download_direct_image(self,folderpath, printing=False):
		if self.direct_image_link is not None:
			link = self.direct_image_link #don'e modify self.direct_image_link
			if link[:6] != "https:":
				link="https:"+link
			self.saved_path=text_manip.get_file( url=link, folderpath=folderpath, printing=False)
			self.saved_filename=self.saved_path.split('/')[-1]
		else:
			download_main_image(folderpath, printing)


	def download_main_image(self,folderpath, printing=False):
		self.saved_path=text_manip.get_file( url=self.main_img_link, folderpath=folderpath, printing=False)
		self.direct_image_link=self.main_img_link.split("https:")[-1]
		self.saved_filename=self.saved_path.split('/')[-1]
		if printing:
			print "\n\n\nself.saved_filename:",self.saved_filename

	def download_largest_image(self, folderpath, printing=False):
		if self.img_px_to_links_map!={}:
			max_index=max(self.img_px_to_links_map)
			max_link=self.img_px_to_links_map[max_index][0]
			self.saved_path=text_manip.get_file( url=max_link, folderpath=folderpath, printing=False) #max(dictionary) == max key in dictionary
			self.direct_image_link=max_link.split("https:")[-1]
			if printing:
				print "self.direct_image_link :",self.direct_image_link
			self.saved_filename=self.saved_path.split('/')[-1]
		else:
			if printing:
				print "ERROR in download_smallest_image: The extraction is empty. Downloading main image instead"
			self.download_main_image(folderpath)


	def download_smallest_image(self, folderpath, printing=False):
		if self.img_px_to_links_map!={}:
			min_index=min(self.img_px_to_links_map)
			min_link=self.img_px_to_links_map[min_index][0]
			self.saved_path=text_manip.get_file( url=min_link, folderpath=folderpath, printing=False )
			self.direct_image_link=min_link.split("https:")[-1]
			if printing:
				print "self.direct_image_link :",self.direct_image_link
			self.saved_filename=self.saved_path.split('/')[-1] 
		else:
			if printing:
				print "ERROR in download_smallest_image: The extraction is empty. Downloading main image instead"
			# self.download_main_image(folderpath)





def download_wiki_page(wiki_link, parent_folder_path, printing=False): 
	#	downloads wikipedia pages and images (in a seperate folder), and links the pages to the images:

	#	make an object of the wiki link:
	wiki_obj=Wiki_page_obj(wiki_link)

	#	make folder:
	imgs_folder_name="imgs_%s"%(wiki_obj.heading)
	imgs_folder_path=text_manip.make_folder_path(parent_folder_path=parent_folder_path, folder_name=imgs_folder_name)
	text_manip.make_directory_if_not_exists(imgs_folder_path, printing=False)

	#	download all images and make replacements to HTML:
	for img_link in wiki_obj.img_links:
		if printing:
			print ""
			print "img_link:",img_link
	#	download image:
		image=Wikipedia_img_page_object(direct_url=img_link)
		image.download_direct_image(imgs_folder_path)


		if image.saved_filename is not None: 
	#	make modification/s to wiki_obj.replaced_html:
			image_filepath=text_manip.make_file_path(folderpath="./"+imgs_folder_name, filename=image.saved_filename, extension="") 

	#	change <a href="____"> to <a href=image_filepath>
			if printing:
				print "image_filepath:",image_filepath
			# old=wiki_obj.replaced_html
			wiki_obj.replaced_html = wiki_obj.replaced_html.replace('href="%s'%wiki_obj.direct_img_to_img_map[img_link], 'href="%s'%image_filepath)
			# if old == wiki_obj.replaced_html:
			# 	print "ERROR: NO replacements of <a> href"

	#	change <img src="____"> to <img src=image_filepath>
			if printing:
				print "image.direct_image_link:",image.direct_image_link
			# old=wiki_obj.replaced_html
			wiki_obj.replaced_html = wiki_obj.replaced_html.replace('src="%s'%image.direct_image_link, 'src="%s'%image_filepath)
			# if old == wiki_obj.replaced_html:
			# 	print "ERROR: NO replacements of <img> src"
						
	#	write replaced_html to file:
	output_wiki_filepath = wiki_obj.write_to_file(parent_folder_path)

	#	return output filepath for later use
	return (output_wiki_filepath, wiki_obj.article_links)




def link_to_style_file(style_file_path, input_html_file_path=None, input_raw_html=None, remove_external_stylesheets=False):
	html=""
	
	if input_raw_html is not None:
		html=input_raw_html
	elif input_html_file_path is not None:
		with open(input_html_file_path, "r") as input_html_file:
			html=input_html_file.read()
	else: 
		print "ERROR: in link_to_style_file, both input_html_file and input_raw_html cannot be None"
		exit(0)


	if remove_external_stylesheets:
		html=text_manip.regex_and_remove(regex='<link.*rel="stylesheet".*?/.*?>', text=html)

	html=html.replace("</head>", '<link rel="stylesheet" href="%s"/></head>'%style_file_path)

	if input_raw_html is not None:
		return html	

	if input_html_file_path is not None:
		with open(input_html_file_path, "w") as output_html_file:
			output_html_file.write(html)
	


def replace_links(folderpath, downloaded_pages, style_file_relative_path):
	html_file_names= text_manip.list_files_in_folder_with_extension(folderpath=folderpath, extension=".html")
	html=""
	for html_file_name in html_file_names:
		filepath=text_manip.make_file_path(folderpath=folderpath, filename=html_file_name, extension="")
		with open(filepath, "r") as html_file:
			html=html_file.read()
			for page_link in downloaded_pages:
				if folderpath.split('/')[-1][:5]=="root_": # if we are dealing with the root html file
					filesystem_link="./lvl%s/%s"%(downloaded_pages[page_link][0], downloaded_pages[page_link][1])
				else:
					if downloaded_pages[page_link][0] == 0: # root
						filesystem_link="../%s"%(downloaded_pages[page_link][1])
					else: filesystem_link="./lvl%s/%s"%(downloaded_pages[page_link][0], downloaded_pages[page_link][1])

				# old = html
				
				html=text_manip.HTML_attribute_content_replace(text=html, attr="href", current=page_link, replace_with=filesystem_link)
				# if html !=old:
					# print "REPLACED: %s----->%s"%(page_link, filesystem_link)	
					
			html_file.close()

		html=link_to_style_file(style_file_path=style_file_relative_path, input_raw_html=html, remove_external_stylesheets=True)
		with open(filepath, "w") as html_file:
			html_file.write(html)
			html_file.close()










def wiki_get_all(root_link, max_depth=1, input_root_folderpath="./", skip_already_downloaded=False, force_redo=False):

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
				- key is the root's real url
				- values are a tuple: (level, file_name)
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
	
	root_wiki_obj=Wiki_page_obj(wikipedia_url=root_link, just_heading=True) #gets only the file and its heading, no further processing

	#	make root_<root.heading> folder inside input_root_folderpath:
	root_folder_name="root_%s"%(root_wiki_obj.heading)
	root_folder_path=text_manip.make_folder_path(parent_folder_path=input_root_folderpath, folder_name=root_folder_name)
	text_manip.make_directory_if_not_exists(root_folder_path, printing=False)

	#	download style file:
	full_style_file_path=text_manip.make_file_path(root_folder_path, "wiki_style",".css")
	with open(full_style_file_path, "w") as style_file:
		style_file.write(text_manip.ensure_ASCII(root_wiki_obj.get_external_styling() ))


	#	download the root and all of its associated images:
	root_download_tuple=download_wiki_page(wiki_link=root_link, parent_folder_path=root_folder_path)
	root_full_html_filepath= root_download_tuple[0]


	#	link to style file:
	relative_root_style_path="./"+full_style_file_path.split('/')[-1]
	# print "relative_root_style_path:",relative_root_style_path
	link_to_style_file(style_file_path=relative_root_style_path, input_html_file_path=root_full_html_filepath)

	relative_style_path="../"+full_style_file_path.split('/')[-1]  # to be used for all other article files
	

	#	make a dict of already downloaded pages. Use the relative paths
	downloaded_pages=defaultdict(lambda:None)
	downloaded_pages[root_link]=(0,root_full_html_filepath.split('/')[-1])

	#	make a dict of pages we must now download
	associated_links=defaultdict(lambda:[])
	associated_links[0]=root_download_tuple[1]


	print "Level 0 (root level) :\n"
	print "\tNumber of pages obtained at this level= "+str(len(downloaded_pages))
	print "\tNumber of links to next level= "+str(len(associated_links[0]))

	# for link in associated_links[0]:
	# 	print link

	for current_level in range(0,max_depth):
		print "\n\nLevel %s :\n"%(current_level+1)
		download_count=0
		existing_downloaded_count=len(downloaded_pages)
		child_folder_name="lvl%s"%(current_level+1)
		child_folder_path=text_manip.make_folder_path(parent_folder_path=root_folder_path, folder_name=child_folder_name)

		if force_redo or text_manip.make_directory_if_not_exists(child_folder_path) :
			# i.e. if the directory does not already exist, do the following; if it does, we skip it
			for associated_link in associated_links[current_level]:
				if downloaded_pages[associated_link] is None:
					download_tuple = download_wiki_page(wiki_link=associated_link, parent_folder_path=child_folder_path)
					# print "\rDone Downloading",
					if current_level+1 != max_depth:
						associated_links[current_level+1].append(download_tuple[1])
					downloaded_pages[associated_link]=( current_level+1, download_tuple[0].split('/')[-1] )
					download_count+=1
					print "\r\tNumber of pages downloaded so far = %s"%download_count,
		if current_level+1 != max_depth:
			associated_links[current_level+1]=list(set(associated_links[current_level+1][0]))


		new_download_count=len(downloaded_pages)
		print "\n\tNumber of pages obtained at this level= "+str(new_download_count-existing_downloaded_count)
		print "\tNumber of links to next level= "+str(len(associated_links[current_level+1]))


	# print "\n\n\nDOWNLOADED PAGES:"
	# for page in downloaded_pages:
	# 	print str(page),"--->",str(downloaded_pages[page])


	#	replace all links with links to the filesystem:
	
	# replace root links:
	style_file_relative_path="./wiki_style.css"
	replace_links(folderpath=root_folder_path, downloaded_pages=downloaded_pages, style_file_relative_path=style_file_relative_path)
	# replace rest of links
	style_file_relative_path="../wiki_style.css"
	for current_level in range(1,max_depth+1):
		lvl_folder=text_manip.make_folder_path(parent_folder_path=root_folder_path, folder_name="lvl%s"%(current_level))
		replace_links(folderpath=lvl_folder, downloaded_pages=downloaded_pages, style_file_relative_path=style_file_relative_path)



