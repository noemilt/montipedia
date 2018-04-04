import urllib.request
import re
import time
import string
from bs4 import BeautifulSoup
from dateutil import parser
from geopy.geocoders import Yandex
#from reason_classifier import ReasonClassifier

class MontipediaScraper():

	def __init__(self):
		self.url = "http://www.montipedia.com"
		self.subdomain = "/montanas/"
		self.data = []
#		self.geolocator = Yandex()
#		self.reason_classifier = (
#			ReasonClassifier("../train/summary_train_set.txt"))

	def __download_html(self, url):
#PENDENT: cal fer proves per a que no peti amb la Ñ. He trobat aquesta info sobre parse https://docs.python.org/dev/library/urllib.parse.html#urllib.parse.quote
		url=urllib.parse.unquote(url, encoding='utf-8')  
		response = urllib.request.urlopen(url)
#		html=response.read().decode(charset)
		html = response.read()
		return html

	def __get_montana_links(self, montana):
		pag_links = []
		montana_links = []
		pag_links.append(montana)

		html = self.__download_html(self.url + montana)

		bs = BeautifulSoup(html, 'html.parser')

		divpag = bs.find("div", {"id": "paginador"})
		if divpag:
			aas = divpag.findAll('a')			
			for a in aas:
				if a.name == 'a':
					href = a['href']
					pag_links.append(href)
					print("pag_links: " + href)
			pag_links.pop()

		for i in range(len(pag_links)):
			pag = pag_links[i]
			print("pagina: " + pag)
			html = self.__download_html(self.url + pag)
			bs = BeautifulSoup(html, 'html.parser')
			divact = bs.find("div", {"id": "montanas"})
			ul1 = divact.find("ul", {"id": "abc"})
			ul2 = ul1.find_next_sibling('ul')
			lis = ul2.findAll("li")
		
			for li in lis:
				# Has this <li> element an <a> child?
				a = li.next_element
				if a.name == 'a':
					href = a['href']
					# Preppend '/' if needed
#					if href[0] != '/':
#						href = '/' + href
					# Extract year
					#year = re.search('[0-9]{4}', href).group(0)
					# Preppend year
					#href = '/' + year + href
					print("href: " + a['href'] + " Content: " + a.contents[0] + " Title: " + a['title'])
					montana_links.append(href)
	

		return montana_links

	def __clean_feature_name(self, feature_name):
		feature_name = feature_name.replace(':', '')
		feature_name = re.sub('\s+', '', feature_name)
		return feature_name

	def __clean_example_datum(self, example_datum):
		# For features 'Aboard' and 'Fatalities', extract just the 1st number
		example_datum = re.sub("[^\d]*(passengers.*crew.*)", '', example_datum)
		example_datum.strip()

		# Number?
		try:
			example_datum = int(example_datum)
			example_datum = str(example_datum)
		except ValueError:
			# Time?
			try:
				example_datum = re.search("\d\d:\d\d", example_datum).group(0)
			except AttributeError:
				# Date?
				try:
					datetime = parser.parse(example_datum)
					example_datum = str(datetime.day) + \
						'/' + str(datetime.month) + '/' + str(datetime.year)
				except ValueError:
					#String
					pass

		example_datum = str(example_datum.encode('utf-8')).strip()
		return example_datum

	def __get_geographical_coordinates(self, location_str):
		try:
			location = self.geolocator.geocode(location_str)
		except:
			return '?', '?'

		if location is None:
			return '?', '?'
		else:
			return str(location.latitude), str(location.longitude)

	def __scrape_montana_data(self, html):
		bs = BeautifulSoup(html, 'html.parser')
		montana_data = []
		features_names = []
		h1 = bs.find('h1').text
		print("h1: "+ h1)
		nom = h1[0:h1.find(",")].strip()
		print("nom: "+ nom)
		features_names.append('nom')
		montana_data.append(nom)
		tipus = h1[h1.find(",")+1:h1.find("(")].strip()
		print("tipus: "+ tipus)
#h2 conté la unidad de relieve i el continente
		h2 = bs.find('h2')
		p = h2.find_next_sibling('p')
		print("p: "+ p.text)
		h2 = h2.text
		print("h2: "+ h2)
		continent = h2[h2.find("(")+1:h2.find(")")].strip()
		print("continent: "+ continent)
		
#PENDENT: de la <p> recuperar keywords
		
		ul = p.find_next_sibling("ul")
		lis = ul.findAll('li')		
		for li in lis:
			print("li: "+ li.text)
			if ":" in li.text:
				print("clau: " + li.text.split(":")[0])
				print("valor: " + li.text.split(":")[1])


#PENDENT: parsejar h1,h2,p,li... per extreure els atributs, https://stackoverflow.com/questions/15037301/python-extracting-data-from-html-using-split

		# The first <tr> element does not provide useful info
#		trs.pop(0)

#		for tr in trs:
#			tds = tr.findAll('td')

			# Read features' names?
#			if len(self.data) == 0:
#				feature_name = tds[0].next_element.text
#				feature_name_cleaned = self.__clean_feature_name(feature_name)
#				features_names.append(feature_name_cleaned)

#			example_datum = tds[1].next_element.text
#			example_datum_cleaned = self.__clean_example_datum(example_datum)
#			montana_data.append(example_datum_cleaned)

			# If the datum is the LOCATION (index 2), add latitude and longitude
#			if tr == trs[2]:
#				location = (
#					self.__get_geographical_coordinates(tds[1].next_element.text)
#				)
#				if len(self.data) == 0:
#					features_names.append('Latitude')
#					features_names.append('Longitude')
#				montana_data.append(location[0])
#				montana_data.append(location[1])

			# If the datum is the SUMMARY (index 12), assign it a category
			# (reason) using text mining techniques
#			elif tr == trs[12]:
#				summary = tds[1].next_element.text
#				if len(self.data) == 0:
#					features_names.append('Reason')
##				reason = self.reason_classifier.classify(summary)
##				montana_data.append(reason)

		# Store features' names
		if len(features_names) > 0:
			if len(self.data) == 0:
				self.data.append(features_names)

		# Store the data
		self.data.append(montana_data)

	def __get_letters_links(self, html):
		print (" __get_letters_links.\n")
		bs = BeautifulSoup(html, 'html.parser')
#		anchors = bs.findAll('a', href=True)
		uls = bs.find('ul', attrs={'id':'abc'})
		lis = uls.findAll('li')


		
		letters_links = []
		for li in lis:
			a = li.next_element
			if a.name == 'a':
				href = a['href']
#				print (" href "+href)
				if href[0] != '/':
					href = '/' + href
				letters_links.append(href)

		return letters_links

	def scrape(self):
		print ("Web Scraping of montipedia data from " + "'" + self.url + "'...")

		print ("This process could take roughly ??? minutes.\n")

		# Start timer
		start_time = time.time()

		# Download HTML
		html = self.__download_html(self.url + self.subdomain)
		bs = BeautifulSoup(html, 'html.parser')

		# Get the links of each letter
		letters_links = self.__get_letters_links(html)

		# For each letter, get its montana' links
		montanas_links = []
		for y in letters_links:			
			y ='/montanas/f/'
			print ("Found link to a letter of mountain: " + self.url + " y: "+y)
			current_letter_montana = self.__get_montana_links(y)
			montanas_links.append(current_letter_montana)
#PENDENT: hi ha el break per només fer proves amb la lletra A
			# Uncomment this break in case of debug mode
			break

		# For each montana, extract its data
		for i in range(len(montanas_links)):
			for j in range(len(montanas_links[i])):
				print ("scraping montana data: " + self.url + montanas_links[i][j])
				html = self.__download_html(self.url + \
					montanas_links[i][j])
				self.__scrape_montana_data(html)

		# Show elapsed time
		end_time = time.time()
		print ("\nelapsed time: " + str(round(((end_time - start_time) / 60) , 2)) + " minutes")

	def data2csv(self, filename):
		# Overwrite to the specified file.
		# Create it if it does not exist.
		file = open("../csv/" + filename, "w+")

		# Dump all the data with CSV format
		for i in range(len(self.data)):
			for j in range(len(self.data[i])):
				file.write(self.data[i][j] + ";");
			file.write("\n");
