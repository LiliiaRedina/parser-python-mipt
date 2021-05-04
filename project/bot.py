import html
import json
import logging
import traceback

from telegram import ParseMode
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from parser_news import Parser, Completeness_of_search
from statistics import Statistics


class Bot:
    def __init__(self):
        self.BOT_TOKEN = "1740832184:AAGf2ZFfdLVhSdjVeuzjX08OeMoEsRaPOuQ"
        self.parser = Parser()
        self.statistics = Statistics()

    def start(self, update: Update, _: CallbackContext):
        user = update.effective_user
        update.message.reply_markdown_v2('Hi {}'.format(user.mention_markdown_v2()))

    def help_command(self, update: Update, _: CallbackContext):
        update.message.reply_text('Все команды: \n\nhelp - показать все, что может бот \n\n' +
                                  'new_docs <N> - показать N самых свежих новостей (по одной на каждую из N тем) \n\n' +
                                  'new_topics <N> - показать N самых свежих тем \n\n' +
                                  'topic <topic_name> - показать описание темы и заголовки 5 самых ' +
                                  'свежих новостей в этой теме \n\n' +
                                  'doc <doc_title> - показать текст документа с заданным заголовком \n\n' +
                                  'words <topic_name> - показать 5 ключевых слов по теме \n\n' +
                                  'describe_doc <doc_title> - вывести статистику по документу. \n' +
                                  '    Статистика: \n' +
                                  '        распределение частот слов \n' +
                                  '        распределение длин слов\n\n' +
                                  'describe_topic <topic_name> - вывести статистику по теме. \n\n' +
                                  '    Статистика: \n' +
                                  '        количество документов в теме \n' +
                                  '        средняя длина документов \n' +
                                  '        распределение частот слов в рамках всей темы \n' +
                                  '        распределение длин слов в рамках всей темы \n\n' +
                                  'drop_parser - сбросить парсер')

    def new_docs(self, update: Update, text):
        num_docs = int(text.args[0])
        update.message.reply_text("Начинаю поиск")

        self.parser.parse(complet_of_search=Completeness_of_search.WITH_SHORT_NEWS,
                          requested_num_topics=num_docs, requested_num_docs=1)

        for i in range(num_docs):
            topic = self.parser.items_list[i]
            update.message.reply_text(topic['title'] + '\n' + topic['link'] + '\n\n' +
                                      topic['docs'][0]['title_news'] + '\n\n' +
                                      topic['docs'][0]['short_text'] + '\n' +
                                      topic['docs'][0]['link_full_news'] + '\n' +
                                      topic['docs'][0]['time_news'])

    def new_topics(self, update: Update, text):
        num_topics = int(text.args[0])
        update.message.reply_text("Начинаю поиск")

        self.parser.parse(complet_of_search=Completeness_of_search.ONLY_TITLE,
                          requested_num_topics=num_topics, requested_num_docs=1)

        for i in range(num_topics):
            topic = self.parser.items_list[i]
            update.message.reply_text(topic['title'] + '\n' + topic['link'] + '\n\n' +
                                      topic['description'] + '\n\n' + topic['num_docs'] + '\n' +
                                      topic['last_update'])

    def topic(self, update: Update, text):
        title_topic = ' '.join(text.args)
        update.message.reply_text("Начинаю поиск")

        const_count_docs = 5

        if self.parser.complet_of_search_parser == 0:
            self.parser.parse(complet_of_search=Completeness_of_search.ONLY_TITLE,
                              requested_num_docs=const_count_docs)

        for topic in self.parser.items_list:
            if topic['title'].lower() == title_topic.lower():
                topic_docs = []
                self.parser.get_add_content_from_news_title(link=topic['link'], docs_list=topic_docs,
                                                            complet_of_search=Completeness_of_search.WITH_SHORT_NEWS)
                topic['docs'] = topic_docs

                update.message.reply_text(topic['title'] + '\n' + topic['link'] + '\n\n' +
                                          topic['description'] + '\n\n' + topic['num_docs'] + '\n' +
                                          topic['last_update'])
                for i in range(const_count_docs):
                    try:
                        update.message.reply_text(topic['docs'][i]['title_news'] + '\n' +
                                                  topic['docs'][i]['link_full_news'] + '\n\n' +
                                                  topic['docs'][i]['time_news'])
                    except:
                        break
                break
        else:
            update.message.reply_text('Такой темы нет:(')

    def doc(self, update: Update, text):
        title_doc = ' '.join(text.args)
        update.message.reply_text("Начинаю поиск")

        if self.parser.complet_of_search_parser != Completeness_of_search.FULL_INFO:
            self.parser.parse(complet_of_search=Completeness_of_search.FULL_INFO)

        for topic in self.parser.items_list:
            for doc in topic['docs']:
                if doc['title_news'].lower() == title_doc.lower():
                    update.message.reply_text(doc['title_news'] + '\n' +
                                              doc['link_full_news'] + '\n\n' +
                                              doc['full_text'] + '\n\n' +
                                              doc['time_news'])
                    return
        else:
            update.message.reply_text('Такой новости нет:(')

    def words(self, update: Update, text):
        title_topic = ' '.join(text.args)
        update.message.reply_text("Начинаю поиск")

        if self.parser.complet_of_search_parser == 0:
            self.parser.parse(complet_of_search=Completeness_of_search.ONLY_TITLE)

        for topic in self.parser.items_list:
            if topic['title'].lower() == title_topic.lower():
                topic_docs = []
                self.parser.get_add_content_from_news_title(link=topic['link'], docs_list=topic_docs,
                                                            complet_of_search=Completeness_of_search.WITH_SHORT_NEWS)
                topic['docs'] = topic_docs

                dict_word_frequency_in_topic = self.statistics.get_stat_topic(topic)[0]

                sorted_tuples_word = sorted(dict_word_frequency_in_topic.items(), key=lambda item: -item[1])

                message_words = ''
                for i in range(5):
                    message_words += (str(sorted_tuples_word[i][0]) + ': ' +
                                      str(sorted_tuples_word[i][1]) + ' раз \n')

                update.message.reply_text(topic['title'] + '\n' + topic['link'] + '\n\n' +
                                          'Ключевые слова: ' + '\n' + message_words)

                break
        else:
            update.message.reply_text('Такой темы нет:(')

    def describe_doc(self, update: Update, text):
        title_doc = ' '.join(text.args)
        update.message.reply_text("Начинаю поиск")

        if self.parser.complet_of_search_parser != Completeness_of_search.FULL_INFO:
            self.parser.parse(complet_of_search=Completeness_of_search.FULL_INFO)

        for topic in self.parser.items_list:
            for doc in topic['docs']:
                if doc['title_news'].lower() == title_doc.lower():
                    dicts = self.statistics.get_stat_doc(doc['full_text'])
                    dict_word_frequency_in_doc = dicts[0]
                    dict_len_word_frequency_in_doc = dicts[1]

                    sorted_tuples_word = sorted(dict_word_frequency_in_doc.items(), key=lambda item: -item[1])
                    sorted_tuples_len = sorted(dict_len_word_frequency_in_doc.items(), key=lambda item: -item[1])

                    message_words = ''
                    message_lens = ''
                    for i in range(5):
                        message_words += (str(sorted_tuples_word[i][0]) + ': ' +
                                          str(sorted_tuples_word[i][1]) + ' раз \n')

                        message_lens += (str(sorted_tuples_len[i][0]) + ': ' +
                                         str(sorted_tuples_len[i][1]) + ' раз \n')

                    update.message.reply_text(doc['title_news'] + '\n' +
                                              doc['link_full_news'] + '\n\n' +
                                              'Длина статьи: ' + str(len(doc['full_text'])) + '\n' +
                                              'Самые частые слова: ' + '\n' + message_words + '\n\n' +
                                              'Самые частые длины:' + '\n' + message_lens)
                    return
        else:
            update.message.reply_text('Такой новости нет:(')

    def describe_topic(self, update: Update, text):
        title_topic = ' '.join(text.args)
        update.message.reply_text("Начинаю поиск")

        if self.parser.complet_of_search_parser == 0:
            self.parser.parse(complet_of_search=Completeness_of_search.ONLY_TITLE)

        for topic in self.parser.items_list:
            if topic['title'].lower() == title_topic.lower():
                topic_docs = []
                self.parser.get_add_content_from_news_title(link=topic['link'], docs_list=topic_docs,
                                                            complet_of_search=Completeness_of_search.WITH_SHORT_NEWS)
                topic['docs'] = topic_docs

                dicts = self.statistics.get_stat_topic(topic)
                dict_word_frequency_in_topic = dicts[0]
                dict_len_word_frequency_in_topic = dicts[1]
                average_len_doc_in_topic = dicts[2]

                sorted_tuples_word = sorted(dict_word_frequency_in_topic.items(), key=lambda item: -item[1])
                sorted_tuples_len = sorted(dict_len_word_frequency_in_topic.items(), key=lambda item: -item[1])

                message_words = ''
                message_lens = ''
                for i in range(5):
                    message_words += (str(sorted_tuples_word[i][0]) + ': ' +
                                      str(sorted_tuples_word[i][1]) + ' раз \n')

                    message_lens += (str(sorted_tuples_len[i][0]) + ': ' +
                                     str(sorted_tuples_len[i][1]) + ' раз \n')

                update.message.reply_text(topic['title'] + '\n' +
                                          topic['link'] + '\n\n' +
                                          'Количество документов в теме:' + topic['num_docs'] + '\n\n' +
                                          'Средняя длина статей: ' + str(average_len_doc_in_topic) + '\n' +
                                          'Самые частые слова: ' + '\n' + message_words + '\n\n' +
                                          'Самые частые длины:' + '\n' + message_lens)

                break
        else:
            update.message.reply_text('Такой темы нет:(')

    def drop_parser(self):
        self.parser.drop_parser()
