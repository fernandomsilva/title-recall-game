import json

mapping = {
	"Album": "albums",
	"Book": "books",
	"Cartoon/Anime": "cartoons", 
	"Character": "characters",
	"Comic Book/Manga": "comics",
	"Fine Art": "art",
	"Game": "games",
	"Movie": "movies",
	"Musical/Play": "musical",
	"Person": "person",
	"Song": "songs",
	"TV Show": "tv"
}

result = {}

for category in mapping:
	result[category] = []

	input_file = open(mapping[category] + '_list_english', 'r')

	for line in input_file:
		result[category].append({'title': line.replace('\n','').lstrip().rstrip(), 'category': category})

	input_file.close()

output_file = open('en.card.data.js', 'w')
output_file.write('var carddata = {}'.format(json.dumps(result)))
output_file.close()