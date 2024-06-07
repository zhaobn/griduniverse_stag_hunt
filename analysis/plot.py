# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# %%
# Read the CSV file
df = pd.read_csv('all_data.csv', index_col=0).reset_index(drop=True)
df_items = df[df['action'] == 'item']
df_items['time_stamp'] = pd.to_datetime(df_items['time_stamp'])

# Function to determine action based on item choices
def determine_action(group):
  if (group['value'] == 'stag').all():
    return 'stag'
  elif (group['value'] == 'hare').all():
    return 'hare'
  else:
    return 'miss'

# cooperation rate
grouped_df = df_items.groupby(['game_id', 'round_id', 'chat_visible', 'others_visible']).apply(determine_action).reset_index()
grouped_df.columns = ['game_id', 'round_id', 'chat_visible', 'others_visible', 'action']
percentage_stag = grouped_df.groupby(['round_id', 'chat_visible', 'others_visible'])['action'].apply(lambda x: (x == 'stag').mean() * 100).reset_index()
standard_errors = grouped_df.groupby(['round_id', 'chat_visible', 'others_visible'])['action'].apply(lambda x: (x == 'stag').sem() * 100).reset_index()

# Merge percentage_stag and standard_errors
merged_df = pd.merge(percentage_stag, standard_errors, on=['round_id', 'chat_visible', 'others_visible'], suffixes=('_percentage', '_error'))

# Plot
groups = merged_df.groupby(['chat_visible', 'others_visible'])
plt.figure(figsize=(8, 6))
colors = ['blue', 'green', 'red', 'orange']
linestyles = ['-', '--', '-.', ':']
for i, (name, group) in enumerate(groups):
    plt.errorbar(group['round_id'], group['action_percentage'], yerr=group['action_error'], label=name, color=colors[i % len(colors)], linestyle=linestyles[i % len(linestyles)])

plt.xlabel('Round ID')
plt.ylabel('Cooperation Percentage')
plt.title('Cooperation Percentage by Round')
plt.xticks([1, 2, 3, 4, 5])
plt.legend(title=('Chat Visible', 'Others Visible'))
plt.grid(True)

# %%
# Number of chats
chat_df = df[(df['chat_visible'] == True) & (df['action'] == 'chat')]
chats_per_round = chat_df.groupby(['round_id', 'others_visible'])['action'].count().reset_index()
game_count = chat_df.groupby('others_visible')['game_id'].nunique()

merged_df = chats_per_round.merge(game_count, left_on='others_visible', right_index=True)
merged_df['mean_chats'] = merged_df['action'] / merged_df['game_id']
merged_df['mean_chats'] = merged_df['mean_chats'].round(2)

plt.figure(figsize=(8, 6))
sns.barplot(data=merged_df, x='round_id', y='mean_chats', hue='others_visible', palette='colorblind', dodge=True)

# %%
# Games chatted
chats_per_game = chat_df.groupby(['game_id', 'others_visible'])['action'].count().reset_index()
chats_per_game['others_visible'] = chats_per_game['others_visible'].astype(str)

# Get unique values in 'others_visible'
unique_values = chats_per_game['others_visible'].unique()

# Define the custom color palette for the unique values in 'others_visible'
custom_palette = {value: 'blue' if value == 'False' else 'orange' for value in unique_values}

plt.figure(figsize=(8, 6))
sns.histplot(data=chats_per_game, x='action', hue='others_visible', palette=custom_palette, binwidth=1, multiple='stack')

plt.title('Histogram of Number of Actions per Game ID')
plt.xlabel('Number of Actions')
plt.ylabel('Frequency')

legend_labels = ['False', 'True']
legend_handles = [plt.Rectangle((0,0),1,1, color=custom_palette[label]) for label in legend_labels]
plt.legend(legend_handles, legend_labels, title='others_visible')


# %%
