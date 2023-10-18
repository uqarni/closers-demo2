import streamlit as st
from functions import ideator
import json
import os
import sys
from datetime import datetime
from supabase import create_client, Client

#connect to supabase database
urL: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(urL, key)
data, count = supabase.table("bots_dev").select("*").eq("id", "pat").execute()
bot_info = data[1][0]

# id
# org_id
# system_prompt
# max_followup_count
# followup_time
# followup_prompt



def main():
    # Create a title for the chat interface
    st.title("ClosersIO Bot (named Pat)")
    st.write("To test, first select some fields then click the button below.")
  
    #variables for system prompt
    name = 'Pat'
    booking_link = 'closerslbooking.com'
    
    lead_first_name = st.text_input('Lead First Name', value = 'John')
    booked_status = "not yet booked"
    reschedule_link = "N/A"

    system_prompt = bot_info['system_prompt']
    system_prompt = system_prompt.format(lead_first_name = lead_first_name, booking_link = booking_link, agent_name = name, booked_status = booked_status, reschedule_link = reschedule_link)

    initial_text = bot_info['initial_text']
    initial_text = initial_text.format(lead_first_name = lead_first_name, agent_name = name)
    
    if st.button('Click to Start or Restart'):
        st.write(initial_text)
        restart_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('database.jsonl', 'r') as db, open('archive.jsonl','a') as arch:
        # add reset 
            arch.write(json.dumps({"restart": restart_time}) + '\n')
        #copy each line from db to archive
            for line in db:
                arch.write(line)

        #clear database to only first two lines
        with open('database.jsonl', 'w') as f:
        # Override database with initial json files
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": initial_text}            
            ]
            f.write(json.dumps(messages[0])+'\n')
            f.write(json.dumps(messages[1])+'\n')

    userresponse = st.text_input("Enter your message")
    

    # Create a button to submit the user's message
    if st.button("Send"):
        #prep the json
        newline = {"role": "user", "content": userresponse}

        #append to database
        with open('database.jsonl', 'a') as f:
        # Write the new JSON object to the file
            f.write(json.dumps(newline) + '\n')

        #extract messages out to list
        messages = []

        with open('database.jsonl', 'r') as f:
            for line in f:
                json_obj = json.loads(line)
                messages.append(json_obj)

        #generate OpenAI response
        messages, count = ideator(messages)

        #append to database
        with open('database.jsonl', 'a') as f:
                for i in range(count):
                    f.write(json.dumps(messages[-count + i]) + '\n')



        # Display the response in the chat interface
        string = ""

        for message in messages[1:]:
            if 'This is a secret internal thought' not in str(message):
                string = string + message["role"] + ": " + message["content"] + "\n\n"
        st.write(string)
        print(string)

        

if __name__ == '__main__':
    main()