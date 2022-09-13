# Vanad veamärgendid
conll_tagset = ['Viga=orto', 'Viga=kaandvorm',
		'Viga=verbivorm', 'Viga=algustaht', 'Viga=kokku-lahku',
		'Viga=sonavalik', 'Viga=sonajargalgus', 
		'Viga=sonajarglopp', 'Viga=valemark', 'Viga=puuduvsona',
		'Viga=puuduvmark', 'Viga=liignesona', 'Viga=liignemark']

# Uued veamärgendid
# Sõnajärjevea märgendeid on esialgu kaks, et määrata vea skoop.
m2_tagset = ['R:SPELL', 'R:NOM:FORM', 'R:VERB:FORM',
		'R:CASE', 'R:WS', 'R:LEX', 'R:WO1', 'R:WO2',
		'R:PUNCT', 'M:LEX', 'M:PUNCT', 'U:LEX', 'U:PUNCT']

# Sama sõna puhul koosesinevad vead, millel on ühine parandus.
combined_errors = [['R:NOM:FORM', 'R:SPELL', 'R:CASE'],
	['R:VERB:FORM', 'R:SPELL', 'R:CASE'], ['R:WS', 'R:NOM:FORM', 'R:SPELL'],
	['R:WS', 'R:VERB:FORM', 'R:SPELL'], ['R:NOM:FORM', 'R:SPELL'],
	['R:VERB:FORM', 'R:SPELL'], ['R:NOM:FORM', 'R:CASE'],
	['R:VERB:FORM', 'R:CASE'], ['R:LEX', 'R:SPELL'], ['R:LEX', 'R:CASE'], 
	['R:LEX', 'R:NOM:FORM'], ['R:LEX', 'R:VERB:FORM'], ['R:LEX', 'R:WS'], 
	['R:SPELL', 'R:CASE'], ['R:WS', 'R:SPELL'], ['R:WS', 'R:CASE'], 
	['R:WS', 'R:NOM:FORM'], ['U:LEX', 'R:SPELL']]

# Liitveamärgendid	
combined_error_tags = ['R:NOM:FORM:SPELL:CASE', 'R:VERB:FORM:SPELL:CASE',
	'R:WS:NOM:FORM:SPELL', 'R:WS:VERB:FORM:SPELL', 'R:NOM:FORM:SPELL', 
	'R:VERB:FORM:SPELL', 'R:NOM:FORM:CASE', 'R:VERB:FORM:CASE',
	'R:LEX:SPELL', 'R:LEX:CASE', 'R:LEX:NOM:FORM', 'R:LEX:VERB:FORM', 
	'R:LEX:WS', 'R:SPELL:CASE', 'R:WS:SPELL', 'R:WS:CASE', 'R:WS:NORM:FORM',
	'U:LEX:SPELL']

def changetags(tags: str) -> list:
	'Funktsioon tagastab teisendatud veamärgendite loendi.'
	new_tags = []
	for tag in tags.split('|'):
		for i in range(len(conll_tagset)):
			if conll_tagset[i] in tag:
				new_tag = m2_tagset[i]
				new_tags.append(new_tag)
	return new_tags
    
def combinetags(tags: list) -> list:
	'Funktsioon liidab märgendid, kui sõnas on mitu viga.'
	for i in range(len(combined_errors)):
		if len(combined_errors[i]) == 3:
			if combined_errors[i][0] in tags and combined_errors[i][1] in tags\
				and combined_errors[i][2] in tags:
				tags.remove(combined_errors[i][0])
				tags.remove(combined_errors[i][1])
				tags.remove(combined_errors[i][2])
				tags.append(combined_error_tags[i])
				break
		else:
			if combined_errors[i][0] in tags and combined_errors[i][1] in tags:
				tags.remove(combined_errors[i][0])
				tags.remove(combined_errors[i][1])
				tags.append(combined_error_tags[i])
	return tags

def findcorrections(tags: str, token: str) -> list:
	'Funktsioon leiab algses märgenduses pakutud paranduse.'
	corrections = []
	corrected_word = ''
	for tag in tags.split('|'):
		if 'puuduv' in tag:
			correction = tag[16:-1]
			# Vahel on pakutud mitu sobivat sõna.
			# Neid eraldab semikoolon, mis asendatakse 2 püstkriipsuga.
			if ';' in correction:
				correction = correction.replace(';', '||')
			corrections.append(correction)
		elif 'valemark' in tag:
			correction = tag[14:-1]
			corrections.append(correction)
		elif 'sonavalik' in tag:
			correction = tag[15:-1]
			if ';' in correction:
				correction = correction.replace(';', '||')
			corrections.append(correction)
			# Sõnaasendus talletatakse juhuks, 
			# kui seda on vaja kuvada sõnajärjeparanduses.
			corrected_word = correction
		elif 'OigeSona' in tag:
			correction = tag[9:]
			if correction.startswith('('):
				correction = correction[1:-1]
				correction = correction.replace(';', '||')
			corrections.append(correction)
			# Sõnaparandus talletatakse juhuks,
			# kui seda on vaja kuvada sõnajärjeparanduses.
			corrected_word = correction
		elif 'sonajarg' in tag:
			if 'OigeSona' in tags or 'sonavalik' in tags:
				correction = corrected_word
			else:
				# Kui sõnajärjevea alguses/lõpus esinevas sõnas
				# viga ei ole, siis talletatakse algne tekstisõna.
				correction = token
			corrections.append(correction)
		elif 'liigne' in tag:
			correction = '-NONE-'
			corrections.append(correction)
		else:
			pass
	return corrections