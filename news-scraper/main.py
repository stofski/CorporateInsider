from gnews import GNews
from openai import OpenAI
import json
import sqlite3
import os

# print(str(os.environ.get("OPENAI_API_KEY")))

client = OpenAI(api_key=str(os.environ.get("OPENAI_API_KEY")))

job_name = "Software Developer"
google_news = GNews()
google_news.period = '7d'
google_news.max_results = 20
google_news.country = 'Australia'
# Scrape the top 20 news articles 
amazon_news = google_news.get_news('Amazon')
# print(amazon_news)

# Sort the news articles with the top 10 of relevant to me
prompt = "Sort the following JSON data, with the most relevant to a software developer that works at :" + str(amazon_news)
# print(str(amazon_news))
response = client.chat.completions.create(
  model="gpt-3.5-turbo-1106",
  messages=[
    {
      "role": "system",
      "content": "You will be provided a json data that describes news articles about Amazon. Please sort the news articles in terms of relevance to a software developer at Amazon.Include a mininum of 5 articles. Please output in json format with the following tags; title, relevance to software dev , date. Do not include anything that is not json. I want to be validate the output as json immediately."
    },
    {
      "role": "user",
      "content": str(amazon_news)
    }
  ],
  temperature=0.5,
  max_tokens=1000,
  top_p=1
)

# json_data = json.loads(str(response.choices[0].message.content))

with open('news.txt', 'w') as file:
    file.write(response.choices[0].message.content)

def delete_first_and_last_line(file_path):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Remove the first and last lines
    if len(lines) > 2:
        lines = lines[1:-1]
    else:
        # If the file has less than 3 lines, just clear the content
        lines = []

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)


file_path = 'news.txt'
delete_first_and_last_line(file_path)




