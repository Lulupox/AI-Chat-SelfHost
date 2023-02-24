def count_unique_words(file_path):
    with open(file_path, 'r', encoding='utf8') as f:
        words = f.read().split()
    unique_words = set(words)
    return len(unique_words)

# Exemple d'utilisation :
file_path = 'filtered_training_data.md'
count = count_unique_words(file_path)
print(f"Le fichier {file_path} contient {count} mots différents.")
