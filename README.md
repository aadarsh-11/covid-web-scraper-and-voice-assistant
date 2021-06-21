# Covid19-web-scraper-and-voice-assistant
A python application which scraps data from worldometers using parsehub and use voice to interact and get the data

## Description
1. Parsehub is a tool which does the web scraping work for us and provide us an api to get the scraped data.
2. In this project an api project is created by scraping data from [worldometers](https://www.worldometers.info/coronavirus/) and using it the the python program.
3. The api provides the details for population, total cases, total deaths, active cases etc for all the available countries.
4. Using pyttsx3 for text-to-speech and speechrecognition for speech-to-text, the program interfaces interaction using voice.
5. From the extracted text specific keywords are filtered using regex patterns and the corresponding data is collected.
6. The data is then given as output through both speech and text.
7. The scraping takes time on the parsehub servers(around 5-10 mins) and hence the data is not scraped continiously, so to update the data a post request is made to parsehub commanding it to scrape the website again.
8. This request is triggered when the user says update in any of its input.
9. The concept of threadding is used to check if the data is update in the background and hence the program still works using its previous data.
10. when the data is updated the background checking is stopped and the search is now done on the updated data.
