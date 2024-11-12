from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import spacy
from urllib.request import urlretrieve

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")  # Load SpaCy NLP model

# Define FAQs with intents
faqs = {
    "gst registration": "GST registration is the process of registering your business under the Goods and Services Tax.",
    "eligibility": "Businesses with an annual turnover of over ₹20 lakhs need to register for GST.",
    "required documents": "The documents required for GST registration are PAN card, address proof, and business incorporation proof."
}

@app.route("/sms", methods=["POST"])
def sms_reply():
    """Respond to incoming WhatsApp messages with GST info and handle document upload."""
    incoming_msg = request.form.get("Body").lower()  # Incoming message text
    media_url = request.form.get("MediaUrl0")  # Check if media (like files) is sent

    # Create a Twilio response object
    resp = MessagingResponse()
    msg = resp.message()

    # Process user message for response
    response_text = get_response(incoming_msg)
    
    if media_url:
        # Save the uploaded file if there's media
        save_uploaded_file(media_url)
        msg.body("Document received! Thank you for sharing the required documents.")
    else:
        msg.body(response_text)

    return str(resp)

def get_response(user_message):
    """Use NLP to find the best matching FAQ response."""
    user_doc = nlp(user_message.lower())
    best_match = None
    highest_similarity = 0

    for question, answer in faqs.items():
        question_doc = nlp(question)
        similarity = user_doc.similarity(question_doc)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = answer

    # Threshold to avoid incorrect responses
    if highest_similarity > 0.75:
        return best_match
    else:
        return "I'm sorry, I didn't understand that. Please ask about GST registration, eligibility, or required documents."

def save_uploaded_file(media_url):
    """Download and save the uploaded document locally."""
    if not os.path.exists("uploaded_documents"):
        os.makedirs("uploaded_documents")
    filename = os.path.join("uploaded_documents", media_url.split("/")[-1])
    urlretrieve(media_url, filename)
    print(f"File saved: {filename}")

if __name__ == "__main__":
    app.run(debug=True)
