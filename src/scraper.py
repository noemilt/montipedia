import urllib.request
import requests
import re
import time
import string
from bs4 import BeautifulSoup
from dateutil import parser
from geopy.geocoders import Yandex

class MontipediaScraper():

	def __init__(self):
		self.url = "http://www.montipedia.com"
		self.subdomain = "/montanas/"
		self.data = []

	def __download_html(self, url):
		try:
			url=urllib.parse.unquote(url, encoding='utf-8')  
			html = requests.get(url).content

		except ValueError:			
			print ("****** Error __download_html ******")
			pass
			
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
			html = self.__download_html(self.url + pag)
			bs = BeautifulSoup(html, 'html.parser')
			divact = bs.find("div", {"id": "montanas"})
			ul1 = divact.find("ul", {"id": "abc"})
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

	def __scrape_montana_data(self, html):
		bs = BeautifulSoup(html, 'html.parser')
		montana_data = []
		features_names = []
		keyword_data=''

		#capçalera amb els noms dels atributs
		if len(self.data) == 0:
			features_names.insert(0,'Nom')
			features_names.insert(1,'Nom alternatiu')
			features_names.insert(2,'Tipus')	
			features_names.insert(3,'Continent')
			features_names.insert(4,'Unitat de relleu')
			features_names.insert(5,'País')
			features_names.insert(6,'Cimera')
			features_names.insert(7,'Regió')
			features_names.insert(8,'Altitud')
			features_names.insert(9,'Classificació per alçada')
			features_names.insert(10,'Latitud')
			features_names.insert(11,'Longitud')
			features_names.insert(12,'Descripció')
			features_names.insert(13,'Keywords')

		nom=""
		nomAlternatiu=""
		tipus=""
		continent=""
		relleu=""
		pais=""
		cimera=""
		regio=""
		altitud=""
		classify=""
		latitud=""
		longitud=""
		descripcio=""
		keywords=""
		

		#recuperem el nom
		divact = bs.find("div", {"id": "montanas"})
		perror = divact.find('p')

		if 'Estamos solucionando este problema' in perror.contents[0]:
			pass			
		else: 
			h1 = divact.find('h1')
			if not h1:
				#la pàgina no conté el títol, per tant, és errònia i no la parsejem
				pass
			else:
				h2s = divact.findAll('h2')				
				titol= h2s[0]
				h1=h1.text
				nom = h1[0:h1.find(",")].strip()
				print("nom: "+ nom)

				#recuperem el tipus
				tipus = h1[h1.find(",")+1:h1.find("(")].strip()

				#recuperem la descripcio	
				ps = divact.findAll('p')			
				for p in ps:
					descripcio = descripcio + p.text.replace(';',',').replace('\n',' ').replace('\r',' ')							
					#recuperem els keywords
					if descripcio:
						aas = p.findAll('a')
						p=p.text.replace(';',',').replace('\n',' ').replace('\r',' ')
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
				continent = titol.text[titol.text.find("(")+1:titol.text.find(")")].strip()

				if len(h2s)>1:
					cos= h2s[1]
					#recuperem la resta d'atributs i creem la classificació en funció de l'altitud
					ul = cos.find_next_sibling("ul")

					lis = ul.findAll('li')		
					for li in lis:
						if ":" in str(li):
							clau=li.text.split(":")[0]
							valor=li.text.split(":")[1].strip()
						elif "Cumbre" in str(li):	
							clau="Cimera"
							valor=li.text
							valor=valor[7:]
						else:
							clau=""
							valor=""
						
						#print("clau: " + clau)
						#print("valor: " + valor)

						if "Nombre alternativo" in clau:
							nomAlternatiu=valor
						elif "Unidad de relieve" in clau:
							relleu=valor
						elif "País" in clau:
							pais=valor[0:valor.find("(")].strip()				
						elif "Cimera" in clau:
							cimera=valor
						elif "Región" in clau:
							regio=valor
						elif "Altitud" in clau:
							altitud=valor
							alt=valor[0:valor.find("m")].strip()
							alt=int(re.sub('\D', '', alt))
							
							#Classificació per alçada
							#Ficar la classificació en una altra funció o .py
							if alt < 1000: 
								classify="menor de 1000"
							elif alt < 2000:
								classify="mil"
							elif alt < 3000:
								classify="dos mil"
							elif alt < 4000:
								classify="tres mil"
							elif alt < 5000:
								classify="quatre mil"
							elif alt < 6000:
								classify="cinc mil"
							elif alt < 7000:
								classify="sis mil"
							elif alt < 8000:
								classify="set mil"
							else:
								classify="vuit mil"
						elif "Latitud" in clau:
							latitud=valor
						elif "Longitud" in clau:
							longitud=valor						

					montana_data.insert(0,nom)
					montana_data.insert(1,nomAlternatiu)							
					montana_data.insert(2,tipus)
					montana_data.insert(3,continent)
					montana_data.insert(4,relleu)	
					montana_data.insert(5,pais)		
					montana_data.insert(6,cimera)	
					montana_data.insert(7,regio)
					montana_data.insert(8,altitud)	
					montana_data.insert(9,classify)	
					montana_data.insert(10,latitud)
					montana_data.insert(11,longitud)					
					montana_data.insert(12,descripcio)	
					montana_data.insert(13,keyword_data)		
						

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

		print ("This process could take roughly 15 minutes.\n")

		# Start timer
		start_time = time.time()

		# Download HTML
		html = self.__download_html(self.url + self.subdomain)
		#bs = BeautifulSoup(html, 'html.parser')

		# Get the links of each letter
		letters_links = self.__get_letters_links(html)

		# For each letter, get its montana' links
		montanas_links = []
		for y in letters_links:			
			#y ='/montanas/a/'
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
