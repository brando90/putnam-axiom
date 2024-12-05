import Levenshtein

# Define the strings
str1 = 'kitten'
str2 = 'sitting'

# Calculate the Levenshtein distance
distance = Levenshtein.distance(str1, str2)

print(f'The Levenshtein distance between "{str1}" and "{str2}" is {distance}.')
