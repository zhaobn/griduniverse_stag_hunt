# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# %%
# Read the CSV file
df = pd.read_csv('all_cleaned.csv')
df['time_stamp'] = pd.to_datetime(df['time_stamp'])

# Function to determine action based on item choices
def determine_action(group):
  if (group['item'] == 'stag').all():
    return 'stag'
  elif (group['item'] == 'hare').all():
    return 'hare'
  else:
    return 'miss'

# cooperation rate
grouped_df = df.groupby(['game_id', 'round_id', 'chat_visible', 'others_visible']).apply(determine_action).reset_index()
grouped_df.columns = ['game_id', 'round_id', 'chat_visible', 'others_visible', 'action']

# %%
# make plot
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
