#!/usr/bin/python

# *****************************************************************************
#
# Author: Aditya Chatterjee
#
# Interweb/ contacts: GitHub.com/AdiChat
#                     Email: aditianhacker@gmail.com
#
# Implementation of the TextTiling Algorithm
#
# MIT License
#
# To keep up with the latest version, consult repository: GitHub.com/AdiChat/Read-Less
#
# To get an overview of the TextTiling Algorithm, consult wiki: Github.com/AdiChat/Read-Less/wiki/TextTiling
#
# *****************************************************************************

from __future__ import division
import re
import sys
import numpy as np
import os
import glob
from math import sqrt
from collections import Counter
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import brown

lemmatizer = WordNetLemmatizer()
stop_words = stopwords.words('english')

def tokenize_string(input_string, w):
    '''
    Tokenize a string using the following four steps:
        1) Turn all text into lowercase and split into tokens by
           removing all punctuation except for apostrophes and internal
           hyphens
        2) Remove stop words 
        3) Perform lemmatization 
        4) Group the tokens into groups of size w, which represents the 
           pseudo-sentence size.
 
    Arguments :
        input_string : A string to tokenize
        w: pseudo-sentence size

    Returns:
        A tuple (token_sequences, unique_tokens, paragraph_breaks), where:
            token_sequences: A list of token sequences, each w tokens long.
            unique_tokens: A set of all unique words used in the text.
            paragraph_breaks: A list of indices such that paragraph breaks
                              occur immediately after each index.
    '''

    tokens = []
    paragraph_breaks = []
    token_count = 0
    token_sequences = []
    index = 0  
    count = Counter() 

    # split text into paragraphs
    paragraphs = [s.strip() for s in input_string.splitlines()]
    paragraphs = [s for s in paragraphs if s != ""]

    pattern = r"((?:[a-z]+(?:[-'][a-z]+)*))" # For hyphen seperated words

    # Count number of tokens - words and words seperated by hyphen
    for paragraph in paragraphs:
        paragraph_tokens = re.findall(pattern, paragraph)
        tokens.extend(paragraph_tokens)
        token_count += len(paragraph_tokens)
        paragraph_breaks.append(token_count)

    paragraph_breaks = paragraph_breaks[:-1]

    # split tokens into groups of size w
    for i in xrange(len(tokens)):
        count[tokens[i]] += 1
        index += 1
        if index % w == 0:
            token_sequences.append(count)
            count = Counter()
            index = 0

    # remove stop words from each sequence
    for i in xrange(len(token_sequences)):
        token_sequences[i] = [lemmatizer.lemmatize(word) for word in token_sequences[i] if word not in stop_words]

    # lemmatize the words in each sequence
    for i in xrange(len(token_sequences)):
        token_sequences[i] = [lemmatizer.lemmatize(word) for word in token_sequences[i]]

    # get unique tokens
    unique_tokens = [word for word in set(tokens) if word not in stop_words] 

    return (token_sequences, unique_tokens, paragraph_breaks)

def block_score(k, token_sequence, unique_tokens):
    """
    Computes the similarity scores for adjacent blocks of token sequences.
    Args:
        k: the block size
        token_seq_ls: list of token sequences, each of the same length
        unique_tokens: A set of all unique words used in the text.
    Returns:
        list of block scores from gap k through gap (len(token_sequence)-k-2) both inclusive.
    Raises:
        None.
    """
    score_block = []
    before_count = Counter()
    after_count = Counter()

    # calculate score for each gap with at least k token sequences on each side
    for gap_index in range(1, len(token_sequence)):
        current_k = min(gap_index, k, len(token_sequence) - gap_index)
        before_block = token_sequence[gap_index - current_k : gap_index]
        after_block = token_sequence[gap_index : gap_index + current_k]
        
        for j in xrange(current_k):
            before_count = before_count + Counter(token_sequence[gap_index + j - current_k])
            after_count = after_count + Counter(token_sequence[gap_index + j])
        
        # calculate and store score
        numerator = 0.0
        before_sum = 0.0
        after_sum = 0.0

        for token in unique_tokens:
            numerator = numerator + (before_count[token] * after_count[token])
            before_sum = before_sum + (before_count[token] ** 2)
            after_sum = after_sum + (after_count[token] ** 2)

        denominator = sqrt(before_sum * after_sum)

        if denominator == 0:
            denominator = 1

        score_block.append(numerator / denominator)

    return score_block
