from flask import Flask, jsonify
import pickle
import pandas as pd
from preprocessing import preprocessing_text_with_stemming
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/dataset', methods=['GET'])
def get_dataset():
    fix_file = "dataset/fix_data.csv"
    fix_df = pd.read_csv(fix_file)
    fix_data_json = fix_df.to_dict(orient='records')
    return jsonify(fix_data_json), 200

@app.route('/predict/<text>', methods=['GET'])
def predict(text):
    f = open('tfidf.pickle', 'rb')
    tfidf = pickle.load(f)
    f.close()

    w = open('mnb.pickle', 'rb')
    mnb = pickle.load(w)
    w.close()

    preprocessed_text = preprocessing_text_with_stemming(text)
    transformed_input = tfidf.transform_tfidf([' '.join(preprocessed_text)])
    predicted_class = mnb.predict(transformed_input)[0]
    label = "Sincere" if predicted_class == 0 else "Insincere"

    tfidf_per_word = getTFIDF(tfidf.vocabulary, transformed_input, preprocessed_text)
    likelihood_per_word_0 = getLikelihood(tfidf.vocabulary, mnb.likelihood, preprocessed_text, 0)
    likelihood_per_word_1 = getLikelihood(tfidf.vocabulary, mnb.likelihood, preprocessed_text, 1)
    priors = {0 : mnb.prior[0], 1 : mnb.prior[1] }
    likelihoods = {0 : likelihood_per_word_0, 1: likelihood_per_word_1}
    posteriors = {0 : mnb.posteriors[0], 1: mnb.posteriors[1]}
    
    result = {
        "input_text": text,
        "predicted_class": label,
        "tfidf_per_word": tfidf_per_word,
        # "tfidf": f"{transformed_input[0]}",
        "preprocessed_text": preprocessed_text,
        "priors": priors,
        "likelihoods": likelihoods,
        "posteriors": posteriors
    }
    return jsonify(result), 200

def getTFIDF(vocab, tfidf_score, sentence):
    tfidf_sentence = [0] * len(sentence)
    for i, word in enumerate(sentence):
        for j, val in enumerate(vocab):
            if val == word:
                tfidf_sentence[i] = tfidf_score[0][j]
    return tfidf_sentence

def getLikelihood(vocab, likelihood, sentence, label):
    likelihood_sentence = [0] * len(sentence)
    for i, word in enumerate(sentence):
        for j, val in enumerate(vocab):
            if val == word:
                likelihood_sentence[i] = likelihood[label].tolist()[j]
    return likelihood_sentence

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
    predict("aselole")
