# gutenberg-dialog &middot; [![twitter](https://img.shields.io/twitter/url/https/shields.io.svg?style=social)](https://ctt.ac/GZedD)
[![Paper](https://img.shields.io/badge/Accepted%20at-EACL%202021-yellow.svg)](https://arxiv.org/abs/2004.12752)
[![Paper](https://img.shields.io/badge/Try-Chatbot-red.svg)](https://ricsinaruto.github.io/chatbot.html)  
Code for downloading and building your own version of the [Gutenberg Dialog Dataset](https://arxiv.org/abs/2004.12752). Easily extendable with new languages. Try trained chatbots in various languages here: https://ricsinaruto.github.io/chatbot.html.


## Download datasets

|Download link | Number of utterances | Average utterance length | Number of dialogues | Average dialogue length |
| :--- | ---: | ---: | ---: | ---: | 
|[**English**](https://mega.nz/file/uZ8iFL4J#__kDHoJVhgv7JOl4sKQtPoTW9COHhlKdzd2U8m95ej0)| 14 773 741 | 22.17 | 2 526 877 | 5.85 |
|[**German**](https://mega.nz/file/jVlGmTbY#gT_-3xMNi2FX5782ybGLcqz2DiCMtE_Ga6QIPZYB8qg) | 226 015 | 24.44 | 43 440 | 5.20 |
|[**Dutch**](https://mega.nz/file/DRFEXTiK#Dh5adlppRc7yoBsZUhf3jPwJvTpZgoyixdw8ELRLjW0) | 129 471 | 24.26 | 23 541 | 5.50 |
|[**Spanish**](https://mega.nz/file/SZ8GiRoY#9oEAG5EYzlKFSiSh_9dpNRhEwVa8m9_GMSDBDH_z7ZE) | 58 174 | 18.62 | 6 912 | 8.42 |
|[**Italian**](https://mega.nz/file/vJF2DDSC#3b-Qjeqi85hhcLeDyun16DIYUMB4iNwGUn47BTBKu6I) | 41 388 | 19.47 | 6 664 | 6.21 |
|[**Hungarian**](https://mega.nz/file/GNFCUJhS#8uEsZa53uCTEzI04_TzzDHmvGmfgbpXAhY5N-unPStM) | 18 816 | 14.68 | 2 826 | 6.66 |
|[**Portuguese**](https://mega.nz/file/eMkgmRIC#7zdi0VGhCZSG2ULqFi6MU0NXndwlhgTEJCaXcvki8sA) | 16 228 | 21.40 | 2 233 | 7.27 |


## Download resources for The Gutenberg Dialogue Dataset paper
#### Download responses from GPT2 trainings [here](https://mega.nz/file/KEkmFBIS#jI4CNeUifjSjVytayl7pXZHiUOMConFifeusP_rUb1c)
#### Download data used in the paper [here](https://mega.nz/file/aIcTiIZR#ZAvDCYOcIaPedfSDXRaLK5-panAJ-Wai99JCMuiIpe4)
#### Download trained models [here](https://mega.nz/file/WcMXBCRZ#9XRnMKPm8t7-YHSVESjGeAHc9l7Ll_3WxQarfIfDfKg)
##### The gpt2_training_scripts folder contains code for running the trainings from the paper. Code adapted from [here](https://github.com/huggingface/transfer-learning-conv-ai).

## Features
  :twisted_rightwards_arrows: &nbsp; Generate your own dataset by tuning parameters affecting the size-quality trade-off of the dataset  
  :rocket: &nbsp; The modular interface makes it easy to extend the dataset to other languages  
  :floppy_disk: &nbsp; You can easily exclude books manually when building the dataset  


## Setup
Run setup.py which installs required packages.
```
python setup.py
```

## Usage
The main file should be called from the root of the repo. The command below runs the dataset building pipeline for the comma-separated languages given as argument. Currently English, German, Dutch, Spanish, Portuguese, Italian, and Hungarian are supported.
```
python code/main.py -l=en,de,nl,es,pt,it,hu -a
```
All settable arguments can bee seen below:  
<a><img src="https://github.com/ricsinaruto/gutenberg-dialog/blob/master/docs/help.png" align="top" height="500" ></a>

### Pipeline steps
The *-a* flag controls whether to run the whole pipeline automatically. If *-a* is omitted a subset of steps have to be specified using flags (see help above). Once a step is finished its output can be used in subsequent steps and it only has run again if parameters or code related to that step is changed. All steps run separately for each language.

#### 1. Download (-d)
Download books for given languages.

**Note:** if all books fail to download with the error "Could not download book", a likely cause is that the default mirror used by the *gutenberg* package has become inaccessible. In the event that this occurs, it is possible to use any of the alternate mirrors listed at https://www.gutenberg.org/MIRRORS.ALL via the *GUTENBERG_MIRROR* environment variable. For example:
```
export GUTENBERG_MIRROR="https://gutenberg.pglaf.org"
python code/main.py ...
```

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

[Languages statistics](https://docs.google.com/spreadsheets/d/15v7lhZJusknd6UfnPfaHIriKvIlShFq2tqTsU7M82bI/edit?usp=sharing)

### delimiters
This function should return a dictionary where the keys are potential delimiters. For each delimiter a function should be defined (values in dictionary), which takes as input a line and returns a number. This number can be for example the count of delimiters, a flag whether there is a delimiter in the line, etc. Usually a weighted count is advisable, depending on the importance of different delimiters. The values will be used to determine the delimiter that should be used in the respective book (passed to the function below), and for filtering books which contain a low amount of delimiters. [en.py](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/code/languages/en.py) contains examples of multiple delimiters.

### process_file(paragraph_list, delimiter)
This function should extract the dialogs from a book and append them to *self.dialogs*, which is a list of dialogs, and each dialog is a list of consecutive utterances. *paragraph_list* contains the book as a list of consecutive paragraphs. *delimiter* is the most common delimiter in this file which should be used to extract dialogs.

### clean_line(line)
This function is used for post-processing dialogs (e.g. remove certain characters). It takes as input an utterance. Please note that nltk word tokenization is run automatically.


## Authors
* **[Richard Csaky](https://ricsinaruto.github.io)** (If you need any help with running the code: ricsinaruto@hotmail.com)

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/ricsinaruto/gutenberg-dialog/blob/master/LICENSE) file for details.  
Please include a link to this repo if you use any of the dataset or code in your work and consider citing the following paper:
```
@inproceedings{Csaky:2021,
    title = "The Gutenberg Dialogue Dataset",
    author = "Cs{\'a}ky, Rich{\'a}rd and Recski, G{\'a}bor",
    booktitle = "Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics",
    month = apr,
    year = "2021",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/2004.12752",
}
```
