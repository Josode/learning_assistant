import speech_recognition as sr
import pyttsx3
import threading, re, datetime, random
from data import vocab_dict



close = list("1234567890qwertyuiop[asdfghjkl:zxcvbnm,")  # letters and char's that are close together on keyboard
vocab = vocab_dict.VOCAB

class Assistant:
    def __init__(self, bot_name="Dragon"):
        self.bot_name = bot_name
        self.gender = "male"
        self.user_name = "You"

        self.vocab = vocab_dict.VOCAB
        self.previous_responses = []

        self.speak_rate = 185
        self.input_type = ""
        self.session_log = ""
        self.input_type = ""

        # Holds data in save_data.txt
        self.data_types = {}

        # speech recognition
        self.r = sr.Recognizer()
        self.r.operation_timeout = None
        self.mic = sr.Microphone()

        # text to speech
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', self.speak_rate)
        self.voices = self.engine.getProperty("voices")


        # get previous session data from save_data.txt
        self.get_data()
        self.set_gender(self.gender)

    def set_speak_rate(self, speak_rate):
        self.engine.setProperty('rate', speak_rate)

    def set_gender(self, gender):
        self.gender = gender
        self.save_data("voice_gender", self.gender)

        if gender == "female":
            self.engine.setProperty("voice", self.voices[1].id)
        elif gender == "male":
            self.engine.setProperty("voice", self.voices[0].id)

    def clear_chat_history(self):
        with open("data/chat_history.txt", 'w') as file:
            file.write("")

    # returns text of spoken or typed input
    def listen(self, say=None):
        if say is not None:
            # allows Bot to say something and then listen. Kinda like input("text")
            self.say(say)
            self.save_log(say, self.bot_name)

        user_input = ""

        try:
            with self.mic as source:
                print("\nlistening... speak clearly into mic.")
                self.r.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.r.listen(source)
            print("no longer listening.\n")

            user_input = self.r.recognize_google(audio)

            print(self.user_name + ": ", user_input)

        except sr.UnknownValueError:
            print("Error understanding. Speak again.\n")
            self.listen()
        return user_input

    # text to speech
    def say(self, phrase):
        print(self.bot_name + ": ", phrase)
        self.save_log(phrase, self.bot_name)

        self.engine.setProperty('rate', self.speak_rate)
        self.engine.say(phrase)
        try:
            self.engine.runAndWait()
        except RuntimeError:
            pass

    def save_vocab(self):
        with open("data/vocab_dict.py", 'w')as file:
            file.write("VOCAB = " + str(self.vocab))

    # uses matching algorithm to find best fit response
    def getBestResponse(self, message):
        message_list = message.split() # ["how", "are", "you"]
        vocab_list = [] # ["hello there", "how are you", "What is up"]
        score_list = [] # [3, 4, 5]

        try:

            best_match = ""

            for i in vocab:
                vocab_list.append(i)

            for item in vocab_list:
                print("item: " + item)
                score = 0
                len_diff = abs(len(item) - len(message))
                score -= (len_diff)/3

                if item == message:
                    print(item + " == " + message + ", +2")
                    score+=2


                try:
                    if self.previous_responses[-1] in item:
                        print(self.previous_responses[-1] + " in " + item + ", +0.5")
                        score-=1
                    elif self.previous_responses[-2] in item:
                        print(self.previous_responses[-2] + " in " + item + ", +0.3")
                        score-=1
                    elif self.previous_responses[-3] in item:
                        print(self.previous_responses[-3] + " in " + item + ", +0.2")
                        score-= 1
                except IndexError:
                    pass

                item = item.split()
                print(item)

                # itterates through words of each vocab item, compares each to each word in message
                for word in item:
                    for i in range(0, len(message_list)):
                        if word in message_list[i] or message_list[i] in word:
                            if word == "" or message_list[i] == "":
                                continue
                            if len(word) >= 2:
                                score+=1
                                print(word + " in " + message_list[i] + " or vice versa, +0.5")
                        elif word == message_list[i]:
                            print(word + " == " + message_list[i] + ", +1")
                            score+=1

                score_list.append(score)

                print("score: " + str(score_list[-1])+"\n\n")

            top_match = 0
            for num in score_list:
                if num >= top_match:
                    top_match = num

            try:
                best_match = random.choice(vocab[vocab_list[score_list.index(top_match)]])
            except ValueError:
                print("value error")
                pass

            print("best match: " + str(top_match) + "\nmessage: " + message + "\ntrained from: " +
                  vocab_list[score_list.index(top_match)] + "\n\n")

            return [best_match]

        except KeyError:
            return ["No response, please train."]

    def loop(self, message):
        if self.user_name + ": " in message:
            message.replace(self.user_name + ": ", "")

        # if input NOT in vocab
        if message not in self.vocab:
            '''
            print("please train:")
            self.vocab[message] = []

            temp_response = self.listen()
            # add response as value to key
            temp_response = temp_response.lower()
            self.vocab[message].append(str(temp_response))

            self.save_vocab()
            return [temp_response, True]
            '''
            best_response = self.getBestResponse(message)[0]

            return [best_response, False]

        # if input IS IN vocab
        else:
            response = self.vocab[message]

            # add response as value to key
            temp_response = response
            temp_response = temp_response.lower()
            return [response, False]


    # returns response of passed user_input
    def get_conversational_response(self, user_input):
        trainer = self.loop(user_input)
        while trainer[1] is True:
            trainer = self.loop(trainer[0])
        self.previous_responses.append(trainer[0])
        return trainer[0]

    # begins new session
    def begin_session(self):
        # indicate new session in chat log file
        new_session_save = "\n\nSESSION LOG FROM " + datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        self.save_log(new_session_save, speaker="")

        # if encountering brand new user (grader)
        if self.user_name == "You":
            self.say("Hello, it looks like we haven't met before. I'm your personal assistant!")
            self.say("You can ask about what I can do, or we can just talk.\n")

            # get users name
            response = self.command("change my name")
            self.say(response)

        # get users input
        user_in = self.listen().lower()
        self.save_log(user_in, self.user_name)

        # finds command and returns answer
        bot_response = self.command(user_in)

        # no relavent command found, use conversational response from cleverbot
        if bot_response is None:
            bot_response = self.get_conversational_response(user_in).lower()

            # add comments relavent to user interests for more personalized conversation
            for data in self.data_types:
                if data in bot_response:
                    self.say(bot_response)

                    self.say("Speaking of which, didn't you tell me your favorite " + data + " was "
                            + self.data_types[data] + "?")
                    break
                else:
                    self.say(bot_response)
                    break
        else:
            self.say(bot_response)


    # saves/updates log of session to file "chat_history.txt"
    def save_log(self, phrase, speaker):

        with open("data/chat_history.txt", 'a') as file:
            if speaker != "":
                try:
                    file.write(speaker + ": " + phrase + "\n")
                except:
                    file.write(speaker + ": " + "Error saving message." + "\n")
            else:
                file.write(phrase + "\n")

    # save data like users name, bots name, and user facts across sessions
    def save_data(self, type, data):
        self.data_types[type] = data

        with open("data/save_data.txt", 'w') as file:
            for key in self.data_types:
                file.write(key + ":" + self.data_types[key] + "\n")

    # get data from previous sessions (users name, etc)
    def get_data(self):

        with open("data/save_data.txt", 'r') as file:
            lines = file.readlines()

            for line in lines:

                line = line.replace("\n", "").split(":")
                type = line[0]
                data = line[1]

                # add data to dict

                self.data_types[type] = data
                if type == "user_name":
                    self.user_name = data
                if type == "bot_name":
                    self.bot_name = data
                if type == "voice_gender":
                    self.gender = data

# COMMANDS: looks for relevant command, otherwise returns None
    def command(self, user_input):
        user_input = user_input.lower()

        # HELP
        if ("what can you do" in user_input or "what do you do" in user_input or "what can i ask" in user_input):
            help_message = "I can do lots of things.\n" \
                           "- We can have a conversation about anything\n" \
                           "- Try telling me what all of your favorite things are\n" \
                           "- Ask me for the time or date\n" \
                           "- You can set reminders and timers\n" \
                           "- Ask to change my name or your name\n" \
                           "- You can also change my voice to male or female\n" \
                           "- I can generate a random number\n"
            return help_message

        # date?
        elif( "what" in user_input) and ("day" in user_input or "date" in user_input) and ("is" in user_input):
            date = datetime.datetime.now()
            return_msg = "It's " + date.strftime('%A %B %d, %Y')
            return return_msg

        # time?
        elif "what" in user_input and "time" in user_input:
            time = datetime.datetime.now().strftime("%I:%M %p")
            return_msg = "It's currently " + time
            return return_msg

        #create backup of vacab_dict
        elif ("create" in user_input and "backup" in user_input):
            filename = "vocab_" + datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
            with open("backups/"+filename, 'w')as backup_:
                backup_.write(str(self.vocab))

        # change bots voice gender
        elif "change" in user_input and ("voice" in user_input or "gender" in user_input):
            if "female" in user_input or "girl" in user_input or "woman" in user_input:
                self.set_gender("female")
                return "Alright, I changed my voice to female."
            elif ("male" in user_input or "boy" in user_input or "man" in user_input) and "female" not in user_input:
                self.set_gender("male")
                return "Alright, I changed my voice to male"
            else:
                self.say("Do you want a male voice or a female voice?")
                new_gender = self.listen()
                if new_gender != "male" or new_gender != "female":
                    return "I only have a male and a female voice."
                self.set_gender(new_gender)
                return "Alright, I changed my voice to " + self.gender

        # change bots name
        elif ("you" in user_input or "your" in user_input) and ("call" in user_input or "name" in user_input)\
                and (("change" in user_input) or "give" in user_input):

            user_answer = self.listen("What do you want my new name to be? I hope it's a good one...")
            self.bot_name = user_answer
            self.save_log(user_answer, self.user_name)
            self.save_data(type="bot_name", data=self.bot_name)
            return self.bot_name + ". I like it. It has a nice ring to it."

        # what's bots name?
        elif ("what" in user_input) and ("your" in user_input) and ("name" in user_input):
            if self.user_name != "You":
                return "My current name is " + self.bot_name + ". You can change what my name is, just ask."
            else:
                return "You haven't given me a name yet. "

        # what's my name?
        elif ("what" in user_input) and ("my" in user_input) and ("name" in user_input):
            if user_input.index("what") < user_input.index("my") and user_input.index("my") < user_input.index("name"):
                if self.user_name != "You":
                    return "You told me to call you " + self.user_name
                else:
                    return "You haven't told me your name yet. Just ask me to change it, and I'll remember it!"

        # change users name
        elif (("my" in user_input or "me" in user_input) and ("name" in user_input) and
                ("change" in user_input or "is" in user_input)) or "call me" in user_input:

            if "change my name to" in user_input or "call me" in user_input or "my name is" in user_input:
                new_user_name = user_input.split()
                user_answer = new_user_name[-1]
                self.user_name = user_answer
            else:
                user_answer = self.listen("What do you want me to call you?")
                self.user_name = user_answer

            self.save_data(type="user_name", data=self.user_name)
            return "Alright " + self.user_name + ", I'll start calling you that."

        # remembers facts about the user, such as "my favorite color is pink"
        elif "my favorite" in user_input and "is" in user_input and len(user_input) >= 5 and "what" not in user_input\
                and "least" not in user_input:

            user_data = user_input.split()

            data_type = ''
            data_val = ''

            # "my favorite color is blue"
            if user_data.index("is") > user_data.index("favorite"):
                for i in range(user_data.index('favorite') + 1, user_data.index('is')):
                    data_type = data_type + user_data[i] + " "
                for i in range(user_data.index("is") + 1, len(user_data)):
                    data_val = data_val + user_data[i] + " "

                self.save_data(data_type.strip(), data_val.strip())
                return data_val + "? Good choice."

        # what is my favorite _______
        elif ("what" in user_input or "who" in user_input) and "my favorite" in user_input:
            user_data = user_input.replace("?", "").split()
            data_type = ""
            data_val = ""

            if user_data.index("favorite") > user_data.index("my"):
                for i in range(user_data.index('favorite') + 1, len(user_data)):
                    data_type = data_type + user_data[i] + " "

            data_type = data_type.strip()

            if data_type in self.data_types:
                data_val = self.data_types[data_type]
                return "You told me your favorite " + data_type + " is " + data_val
            else:
                return "You haven't told me what your favorite " + data_type + " is."

        # generate a random number
        elif (("number" in user_input) and (("generate") or ("create") or ("give me") in user_input)):
            num_list = list(map(int, re.findall('\d+', user_input)))
            if(len(num_list) >= 2):
                num1 = num_list[0]
                num2 = num_list[1]

                return random.randrange(num1, num2)
            else:
                if len(num_list) < 2:
                    return random.randrange(0, 100)

        # set a reminder
        elif ("start" in user_input or "set" in user_input or "make" in user_input or "create" in
            user_input or "me to" in user_input) and ("reminder" in user_input or "remind" in user_input):

            desciption = ""

            def reminder():

                self.say("What would you like to be reminded of?")
                description = self.listen()

                self.say("In how long would you like to be reminded?")
                length = self.listen()

                def start_():
                    self.say("You asked me to remind you this: " + description + "\n")

                # Determines if user is using seconds or minutes
                if "sec" in length:
                    # extracts letters and turns time into just number
                    length_num = float(int(re.sub("\D", "", length)))
                    if type(length_num) is not float:
                        self.say("Sorry, I only speak in integers...")
                        reminder()

                    if length_num > 1 or length_num == 0:
                        self.say("Ok, I'll remind you in " + str(length_num) + " seconds.")
                    elif length_num == 1:
                        self.say("Ok, I'll remind you in " + str(length_num) + " second.")
                    else:
                        self.say("Time can't go backwards...")
                    t = threading.Timer(length_num, start_)
                    t.start()

                elif "min" in length:
                    # extracts letters and turns time into just number
                    length_num = float(int(re.sub("\D", "", length)))
                    if type(length_num) is not float:
                        self.say("Sorry, I only speak in integers...")
                        reminder()

                    if length_num > 1 or length_num == 0:
                        self.say("Ok, I'll remind you in " + str(length_num) + " minutes.")
                    elif length_num == 1:
                        self.say("Ok, I'll remind you in " + str(length_num) + " minute.")
                    else:
                        self.say("Time can't go backwards...")
                    t = threading.Timer(length_num * 60, start_)
                    t.start()

                else:
                    self.say("Please specify how many seconds or minutes you want. (Ex: 25 seconds)")
                    return reminder()
            return reminder()

        elif ("start" in user_input or "set" in user_input or "make" in user_input or "create" in
                user_input or "me to" in user_input) and ("timer" in user_input):

            def start_():
                self.say("Your timer is done!\n")

            if "for" in user_input and ("sec" in user_input or "min" in user_input):
                timer_len = float(re.sub("\D", "", user_input))

                if "min" in user_input and timer_len >= 0:
                    t = threading.Timer(timer_len, start_)
                    t.start()
                    return "Alright, I started a " + str(timer_len) + " minute timer."
                elif "sec" in user_input and timer_len >= 0:
                    t = threading.Timer(timer_len, start_)
                    t.start()
                    return "Alright, I started a " + str(timer_len) + " second timer."

            else:
                response = self.listen("For how long?")
                timer_len = float(re.sub("\D", "", response))

                if "min" in response and timer_len >= 0:
                    t = threading.Timer(timer_len, start_)
                    t.start()
                    return "Alright, I started a " + str(timer_len) + " minute timer."
                elif "sec" in response and timer_len >= 0:
                    t = threading.Timer(timer_len, start_)
                    t.start()
                    return "Alright, I started a " + str(timer_len) + " second timer."

        # No command for input
        else:
            return None