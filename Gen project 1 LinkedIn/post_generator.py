from llm_hleper import llm
from few_shot import FewShotPosts

# Instantiate FewShotPosts
fs = FewShotPosts()

def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":  # Fixed condition
        return "11 to 15 lines"
    return "Unknown length"

def get_prompt(length, language, tag):
    length_str = get_length_str(length)
    prompt = f'''
    Generate a LinkedIn post using the below information. No preamble.

    1) Topic: {tag}
    2) Length: {length_str}
    3) Language: {language}
    '''
    examples = fs.get_filtered_posts(language, length, tag)
    if len(examples) > 0:
        prompt += "\n4) Use the writing style as per the following examples."
        for i, post in enumerate(examples):
            post_text = post['text']
            prompt += f"\n\nExample {i+1}:\n{post_text}"
            if i == 1:  # Limit to 2 examples
                break
    return prompt

def generate_post(length, language, tag):
    prompt = get_prompt(length, language, tag)
    response = llm.invoke(prompt)  # Ensure llm.invoke() is properly implemented
    return response.content

if __name__ == "__main__":
    post = generate_post("Short", "English", "Job Search")
    print(post)
