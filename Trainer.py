import praw, re
from data import Config, vocab_dict

alphabetnums = 'abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+{}|":><?~`-=[]\'/., '
vocab = vocab_dict.VOCAB
subreddit = ""
comments_to_train = 200


def save_vocab():
    with open("D:/programs/DragonAI/data/vocab_dict.py", 'w')as file:
        try:
            file.write("VOCAB = " + str(vocab).lower())
        except UnicodeEncodeError:
            print("\n\n\nError, unicode. Skipping.\n\n\n")

def run_bot(r):
    sub = r.subreddit(subreddit)
    submissions = sub.stream.submissions()
    comment_number = 0

    for submission in submissions:

        if comment_number >= comments_to_train:
            break

        for top_level_comment in submission.comments:
            comment_number += 1

            if comment_number >= comments_to_train:
                break

            top_level_comment_ = re.sub('[~!@#$%^&*()_+{}|:"<>?.]', '', top_level_comment.body)
            for second_level_comment in top_level_comment.replies:
                try:
                    second_level_comment_ = re.sub('[~!@#$%^&*()_+{}|:"<>?.]', '', second_level_comment.body)

                    print("\nCOMMENT: " + top_level_comment_)
                    print("REPLY: " + second_level_comment_)
                    count1 = 0
                    count2 = 0

                    for char in top_level_comment.body.lower():
                        if char in alphabetnums:
                            count1 += 1

                    for char in second_level_comment.body.lower():
                        if char in alphabetnums:
                            count2 += 1

                    if (count1 >= int(len(top_level_comment.body.lower()))) and \
                            (count2 >= int(len(second_level_comment.body.lower()))):
                        list_ = []
                        list_.append(re.sub('[~!@#$%^&*()_+{}|:"<>?]', '', second_level_comment.body))
                        vocab[re.sub('[~!@#$%^&*()_+{}|:"<>?]', '', top_level_comment.body)] = list_
                        save_vocab()


                except AttributeError:
                    pass
    print("training finished.")


def bot_login():
    reddit = praw.Reddit(username=Config.username,
                         password=Config.password,
                         client_id=Config.client_id,
                         client_secret=Config.client_secret,
                         user_agent="I am testing a bot.")
    print(reddit.user.me())

    return reddit
