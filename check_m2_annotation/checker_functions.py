import string

def validate_chars(input_line: str) -> bool:
    'Funktsioon kontrollib, kas tekstirida sisaldab lubatud sümboleid.'
    correct_chars = True
    for char in input_line:
        if char not in string.ascii_letters and char not in 'õäöüšžÕÄÖÜŠŽ'\
            and char not in string.digits and char not in string.whitespace\
                and char not in '.,:;!?-"()|€@' and char not in "'’":
            correct_chars = False
    return correct_chars

def validate_indices(error_indices: str) -> bool:
    'Funktsioon kontrollib, kas veaindeksid on sisestatud õiges formaadis.'
    index_error = False
    if len(error_indices.split()) == 1:
        index_error = True
    for index in error_indices.split():
        if not index.isnumeric():
            if index != '-1':
                index_error = True
        else:
            if len(index) > 2:
                index_error = True
    return index_error

def validate_punct_spaces(correction: str) -> bool:
    'Funktsioon kontrollib, kas kirjavahemärgid on paranduses tühikuga eraldatud.'
    punct_spaces = True
    punct_marks = ['.', ',', ':', ';', '!', '?', '"', '(', ')']
    for token in correction.split():
        if any(char in token for char in punct_marks) == True and len(token) > 1:
            if '.' in token:
                for i in range(len(token)):
                    if token[i] == '.':
                        if not token[i-1].isnumeric() or not token[i-1].isupper():
                            punct_spaces = False
            else:
                punct_spaces = False
    return punct_spaces

def count_empty_lines(input_lines: list, i: int) -> bool:
    'Funktsioon kontrollib, kas märgenduses leidub liigseid tühje ridu.'
    multiple_empty_lines = False
    if i < len(input_lines) - 2:
        if len(input_lines[i+1]) == 0:
            if not input_lines[i+2].startswith('S'):
                multiple_empty_lines = True
    return multiple_empty_lines

def compare_annotation_ids(
    annotation_id: str,
    error_tag: str,
    input_lines: list,
    i: int
    ) -> bool:
    'Funktsioon kontrollib, et märgendusversiooni indeksid esineks suurenevas järjekorras.'
    id_error = False
    if i > 0:
        if input_lines[i-1].startswith('A'):
            previous_annotation_id = input_lines[i-1].split('|||')[-1]
            if previous_annotation_id in ['0', '1', '2']:
                if int(annotation_id) < int(previous_annotation_id):
                    id_error = True
                if int(annotation_id) - int(previous_annotation_id) > 1:
                    id_error = True
    if error_tag == 'noop':
        if i < len(input_lines) - 1:
            if int(annotation_id) < 2:
                if input_lines[i+1].startswith('A'):
                    next_annotation_id = input_lines[i+1].split('|||')[-1]
                    if next_annotation_id in ['0', '1', '2']:
                        if int(annotation_id) >= int(next_annotation_id):
                            id_error = True
    return id_error
