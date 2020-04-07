# gutenberg-dialog
Code for downloading and building your own versions of the Gutenberg Dialog Dataset. Easily extendable with new languages.

## Setup
Run setup.py which installs required packages and steps you through downloading datasets if wanted.  
Please note that the gutenberg package dependency requires [extra setup](https://github.com/c-w/Gutenberg#python-3) in python 3.
```
python setup.py
```

## Usage
The main file should be called from the root of the repo. The command below will automatically run the dataset building pipeline for the comma-separated languages given as argument.
```
python code/main.py -l=en,fr,it,hu -a
```
With the -h flag you can print out all the settable parameters:
<a><img src="https://github.com/ricsinaruto/gutenberg-dialog/blob/master/docs/help.png" align="top" height="400" ></a>

## Extend to other languages
The code can be easily extended to process other languages. You have to write 3 short functions and put them in a file named \<language code\>.py in the languages folder. Please see [hu.py](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/hu.py) as an example.

### delimiters
This function should return a dictionary where the keys are potential delimiters. For each delimiter you have to define a function (values in dictionary), which returns the number of delimiters in a line. This will be used to determine the most common delimiter in a respective book, and passed to the function below. Feel free to adjust the delimiter counts to determine which delimiter should be used ([en.py](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/en.py) contains examples of multiple delimiters).

### process_file(cfg, dialogs, paragraph_list, filename, delimiter)
This function should extract the dialogs from a book and append them to the *dialogs* parameter, which is a list of dialogs, and each dialog is a list of consecutive utterances. With *cfg* you can access config parameters. *paragraph_list* contains the book as a list of consecutive paragraphs. *filename* is the name of the book file with which you should start each extracted utterance (as in the example), because this is used for later statistics. Finally, *delimiter* is the most common delimiter in this file which should be used to extract dialogs.

### clean_line(line)
This function is used for post-processing the dialogs. It takes as input an utterance on which you can run whatever processing you need (like removing certain characters). Please note that nltk word tokenization is run automatically.
