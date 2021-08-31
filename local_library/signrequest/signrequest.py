import requests
import json


def get_page_metadata(page):
    """
    Gets the SignRequest API metadata for sent signrequests on a single page (10-50 documents)
    
    Args:
        page: An integer representing the page number
        
    Returns:
        response: A requests object containing the SignRequest response.
    """
    
    response = requests.get(
        "https://wethinkcode.signrequest.com/api/v1/documents/",
        headers={"Authorization": "Token c37da7fb557f0208fd1fbf18dc6896a5bff4e9ef"},
        params={"page":page, "limit":20}
    )

    #print(f"Get Page Status: {response.status_code}")
    return response


def check_email(result, emails):
    """
    Checks if result dictionary email value is in the emails list.
    
    Args:
        result: A disctionary containg metadata for a signrequest API response.
        emails: A list of strings representing emails.
        
    Returns:
        _: A bool indicating if dictionary email value is in the emails list.
    """
    
    return True if result['signrequest']['signers'][-1]['email'] in emails else False


def check_template(result, template_ids):
    """
    Checks if result dictionary template id value is the same as template_id
    
    Args:
        result: A disctionary containg metadata for a signrequest API response.
        template_id: A string representing the ID of a signrequest template.
        
    Returns:
        _: A bool indicating if result dictionary template id value is the same as template_id
    """
    if not result['template']:
        return False
    return True if result['template'].split("/")[-2] in template_ids else False


def filter_results(results, template_ids, emails):
    """
    Filter API call metadata results by email
    
    Args:
        results: A jsonified API call response.
        emails: A list of strings each representing an email.
        
    Returns:
        A filtered list of signrequests metadata.
    """
    
    return list(
        filter(
            lambda result: True if check_template(result, template_ids) and check_email(result, emails) else False, results
        )
    )


def map_status(status_code):
    """
    Maps a status code to the actual status.
    
    Args:
        status_code: A status code representing the status of a signrequest.
        
    Returns:
        _: A string representing the status of a signrequest.
    """
    
    signrequest_status_map = {
        "co":"converting", "ne":"new", "se":"sent", "vi":"viewed", "si":"signed",
        "do":"downloaded", "sd":"signed and downloaded", "ca":"cancelled",
        "xp":"expired", "de":"declined", "ec":"error converting", "es":"error sending"
    }
    return signrequest_status_map[status_code]


def create_new_object(result):
    """
    Creates a new object using specific data which is a subset of the old object.
    
    Args:
        result: A json object representing a signrequest result.
        
    Returns:
        new_object: A json object containing subset data of the result object.
    """
    
    template_id =  result['template'] if result['template'] else "Nothing/ "
    new_object = {
        "email":result['signrequest']['signers'][-1]['email'],
        "template_id":template_id.split("/")[-2],
        "signrequest_status":map_status(result["status"]),
        "document_url":result["pdf"],
    }
    return new_object


def get_specific_data(results_array):
    """
    Gets specific data for each result in the signrequest results array.
    
    Args:
        results_array: An array of objects each representing a signrequest result.
        
    Returns:
        _: An array of objects containing specific data.
    """
    
    return [create_new_object(result) for result in results_array]

def signrequest_documents(emails, template_ids, page_number):
    """
    Gets relevant metadata for signrequests documents on a particular page.
    
    Args:
        emails: A list of strings representing all the emails to return.
        template_id: A list of ids representing all the templates to return.
        page_number: An int representing the signrequest page to return.
        
    Returns:
        _: A list of all relevant SignRequests on a page.
    """
    
    response = get_page_metadata(page_number)
    json_response = response.json()
    filtered_results = filter_results(json_response['results'], template_ids, emails)
    return get_specific_data(filtered_results), json_response['next']


def create_tags(row, columns):
    """
    Creates the prefill tags neccessary for prefilling signrequest documents.
    
    Args:
        row: A dictionary whose values will prepopulate the signrequest documents.
        columns: A list of dictionary keys.
        
    Returns:
        prefill_tags: A list of dictionaries.
    """
    
    prefill_tags = []
    for column in columns:
        tags = {}
        tags["external_id"] = column
        tags["text"] = row[column]
        prefill_tags.append(tags)
        
    return prefill_tags



    
    
def send_signrequest(prefill_tags, signers, template_id):
    """
    Send a SignRequest using API calls.
    
    Args:
        prefill_tags: A list of dictionaries representing tags to prefil the SignRequest.
        signers: A list of strings representing the emails of the SignRequest signers.
        template_id: A string representing the id of the template for the SignRequest.
        
    Returns:
        _: A boolean value with true representing success.
    """
    
    #create data object
    data = {
        "template": f'https://wethinkcode.signrequest.com/api/v1/templates/{template_id}/',
        "signers": signers,
        "from_email": "no-reply@wethinkcode.co.za",
        "message": "Please sign this document. \n\n Kind regards, \n\n WeThinkCode_",
        "subject": "WeThinkCode_ has sent you a SignRequest",
        "who": "o",
        "needs_to_sign": "true",
        "prefill_tags": prefill_tags,
        # Add other parameters here
    }
    
    #send signrequest through post
    response = requests.post(
        "https://wethinkocode.signrequest.com/api/v1/signrequest-quick-create/",
        headers={"Authorization": "Token c37da7fb557f0208fd1fbf18dc6896a5bff4e9ef"},
        json=data
    )

    #create a json response object
    json_response = json.dumps(response.json(), indent=4)

    #check if signrequest was a success.
    if response.status_code == 201:
        print(f"Signer: {signers[0]['email']} , Status: {response.status_code}")
        return True
    elif response.status_code == 400:
        print("Not found.")
        print("Response: ", json_response)
    
    return False


def send_bulk_signrequest(target_df, target_columns, template_column):
    """
    Sends signrequests in bulk using data from a dataframe to prepopulate the signrequests.
    
    Args:
        target_df: A dataframe containing the data for prepopulation.
        target_columns: A list representing the dataframe columns to be used for prepopulation.
        template_column: A string representing the dataframe column containing the template id.
        
    Returns:
        N/A
    """
    
    for index, row in target_df.iterrows():
        
        #create prefill tags
        prefill_tags = create_tags(row, target_columns)
    
        #set signers
        signers = [{"email": row["learner_email"]}]
    
        #send signrequest
        send_signrequest(prefill_tags, signers, row[template_column])

