
import json

from IPython.display import display, HTML
import markdown

class Tools:
    def __init__(self):
        self.tools = {}
        self.functions = {}

    def add_tool(self, function, description):
        # Store the tool description in OpenAI format
        tool_spec = {
            "type": "function",
            "function": description
        }
        self.tools[function.__name__] = tool_spec
        self.functions[function.__name__] = function
    
    def get_tools(self):
        return list(self.tools.values())

    def function_call(self, tool_call_function):
        function_name = tool_call_function.name
        arguments = json.loads(tool_call_function.arguments)

        # Handle parameter name mapping for get_weather function
        if function_name == "get_weather" and "location" in arguments:
            arguments["city"] = arguments.pop("location")

        f = self.functions[function_name]
        result = f(**arguments)

        return {
            "type": "function_call_output",
            "output": json.dumps(result, indent=2),
        }


def shorten(text, max_length=50):
    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


class ChatInterface:
    def input(self):
        question = input("You:")
        return question
    
    def display(self, message):
        print(message)

    def display_function_call(self, tool_call_function, result):
        call_html = f"""
            <details>
            <summary>Function call: <tt>{tool_call_function.name}({shorten(tool_call_function.arguments)})</tt></summary>
            <div>
                <b>Call</b>
                <pre>{tool_call_function.name}({tool_call_function.arguments})</pre>
            </div>
            <div>
                <b>Output</b>
                <pre>{result['output']}</pre>
            </div>
            
            </details>
        """
        display(HTML(call_html))

    def display_response(self, entry):
        response_html = markdown.markdown(entry.content[0].text)
        html = f"""
            <div>
                <div><b>Assistant:</b></div>
                <div>{response_html}</div>
            </div>
        """
        display(HTML(html))



class ChatAssistant:
    def __init__(self, tools, developer_prompt, chat_interface, client):
        self.tools = tools
        self.developer_prompt = developer_prompt
        self.chat_interface = chat_interface
        self.client = client
    
    def gpt(self, chat_messages):
        return self.client.chat.completions.create(
            model='deepseek-chat',
            messages=chat_messages,
            tools=self.tools.get_tools(),
        )


    def run(self):
        chat_messages = [
            {"role": "system", "content": self.developer_prompt},
        ]

        # Chat loop
        while True:
            question = self.chat_interface.input()
            if question.strip().lower() == 'stop':  
                self.chat_interface.display("Chat ended.")
                break

            message = {"role": "user", "content": question}
            chat_messages.append(message)

            while True:  # inner request loop
                response = self.gpt(chat_messages)
                
                assistant_message = response.choices[0].message
                chat_messages.append(assistant_message)
                
                has_tool_calls = False
                
                # Check if there are tool calls
                if assistant_message.tool_calls:
                    has_tool_calls = True
                    for tool_call in assistant_message.tool_calls:
                        result = self.tools.function_call(tool_call.function)
                        
                        # Add tool result to messages
                        tool_message = {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result["output"]
                        }
                        chat_messages.append(tool_message)
                        
                        self.chat_interface.display_function_call(tool_call.function, result)
                else:
                    # Display the assistant's response
                    self.chat_interface.display(f"Assistant: {assistant_message.content}")
                
                if not has_tool_calls:
                    break
    


