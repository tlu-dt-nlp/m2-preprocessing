import os

# M2-märgendusega failide sisselugemine
for entry in os.scandir('m2_texts'):
    if entry.name.endswith('.txt'):
        # Failiridade loend
        input_lines = []
        with open('m2_texts/' + entry.name, 'r', encoding='utf-8') as f:
            for f_line in f.read().splitlines():
                input_lines.append(f_line)
        input_lines.append('')

        # Uus loend, kuhu talletada olemasolevad ja lisatavad märgendusread
        output_lines = []
        noop_line = 'A -1 -1|||noop|||-NONE-|||-NONE-|||-NONE-|||0'
        for i in range(len(input_lines)):
            output_lines.append(input_lines[i])
            if input_lines[i].startswith('S') and len(input_lines[i+1]) == 0:
                output_lines.append(noop_line)
        
        # Uute, täiendatud failide kirjutamine teise kausta
        with open('m2_texts_modified/' + entry.name, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines[:-1]))