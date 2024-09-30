# https://chatgpt.com/c/66f9fdee-d1e4-8001-8ec5-4fcffa6040cc

import pandas as pd

# Data from the table
data = {
    'Model': ['Claude-3.5 Sonnet', 'GPT-4', 'Qwen2-Math-7B-Instruct', 'DeepSeek-Math-Instruct', 'Llama-3-8b Instruct', 'Gemma-7B-it', 'Gemma-2B-it', 'Mistral-7B-Instruct-v0.3',
              'DeepSeek-Math-RL', 'NuminaMath-7B', 'Qwen2-Math-7B', 'Mistral-7B-v0.3', 'DeepSeek-Math-7B', 'Llama-3-8B', 'Gemma-7B', 'Gemma-2B'],
    'Original_Percentage': [26.40, 13.20, 10.19, 7.92, 7.92, 3.39, 3.39, 2.26, 10.56, 10.56, 9.81, 6.78, 6.03, 3.77, 3.01, 2.63],
    'Variation_Percentage': [13.2, 9.43, 6.41, 3.77, 3.01, 2.64, 1.88, 3.39, 8.67, 4.53, 5.28, 3.39, 4.15, 1.88, 2.26, 2.26]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Calculate the absolute and relative decreases
df['Absolute_Decrease'] = df['Original_Percentage'] - df['Variation_Percentage']
df['Relative_Decrease'] = (df['Absolute_Decrease'] / df['Original_Percentage']) * 100

# Compute the averages
average_absolute_decrease = df['Absolute_Decrease'].mean()
average_relative_decrease = df['Relative_Decrease'].mean()

average_absolute_decrease, average_relative_decrease
