import re
import os
from app.env import (
    REDACT_EMAIL_PATTERN,
    REDACT_PHONE_PATTERN,
    REDACT_CREDIT_CARD_PATTERN,
    REDACT_SSN_PATTERN,
    REDACT_USER_DEFINED_PATTERN,
    REDACTION_ENABLED,
)


def redact_string(input_string: str) -> str:
    """
    Redact sensitive information from a string (inspired by @quangnhut123)

    Args:
        - input_string (str): the string to redact

    Returns:
        - str: the redacted string
    """
    output_string = input_string
    if REDACTION_ENABLED:
        output_string = re.sub(REDACT_EMAIL_PATTERN, "[EMAIL]", output_string)
        output_string = re.sub(
            REDACT_CREDIT_CARD_PATTERN, "[CREDIT CARD]", output_string
        )
        output_string = re.sub(REDACT_PHONE_PATTERN, "[PHONE]", output_string)
        output_string = re.sub(REDACT_SSN_PATTERN, "[SSN]", output_string)
        output_string = re.sub(REDACT_USER_DEFINED_PATTERN, "[REDACTED]", output_string)

    return output_string
    
def log(ts: str, text: str):
    if(not os.path.exists("./logs")):
        os.makedirs("./logs")
    try:
        file = open(f"./logs/{ts}.txt",'x')
    except:
        file = open(f"./logs/{ts}.txt",'a')
    file.write(text)
    file.write("\n")
    file.write("\n")
    file.close()
    return

def feedback(ts: str, prompt: str, response: str, mood: str):
    path=""
    match(mood):
        case "+1":
            path="./feedback/good"
        case "-1":
            path="./feedback/bad"
        case "warning":
            path="./feedback/error"
        case _:
            return
    if(not os.path.exists(path)):
        os.makedirs(path)
    file = open(path+f"/{ts}.txt",'x')
    file.write(prompt)
    file.write("\n")
    file.write("\n")
    file.write(response)
    file.close()
    return