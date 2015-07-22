#hyperlink_fetch
import re
import text_manip
import urllib2
from bs4 import BeautifulSoup



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