import re
import os
import datetime
from app.env import (
    REDACT_EMAIL_PATTERN,
    REDACT_PHONE_PATTERN,
    REDACT_CREDIT_CARD_PATTERN,
    REDACT_SSN_PATTERN,
    REDACT_USER_DEFINED_PATTERN,
    REDACTION_ENABLED,
    OPENAI_MODEL
)
import mysql.connector
from sys import getsizeof
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
    
def log(ts: str, prompt: str, response: str, thread: str, user: str, channel: str, start: float, end: float):
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
        user="root"
    )
    print("connected")
    cursor = mydb.cursor()
    sql="CREATE DATABASE IF NOT EXISTS db"
    cursor.execute(sql)

#mycursor.execute("CREATE DATABASE gptdb")
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        database="db"
    )
    cursor=db.cursor()
    responsetime=end-start
    senddate=datetime.datetime.fromtimestamp(start)
    sql = "CREATE TABLE IF NOT EXISTS log (primary_id SERIAL, message_id VARCHAR(66) NOT NULL, thread_id VARCHAR(66) NOT NULL, channel_id VARCHAR(60) NOT NULL, user_id VARCHAR(60) NOT NULL, prompt_send_datetime DATETIME NOT NULL, response_time DOUBLE NOT NULL, prompt TEXT NOT NULL, response TEXT NOT NULL, upvote int NOT NULL, downvote int NOT NULL, error_vote int NOT NULL, model_name TEXT NOT NULL, PRIMARY KEY(primary_id))"
    cursor.execute(sql)
    sql = "INSERT INTO log (message_id, thread_id, channel_id, user_id, prompt_send_datetime, response_time, prompt, response, upvote, downvote, error_vote, model_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (ts,thread,channel,user,senddate,responsetime,prompt,response,0,0,0,OPENAI_MODEL)
    
    cursor.execute(sql, val)
    db.commit()
    db.disconnect()
    return

def feedback(ts: str, mood: str, channel: str, added: bool):
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
        database="db"
    )
    cursor=db.cursor()
    # ID to match
    ts_to_match = ts
    # Execute the SQL query
    if added:
        incr=1
    else:
        incr=-1
    query = "SELECT * FROM log WHERE message_id = %s AND channel_id = %s"
    cursor.execute(query, (ts_to_match,channel))
    result = cursor.fetchall()
    match(mood):
        case "+1":
            values=(str(int(result[0][9])+incr),str(result[0][1]),str(result[0][3]))
            cursor.execute("UPDATE log SET upvote = %s WHERE message_id = %s AND channel_id = %s ",values)
        case "-1":
            values=(str(int(result[0][10])+incr),str(result[0][1]),str(result[0][3]))
            cursor.execute("UPDATE log SET downvote = %s WHERE message_id = %s AND channel_id = %s",values)
        case "warning":
            values=(str(int(result[0][11])+incr),str(result[0][1]),str(result[0][3]))
            cursor.execute("UPDATE log SET error_vote = %s WHERE message_id = %s AND channel_id = %s",values)
        case _:
            return
    
    db.commit()

    db.disconnect()
    return