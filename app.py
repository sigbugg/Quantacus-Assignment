from flask import Flask, request, render_template
import wikipediaapi, openai, os

# Assume you have a summarization function or API client set up
# from summarizer import summarize

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')

def call_openai_gpt(text,task):
    if task == "summarize":
        system = """You are an expert in writing summary.
        """
        content = f"""Summarize the following input text:\n\n{text}\n\n
        *****Only return the summarized sentences!"""
    elif task == "paraphrase":
        system= """You are an expert in paraphrasing.
        """
        content = f"""Paraphrase the following input text :\n\n{text}\n\n
        *****Only return the paraphrased sentences!"""

    messages =  [
        {'role':'system', 'content': system},
        {'role':'user', 'content': content}]
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=0.4,
            top_p=1.0,
            frequency_penalty=0.35,
            presence_penalty=0.4,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Error generating text."

def format_page_name(page_name):
    words = page_name.split()
    return ' '.join(word.capitalize() for word in words)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        raw_page_name = request.form['page_name']
        formatted_page_name = format_page_name(raw_page_name)
        wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent='Quantacus-Case-Study')
        page = wiki_wiki.page(formatted_page_name)
        
        if not page.exists():
            return render_template('index.html', error="Page not found! Type a valid page name.", page_name=raw_page_name)
        
        section_titles = [section.title for section in page.sections]
        return render_template('index.html', sections=section_titles, page_name=formatted_page_name, raw_page_name=raw_page_name)
    
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    # Extract the page name and section title from the form data
    page_name = request.form.get('page_name')
    section_title = request.form.get('section_title')

    # Initialize the Wikipedia API
    wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent='Quantacus-Case-Study')
    page = wiki_wiki.page(format_page_name(page_name))

    # Check if the page exists
    if not page.exists():
        return render_template('index.html', error="Page not found! Type a valid page name.", page_name=page_name)

    # Attempt to find the requested section
    section = page.section_by_title(section_title)
    if section:
        summary_text = call_openai_gpt(section.text,'summarize')
    else:
        # If the section wasn't found
        summary_text = "Section not found! Please try again."

    # Render a template with the summary
    return render_template('summary.html', summary=summary_text, section_title=section_title, page_name=page_name)


@app.route('/paraphrase', methods=['POST'])
def paraphrase():
    page_name = request.form.get('page_name')
    section_title = request.form.get('section_title')
    summary = request.form.get('summary')  # This will hold the summary if it's being passed directly

    # If a summary is provided directly, use it
    if summary:
        text_to_paraphrase = summary
    else:
        # Initialize the Wikipedia API
        wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent='Quantacus-Case-Study')
        page = wiki_wiki.page(page_name)

        # Check if the page exists
        if not page.exists():
            return render_template('index.html', error="Page not found! Type a valid page name.", page_name=page_name)

        # Attempt to find the requested section
        section = page.section_by_title(section_title)
        if section:
            text_to_paraphrase = section.text
        else:
            # If the section wasn't found, use a placeholder error message
            return render_template('index.html', error="Section not found! Please try again.", page_name=page_name, section_title=section_title)

    paraphrase_text = call_openai_gpt(text_to_paraphrase, 'paraphrase')

    # Render a template with the paraphrased text
    return render_template('paraphrase.html', paraphrase=paraphrase_text, section_title=section_title, page_name=page_name)


if __name__ == '__main__':
    app.run(debug=True)
