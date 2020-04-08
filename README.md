# gutenberg-dialog
Code for downloading and building your own versions of the Gutenberg Dialog Dataset. Easily extendable with new languages.

## Setup
Run setup.py which installs required packages.
```
python setup.py
```

## Usage
The main file should be called from the root of the repo. The command below runs the dataset building pipeline for the comma-separated languages given as argument. Currently only English, French, Italian, and Hungarian is supported.
```
python code/main.py -l=en,fr,it,hu -a
```
All settable arguments can bee seen below:
<a><img src="https://github.com/ricsinaruto/gutenberg-dialog/blob/master/docs/help.png" align="top" height="400" ></a>

## Extend to other languages
The code can be easily extended to process other languages. A file named \<language code\>.py has to be created in the languages folder. Here a class should be defined named LANG, with [LANG_base](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/lang.py) as parent. With *self.cfg* config parameters can be accessed. Inside this class the 3 functions below have to be defined. Please see [hu.py](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/hu.py) for an example.

### delimiters
This function should return a dictionary where the keys are potential delimiters. For each delimiter you have to define a function (values in dictionary), which takes as input a line and returns a number. This number can be for example the count of delimiters or a flag whether there is a delimiter in the line, etc. Usually a weighted count is advisable, depending on the importance of different delimiters. The values will be used to determine which delimiter should be used in the respective book (passed to the function below), and for filtering books which contain a low amount of delimiters. [en.py](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/en.py) contains examples of multiple delimiters.

### process_file(paragraph_list, delimiter)
This function should extract the dialogs from a book and append them to *self.dialogs*, which is a list of dialogs, and each dialog is a list of consecutive utterances. *paragraph_list* contains the book as a list of consecutive paragraphs. *delimiter* is the most common delimiter in this file which should be used to extract dialogs.

### clean_line(line)
This function is used for post-processing the dialogs. It takes as input an utterance on which you can run whatever processing you need (like removing certain characters). Please note that nltk word tokenization is run automatically.
