from rag import handler
import json

event = {
    "body": json.dumps({"question": " how can API user to obtain error information?"})
}

response = handler(event, {})

print(response)

# add file _init_.py 
