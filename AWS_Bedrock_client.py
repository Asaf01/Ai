import boto3
import pprint

# Initialize AWS Bedrock client
bedrock = boto3.client(service_name='bedrock', region_name='us-west-2')

pp = pprint.PrettyPrinter(depth=4)

def get_llama_model():
    try:
        # Fetch list of foundation models
        response = bedrock.list_foundation_models()
        models = response.get("modelSummaries", [])

        if not models:
            print("No foundation models found.")
            return
        
        # Find the Llama model
        for model in models:
            if model.get("modelName") == "Llama 3.1 8B Instruct":
                model_id = model.get("modelId")
                print(f"Found model: {model_id}")

                # Fetch details of this specific model
                model_details = bedrock.get_foundation_model(modelIdentifier=model_id)
                pp.pprint(model_details)
                return
        
        print("Llama 3.1 8B Instruct model not found.")

    except Exception as e:
        print(f"Error: {e}")

# Run the function
get_llama_model()
