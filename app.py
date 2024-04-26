from flask import Flask, request, render_template, jsonify
from openai import OpenAI
from amazon_scraper import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    verdict = ""
    if request.method == 'POST':
        url = request.get_json().get('url')
        if url:
            url = sanitizeURL(url)
            product_name, review_texts, content = get_product_name_and_reviews(url)
            i = 0
            for review_page in review_texts:
                i += 1
                content += f"{i} Star Reviews --> "
                j = 0
                for review in review_page:
                    j += 1
                    content += f'\nReview {j}: ' + (review.encode('cp1252', errors='ignore').decode('cp1252'))
                content += '\n\n'

        if content.strip():  # Check if content is not empty after stripping whitespace
            client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
            completion = client.chat.completions.create(
                model="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
                messages=[
                    {"role": "system", "content": "Following are a sequence of user reviews for a product. Generate a specific and concise summary of the reviews. Give less preference to the negative reviews unless they expose some fatal flaws, and more preference to the positive reviews. The summary should be 1-2 paragraphs. Also try to mention the product by name. Give a small list of Pros and Cons too."},
                    {"role": "user", "content": f"{content}"}
                ],
                temperature=0.7,
            )
            verdict = completion.choices[0].message.content
        else:
            verdict = "No reviews found for the provided product URL."
        return jsonify(verdict=verdict)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run (debug=True)