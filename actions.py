# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa-pro/concepts/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


"""from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
from rasa_sdk.events import SlotSet


# Load the Excel file
df = pd.read_csv("Home Remedies (1).csv")  # Make sure the path is correct

# Store the user session's progress in a dictionary
user_remedy_progress = {}

class ActionProvideHomeRemedy(Action):
    def name(self) -> Text:
        return "action_provide_home_remedy"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = tracker.sender_id  # Unique ID for the user
        user_message = tracker.latest_message.get("text", "").lower()


        health_issue = tracker.get_slot("health_issue")

        # Extract the health issue from user input (if it's a new query)
        if not health_issue:
            health_issues = df["Health Issue"].str.lower().tolist()
            matching_issues = [issue for issue in health_issues if issue in user_message]

            if not matching_issues:
                dispatcher.utter_message(text="Sorry, I don't have a home remedy for that.")
                return []

            health_issue = matching_issues[0]  # Store the first matched issue

        # Extract the health issue from user input
        #health_issues = df["Health Issue"].str.lower().tolist()
        #matching_issues = [issue for issue in health_issues if issue in user_message]

        #if not matching_issues:
        #    dispatcher.utter_message(text="Sorry, I don't have a home remedy for that.")
        #    return []

        #issue = matching_issues[0]  # Take the first matched issue
        remedies_list = df[df["Health Issue"].str.lower() == health_issue]
        

        
        # Store progress if the user is asking for the first time
        if user_id not in user_remedy_progress or "more" not in user_message:
            user_remedy_progress[user_id] = 0  # Start from first remedy

        start_idx = user_remedy_progress[user_id]
        end_idx = start_idx + 2  # Show 2 remedies at a time

        remedies_chunk = remedies_list.iloc[start_idx:end_idx]

        if remedies_chunk.empty:
            dispatcher.utter_message(text="There are no more remedies available.")
            return []

        for _, row in remedies_chunk.iterrows():
            dispatcher.utter_message(
                text=f"To treat {row['Health Issue']}, you can use {row['Name of Item']}. Remedy: {row['Home Remedy']}.\n"
            )

        # Update progress for next request
        user_remedy_progress[user_id] = end_idx

        # If there are more remedies left, ask if the user wants more
        if end_idx < len(remedies_list):
            dispatcher.utter_message(text="Would you like to see more remedies? Say 'more'.")

        return [SlotSet("health_issue", health_issue)]"""


"""from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import pandas as pd

# Load the CSV file (Ensure the file path is correct)
df = pd.read_csv("Home Remedies (1).csv")

# Dictionary to track remedy progress for users
user_remedy_progress = {}

class ActionProvideHomeRemedy(Action):
    def name(self) -> Text:
        return "action_provide_home_remedy"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = tracker.sender_id  # Unique identifier for user session
        user_message = tracker.latest_message.get("text", "").lower()
        previous_health_issue = tracker.get_slot("health_issue")  # Check existing slot value

        # Check if the user is asking for "more"
        if "more" in user_message and previous_health_issue:
            health_issue = previous_health_issue  # Continue from the last issue
        else:
            # Extract health issue from the message
            health_issues = df["Health Issue"].str.lower().unique().tolist()
            matching_issues = [issue for issue in health_issues if issue in user_message]

            if not matching_issues:
                dispatcher.utter_message(text="Sorry, I don't have a home remedy for that.")
                return []

            health_issue = matching_issues[0]  # Select first matched issue
            user_remedy_progress[user_id] = 0  # Reset progress for the new issue

        # Filter remedies for the selected health issue
        remedies_list = df[df["Health Issue"].str.lower() == health_issue.lower()]

        if remedies_list.empty:
            dispatcher.utter_message(text="Sorry, I don't have any home remedies for this issue.")
            return [SlotSet("health_issue", None)]  # Clear slot if no remedies are found

        # Get the next set of remedies
        start_idx = user_remedy_progress.get(user_id, 0)
        end_idx = start_idx + 2  # Show 2 remedies at a time
        remedies_chunk = remedies_list.iloc[start_idx:end_idx]

        if remedies_chunk.empty:
            dispatcher.utter_message(text="There are no more remedies available.")
            return []

        # Display remedies
        for _, row in remedies_chunk.iterrows():
            dispatcher.utter_message(
                text=f"To treat {row['Health Issue']}, you can use {row['Name of Item']}. Remedy: {row['Home Remedy']}.\n"
            )

        # Update progress
        user_remedy_progress[user_id] = end_idx

        # If more remedies are available, prompt user
        if end_idx < len(remedies_list):
            dispatcher.utter_message(text="Would you like to see more remedies? Say 'more'.")

        # Update the slot with the current health issue
        return [SlotSet("health_issue", health_issue)]"""



from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
from rasa_sdk.events import SlotSet
import google.generativeai as genai
from textblob import TextBlob


# Load the CSV file (Ensure the correct path)
df = pd.read_csv("Home Remedies (1).csv")

class ActionProvideHomeRemedy(Action):
    def name(self) -> Text:
        return "action_provide_home_remedy"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text", "").lower()
        health_issue = tracker.get_slot("health_issue")
        remedy_index = tracker.get_slot("remedy_index") or 0  # Default to 0 if None

        # Debug: Print slot values
        print(f"Debug: Health Issue Slot = {health_issue}")
        print(f"Debug: Remedy Index Slot = {remedy_index}")

        # 🔹 Check if the user is asking for more remedies
        if "more" in user_message:
            if not health_issue:
                dispatcher.utter_message(text="I’m sorry, I don’t remember your health issue. Can you specify again?")
                return []
            elif health_issue:
                remedies_list = df[df["Health Issue"].str.lower() == health_issue.lower()]

                # Debug: Print filtered remedies
                print(f"Debug: Filtered Remedies for {health_issue} = {remedies_list}")
                print(f"health issue is:{health_issue}")
                # 🔹 Ensure remedies exist for the health issue
                if remedies_list.empty:
                    dispatcher.utter_message(text="I’m sorry, but I don’t have any home remedies for this issue.")
                    return []

                # 🔹 Show remedies in chunks of 2
                start_idx = remedy_index
                end_idx = start_idx + 2
                remedies_chunk = remedies_list.iloc[start_idx:end_idx]

                if remedies_chunk.empty:
                    dispatcher.utter_message(text="There are no more remedies available.")
                    return []

                
                for _, row in remedies_chunk.iterrows():
                    name_of_item = row['Name of Item']
                    remedy = row['Home Remedy']
                    health_issue = row['Health Issue']
                 
                    if pd.isna(name_of_item):
                        response = (
                            f"For addressing {health_issue}, here’s a recommended remedy:\n\n{remedy}"
                        )
                    else:
                        response = (
                            f"For addressing {health_issue}, you may consider using **{name_of_item}**. "
                            f"Here’s a recommended remedy:\n\n{remedy}"
                        )

                    dispatcher.utter_message(text=response)



                # 🔹 Update remedy index
                new_remedy_index = end_idx

                # 🔹 If more remedies exist, prompt the user
                if end_idx < len(remedies_list):
                    dispatcher.utter_message(text="Would you like to see more remedies? Say 'more'.")

                return [
                    SlotSet("health_issue", health_issue),  # Store health issue
                    SlotSet("remedy_index", new_remedy_index),  # Update remedy index
                ]
        else:
            # Extract the health issue from user input (only if the user is not saying "more")
            health_issues = df["Health Issue"].str.lower().tolist()
            matching_issues = [issue for issue in health_issues if issue in user_message]

        
            
            if not matching_issues:
            # Check spelling suggestions using TextBlob
                corrected_text = str(TextBlob(user_message).correct())

                if corrected_text != user_message:
                    dispatcher.utter_message(
                        text=f"Sorry, I don't have a home remedy for that. Did you mean: {corrected_text}?"
                    )
                else:
                    dispatcher.utter_message(text="Sorry, I don't have a home remedy for that.")
                
                return []

            

            # 🔹 If the user specifies a new health issue, reset the remedy index
            if health_issue != matching_issues[0]:
                remedy_index = 0

            health_issue = matching_issues[0]  # Store the matched issue

        # 🔹 Filter remedies for the health issue
        remedies_list = df[df["Health Issue"].str.lower() == health_issue]

        # Debug: Print filtered remedies
        print(f"Debug: Filtered Remedies for {health_issue} = {remedies_list}")

        # 🔹 Ensure remedies exist for the health issue
        if remedies_list.empty:
            dispatcher.utter_message(text="I’m sorry, but I don’t have any home remedies for this issue.")
            return []

        # 🔹 Show remedies in chunks of 2
        start_idx = remedy_index
        end_idx = start_idx + 2
        remedies_chunk = remedies_list.iloc[start_idx:end_idx]

        if remedies_chunk.empty:
            dispatcher.utter_message(text="There are no more remedies available.")
            return []
        count=0
        for _, row in remedies_chunk.iterrows():
            name_of_item = row['Name of Item']
            remedy = row['Home Remedy']
            health_issue = row['Health Issue']
            print(f"this is remedy {remedy}")
            if(count==0):
                if pd.isna(name_of_item):
                    response = (
                                f"For addressing {health_issue}, here’s a recommended remedy:\n\n{remedy}"
                            )
                else:
                    response = (
                                f"For addressing {health_issue}, you may consider using {name_of_item}. "
                                f"Here’s a recommended remedy:\n\n{remedy}"
                            )
                count=count+1
            else:
                break



            dispatcher.utter_message(text=response)
        # 🔹 Update remedy index
        new_remedy_index = end_idx

        # 🔹 If more remedies exist, prompt the user
        if end_idx < len(remedies_list):
            dispatcher.utter_message(text="Would you like to see more remedies? Say 'more'.")

        return [
            SlotSet("health_issue", health_issue),  # Store health issue
            SlotSet("remedy_index", new_remedy_index),  # Update remedy index
        ]
    






class ActionGenerateHealthSchedule(Action):
    def name(self) -> Text:
        return "action_generate_health_schedule"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the health issue from the slot
        health_issue = tracker.get_slot("health_issue")

        if not health_issue:
            dispatcher.utter_message(text="Please specify a health issue.")
            return []

        # Configure Gemini API
        genai.configure(api_key="AIzaSyBO3-HG-WcITn58PdpK7mMyvFQitoH00qA")  # Replace with your Gemini API key

        # Define the prompt for Gemini API
        prompt = f"Generate a 7-day schedule with time to manage or recover from {health_issue} at home using home remedies. Provide the schedule in a clear and structured format without bold words."

        # Call Gemini API
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')  # Use the Gemini Pro model
            response = model.generate_content(prompt)

            # Extract the generated schedule from the API response
            schedule = response.text.strip()
            dispatcher.utter_message(text=schedule)
        except Exception as e:
            dispatcher.utter_message(text=f"Sorry, I couldn't generate the schedule. Error: {str(e)}")

        return []


# Example data
ingredient_data = {
    "garlic": {
        "uses": "Some studies show that people who eat more garlic are less likely to get certain types of cancer (garlic supplements don’t seem to have the same effect). It also may lower blood cholesterol and blood pressure levels, but it doesn’t seem to help that much"
    },
    "peppermint":{
        "uses":"Mint has been used for hundreds of years as a health remedy. Peppermint oil might help with irritable bowel syndrome -- a long-term condition that can cause cramps, bloating, gas, diarrhea, and constipation -- and it may be good for headaches as well. More studies are needed to see how much it helps and why. People use the leaf for other conditions, too, but there’s very little evidence it helps with any of them. "
    },
    "honey":{
        "uses":"This natural sweetener may work just as well for a cough as over-the-counter medicines. That could be especially helpful for children who aren’t old enough to take those. But don’t give it to an infant or a toddler younger than 1. There’s a small risk of a rare but serious kind of food poisoning that could be dangerous for them. And while you may have heard that “local” honey can help with allergies, studies don’t back that up."
    },
    "ginger": {
        "uses": "It’s been used for thousands of years in Asian medicine to treat stomachaches, diarrhea, and nausea, and studies show that it works for nausea and vomiting. There’s some evidence that it might help with menstrual cramps, too. But it’s not necessarily good for everyone. Some people get tummy trouble, heartburn, diarrhea, and gas because of it, and it may affect how some medications work. So talk to your doctor, and use it with care."
    },
    "turmeric": {
        "uses": "This spice has been hyped as being able to help with a variety of conditions from arthritis to fatty liver. There is some early research to support this. Other claims, such as healing ulcers and helping with skin rashes after radiation are lacking proof. If you try it, don’t overdo it: High doses can cause digestive problems."
    },
    "green tea":{
        "uses":"This comforting drink does more than keep you awake and alert. It’s a great source of some powerful antioxidants that can protect your cells from damage and help you fight disease. It may even lower your odds of heart disease and certain kinds of cancers, like skin, breast, lung, and colon."
    },
    "chicken soup":{
        "uses":"Turns out, Grandma was right: Chicken soup can be good for a cold. Studies show it can ease symptoms and help you get rid of it sooner. It also curbs swelling and clears out nasal fluids."
    },
    "neti spot":{
        "uses":"You put a salt and warm water mixture in something that looks like a little teapot. Then pour it through one nostril and let it drain out the other. You have to practice a little, but once you get the hang of it, it can ease allergy or cold symptoms and may even help you get rid of a cold quicker. Just make sure you use distilled or cooled boiled water and keep your neti pot clean. "
    },
    "cinnamon":{
        "uses":"You may have heard that it can help control blood sugar for people who have prediabetes or diabetes. But there’s no evidence that it does anything for any medical condition. If you plan to try it, be careful: Cinnamon extracts can be bad for your liver in large doses"
    },
    "hot bath":{
        "uses":"It’s good for all kinds of things that affect your muscles, bones, and tendons (the tissues that connect your muscles to your bones), like arthritis, back pain, and joint pain. And warm water can help get blood flow to areas that need it, so gently stretch and work those areas while you’re in there. But don’t make it too hot, especially if you have a skin condition. The ideal temperature is between 92 and 100 F"
    }
}

class ActionIngredientUses(Action):
    def name(self) -> Text:
        return "action_ingredient_uses"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract the ingredient entity
        ingredient = next(tracker.get_latest_entity_values("ingredient"), None)

        if not ingredient:
            dispatcher.utter_message(text="Please specify an ingredient.")
            return []

        # Fetch the ingredient's uses and specialty
        ingredient_info = ingredient_data.get(ingredient.lower())
        if ingredient_info:
            uses = ingredient_info.get("uses", "No information available.")
            specialty = ingredient_info.get("specialty", "No specialty information available.")
            response = f"**{ingredient.capitalize()}**:\n\n- **Uses**: {uses}\n"
        else:
            response = f"Sorry, I don't have information about {ingredient}."

        dispatcher.utter_message(text=response)
        return []