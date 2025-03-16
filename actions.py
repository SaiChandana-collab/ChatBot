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

                for _, row in remedies_chunk.iterrows():
                    dispatcher.utter_message(
                        text=f"To treat {row['Health Issue']}, you can use {row['Name of Item']}. Remedy: {row['Home Remedy']}."
                    )

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

        for _, row in remedies_chunk.iterrows():
            dispatcher.utter_message(
                text=f"To treat {row['Health Issue']}, you can use {row['Name of Item']}. Remedy: {row['Home Remedy']}."
            )

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
        prompt = f"Generate a 7-day schedule to manage or recover from {health_issue} at home using home remedies. Provide the schedule in a clear and structured format."

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