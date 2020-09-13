import requests
from bs4 import BeautifulSoup

headers = {
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
}

response = requests.get("https://en.wikipedia.org/wiki/List_of_best-selling_singles", headers=headers)

page = response._content

soup = BeautifulSoup(page, 'html.parser')

#for article in soup.find_all('article'):
#	print(article["data-heading"])

for link in soup.find_all('a'):
	try:
		print(link.get_text())
#		if '/m/' in link['href']:
#			print(link.get_text().split('(')[0])
	except:
		pass