import json
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from llm_hleper import llm

def process_posts(raw_file_path, processed_file_path="processed_post.json"):
    enriched_posts = []
    
    # Read and process the raw file
    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)
        for post in posts.get("posts", []):  # Ensure posts key exists in JSON
            metadata = extract_metadata(post["title"])
            post_with_metadata = {**post, **metadata}  # Use dictionary unpacking for Python >= 3.5
            enriched_posts.append(post_with_metadata)

    print(f"Debug: Enriched Posts Data: {enriched_posts}")  # Log the enriched posts to check tags
    
    unified_tags = get_unified_tags(enriched_posts)
    for post in enriched_posts:
        current_tags = post['tags']
        new_tags = {unified_tags.get(tag, tag) for tag in current_tags}
        post['tags'] = list(new_tags)

        # Handle posts without tags
        if not post.get('tags'):
            post['tags'] = ["Uncategorized"]  # Assign default tag if none exist

    with open(processed_file_path, encoding='utf-8', mode="w") as outfile:
        json.dump(enriched_posts, outfile, indent=4)

def extract_metadata(post_title):
    template = '''
    You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
    1. Return a valid JSON. No preamble. 
    2. JSON object should have exactly three keys: line_count, language and tags. 
    3. tags is an array of text tags. Extract maximum two tags.
    4. Language should be English or Hinglish (Hinglish means hindi + english)
    
    Here is the actual post on which you need to perform this task:  
    {post}
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"post": post_title})

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
        print(f"Debug: Extracted metadata: {res}")  # Log the metadata extracted
    except OutputParserException:
        print(f"Error: Failed to parse LLM response: {response.content}")
        raise OutputParserException("Context too big. Unable to parse jobs.")
    
    return res

def get_unified_tags(posts_with_metadata):
    unique_tags = set()
    
    for post in posts_with_metadata:
        tags = post.get("tags", [])
        if tags:
            unique_tags.update(tags)
        else:
            print(f"Warning: Post without tags: {post.get('title', 'Unknown title')}")  # Log posts without tags

    if not unique_tags:
        raise ValueError("No tags found in posts. Unable to unify tags.")

    unique_tags_list = ','.join(unique_tags)
    print(f"Debug: Unique Tags List: {unique_tags_list}")  # Log tags being passed to LLM

    template = '''I will give you a list of tags. You need to unify tags with the following requirements,
    1. Tags are unified and merged to create a shorter list. 
       Example 1: "Jobseekers", "Job Hunting" can be all merged into a single tag "Job Search". 
       Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
       Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
       Example 4: "Scam Alert", "Job Scam" etc. can be mapped to "Scams"
    2. Each tag should follow title case convention. Example: "Motivation", "Job Search".
    3. Output should be a JSON object, with mappings of original tag and the unified tag. 
       For example: {"Jobseekers": "Job Search",  "Job Hunting": "Job Search", "Motivation": "Motivation"}
    
    Here is the list of tags: 
    {tags}
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm

    try:
        response = chain.invoke(input={"tags": unique_tags_list})
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        print(f"Error: LLM response is invalid JSON. Response content: {response.content}")
        raise OutputParserException("Invalid JSON output from LLM.")

    return res

if __name__ == "__main__":
    # Use raw strings or double backslashes for file paths on Windows
    raw_file_path = r"C:\Python Program\PYTHON\Gen AI\post.json"
    processed_file_path = r"C:\Python Program\PYTHON\Gen AI\processed_post.json"
    
    # Ensure paths exist before processing
    if os.path.exists(raw_file_path):
        process_posts(raw_file_path, processed_file_path)
    else:
        print(f"Error: The file {raw_file_path} does not exist.")
