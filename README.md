# Preprocessing scripts for the EstGEC-L2 corpus

Scripts for preprocessing the [Estonian L2 Grammatical Error Correction Corpus (EstGEC-L2)](https://github.com/tlu-dt-nlp/m2-corpus) that contains L2 learner texts error-annotated in the M2 format.
* `convert_conll_to_m2` – used for converting the previous CoNLL-U format error annotation to the M2 format and updating the error tags
* `check_m2_annotation` – used for validating manual annotation to detect possible format errors 
* `insert_noop_lines` – used for adding the 'noop' annotation to sentences that were not corrected by any of the annotators (the latest version of the converter also adds 'noop' annotations)
