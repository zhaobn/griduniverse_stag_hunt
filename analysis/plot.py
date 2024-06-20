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

# %% Basic stats
cond_data = df.groupby(['chat_visible', 'others_visible'])['game_id'].nunique().reset_index()
cond_data.columns = ['chat_visible', 'others_visible', 'num_games']


# %%
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
grouped_df.to_csv('all_actions.csv')

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

# %% Only last time
game_elapse = last_item_actions.groupby(['round_id', 'chat_visible', 'others_visible'])['round_elapse'].mean().reset_index()
game_elapse_se = last_item_actions.groupby(['round_id', 'chat_visible', 'others_visible'])['round_elapse'].apply(sem).reset_index()
game_elapse = game_elapse.merge(game_elapse_se, on=['round_id', 'chat_visible', 'others_visible'], suffixes=('_mean', '_sem'))

groups = game_elapse.groupby(['chat_visible', 'others_visible'])
plt.figure(figsize=(8, 6))
colors = ['blue', 'green', 'red', 'orange']
linestyles = ['-', '--', '-.', ':']
for i, (name, group) in enumerate(groups):
    plt.errorbar(group['round_id'], group['round_elapse_mean'], yerr=group['round_elapse_sem'], label=name, color=colors[i % len(colors)], linestyle=linestyles[i % len(linestyles)])

plt.xlabel('Round ID')
plt.ylabel('Time Elapse (seconds)')
plt.title('Game Time by Round')
plt.xticks([1, 2, 3, 4, 5])
plt.legend(title=('Chat Visible', 'Others Visible'))
plt.grid(True)

# %%
# Do groups ever switch from stag to hare?
def compute_group_type(sub_df):
  # Find the earliest round where action is 'stag'
  stag_rounds = sub_df[sub_df['action'] == 'stag']
  if stag_rounds.empty:
    return 0
  earliest_stag_round = stag_rounds['round_id'].min()

  # Check if all subsequent rounds are 'stag'
  subsequent_rounds = sub_df[sub_df['round_id'] >= earliest_stag_round]
  if (subsequent_rounds['action'] == 'stag').all():
    return earliest_stag_round
  else:
    return -1

group_type_df = grouped_df.groupby(['game_id', 'chat_visible', 'others_visible'])
group_type_df = group_type_df.apply(compute_group_type).reset_index(name='group_type')

percentage_df = group_type_df.groupby(['chat_visible', 'others_visible', 'group_type']).size().reset_index(name='count')
total_counts = group_type_df.groupby(['chat_visible', 'others_visible']).size().reset_index(name='total')
percentage_df = pd.merge(percentage_df, total_counts, on=['chat_visible', 'others_visible'])
percentage_df['percentage'] = (percentage_df['count'] / percentage_df['total']) * 100

g = sns.FacetGrid(percentage_df, col='chat_visible', row='others_visible', margin_titles=True, height=4, aspect=0.8)
g.map_dataframe(sns.barplot, x='group_type', y='percentage', order=sorted(group_type_df['group_type'].unique()))
g.set_axis_labels('Group Type', 'Percentage')
g.set_titles(col_template='chat_visible={col_name}', row_template='others_visible={row_name}')

plt.tight_layout()

# %% Does actually chatting improve collaboration?
def has_chatted(group):
  chat_count = group['action'].eq('chat').sum()
  return chat_count if chat_count > 0 else 0

filtered_df = df[df['chat_visible'] == True]
chat_grouped = filtered_df.groupby(['game_id', 'others_visible'])
chat_grouped = chat_grouped.apply(lambda x: pd.Series({'chat_count': has_chatted(x)})).reset_index()
chat_grouped['has_chatted'] = (chat_grouped['chat_count'] > 0).astype(int)

# %%
percentage_has_chatted = chat_grouped.groupby('others_visible')['has_chatted'].mean() * 100
plt.figure(figsize=(2, 4))
sns.barplot(x=percentage_has_chatted.index, y=percentage_has_chatted.values)
plt.xlabel('Others Visible')
plt.ylabel('Percentage')
plt.title('Have Chatted')
plt.ylim(0, 100)

# %%
filtered_grouped_df = grouped_df[grouped_df['chat_visible'] == True]
chat_extra = filtered_grouped_df.merge(chat_grouped, on=['game_id', 'others_visible'], how='left')

chat_percentage_stag = chat_extra.groupby(['round_id', 'others_visible', 'has_chatted'])['action'].apply(lambda x: (x == 'stag').mean() * 100).reset_index()
chat_standard_errors = chat_extra.groupby(['round_id', 'others_visible', 'has_chatted'])['action'].apply(lambda x: (x == 'stag').sem() * 100).reset_index()
chat_merged_df = pd.merge(chat_percentage_stag, chat_standard_errors, on=['round_id', 'others_visible', 'has_chatted'], suffixes=('_percentage', '_error'))

groups = chat_merged_df.groupby(['others_visible', 'has_chatted'])
plt.figure(figsize=(8, 6))
colors = ['blue', 'green', 'red', 'orange']
linestyles = ['-', '--', '-.', ':']
for i, (name, group) in enumerate(groups):
  plt.errorbar(group['round_id'], group['action_percentage'], yerr=group['action_error'], label=name, color=colors[i % len(colors)], linestyle=linestyles[i % len(linestyles)])

plt.xlabel('Round ID')
plt.ylabel('Cooperation Percentage')
plt.title('Cooperation Percentage by Round')
plt.xticks([1, 2, 3, 4, 5])
plt.legend(title=('Others Visible', 'Has Chatted'))
plt.grid(True)

# %%
chat_merged_df_true = chat_merged_df[chat_merged_df['others_visible'] == True]
chat_merged_df_false = chat_merged_df[chat_merged_df['others_visible'] == False]

# Plot
groups_false = chat_merged_df[chat_merged_df['others_visible'] == False].groupby('has_chatted')
groups_true = chat_merged_df[chat_merged_df['others_visible'] == True].groupby('has_chatted')

fig, axes = plt.subplots(2, 1, figsize=(5, 6))

# Plot for others_visible True
ax = axes[0]
for i, (name, group) in enumerate(groups_true):
    ax.errorbar(group['round_id'], group['action_percentage'], yerr=group['action_error'], label=name, color=colors[i], linestyle=linestyles[i])

ax.set_xlabel('Round ID')
ax.set_ylabel('Cooperation Percentage')
ax.set_title('Cooperation Percentage by Round (Others Visible = True)')
ax.set_xticks([1, 2, 3, 4, 5])
ax.legend(title='Has Chatted')
ax.grid(True)

# Plot for others_visible False
ax = axes[1]
for i, (name, group) in enumerate(groups_false):
    ax.errorbar(group['round_id'], group['action_percentage'], yerr=group['action_error'], label=name, color=colors[i], linestyle=linestyles[i])

ax.set_xlabel('Round ID')
ax.set_ylabel('Cooperation Percentage')
ax.set_title('Cooperation Percentage by Round (Others Visible = False)')
ax.set_xticks([1, 2, 3, 4, 5])
ax.legend(title='Has Chatted')
ax.grid(True)


plt.tight_layout()

# %%
grouped_chat_extra = chat_extra.groupby(['game_id', 'others_visible'])
cooperation_rate = grouped_chat_extra['action'].apply(lambda x: (x == 'stag').mean() * 100).reset_index(name='cooperation_rate')
group_chat_count = grouped_chat_extra['chat_count'].max().reset_index()
chat_coor_grouped_df = pd.merge(cooperation_rate, group_chat_count, on=['game_id', 'others_visible'])

plt.figure(figsize=(5, 5))
sns.scatterplot(data=chat_coor_grouped_df, x='chat_count', y='cooperation_rate', hue='others_visible', style='others_visible', palette='colorblind', markers=['o', 's'])
sns.regplot(data=chat_coor_grouped_df[chat_coor_grouped_df['others_visible'] == True], x='chat_count', y='cooperation_rate', scatter=False, ci=95, color='blue', label='Others Visible True')
sns.regplot(data=chat_coor_grouped_df[chat_coor_grouped_df['others_visible'] == False], x='chat_count', y='cooperation_rate', scatter=False, ci=95, color='green', label='Others Visible False')

plt.xlabel('Chat Count')
plt.ylabel('Cooperation Rate')
plt.title('Scatter Plot of Cooperation Rate vs Chat Count with Regression Lines')
plt.legend(title='Others Visible')


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
