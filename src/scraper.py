import urllib.request
import requests
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
<<<<<<< HEAD
		try:
			url=urllib.parse.unquote(url, encoding='utf-8')  
			html = requests.get(url).content

		except ValueError:			
			print ("****** Error __download_html ******")
			pass
			
=======
		url=urllib.parse.unquote(url, encoding='utf-8')  
		html = requests.get(url).content

>>>>>>> 775ed4ae4fad8b25c16e16dede03c1cc61430db2
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
#PENDENT: cal fer proves per a que no peti quan no hi ha cap montanya (exemple /ñ )
			ul2 = ul1.find_next_sibling('ul')
			if ul2:
				lis = ul2.findAll("li")
		
				for li in lis:
					# Has this <li> element an <a> child?
					a = li.next_element
					if a.name == 'a':
						href = a['href']
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
		keyword_data=''

		#divact = bs.find("div", {"id": "montanas"})

		#capçalera amb els noms dels atributs
		if len(self.data) == 0:
			features_names.insert(0,'Nom')
			features_names.insert(1,'Tipus')	
			features_names.insert(2,'Continent')
			features_names.insert(3,'Unitat de relleu')
			features_names.insert(4,'País')
			features_names.insert(5,'Cumbre')
			features_names.insert(6,'Regió')
			features_names.insert(7,'Altitud')
			features_names.insert(8,'Classificació per alçada')
			features_names.insert(9,'Latitud')
			features_names.insert(10,'Longitud')
			features_names.insert(11,'Descripció')
			features_names.insert(12,'Keywords')

		#recuperem el nom
		h1 = bs.find('h1')
		if not h1:
			#la pàgina no conté el títol, per tant, és errònia i no la parsejem
			pass
		else:
			h1=h1.text
			nom = h1[0:h1.find(",")].strip()
			#print("nom: "+ nom)
			montana_data.insert(0,nom)

			#recuperem el tipus
			tipus = h1[h1.find(",")+1:h1.find("(")].strip()
			#print("tipus: "+ tipus)
			montana_data.insert(1,tipus)

			#recuperem la descripcio
			h2 = bs.find('h2')
			descripcio = h2.find_next_sibling('p')
			#print("descripcio: "+ descripcio.text)

			#recuperem els keywords
			aas = descripcio.findAll('a')
			for a in aas:
				#if a.name == 'a':
				if a.contents[0].name=='a':
					keyword = str(a.contents[0].contents[0])
				else:
					keyword = str(a.contents[0])
				#print("keyword: "+keyword)
				keyword_data = keyword_data + keyword + ','
			keyword_data=keyword_data[:len(keyword_data)-1]

			#recuperem el continent
			h2 = h2.text
			continent = h2[h2.find("(")+1:h2.find(")")].strip()
			#print("continent: "+ continent)
			montana_data.insert(2,continent)
			
			#recuperem la resta d'atributs: unitat de relleu, país, regió, altitud, latitud i longitud	
			#creem la classificació en funció de l'altitud
			ul = descripcio.find_next_sibling("ul")
			lis = ul.findAll('li')		
			atribut=3
			i=0
			while i<=7:
				if i<len(lis):
					li = lis[i]
				else:
					li = ""
				print("li: "+ str(li))
				print("Atribut: "+str(atribut))

				if ":" in str(li):
					clau=li.text.split(":")[0]
					valor=li.text.split(":")[1].strip()
				elif "Cumbre" in str(li):	
					clau="Cumbre"
					valor=li.text
					valor=valor[7:]
				else:
					clau=""
					valor=""
				print("clau: " + clau)
				print("valor: " + valor)

				if "Unidad de relieve" in clau:
					montana_data.insert(3,valor)
				elif "País" in clau:
					pais=valor[0:valor.find("(")].strip()				
					montana_data.insert(4,pais)
				elif "Cumbre" in clau:
					montana_data.insert(5,valor)	
				elif "Región" in clau:
					montana_data.insert(6,valor)					
				elif "Altitud" in clau:
					#si estem en atribut 6, vol dir que no ha entrat a regió, per tant l'inserim nul.la
					if atribut==6:
						montana_data.insert(6,"")						
					altitud=valor[0:valor.find("m")].strip()
					altitud=int(re.sub('\D', '', altitud))
					montana_data.insert(7,valor)		
					
					#Classificació per alçada
					if altitud < 1000: 
						classify="menor de 1000"
					elif altitud < 2000:
						classify="mil"
					elif altitud < 3000:
						classify="dos mil"
					elif altitud < 4000:
						classify="tres mil"
					elif altitud < 5000:
						classify="quatre mil"
					elif altitud < 6000:
						classify="cinc mil"
					elif altitud < 7000:
						classify="sis mil"
					elif altitud < 8000:
						classify="set mil"
					else:
						classify="vuit mil"

					montana_data.insert(8,classify)	
					atribut=8

				elif "Latitud" in clau:
					montana_data.insert(9,valor)	
				elif "Longitud" in clau:
					montana_data.insert(10,valor)					
				elif atribut==9:
					montana_data.insert(9,"")
				elif atribut==10:
					montana_data.insert(10,"")	

				atribut+=1
				i+=1

					

			montana_data.insert(11,descripcio.text)	
			montana_data.insert(12,keyword_data)		

			# Store features' names
			if len(features_names) > 0:
				self.data.append(features_names)

			# Store the data
			self.data.append(montana_data)

	def __get_letters_links(self, html):
		print (" __get_letters_links.\n")
		bs = BeautifulSoup(html, 'html.parser')
		uls = bs.find('ul', attrs={'id':'abc'})
		lis = uls.findAll('li')
		
		letters_links = []
		for li in lis:
			a = li.next_element
			if a.name == 'a':
				href = a['href']
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
<<<<<<< HEAD
			#y ='/montanas/b/'
=======
			#y ='/montanas/f/'
>>>>>>> 775ed4ae4fad8b25c16e16dede03c1cc61430db2
			print ("Found link to a letter of mountain: " + self.url + " y: "+y)
			current_letter_montana = self.__get_montana_links(y)
			montanas_links.append(current_letter_montana)

			# Uncomment this break in case of debug mode
			#break

		# For each montana, extract its data
		for i in range(len(montanas_links)):
			for j in range(len(montanas_links[i])):
				print ("scraping montana data: " + self.url + montanas_links[i][j])
				html = self.__download_html(self.url + montanas_links[i][j])
				if html:
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
