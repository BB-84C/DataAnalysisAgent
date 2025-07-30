import base64
import glob
import inspect
import io
import json
import os
import re
import shutil
import sys

import numpy as np
from openai import OpenAI
import pandas as pd
import requests

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

         
class GlobalNamespaceManager:
    def __init__(self):
        self.namespace = {'image_pool': []}
        self.history = []

    def add(self, key, value):
        self.namespace[key] = value
        if key not in self.history:
            self.history.append(key)
        
        # Append to image_pool only if it's not already there
        if isinstance(value, np.ndarray) and value.ndim == 2:
            if key not in self.namespace['image_pool']:
                self.namespace['image_pool'].append(key)

    def get(self, key):
        return self.namespace.get(key)

    def get_all(self):
        return self.namespace

    def summary(self):
        return {
            "variables": list(self.namespace.keys()),
            "image_pool": self.namespace['image_pool'],
            "history": self.history
        }



def auto_tooljsdict(tools_list):
    """
    To generate function parameters that be read by ChatGPT.
    :param functions_list: A list that including one or more than one function objects；
    :return： Returns function objects that meet ChatGPT function parameter's requirement.
    """
    def jsdict_generate(tools_list):
        # Create an empty list to hold the description dictionary for each function
        tools_jsdict = []     
        # Loop through each external function
        for tool in tools_list:
            # Read the function description of the function object
            tool_description = inspect.getdoc(tool)
            # Retrieve the function name string of the function
            
            tool_name = tool.__name__

            system_prompt = "The following is a description of a certain function: %s" % tool_description
            user_prompt = "According to the description of this function, please help me create a dictionary in JSON format which has the following 5 requirements:\
                           1. The dictionary has a total of three key-value pairs;\
                           2. The Key of the first key-value pair is the string 'name', and the value is the name of the function: %s, which is also a string; \
                           3. The Key of the second key-value pair is the string 'description', value is the function's function description, also a string; \
                           4. The Key of the third key-value pair is the string 'parameters', and value is a JSON Schema object that describes the parameter input specification for the function. \
                           5. The output result must be a dictionary in JSON format, and it is sufficient to output only this dictionary, without any before and after modifying or describing statements" % tool_name

            response = client.chat.completions.create(
                              model="gpt-4o",
                              messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                              ]
                            )
            tools_jsdict.append(json.loads(response.choices[0].message.content))
        return tools_jsdict
    
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        try:
            tools_jsdict = jsdict_generate(tools_list)
            break  # If the code executes successfully, jump out of the loop
        except Exception as e:
            attempts += 1  # Increase the number of attempts
            print("Error Occur", e)
            if attempts == max_attempts:
                print("The maximum number of attempts has been reached and the program terminates.")
                raise  # Re-raising the last exception
            else:
                print("Running again....")
    return tools_jsdict

def run_conversation1(messages, tools_list=None, toolsjsdict='', global_namespace=None, model="gpt-4o"):
    """
    Chat model that automates external function calls. Just call chat model once and execute the function, no second call. 
    :param messages: required parameter, dictionary type, pass to the messages parameter object of the Chat model
    :param functions_list: optional parameter, defaults is None, can be set to a list object that contains all external functions
    :param model: Chat model, optional parameter, default model is gpt-4
    :return: output of the Chat model.
    """
    # If there is no external function library, the normal dialog task is executed
    if tools_list == None:
        response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        )
        response_message = response.choices[0].message
        final_response = response_message.content
        
    # If an external function library exists, will select and answer with external functions
    else:
        # Creating the functions object
        # tools = tooljsdict
        # Creating an External Library Dictionary
        available_tools = {tool.__name__: tool for tool in tools_list}

        # first response
        response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        tools=toolsjsdict,
                        tool_choice="auto")

        # Determine whether function_call is true for the returned result, i.e., determine whether an external function needs to be called to answer the question
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            # Need to call an external function
            for tool_call in tool_calls:
                # Get function name
                function_name = tool_call.function.name
                # Get the function object
                function_to_call = available_tools[function_name]
                print('Excuted function: ['+function_name+'] with arguments: '+tool_call.function.arguments)
                # Get the function parameters
                function_args = json.loads(tool_call.function.arguments)
                # Input the function parameters into the function to get the result of the function calculation
                # Use the provided global namespace or infer it
                if global_namespace is None:
                    global_namespace = inspect.currentframe().f_back.f_globals
                function_response = function_to_call(**function_args, global_namespace=global_namespace)
                
def run_conversation_x(messages, tools_list=None, toolsjsdict='', namespace_manager=None, model="gpt-4o"):
    """
    Chat model that automates external function calls. Just call chat model once and execute the function, no second call. 
    :param messages: required parameter, dictionary type, pass to the messages parameter object of the Chat model
    :param functions_list: optional parameter, defaults is None, can be set to a list object that contains all external functions
    :param model: Chat model, optional parameter, default model is gpt-4
    :return: output of the Chat model.
    """
    # If there is no external function library, the normal dialog task is executed
    if tools_list == None:
        response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        )
        response_message = response.choices[0].message
        final_response = response_message.content
        return response.choices[0].message.content
        
    # If an external function library exists, will select and answer with external functions
    else:
        if namespace_manager is None:
            namespace_manager = GlobalNamespaceManager()
        # Creating the functions object
        # tools = tooljsdict
        # Creating an External Library Dictionary
        available_tools = {tool.__name__: tool for tool in tools_list}
        # Pre-call state
        before_keys = set(namespace_manager.namespace.keys())

        # first response
        response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        tools=toolsjsdict,
                        tool_choice="auto")

        # Determine whether function_call is true for the returned result, i.e., determine whether an external function needs to be called to answer the question
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            # Need to call an external function
            for tool_call in tool_calls:
                # Get function name
                function_name = tool_call.function.name
                # Get the function object
                function_to_call = available_tools[function_name]
                print('Excuted function: ['+function_name+'] with arguments: '+tool_call.function.arguments)
                # Get the function parameters
                function_args = json.loads(tool_call.function.arguments)
                # Input the function parameters into the function to get the result of the function calculation
                # Use the provided global namespace or infer it
                # Execute the tool
                function_to_call(**function_args, global_namespace=namespace_manager.namespace)
                # Post-call: detect new variables
                after_keys = set(namespace_manager.namespace.keys())
                new_keys = after_keys - before_keys
                for key in new_keys:
                    namespace_manager.add(key, namespace_manager.namespace[key])

        return namespace_manager.summary()



def run_conversation2(messages, functions_list=None, model="gpt-4o"):
    """
    Chat model that automates external function calls, and call the chat model for the second time to present response in the final conversation.
    :param messages: required parameter, dictionary type, pass to the messages parameter object of the Chat model
    :param functions_list: optional parameter, defaults is None, can be set to a list object that contains all external functions
    :param model: Chat model, optional parameter, default model is gpt-4
    :return: output of the Chat model.
    """
    # If there is no external function library, the normal dialog task is executed
    if functions_list == None:
        response = openai.ChatCompletion.create(
                        model=model,
                        messages=messages,
                        )
        response_message = response["choices"][0]["message"]
        final_response = response_message["content"]
        
    # If an external function library exists, will select and answer with external functions
    else:
        # Creating the functions object
        functions = auto_functions(functions_list)
        # Creating an External Library Dictionary
        available_functions = {func.__name__: func for func in functions_list}

        # first response
        response = openai.ChatCompletion.create(
                        model=model,
                        messages=messages,
                        functions=functions,
                        function_call="auto")
        response_message = response["choices"][0]["message"]

        # Determine whether function_call is true for the returned result, i.e., determine whether an external function needs to be called to answer the question
        if response_message.get("function_call"):
            # Need to call an external function
            # Get function name
            function_name = response_message["function_call"]["name"]
            # Get the function object
            fuction_to_call = available_functions[function_name]
            # Get the function parameters
            function_args = json.loads(response_message["function_call"]["arguments"])
            # Input the function parameters into the function to get the result of the function calculation
            function_response = fuction_to_call(**function_args)
            
            # Check if function response is a NumPy array
            if isinstance(function_response,np.ndarray):
                string_io = io.StringIO()
                np.savetxt(string_io,function_response, delimiter='')
                function_response=string_io.getvalue()
                # Append the first response
                messages.append(response_message)  
                # Append the function output
                messages.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    }
                ) 
            else:
                function_response=function_response
            

            # Append the first response
            messages.append(response_message)  
            # Append the function output
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )  
            # Call the GPT API for the second time
            second_response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
            )  
            # Acquire the final result
            final_response = second_response["choices"][0]["message"]["content"]
        else:
            final_response = response_message["content"]
    
    return final_response
        


