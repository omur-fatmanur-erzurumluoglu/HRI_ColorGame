import speech_recognition as sr
import socket
import json
import time
from playsound import playsound
import pyttsx3

hints = {"red": "The color of tomatoes", "green": "The color of grass", "blue": "The color of sky"}

# to begin socket connection
HOST = "127.0.0.1"
PORT = 12345
colorGameSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
colorGameSocket.bind((HOST, PORT))
colorGameSocket.listen()
connection, address = colorGameSocket.accept()

# to define recognizer with treshold
googleRecognizer = sr.Recognizer()
googleRecognizer.energy_threshold = 4500

sent_message = bytes("", 'UTF-8')

print(f"Connected with {address}")

# to make the robot talk
robot = pyttsx3.init()
robot.say("Hi, I will open my eyes, ears and chest with the color. You try to say the name the color. If it is correct, "
           "I will say correct. If it is wrong, I will say wrong. You can ask for help by saying 'hint'?")
robot.runAndWait()

time.sleep(1)

done = False
while (1):
    received_message = connection.recv(1024)
    if not received_message:
        break

    # to get from robot controller
    message = json.loads(received_message)

    if message["step"] == "play":
        try:
            print("Listening...")
            with sr.Microphone() as source:

                # in each time before the robot will listen, it will adjust the noise level
                googleRecognizer.adjust_for_ambient_noise(source, duration=1)
                robot.say("Guess the color!")
                robot.runAndWait()
                print("Guess the color!")

                # to listen the user's guessed color
                guessed_color = googleRecognizer.listen(source)

                # to use google recognizer
                recognizedText = googleRecognizer.recognize_google(guessed_color, language="en-US")
                recognizedText = recognizedText.lower()
                print(recognizedText)

                # to check if the user's guess is correct or not
                if recognizedText == message["color"]:
                    robot.say("Correct. Good job. ")
                    done = True
                elif recognizedText == "hint" or recognizedText == "help":
                    robot.say("I will give you a hint,       " + hints[message["goal"]])
                else:
                    robot.say("Wrong. Try again. ")
                robot.runAndWait()

                sent_message = bytes(recognizedText, 'UTF-8')

        except sr.UnknownValueError:
            print("Error occurred due to noise")

        except sr.RequestError as e:
            print("Request results can not occur; {0}".format(e))

        # to send to robot controller
        connection.sendall(sent_message)
        if done:
            playsound('indaclub.wav')
            robot.say("Thank you for playing. Bye bye. ")