from tkinter import *
from Assistant import Assistant
import os, time, webbrowser, random
import Trainer

class DragonAI(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.assistant = Assistant()

        self.prev_message = ""


        menu = Menu(self.master)
        self.master.config(menu=menu, bd=5)

        # File
        file = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Save Chat Log", command=self.save_chat)
        file.add_command(label="Clear Chat", command=self.clear_chat)
        file.add_separator()
        file.add_command(label="Exit", command=self.client_exit)

        # Options
        options = Menu(menu, tearoff=0)
        menu.add_cascade(label="Options", menu=options)

            # Train
        train = Menu(options, tearoff=0)
        options.add_cascade(label="Train", menu=train)
        train.add_command(label="/r/CasualConversation", command=lambda: self.train_subreddit(
            subreddit="casualconversation"))
        train.add_command(label="/r/Science", command=lambda: self.train_subreddit(subreddit="science"))
        train.add_command(label="/r/Python", command=lambda: self.train_subreddit(subreddit="python"))
        train.add_command(label="/r/Teenagers", command=lambda: self.train_subreddit(subreddit="teenagers"))
        train.add_command(label="/r/Minecraft", command=lambda: self.train_subreddit(subreddit="minecraft"))
        train.add_command(label="/r/Rocketleague", command=lambda: self.train_subreddit(subreddit="rocketleague"))
        train.add_command(label="/r/Philosophy", command=lambda: self.train_subreddit(subreddit="philosophy"))



            # Clear Vocabulary
        options.add_command(label="Clear vocabulary", command=lambda: self.clear_vocab())

        options.add_command(label="Backup vocabulary", command=lambda: self.backup_vocab())

        # Help
        help_option = Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_option)

        help_option.add_command(label="Features", command=self.features_msg)
        help_option.add_command(label="About", command=self.about_msg)
        help_option.add_command(label="Source Code", command=self.src_code_msg)

        self.interface()
        self.update()

    def interface(self):
        # Main Frame

        self.mainFrame = Frame(self.master, bg="#00315C", bd="10")
        self.mainFrame.grid_columnconfigure(0, weight=1)
        self.mainFrame.pack(expand=True, fill=BOTH,side=TOP)

        # Chat interface

        # frame containing text box with messages and scrollbar
        self.text_frame = Frame(self.mainFrame, bd=6)
        self.text_frame.pack(expand=True, side=TOP, fill=BOTH)

        # scrollbar for text box
        self.text_box_scrollbar = Scrollbar(self.text_frame, bd=0)
        self.text_box_scrollbar.pack(fill=Y, side=RIGHT)

        # contains messages
        self.text_box = Text(self.text_frame, yscrollcommand=self.text_box_scrollbar.set, state=DISABLED,
                             bd=1, padx=6, pady=6, spacing3=8, wrap=WORD, bg=None, font="Verdana 10", relief=GROOVE,
                             width=10, height=1)
        self.text_box.pack(expand=True, fill=BOTH)
        self.text_box_scrollbar.config(command=self.text_box.yview)

        # Bottom Frame

        self.bottomFrame = Frame(self.mainFrame, bg='white', bd='0')
        self.bottomFrame.grid_columnconfigure(0, weight=1)
        self.bottomFrame.pack(fill=BOTH)

        # mic button
        self.micButton = Button(self.bottomFrame, command=lambda: self.listen(), bg="#30C8EB", bd=5,
                                relief=FLAT, activebackground="#C4F4FF")
        self.microphoneImage = PhotoImage(file="pictures/mic.png")
        self.micButton.config(image=self.microphoneImage)
        self.micButton.pack(side=LEFT, expand=True, fill=BOTH)

        # brain button
        self.brainButton = Button(self.bottomFrame, command=lambda: self.train(), bg="#3dcc30", bd=5,
                                relief=FLAT, activebackground="#a7ff89")
        self.brainImage = PhotoImage(file="pictures/brain.png")
        self.brainButton.config(image=self.brainImage)
        self.brainButton.pack(side=RIGHT, expand=True, fill=BOTH)

        # loop button
        self.loopButton = Button(self.bottomFrame, command=lambda: self.start_session(), bg="#ffff0f", bd=5,
                                  relief=FLAT, activebackground="#ffff93")
        self.loopImage = PhotoImage(file="pictures/loop.png")
        self.loopButton.config(image=self.loopImage)
        self.loopButton.pack(side=RIGHT, expand=True, fill=BOTH)

    def listen(self):
        self.input_ = self.assistant.listen().lower()
        self.prev_message = self.input_
        self.write_text(self.assistant.user_name + ": " + self.input_)
        self.respond()

    def listen_train(self):
        self.input_ = self.assistant.listen().lower()
        self.write_text('Trained new response for "'+ self.prev_message + '": "' + self.input_ + '"')
        return self.input_

    def run_train(self):
        try:
            self.assistant.vocab[self.prev_message].append(self.listen_train())
        except AttributeError:
            self.assistant.vocab[self.prev_message] = self.listen_train()

        self.assistant.save_vocab()

    def train(self):

        try:
            self.run_train()
        except KeyError:
            self.assistant.vocab[self.prev_message] = []
            self.run_train()

    def respond(self):
        response = self.assistant.command(user_input=self.input_)

        if response is None:
            self.assistant.save_vocab()
            try:
                response = self.assistant.get_conversational_response(self.input_)
            except ValueError:
                response = "No responses, please train!"
        else:
            print("passed")
            pass
        self.write_text(self.assistant.bot_name + ": " + str(response))
        self.assistant.say(response)


        self.assistant.vocab[self.input_] = response

    # File functions
    def client_exit(self):
        exit()

    def save_chat(self):
        # creates unique name for chat log file
        time_file = str(time.strftime('%X %x'))
        remove = ":/ "
        for var in remove:
            time_file = time_file.replace(var, "_")

        # gets current directory of program. creates "logs" folder to store chat logs.
        path = os.getcwd() + "\\logs\\"
        new_name = path + "log_" + time_file
        saved = "Chat log saved to {}\n".format(new_name)

        # saves chat log file
        try:
            with open(new_name, 'w')as file:
                self.text_box.configure(state=NORMAL)
                log = self.text_box.get(1.0, END)
                file.write(log)
                self.text_box.insert(END, saved)
                self.text_box.see(END)
                self.text_box.configure(state=DISABLED)

        except UnicodeEncodeError:
            pass

    # clears chat
    def clear_chat(self):
        self.text_box.config(state=NORMAL)
        self.text_box.delete(1.0, END)
        self.text_box.delete(1.0, END)
        self.text_box.config(state=DISABLED)

    # Help functions
    def features_msg(self):
        pass

    def about_msg(self):
        pass

    def src_code_msg(self):
        webbrowser.open('https://github.com/Josode/Python-Chat-Interface')


    def write_text(self, text):
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, text+"\n")
        self.text_box.see(END)
        self.text_box.configure(state=DISABLED)

    def train_subreddit(self, subreddit):
        self.write_text("Training on /r/" + subreddit + "...")
        r = Trainer.bot_login()
        Trainer.subreddit = subreddit
        Trainer.run_bot(r)
        self.write_text("Training finished.")

    def clear_vocab(self):
        with open("data/vocab_dict.py", "w"):
            pass
        self.write_text("Vocabulary cleared.")
        self.assistant.vocab = {}
        self.assistant.save_vocab()

    def start_session(self):
        self.write_text("Listening and responding...")

        while True:
            self.assistant.begin_session()

    def backup_vocab(self):
        filename = "backups/vocab" + str(random.randint(0, 100000))
        with open(filename, 'w')as backup_:
            backup_.write("VOCAB =" + str(self.assistant.vocab))

        print("backup saved: " + filename)
        self.write_text("backup saved: " + filename)


root = Tk()
root.title("DragonAI")
root.minsize(600, 600)
root.geometry("600x600")
root.iconbitmap(default='pictures/neural.png')

dragon = DragonAI(root)
root.mainloop()