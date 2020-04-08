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

### Pipeline steps
The *-a* flag controls whether to run in automatic mode or step-by-step mode. In step mode there are 5 main steps which the program cycles through, asking the user whether specific steps are done and can be skipped.

#### 1. Download
The first step is to download the books. Once they are downloaded this step can be skipped the next time.

#### 2. Pre-filtering
Pre-filtering removes some old books. Once this is done it can be skipped as well, since the books are saved to disk.

#### 3. Dialog extraction
In this step dialogs are extracted from books. When extending the dataset to new languages (see section below), this is the step that can be modified, thus previous steps can be skipped once done. The dialogs in this step are also saved to disk, so if we are happy with the quality of dialogs this step can be skipped as well.

#### 4. Post-filtering
A final filtering step removing some dialogs based on vocabulary.

#### 5. Dataset creation
Putting together the final dataset. Since this is the final step if all previous steps are skipped this has to run.

## Extend to other languages
The code can be easily extended to process other languages. A file named \<language code\>.py has to be created in the languages folder. Here a class should be defined named LANG, with [LANG_base](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/lang.py) as parent. With *self.cfg* config parameters can be accessed. Inside this class the 3 functions below have to be defined. Please see [hu.py](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/hu.py) for an example.

### delimiters
This function should return a dictionary where the keys are potential delimiters. For each delimiter you have to define a function (values in dictionary), which takes as input a line and returns a number. This number can be for example the count of delimiters or a flag whether there is a delimiter in the line, etc. Usually a weighted count is advisable, depending on the importance of different delimiters. The values will be used to determine which delimiter should be used in the respective book (passed to the function below), and for filtering books which contain a low amount of delimiters. [en.py](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/en.py) contains examples of multiple delimiters.

### process_file(paragraph_list, delimiter)
This function should extract the dialogs from a book and append them to *self.dialogs*, which is a list of dialogs, and each dialog is a list of consecutive utterances. *paragraph_list* contains the book as a list of consecutive paragraphs. *delimiter* is the most common delimiter in this file which should be used to extract dialogs.

### clean_line(line)
This function is used for post-processing the dialogs. It takes as input an utterance on which you can run whatever processing you need (like removing certain characters). Please note that nltk word tokenization is run automatically.
