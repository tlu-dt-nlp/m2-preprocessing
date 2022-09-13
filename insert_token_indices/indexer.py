import os

directory = 'testset_m2/non-indexed'
for filename in os.listdir(directory):
    if filename.endswith('.txt'):
        with open('testset_m2/non-indexed/'+filename, 'r') as input_txt:
            lines = input_txt.readlines()
            sent_indexes = []
            for i in range(len(lines)):
                if lines[i].startswith('S'):
                    sent_indexes.append(i)
            for i in range(len(lines)):
                if i in sent_indexes:
                    tokens = lines[i].split(' ')
                    tokens = [token.strip() for token in tokens]
                    token_lengths = [len(token) for token in tokens]
                    token_indexes = []
                    for j in range(len(tokens)):
                        token_indexes.append(j)
                    new_line = ''
                    for j in range(len(tokens)):
                        if token_indexes[j] >= 10 and token_lengths[j] > 1:
                            spaces_and_index = str((token_lengths[j]-1)*' ')+str(token_indexes[j])
                        else:
                            spaces_and_index = str(token_lengths[j]*' ')+str(token_indexes[j])
                        new_line = new_line.lstrip()
                        new_line = new_line + spaces_and_index
                    lines[i] = '#'+new_line+'\n'+lines[i]
            with open('testset_m2/indexed/'+filename, 'w') as output_txt:
                output_txt.writelines(lines)