# gutenberg-dialog ([Download the English dataset](https://mega.nz/file/HcNGCKSQ#kL5PX6CecFfDtqRq0y_onbg-ozt_OmBQBdbXq8vcVag))
Code for downloading and building your own version of the Gutenberg Dialog Dataset. Easily extendable with new languages.  
https://arxiv.org/abs/2004.12752

## Setup
Run setup.py which installs required packages.
```
python setup.py
```

## Usage
The main file should be called from the root of the repo. The command below runs the dataset building pipeline for the comma-separated languages given as argument. Currently only English, Spanish, Portuguese, Italian, and Hungarian are supported.
```
python code/main.py -l=en,es,pt,it,hu -a
```
All settable arguments can bee seen below:  
<a><img src="https://github.com/ricsinaruto/gutenberg-dialog/blob/master/docs/help.png" align="top" height="500" ></a>

### Pipeline steps
The *-a* flag controls whether to run the whole pipeline automatically. If *-a* is omitted a subset of steps have to be specified using flags (see help above). Once a step is finished its output can be used in subsequent steps and it only has run again if parameters or code related to that step is changed. All steps run separately for each language.

#### 1. Download (-d)
Download books for given languages.

#### 2. Pre-filter (-f1)
Pre-filtering removes some old books and noise.

#### 3. Extract (-e)
Dialogs are extracted from books. When extending the dataset to new languages (see section below), this is the step that can be modified, thus previous steps can be skipped once finished.

#### 4. Post-filter (-f2)
A second filtering step removing some dialogs based on vocabulary.

#### 5. Create dataset and manual filtering (-c)
Putting together the final dataset and splitting into train/dev/test data. The final step creates the *author_and_title.txt* file in the output directory containing all books (plus titles and authors) used to extract the final dataset. Users can manually copy lines from this file to *banned_books.txt* corresponding to books which should not be allowed in the dataset. In subsequent runs of any steps, books in this file will not be taken into account.

## Extending to other languages
The code can be easily extended to process other languages. A file named \<language code\>.py has to be created in the languages folder. Here a class should be defined named the upper-case language code (e.g. *En* for English), with [LANG](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/lang.py) or any of the other subclasses as parent. With *self.cfg* config parameters can be accessed. Inside this class the 3 functions below have to be defined. Please see [it.py](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/it.py) for an example.

### delimiters
This function should return a dictionary where the keys are potential delimiters. For each delimiter a function should be defined (values in dictionary), which takes as input a line and returns a number. This number can be for example the count of delimiters, a flag whether there is a delimiter in the line, etc. Usually a weighted count is advisable, depending on the importance of different delimiters. The values will be used to determine the delimiter that should be used in the respective book (passed to the function below), and for filtering books which contain a low amount of delimiters. [en.py](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/en.py) contains examples of multiple delimiters.

### process_file(paragraph_list, delimiter)
This function should extract the dialogs from a book and append them to *self.dialogs*, which is a list of dialogs, and each dialog is a list of consecutive utterances. *paragraph_list* contains the book as a list of consecutive paragraphs. *delimiter* is the most common delimiter in this file which should be used to extract dialogs.

### clean_line(line)
This function is used for post-processing dialogs (e.g. remove certain characters). It takes as input an utterance. Please note that nltk word tokenization is run automatically.
