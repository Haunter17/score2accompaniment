from lxml import html
import requests
import urllib
from bs4 import BeautifulSoup
import re
import os

def scrapeMidi(year):
	yearStr = str(year)

	# make a file for the output if it doesn't exists
	outfile = 'e-competition_out/' + yearStr + '/'
	if(not os.path.exists(outfile)):
		os.makedirs(outfile)

	# get the html from the page
	pageStr = 'http://piano-e-competition.com/midi_' + yearStr + '.asp'
	page = requests.get(pageStr)
	htmlString = page.content;
	soup = BeautifulSoup(htmlString, 'html.parser')

	links = soup.find_all('a', href=re.compile('.*\.mid', re.IGNORECASE))
	linkTexts = [link['href'] for link in links]
	# strip off the end of the link (which will be the performer's name along with
	# the number of the performange e.g. sun09) and use that as the new name
	newNames = [linkText[(linkText.rfind('/') + 1):].lower() for linkText in linkTexts]

	# add on the link root, which the hrefs implicitly refer to
	linkRoot = 'http://piano-e-competition.com/' # sometimes extra / but that shouldn't hurt - some don't have the / so need to account for that
	linksWithRoot = [linkRoot + linkText for linkText in linkTexts]

	# download each file
	[urllib.urlretrieve(linksWithRoot[i], outfile + newNames[i]) for i in range(len(linksWithRoot))]

# call our function to scrape the 6 years they have
scrapeMidi(2002)
scrapeMidi(2004)
scrapeMidi(2006)
scrapeMidi(2008)
scrapeMidi(2009)
scrapeMidi(2011)

#tree = html.fromstring(page.content)

#link = tree