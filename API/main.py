import os
import tensorflow as tf
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class TrainingVisualizer(tf.keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.losses = []
        self.accs = []

    def on_epoch_end(self, epoch, logs={}):
        self.losses.append(logs.get('loss'))
        self.accs.append(logs.get('accuracy'))
        plt.plot(range(len(self.losses)), self.losses, 'b')
        plt.plot(range(len(self.accs)), self.accs, 'r')
        plt.title('Training Loss and Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Loss', 'Accuracy'], loc='upper left')
        plt.show()

# Chargement des données d'entraînement
training_data = open("filtered_training_data.md", "r", encoding='utf8').read()
corpus = training_data.lower().split("\n")

# Création d'un tokenizer
tokenizer = tf.keras.preprocessing.text.Tokenizer()
tokenizer.fit_on_texts(corpus)
total_words = len(tokenizer.word_index) + 1

# Préparation des données d'entraînement
input_sequences = []
for line in corpus:
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

# Remplissage des séquences pour qu'elles aient toutes la même longueur
max_sequence_len = max([len(seq) for seq in input_sequences])
input_sequences = tf.keras.preprocessing.sequence.pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre')

# Séparation des données en entrée (X) et en sortie (y)
X = input_sequences[:,:-1]
y = input_sequences[:,-1]

# Conversion des étiquettes de sortie en format catégoriel
y = tf.keras.utils.to_categorical(y, num_classes=total_words)


# Configuration de la visibilité de la GPU
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_visible_devices(physical_devices, 'GPU')

# Définition du modèle de langage naturel
model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Embedding(total_words, 5314, input_length=max_sequence_len-1))
model.add(tf.keras.layers.LSTM(100, return_sequences=True))
model.add(tf.keras.layers.Dropout(0.2))
model.add(tf.keras.layers.LSTM(100))
model.add(tf.keras.layers.Dropout(0.2))
model.add(tf.keras.layers.Dense(total_words, activation='softmax'))

# route pour entraîner le modèle
@app.route('/train_model', methods=['GET'])
def train_model():
    # Compilation et entraînement du modèle
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    history = model.fit(X, y, epochs=150, verbose=1)

    # Affichage des courbes de perte et d'accuracy
    plt.plot(history.history['loss'])
    plt.plot(history.history['accuracy'])
    plt.title('Evolution de la perte et de l\'accuracy pendant l\'entraînement')
    plt.xlabel('Epoch')
    plt.legend(['Perte', 'Accuracy'], loc='upper right')
    plt.show()

    # Sauvegarde du modèle dans un fichier
    if not os.path.exists("saved_model"):
        os.mkdir("saved_model")
    model.save("saved_model/nlp_model")

    return jsonify({'message': 'Le modèle a été entraîné avec succès!'})

# route pour utiliser le modèle
@app.route('/predict', methods=['POST'])
def predict():
    # Chargement du modèle depuis le fichier
    model = tf.keras.models.load_model("saved_model/nlp_model")

    # Charger les données d'entrée
    input_data = request.get_json()

    seed_text = input_data['seed_text']
    next_words = int(input_data['next_words'])

    

    # Chargement des données d'entraînement
    with open("training_data.txt", "a", encoding='utf8') as f:
        f.write(f'\n{seed_text}')
        f.close()

    for _ in range(next_words):
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        token_list = tf.keras.preprocessing.sequence.pad_sequences([token_list], maxlen=max_sequence_len-1, padding='pre')
        predicted = model.predict(token_list, verbose=0)
        predicted_class = tf.argmax(predicted, axis=-1)
        output_word = ""
        for word, index in tokenizer.word_index.items():
            if index == predicted_class:
                output_word = word
                break
        seed_text += " " + output_word

    response = {'generated_text': seed_text}
    return jsonify(response)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)