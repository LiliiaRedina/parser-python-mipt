from parser_news import Parser, Completeness_of_search
import re


class Statistics:
    def __init__(self):
        self.parser = Parser()

    def get_stat_doc(self, doc_text):
        dict_word_frequency_in_doc = {}
        dict_len_word_frequency_in_doc = {}

        self.word_counter(text=doc_text, dict_word_frequency=dict_word_frequency_in_doc,
                          dict_len_word_frequency=dict_len_word_frequency_in_doc)

        return [dict_word_frequency_in_doc, dict_len_word_frequency_in_doc]

    def get_stat_topic(self, topic):
        average_len_doc_in_topic = 0
        dict_word_frequency_in_topic = {}
        dict_len_word_frequency_in_topic = {}

        total_word_count_in_topic = 0
        num_docs_in_topic = 0

        for doc in topic['docs']:
            num_docs_in_topic += 1
            total_word_count_in_topic += len(doc['full_text'])
            self.word_counter(text=doc['full_text'], dict_word_frequency=dict_word_frequency_in_topic,
                              dict_len_word_frequency=dict_len_word_frequency_in_topic)

        average_len_doc_in_topic = total_word_count_in_topic / num_docs_in_topic

        return [dict_word_frequency_in_topic, dict_len_word_frequency_in_topic, average_len_doc_in_topic]

    def word_counter(self, text, dict_word_frequency, dict_len_word_frequency):
        words_for_counter = re.findall('[a-zа-яё]+', text.lower(), flags=re.IGNORECASE)
        for word in words_for_counter:
            if len(word) > 3:
                count_word = dict_word_frequency.get(word, 0)
                dict_word_frequency[word] = count_word + 1

                count_len = dict_len_word_frequency.get(len(word), 0)
                dict_len_word_frequency[len(word)] = count_len + 1
