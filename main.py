import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time
import config

API_KEY = config.API_KEY
PROJECT_TOKEN = config.PROJECT_TOKEN
RUN_TOKEN = config.RUN_TOKEN

class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {"api_key": self.api_key}
        self.data = self.get_data()

    def get_data(self):
        # post = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run',params = self.params)
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data',
                                params=self.params)
        data = json.loads(response.text)
        return data

    def get_total_cases(self):
        for contents in self.data["total"]:
            if contents['name'] == "Coronavirus Cases:":
                return contents['value']

    def get_total_deaths(self):
        for contents in self.data["total"]:
            if contents['name'] == "Deaths:":
                return contents['value']
        return "0"

    def get_total_recovered(self):
        for contents in self.data["total"]:
            if contents['name'] == "Recovered:":
                return contents['value']
        return "0"

    def get_country_data(self, country):
        for contents in self.data["country"]:
            if contents['name'].lower() == country.lower():
                return contents
        return "0"

    def get_list_of_countries(self):
        countries = []
        for country in self.data["country"]:
            countries.append(country["name"].lower())
        return countries

    def update(self):
        post = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)

        def thread_func():

            old_data = self.data
            update_msg = "Data is being updated in the background, you may continue as this might take a moment!"
            speak(update_msg)
            print("\nUpdate in Progress...")

            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    try:
                        speak("great! the data is sucessfully updated!")
                    except:
                        pass
                    print("\nData Updated!")
                    break
                time.sleep(5)

        new_thread = threading.Thread(target=thread_func)
        new_thread.start()


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Oops, didn't catch you this time!! ", str(e))

    return said.lower()

def get_country_details(data,country):

    print("\n",country.upper() +" :")
    print("Population :", data.get_country_data(country.lower())["population"])
    msg = "Okay, the population of "+ country +" is "
    speak(msg + str(data.get_country_data(country.lower())["population"]))
    # time.sleep(1)

    print("Total cases :", data.get_country_data(country.lower())["total_cases"])
    msg = "Currently its total covid cases are "
    speak(msg + str(data.get_country_data(country.lower())["total_cases"]))
    # time.sleep(1)

    print("Active cases :", data.get_country_data(country.lower())["active_cases"])
    msg = "Its active covid cases are "
    speak(msg + str(data.get_country_data(country.lower())["active_cases"]))
    # time.sleep(1)

    print("Total deaths :", data.get_country_data(country.lower())["total_deaths"])
    msg = "and, so far "
    speak(msg + str(data.get_country_data(country.lower())["total_deaths"] + " people have died from the disease"))
    # time.sleep(1)

    permill = int(data.get_country_data(country.lower())["total_cases"].replace(',', ''))*1000000 // int(data.get_country_data(country.lower())["population"].replace(',', ''))
    print("Total cases per million :", permill)
    msg = "We can also say that, for     every million citizens "
    speak(msg + str(permill) +" people are infected by the pandemic!")
    speak("okay, thats all for "+ country)

def main():
    data = Data(API_KEY, PROJECT_TOKEN)
    country_list = data.get_list_of_countries()
    print("Program Started!!")
    welcome = "Hello and Welcome to our coronavirus web scraping and voice assistant project. I am you voice assistant."
    speak(welcome)
    # print("\nPlease speak out your name... ")
    # name = get_audio()
    # time.sleep(2)
    welcome = "\nAlright, Let's get you started."
    print(welcome)
    speak(welcome)

    END_PHRASE = ['finish', 'stop', 'exit']

    TOTAL_PATTERN = {
        re.compile("[\w\s]* total [\w\s]+ cases"): data.get_total_cases,
        re.compile("[\w\s]* total cases"): data.get_total_cases,
        re.compile("[\w\s]* total death"): data.get_total_deaths,
        re.compile("[\w\s]* total [\w\s]+ death"): data.get_total_deaths,
        re.compile("[\w\s]* total deaths"): data.get_total_deaths,
        re.compile("[\w\s]* total [\w\s]+ deaths"): data.get_total_deaths
    }

    COUNTRY_PATTERN = {
        re.compile("[\w\s]+ details [\w\s]"): lambda country: country,
        re.compile("[\w\s]+ everything [\w\s]"): lambda country: country,
        re.compile("[\w\s]+ information [\w\s]"): lambda country: country,
        re.compile("[\w\s]+ cases [\w\s]"): lambda country: data.get_country_data(country.lower())["total_cases"],
        re.compile("[\w\s]+ death [\w\s]"): lambda country: data.get_country_data(country.lower())["total_deaths"],
        re.compile("[\w\s]+ deaths [\w\s]"): lambda country: data.get_country_data(country.lower())["total_deaths"]
    }

    UPDATE_PATTERN = "update"

    while True:
        print("\nListening...")
        text = get_audio()
        print(text)
        result = None
        matched = False
        EXIT = 0

        if text == UPDATE_PATTERN:
            data.update()
            time.sleep(7)

        for pattern, func in COUNTRY_PATTERN.items():
            if pattern.match(text):
                words = text.split(" ")
                for country in country_list:
                    if country in words:
                        result = func(country)
                        print("matched")
                        matched = True
                        break
                break

        for pattern, func in TOTAL_PATTERN.items():
            if matched:
                break
            elif pattern.match(text):
                result = func()
                print("matched")
                break

        if result in country_list:
            get_country_details(data,country)

        elif result != None:
            print(result)
            speak(result)

        for end in END_PHRASE:
            if text.find(end) != -1:
                EXIT = 1
                break

        if EXIT:
            break

    print("\nThank you!!")
    speak("Alright, let's wrap up for now, Thank you!, and remember, do gaj ki duri, mask hai zaruri!")

main()
