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
import mysql.connector

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
    
def log(ts: str, prompt: str, response: str, thread: str, user: str):
    # if(not os.path.exists("./logs")):
    #     os.makedirs("./logs")
    # try:
    #     file = open(f"./logs/{ts}.txt",'x')
    # except:
    #     file = open(f"./logs/{ts}.txt",'a')
    # file.write(text)
    # file.write("\n")
    # file.write("\n")
    # file.close()
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="gptdb"
    )

    cursor = mydb.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS gptdb")

#mycursor.execute("CREATE DATABASE gptdb")
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="gptdb"
    )
    cursor=db.cursor()
    sql = "CREATE TABLE IF NOT EXISTS GPTlog (ts VARCHAR(255) NOT NULL UNIQUE PRIMARY KEY, thread VARCHAR(255) NOT NULL, user VARCHAR(255) NOT NULL, prompt TEXT NOT NULL, response TEXT NOT NULL, upvote int NOT NULL, downvote int NOT NULL, error int NOT NULL)"
    cursor.execute(sql)
    sql = "INSERT INTO GPTlog (ts, thread, user, prompt, response, upvote, downvote, error) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (ts,thread,user,prompt,response,0,0,0)
    cursor.execute(sql, val)
    db.commit()
    db.disconnect()
    return

def feedback(ts: str, mood: str):
    # path=""
    # match(mood):
    #     case "+1":
    #         path="./feedback/good"
    #     case "-1":
    #         path="./feedback/bad"
    #     case "warning":
    #         path="./feedback/error"
    #     case _:
    #         return
    # if(not os.path.exists(path)):
    #     os.makedirs(path)
    # file = open(path+f"/{ts}.txt",'x')
    # file.write(prompt)
    # file.write("\n")
    # file.write("\n")
    # file.write(response)
    # file.close()

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="gptdb"
    )
    cursor=db.cursor()
    # ID to match
    ts_to_match = ts
    # Execute the SQL query
    query = "SELECT * FROM GPTlog WHERE ts = %s"
    cursor.execute(query, (ts_to_match,))
    result = cursor.fetchall()
    match(mood):
        case "+1":
            values=(str(int(result[0][4])+1),str(result[0][0]))
            cursor.execute("UPDATE GPTlog SET upvote = %s WHERE ts = %s",values)
        case "-1":
            values=(str(int(result[0][5])+1),str(result[0][0]))
            cursor.execute("UPDATE GPTlog SET downvote = %s WHERE ts = %s",values)
        case "warning":
            values=(str(int(result[0][6])+1),str(result[0][0]))
            cursor.execute("UPDATE GPTlog SET error = %s WHERE ts = %s",values)
        case _:
            return
    
    db.commit()
    query = "SELECT * FROM GPTlog WHERE ts = %s"
    cursor.execute(query, (ts_to_match,))
    result = cursor.fetchall()

    db.disconnect()
    return