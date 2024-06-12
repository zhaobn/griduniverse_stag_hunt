# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import sem

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
# Time spent
item_actions = df[df['action'] == 'item']
item_actions_sorted = item_actions.sort_values(by=['game_id', 'round_id', 'time_stamp'])
first_item_actions = item_actions_sorted.groupby(['game_id', 'round_id', 'chat_visible', 'others_visible']).first().reset_index()
last_item_actions = item_actions_sorted.groupby(['game_id', 'round_id', 'chat_visible', 'others_visible']).last().reset_index()

first_item_actions['type'] = 'first'
last_item_actions['type'] = 'last'
combined = pd.concat([first_item_actions, last_item_actions])

# Calculate mean and standard error for each round, type, chat_visible, and others_visible
mean_elapse = combined.groupby(['round_id', 'type', 'chat_visible', 'others_visible'])['round_elapse'].mean().reset_index()
std_error = combined.groupby(['round_id', 'type', 'chat_visible', 'others_visible'])['round_elapse'].apply(sem).reset_index()
mean_elapse = mean_elapse.merge(std_error, on=['round_id', 'type', 'chat_visible', 'others_visible'], suffixes=('_mean', '_sem'))

# Plotting
unique_conditions = mean_elapse[['chat_visible', 'others_visible']].drop_duplicates()
n_conditions = unique_conditions.shape[0]

fig, axes = plt.subplots(2, 2, figsize=(15, 12), sharex=True, sharey=True)
axes = axes.flatten()

for i, (ax, (chat_vis, others_vis)) in enumerate(zip(axes, unique_conditions.values)):
  condition_data = mean_elapse[(mean_elapse['chat_visible'] == chat_vis) & (mean_elapse['others_visible'] == others_vis)]
  sns.barplot(x='round_id', y='round_elapse_mean', hue='type', data=condition_data, ci=None, palette=['blue', 'orange'], ax=ax)

  # Add error bars
  for j in range(len(condition_data)):
      x_pos = j // 2 + (j % 2) * 0.4 - 0.2
      y_val = condition_data.iloc[j]['round_elapse_mean']
      y_err = condition_data.iloc[j]['round_elapse_sem']
      ax.errorbar(x=x_pos, y=y_val, yerr=y_err, fmt='none', capsize=5, color='black')

  ax.set_title(f'Chat Visible: {chat_vis}, Others Visible: {others_vis}')
  ax.set_xlabel('Round ID')
  ax.set_ylabel('Mean Round Elapse')

plt.tight_layout()

# %%
# # Games chatted
# chats_per_game = chat_df.groupby(['game_id', 'others_visible'])['action'].count().reset_index()
# chats_per_game['others_visible'] = chats_per_game['others_visible'].astype(str)

# # Get unique values in 'others_visible'
# unique_values = chats_per_game['others_visible'].unique()

# # Define the custom color palette for the unique values in 'others_visible'
# custom_palette = {value: 'blue' if value == 'False' else 'orange' for value in unique_values}

# plt.figure(figsize=(8, 6))
# sns.histplot(data=chats_per_game, x='action', hue='others_visible', palette=custom_palette, binwidth=1, multiple='stack')

# plt.title('Histogram of Number of Chats per Game ID')
# plt.xlabel('Number of Actions')
# plt.ylabel('Frequency')

# legend_labels = ['False', 'True']
# legend_handles = [plt.Rectangle((0,0),1,1, color=custom_palette[label]) for label in legend_labels]
# plt.legend(legend_handles, legend_labels, title='others_visible')


# %%
