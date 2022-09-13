import re
import os
import pandas as pd
import converter_functions as cf

conll_dir = 'testset_conll'
m2_dir = 'testset_m2'
for entry in os.scandir(conll_dir):
	if entry.name.endswith('.txt'):
		filename = entry.name

		# Sisendfaili lõppu lisatakse tähis,
		# mis lihtsustab selle teisendamist lause kaupa.
		with open (conll_dir+'/'+filename, 'r') as input_txt:
			lines = input_txt.readlines()
			lines.append('# end')

			# Tulpade pealkirjad märgendusridade lugemiseks andmetabelina
			header_list = ['Index', 'Token', 'Lemma', 'UPOS', 'XPOS',
				'Feats', 'Head', 'Deprel', 'Deps', 'MISC'] 
			sent_tokens = []
			sent_tags = []
			wo_index1 = 0
			wo_token1 = ''
			wo_index2 = 0
			wo_token2 = ''
			error_counter = 0

			output_stack = []
			line_error = False
			line_counter = 3

			for line in lines[3:]:
				line_counter += 1
				# Märgendusega ridadest salvestatakse
				# iga lause sõnad-kirjavahemärgid ja veamärgendid.
				# Kui märgendusreas on vale väärtuste arv, siis
				# kuvatakse veateade ja logitakse veainfo. 
				if not line.startswith('#') and len(line.strip()) != 0:
					line_text = re.split(r'\t+', line.strip())
					if len(line_text) != 10:
						print('Error in file "'+filename+'":')
						print('Expected 10 fields in line '+str(line_counter)+
							', saw '+str(len(line_text)))
						converter_log = open('testset_m2/logs/'+filename[:-4]+
                            '_log.txt', 'a')
						converter_log.write('Error: Expected 10 fields, saw '+
                            str(len(line_text))+'\n')
						converter_log.write('Line number: '+str(line_counter)+'\n')
						converter_log.write('Line:\n'+line+'\n\n')
						converter_log.close()
						line_error = True
						pass
					df_dict = dict(zip(header_list, line_text))
					df = pd.DataFrame(df_dict, index=[0])
					token = str(df.iat[0,1]).strip()
					sent_tokens.append(token)
					misc_tag = str(df.iat[0,9]).strip()
					# Vormivigade puhul eristatakse
					# käänd- ja tegusõnade vormivigu.
					if 'Viga=vorm' in misc_tag:
						if str(df.iat[0,4]).strip() == 'V':
							misc_tag = misc_tag.replace('Viga=vorm', 'Viga=verbivorm')
						else:
							misc_tag = misc_tag.replace('Viga=vorm', 'Viga=kaandvorm')
					sent_tags.append(misc_tag)
				else:
					# Uue lauseni või teksti lõppu jõudes trükitakse väljundfaili
					# eelnev lause ja parandused teisendatud veamärgenditega.
					if line.startswith('# sent_id') or line.startswith('# end'):
						output_stack.append('\nS '+' '.join(sent_tokens)+'\n')
						for i in range(len(sent_tags)):
							# Määratakse sõnajärjevea skoop.
							if 'sonajargalgus' in sent_tags[i]:
								wo_index1 = i
							elif 'sonajarglopp' in sent_tags[i]:
								wo_index2 = i
							# Asendatakse vanad veamärgendid ja leitakse parandused.
							if 'Viga=' in sent_tags[i]:
								error_counter += 1
								errortags = cf.changetags(sent_tags[i])
								corrections = cf.findcorrections(sent_tags[i], sent_tokens[i])
								if len(errortags) > 1:
									errortags = cf.combinetags(errortags)
								# Hilisemaks väljatrükiks talletatakse
								# sõnajärjevea algus- ja lõpusõna.
								for j in range(len(errortags)):
									tag = errortags[j]
									if tag == 'R:WO1':
										if len(corrections) > j:
											wo_token1 = corrections[j]
										else:
											wo_token1 = '-NONE-'
									elif tag == 'R:WO2':
										if len(corrections) > j:
											wo_token2 = corrections[j]
										else:
											wo_token2 ='-NONE-'
								# Lause elementide kaupa trükitakse välja veaparandused.
								for j in range(len(errortags)):
									tag = errortags[j]
									if len(corrections) > j:
										correction = corrections[j]
									else:
										correction = '-NONE-'
									# Puuduvate elementide lisamine
									if tag.startswith('M:'):
											output_stack.append('A '+str(i+1)+
												' '+str(i+1)+'|||'+tag+'|||'+correction+
												'|||REQUIRED|||-NONE-|||0\n')
									# Elementide asendamine, v.a sõnajärje- 
									# ja kokku-lahkukirjutamise vigade puhul
									elif tag.startswith('R:')\
										and not tag.startswith('R:WO1')\
										and not tag.startswith('R:WO2')\
										and not tag.startswith('R:WS'):
										# Kui lause jagatakse mitmeks lauseks, siis
										# hõlmab parandus järgneva sõna algustähe muutmist.
										sent_punct = ['.', '!', '?']
										if tag == "R:PUNCT" and correction in sent_punct\
											and sent_tokens[i] not in sent_punct and\
											i < len(sent_tokens)-1:
											correction = correction+\
												' '+sent_tokens[i+1].capitalize()
											output_stack.append('A '+str(i)+' '+str(i+2)+
												'|||'+tag+'|||'+correction+
												'|||REQUIRED|||-NONE-|||0\n')
										else:
											output_stack.append('A '+str(i)+' '+str(i+1)+
												'|||'+tag+'|||'+correction+
												'|||REQUIRED|||-NONE-|||0\n')
									# Alakriips paranduses viitab valele kokkukirjutusele,
									# muidu on tegu vale lahkukirjutusega.
									elif tag.startswith('R:WS'):
										if '_' in correction:
											correction = correction.replace('_', ' ')
											output_stack.append('A '+str(i)+' '+str(i+1)+
												'|||'+tag+'|||'+correction+
												'|||REQUIRED|||-NONE-|||0\n')
										else:
											output_stack.append('A '+str(i)+' '+str(i+2)+
												'|||'+tag+'|||'+correction+
												'|||REQUIRED|||-NONE-|||0\n')                           
									# Sõnajärge parandatakse, kui vea skoop on 2 sõna.
									# Muul juhul tuleb parandus käsitsi lisada.
									# Kui vahetub 1. ja 2. sõna järjekord,
									# siis muudetakse nende algustähte.
									elif tag.startswith('R:WO2'):
										if wo_index2 - wo_index1 == 1:
											if i == 1:
												wo_token2 = wo_token2.capitalize()
												wo_token1 = wo_token1.lower()
											correction = wo_token2 +' '+ wo_token1
											output_stack.append('A '+str(wo_index1)+
												' '+str(wo_index2 + 1)+'|||'+'R:WO|||'+
												correction+'|||REQUIRED|||-NONE-|||0\n')
										else:
											output_stack.append('A '+str(wo_index1)+
												' '+str(wo_index2 + 1)+'|||'+
												'R:WO|||...|||REQUIRED|||-NONE-|||0\n')
									# Liigsete elementide eemaldamine
									elif tag.startswith('U:'):
										# Kui lause algusest kustutatakse sõna, siis
										# hõlmab parandus järgneva sõna algustähe muutmist.
										if i == 0 and 'LEX' in tag:
											correction = sent_tokens[1].capitalize()
											output_stack.append('A 0 2|||'+tag+'|||'+
												correction+'|||REQUIRED|||-NONE-|||0\n')
										else:
											output_stack.append('A '+str(i)+' '+str(i+1)+
												'|||'+tag+'|||'+correction+
												'|||REQUIRED|||-NONE-|||0\n')
									else:
										pass
						# Kui veamärgend puudub, talletatakse nullparandus.
						if error_counter == 0:
							output_stack.append(
								'A -1 -1|||noop|||-NONE-|||-NONE-|||-NONE-|||0\n')
						sent_tokens = []
						sent_tags = []
						wo_index1 = 0
						wo_index2 = 0
						wo_token1 = ''
						wo_token2 = ''
						error_counter = 0
					if line.startswith('# text') or len(line.strip()) == 0:
						continue
			# Kui sisendfailist vale pikkusega märgendusridu ei leitud,
			# kirjutatakse M2 märgendus väljundfaili.
			if line_error == False:
				output_stack[0] = output_stack[0].lstrip()
				output_txt = open(m2_dir+'/'+filename, 'w')
				for row in output_stack:
					output_txt.write(row)
				output_txt.close()