import numpy as np
import pandas as pd
import glob
import re

# sklearn
import sklearn
import sklearn.preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
# metrics
from sklearn.metrics import classification_report

# NLTK
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

# ----------------------------------- Setup -----------------------------------
# INSERT YOUR DATA HERE
# Expected format: One folder per class, e.g.
# train
# --- sports
# |   +-- sports_01.txt
# |   +-- sports_02.txt
# --- politics
# |   +-- politics_01.txt
# |   +-- politics_02.txt
# --- ...
# |   +-- ...txt
#
# Example: https://github.com/jrieke/traingenerator/tree/main/data/text-data
train_data = "data/text-data/train"  # required
val_data = None    # optional
test_data = "data/text-data/test"                # optional

# ------------------------------- Preprocessing -------------------------------
# Set up label encoder.
encoder = sklearn.preprocessing.LabelEncoder()

def preprocess(data, name):
    if data is None:    # val/test can be empty
        return None
    
    # Read documents into Python lists
    documents = [[document.split("\\")[-1], open(document,encoding='utf-8').read(), document.split("\\")[-2]] for document in glob.glob(data + "/*/*.txt")]
    
    # Load them into Pandas DataFrame (easier visualization)
    documents = pd.DataFrame(documents, columns=["doc_name", "text", "class"])

    # Encode label
    if name == "train":
        encoder.fit(documents["class"].values)
    documents["class_encoded"] = documents["class"].apply(lambda x: encoder.transform([x])[0])

    # Cleaning and tokenization
    documents["cleaned"] = documents["text"].apply(lambda x: clean(x))
    documents["tokens"] = documents["cleaned"].apply(lambda x: tokenize(x))

    # Uncomment next line to preview your data
    # print(documents.head())

    labels = documents["class_encoded"].values
    documents = [" ".join(document) for document in documents["tokens"].values]

    # Shuffle train set
    if name == "train":
        documents, labels = sklearn.utils.shuffle(documents, labels)
    
    return [documents, labels]

def clean(document):
    # Regular expression to remove special characters
    replace_no_space = re.compile("(\&)|(\%)|(\$)|(\€)|(\.)|(\;)|(\:)|(\!)|(\')|(\?)|(\,)|(\")|(\()|(\))|(\[)|(\])|(\d+)|(\⁰)|(\•)|(\\')")
    replace_with_space = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)")

    document = replace_no_space.sub("", document.lower())
    document = replace_with_space.sub(" ", document)
    
    return document

def tokenize(document):
    stopset = set(stopwords.words("english"))

    # Tokenize
    tokens = wordpunct_tokenize(document)

    # Stopwords removed
    tokens = [token for token in tokens if token not in stopset and len(token) > 2]
    
    # Text normalization
    text_normalization = "stemming"

    if text_normalization == "stemming":
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]
    elif text_normalization == "lemmatize":
        stemmer = WordNetLemmatizer()
        tokens = [stemmer.lemmatize(token) for token in tokens]
    
    return tokens

processed_train_data = preprocess(train_data, "train")
processed_val_data = preprocess(val_data, "val")
processed_test_data = preprocess(test_data, "test")


# ----------------------------------- Model -----------------------------------
# Don´t forget that you can customize the parameters of both vectorizer and model
if True:
    model = Pipeline([('count', CountVectorizer()),
                     ('clf', SVC())])
elif False:
    model = Pipeline([('tfidf', TfidfVectorizer()),
                     ('clf', BernoulliNB())])

# ----------------------------------- Training -----------------------------------
def evaluate(data, name):
    if data is None:  # val/test can be empty
        return

    documents, labels = data
    acc = model.score(documents, labels)
    print(f"{name + ':':6} accuracy: {acc}")

    if True:
        y_pred = model.predict(documents)
        print(classification_report(labels, y_pred, target_names=encoder.classes_))

# Train on train_data.
model.fit(*processed_train_data)

# Evaluate on all datasets.
evaluate(processed_train_data, "train")
evaluate(processed_val_data, "val")
evaluate(processed_test_data, "test")