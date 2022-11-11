import streamlit  as st
from io import StringIO
from PIL import Image
import re
from gensim.parsing.preprocessing import remove_stopwords
import streamlit.components.v1 as components
import pandas as pd
import os

from fuzzywuzzy import fuzz
from fuzzywuzzy import process



# set interface configuration
st.set_page_config(page_title="Translation Assistant", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# add logo
#logo_main = Image.open('logo-main.jpg')
#st.image(logo_main, use_column_width=True)


def app_File():
    st.title("TRANSLATION ASSIST DEMO APPLICATION")
    st.write("English to Urdu")
    uploaded_file = None
    uploaded_file = st.file_uploader("Choose File for Translation")

    if uploaded_file is not None:
        u_up = str(uploaded_file.name)
        st.write(u_up + " is selected")

    # read parallel en-ur data files 
    en_data = open("data-en.txt", 'r', encoding="utf-8").readlines()
    ur_data = open("data-ur.txt", 'r', encoding="utf-8").readlines()

    if 'ur_file' not in st.session_state:
        st.session_state.ur_file = 0

    if os.path.exists("sample-ur.txt"):
        if st.session_state.ur_file == 0:
            os.remove("sample-ur.txt")
            ur_translated_data = open("sample-ur.txt", "w+", encoding="utf-8")
            st.session_state.ur_file = 1

    col1, col2 = st.columns([2,5])

    # initializing keyI for widgets (en-ur strings)
    if 'keyI' not in st.session_state:
        st.session_state.keyI = 0
            
    # initializing indexKeyI widgets (en-ur words)
    if 'indexKeyI' not in st.session_state:
        st.session_state.indexKeyI = 0 
        
    # initializing ur_text for saving translated english text
    if 'ur_text' not in st.session_state:
        st.session_state.ur_text = "" 

    if uploaded_file is not None:
            # To convert to a string based IO:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                
            # read input data file
            en_translation_data = stringio.readlines()
                
            # length of translation lines
            en_translation_len = str(len(en_translation_data))
            
            if st.session_state.keyI < len(en_translation_data):
                with col1:
                    st.subheader("English Text to be Translated: " + "(" + str(st.session_state.keyI + 1) + "/" + str(en_translation_len) + ")")
                    st.write(en_translation_data[st.session_state.keyI])
                
                with col2:
                    st.subheader("Suggested Urdu Translation:")
                    # check if English string is present in data
                    if en_translation_data[st.session_state.keyI].lower() in en_data:
                        
                        # get indices of all occurances string in data
                        en_line_indices = [i for i, x in enumerate(en_data) if x == en_translation_data[st.session_state.keyI].lower()]
                        
                        # initialize variable to store value of English string translation
                        en_string_meaning = ""
                        
                        # iterate of indices and and concatenate translations in single variable
                        for en_line_index in en_line_indices:
                            en_string_meaning = en_string_meaning + " *** " + ur_data[en_line_index]
                        
                        st.write(en_translation_data[st.session_state.keyI] + ": " + en_string_meaning)
                        # display translations of english string
                        st.session_state.en_text_translation = en_string_meaning
                    
                    else:   # if matched string not found (find closest translations using levenshtein distance (fuzzy logic)
                        # levenshtein_distance (ld)
                        ld_en = []                  # list to save ld score measured against each string in database
                        sorted_ld_en = []           # list to save sorted(descending order) ld score
                        for en_string in en_data:   # for each string in En database
                            # append ld score against current En Text
                            ld_en.append(fuzz.token_sort_ratio(en_translation_data[st.session_state.keyI].lower(), en_string))
                        # sort list
                        sorted_ld_en = sorted(ld_en, reverse = True)
                        # variable to save 3 closest translations
                        en_string_meaning = ""
                        for count, value in enumerate(sorted_ld_en):    # for each value in sorted ld score list
                            if count > 2:                               # counter to get only first three elements
                                break;
                            else:
                                # fetch top 3 closest urdu translations and save in variable
                                en_string_meaning = en_string_meaning + " *** " + ur_data[ld_en.index(value)]
                        
                        st.write(en_translation_data[st.session_state.keyI] + ": " + en_string_meaning)
                        # display fetched closest urdu translations
                        st.session_state.en_text_translation = en_string_meaning
                    
                    # remove stop words and punctuations from english string and split remaining string to get main words of string
                    en_main_words_string = re.sub(r'[^\w\s]', '', remove_stopwords(en_translation_data[st.session_state.keyI].lower()))
                    en_main_words = en_main_words_string.split()
                                
                    # for each word check available translations from data and display
                    for en_word in en_main_words:
                        en_word_meaning = ""
                        en_word_indices = [j for j, y in enumerate(en_data) if y == en_word + "\n"]
                        for en_word_index in en_word_indices:
                            en_word_meaning = en_word_meaning + " *** " + ur_data[en_word_index]
                        if en_word_meaning != "":
                            st.write(en_word + ": " + en_word_meaning)
                            st.session_state.indexKeyI += 1 # increment key en-ur words widgets
                st.session_state.keyI += 1
            

            t_input = st.text_input("Compose Urdu Translation:", "", key="ur_text_area")

        
            if t_input!="":
                ur_translated_data = open("sample-ur.txt", "a", encoding="utf-8")
                ur_translated_data.write(st.session_state.ur_text_area + "\n")
            
            
            if st.button("Prepare Translation File"):
                ur_translated_data = open("sample-ur.txt", "r", encoding="utf-8").read()
                st.download_button('Download Translated Text', ur_translated_data, file_name='sample-ur.txt')

                    
                


def app_Word():
    st.title("TRANSLATION ASSIST DEMO APPLICATION")
    st.write("English to Urdu")

    # read parallel en-ur data files 
    en_data = open("data-en.txt", 'r', encoding="utf-8").readlines()
    ur_data = open("data-ur.txt", 'r', encoding="utf-8").readlines()

    
    en_translation_data = st.text_input("Enter Text in English", value='')

    
    if en_translation_data is not "":        
                    
            # check if English string is present in data
            if en_translation_data.lower() in en_data:
            
                # get indices of all occurances string in data
                en_line_indices = [i for i, x in enumerate(en_data) if x == en_translation_data.lower()]
                st.write("Suggestions:\n",+ str())  # display "Suggestions"
                en_string_meaning = ""                                              # initialize variable to store value of English string translation
                
                # iterate of indices and and concatenate translations in single variable
                for en_line_index in en_line_indices:
                    en_string_meaning = en_string_meaning + " *** " + ur_data[en_line_index]
                
                # display translations of english string
                st.write(en_translation_data + ": " + en_string_meaning,+ str())
            st.write('Suggested Urdu Translation')
            # remove stop words and punctuations from english string and split remaining string to get main words of string
            en_main_words_string = re.sub(r'[^\w\s]', '', remove_stopwords(en_translation_data.lower()))
            en_main_words = en_main_words_string.split()
            
            # for each word check available translations from data and display
            for en_word in en_main_words:
                en_word_meaning = ""
                en_word_indices = [j for j, y in enumerate(en_data) if y == en_word + "\n"]
                for en_word_index in en_word_indices:
                    en_word_meaning = en_word_meaning + " *** " + ur_data[en_word_index]
                if en_word_meaning != "":
                    st.write(en_word + ": " + en_word_meaning)
                    







bar = st.sidebar.radio("Select input format", ('File', 'Text'))

if bar == "File":
    # test_check_file = 0
    app_File()

if bar == "Text":
    app_Word()
    st.session_state.keyI = 0
    st.session_state.indexKeyI = 0
