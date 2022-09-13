import os
import shutil
import checker_functions as ch

# Veamärgendite loend tegeliku märgendusega võrdlemiseks
error_tags = ['R:SPELL', 'R:CASE', 'R:WS', 'R:NOM:FORM', 'R:VERB:FORM', 'R:LEX', 'R:PUNCT',
    'R:WO', 'R:WO:NOM:FORM', 'R:SPELL:CASE', 'R:NOM:FORM:SPELL', 'R:VERB:FORM:SPELL',
    'R:NOM:FORM:CASE', 'R:VERB:FORM:CASE', 'R:NOM:FORM:SPELL:CASE', 'R:VERB:FORM:SPELL:CASE', 
    'R:LEX:SPELL', 'R:LEX:CASE', 'R:LEX:NOM:FORM', 'R:LEX:VERB:FORM', 'R:LEX:WO', 'R:LEX:WS', 
    'R:WS:SPELL', 'R:WS:CASE', 'R:WS:NOM:FORM', 'R:WS:NOM:FORM:SPELL', 'R:WS:NOM:FORM:CASE', 
    'M:LEX', 'M:PUNCT', 'U:LEX', 'U:PUNCT', 'U:LEX:SPELL', 'noop']

for entry in os.scandir('m2_to_check'):
    if entry.name.endswith('.txt'):
        # Failiridade loend
        input_lines = []
        with open('m2_to_check/' + entry.name, 'r', encoding='utf-8') as f:
            for f_line in f.read().splitlines():
                input_lines.append(f_line)
        # Loend veakirjete talletamiseks
        line_errors = []
        for i, input_line in enumerate(input_lines):
            line_nr = str(i + 1)

            ## Rea alguse, sümbolite ja topelttühikute kontroll
            if len(input_line) != 0:
                if not input_line.startswith('S ') and not input_line.startswith('A '):
                    line_errors.append(line_nr + '. rea alguses on vale sümbol:\n' + input_line)
                    continue
                if ch.validate_chars(input_line) == False:
                    line_errors.append(line_nr + '. rida sisaldab lubamatut sümbolit:\n' + input_line)
                if '  ' in input_line:
                    line_errors.append(line_nr + '. rida sisaldab topelttühikut:\n' + input_line)
            
            ## Lauserea kontroll
            if input_line.startswith('S'):
                # Lause pikkuse arvutamine hilisemaks veaindeksite kontrolliks
                sent_len = len(input_line.split())
                # Tühjade lausete kontroll
                if input_line == 'S ':
                    line_errors.append(line_nr + '. reas puudub lause.')
                # Kahe järjestikuse lauserea kontroll
                if i > 0:
                    if input_lines[i-1].startswith('S'):
                        line_errors.append(line_nr + '. rida ei tohiks S-ga alata:\n' + 
                            input_lines[i-1] + '\n' + input_line)
                # Järgnevate tühikute kontroll

            ## Parandusrea kontroll
            if input_line.startswith('A'):
                line_fields = input_line.split('|||')

                # Rea pikkuse kontroll
                if len(line_fields) != 6:
                    line_length = len(line_fields)
                    line_errors.append(line_nr + '. rea pikkus on vale:\n' + input_line)
                    continue

                # Tühjade väljade ja liigsete tühikute kontroll
                for field in line_fields:
                    if len(field) == 0:
                        line_errors.append(line_nr + '. reas on tühi väli:\n' + input_line)
                        continue
                    if field[0].isspace() or field[-1].isspace():
                        line_errors.append(line_nr + '. reas on liigne tühik:\n' + input_line)
                        continue
                
                error_indices = line_fields[0][2:]
                error_tag = line_fields[1]
                correction = line_fields[2]
                annotation_id = line_fields[5]

                # Veaindeksite kontroll
                if ch.validate_indices(error_indices) == True:
                    line_errors.append(line_nr + '. reas on vigased veaindeksid:\n' + input_line)
                else:
                    if int(error_indices.split()[0]) > int(error_indices.split()[1]):
                        line_errors.append(line_nr + '. reas on esimene veaindeks liiga suur:\n' + 
                            input_line)
                    if int(error_indices.split()[1]) > sent_len:
                        line_errors.append(line_nr + '. reas on teine veaindeks liiga suur:\n' + 
                            input_line)

                # Veamärgendite kontroll
                if error_tag not in error_tags:
                    line_errors.append(line_nr + '. reas on tundmatu veamärgend:\n' + input_line)
                    continue
                
                # Paranduse kontroll
                # tühjade paranduste kontroll
                if error_tag == 'noop':
                    if correction != '-NONE-':
                        line_errors.append(line_nr + '. reas on tühi parandus valesti märgitud:\n' + 
                            input_line)

                # kirjavahemärkide tühikuga eraldamise kontroll
                if ch.validate_punct_spaces(correction) == False:
                    line_errors.append(line_nr + '. reas on kirjavahemärk sõna küljes:\n' + 
                            input_line)

                # rööpparanduste pikkuse ja liigsete tühikute kontroll
                if '||' in correction:
                    corrections = correction.split('||')
                    if ':WO' in error_tag:
                        for i in range(len(corrections)):
                            if i > 0:
                                if len(corrections[i].split()) != len(corrections[i-1].split()):
                                    line_errors.append(line_nr + '. reas on rööpparandused eri pikkusega:\n' + 
                                        input_line)
                    for corr in corrections:
                        if corr[0].isspace() or corr[-1].isspace():
                            line_errors.append(line_nr + '. reas on paranduses liigne tühik:\n' + 
                                input_line)

                # Konstantsete väljade kontroll
                if error_tag == 'noop':
                    if line_fields[3] != '-NONE-':
                        line_errors.append(line_nr + '. reas on 4. väljal viga:\n' + input_line)
                else:
                    if line_fields[3] != 'REQUIRED':
                        line_errors.append(line_nr + '. reas on 4. väljal viga:\n' + input_line)
                if line_fields[4] != '-NONE-':
                    line_errors.append(line_nr + '. reas on 5. väljal viga:\n' + input_line)
                
                # Märgendusversiooni indeksite kontroll
                if annotation_id not in ['0', '1', '2']:
                    line_errors.append(line_nr + '. reas on vigane märgendusindeks:\n' + input_line)
                else:
                    if ch.compare_annotation_ids(annotation_id, error_tag, input_lines, i) == True:
                        line_errors.append(line_nr + '. reas on vigane märgendusindeks:\n' + 
                            input_lines[i-1] + '\n' + input_line+ '\n' + input_lines[i+1])

                # Tühjade ridade kontroll
                if ch.count_empty_lines(input_lines, i) == True:
                    line_errors.append(line_nr + '. rea järel on liigne tühi rida:\n' + 
                        input_line + '\n' + input_lines[i+1] + input_lines[i+2])

        # Veakirjete salvestamine failina
        if len(line_errors) != 0:
            with open('error_logs/' + entry.name[:-4] + '_log.txt', 'w', encoding='utf-8') as f:
                for error in line_errors:
                    f.write(error + '\n\n')
        
# Kontrolli edukalt läbinud failide liigutamine
files_with_errors = []
for entry in os.scandir('error_logs'):
    files_with_errors.append(entry.name[:-8] + '.txt')

for entry in os.scandir('m2_to_check'):
    if entry.name not in files_with_errors:
        search_path = 'm2_to_check/' + entry.name
        destination_path = 'm2_checked/' + entry.name
        shutil.move(search_path, destination_path)