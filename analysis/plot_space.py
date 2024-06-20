# %%
import pandas as pd
import numpy as np

import os
import json

import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import sem

# %%
# Get spatial data
def get_positions(file_name, game_id):
  test_data = pd.read_csv(file_name)

  state_data = test_data[test_data['type'] == 'state'][['creation_time', 'details']]
  condition = state_data['details'].str.startswith('{"rows": 15, "items": [{') & state_data['details'].str.contains("\"motion_speed_limit\": 8}, {\"id\":")
  state_data_filtered = state_data[condition]
  state_data_filtered = state_data_filtered.sort_values(by='creation_time').reset_index(drop=True)

  cleaned_data = []
  for index, row in state_data_filtered.iterrows():
    details = json.loads(row['details'])
    round_id = index + 1

    # Extract items data
    item_counter = {}
    for item in details['items']:
      item_id = item['item_id']
      if item_id not in item_counter:
        item_counter[item_id] = 1
      position_x, position_y = item['position']
      item_label = f"{item_id}{item_counter[item_id]}"
      cleaned_data.append([round_id, item_label, position_x, position_y])
      item_counter[item_id] += 1

    # Extract players data
    player_counter = 1
    for player in details['players']:
      item_id = f"player{player_counter}"
      position_x, position_y = player['position']
      cleaned_data.append([round_id, item_id, position_x, position_y])
      player_counter += 1

  cleaned_df = pd.DataFrame(cleaned_data, columns=['round_id', 'item_id', 'position_x', 'position_y'])
  cleaned_df['game_id'] = game_id
  ret_df = cleaned_df[['game_id','round_id','item_id','position_x', 'position_y']]
  return ret_df

ret_df = None
directory = '../demos/Experiment_Data/'
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

for i, file_name in enumerate(sorted(csv_files), start=1):
  game_id = f"{i:03}"  # Format game_id as 3-digit string, e.g., 001, 002, ...
  file_path = os.path.join(directory, file_name)
  cleaned = get_positions(file_path, game_id)
  ret_df = pd.concat([ret_df, cleaned], ignore_index=True)

ret_df.to_csv('start_positions.csv')

# %%
def euclidean_distance(x1, y1, x2, y2):
  return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def get_distance(file_name, game_id):
  cleaned_df = get_positions(file_name, game_id)

  distance_data = []
  round_ids = cleaned_df['round_id'].unique()
  for round_id in round_ids:
    round_data = cleaned_df[cleaned_df['round_id'] == round_id]

    # Get positions of hares and stags
    hare1_pos = round_data[round_data['item_id'] == 'hare1'][['position_x', 'position_y']].values[0]
    hare2_pos = round_data[round_data['item_id'] == 'hare2'][['position_x', 'position_y']].values[0]
    stag1_pos = round_data[round_data['item_id'] == 'stag1'][['position_x', 'position_y']].values[0]

    # Get player positions and calculate distances
    for player_id in ['player1', 'player2']:
      player_pos = round_data[round_data['item_id'] == player_id][['position_x', 'position_y']].values[0]

      to_hare1 = euclidean_distance(player_pos[0], player_pos[1], hare1_pos[0], hare1_pos[1])
      to_hare2 = euclidean_distance(player_pos[0], player_pos[1], hare2_pos[0], hare2_pos[1])
      to_stag1 = euclidean_distance(player_pos[0], player_pos[1], stag1_pos[0], stag1_pos[1])

      distance_data.append([round_id, player_id, to_hare1, to_hare2, to_stag1])

  # Convert the distance data into a new DataFrame
  distance_df = pd.DataFrame(distance_data, columns=['round_id', 'player_id', 'to_hare1', 'to_hare2', 'to_stag1'])
  distance_df['game_id'] = game_id

  ret_df = distance_df[['game_id','round_id','player_id','to_hare1', 'to_hare2', 'to_stag1']]
  return ret_df

ret_df = None
directory = '../demos/Experiment_Data/'
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

for i, file_name in enumerate(sorted(csv_files), start=1):
  game_id = f"{i:03}"  # Format game_id as 3-digit string, e.g., 001, 002, ...
  file_path = os.path.join(directory, file_name)
  cleaned = get_distance(file_path, game_id)
  ret_df = pd.concat([ret_df, cleaned], ignore_index=True)

# ret_df.to_csv('start_distance.csv')

# %% Append game action data
df_action = pd.read_csv('all_actions.csv', index_col=0).reset_index(drop=True)
df_distance = pd.read_csv('start_distance.csv', index_col=0).reset_index(drop=True)

df_distance_action = df_distance.merge(df_action[['game_id', 'round_id', 'chat_visible', 'others_visible', 'action']],
                                       on=['game_id', 'round_id'], how='left')
df_distance_action.to_csv('start_distance.csv', index=False)

# %%
def get_position_type(row):
  if row['to_stag1'] < row['to_hare1'] and row['to_stag1'] < row['to_hare2']:
    return 'stag_closest'
  elif row['to_stag1'] > row['to_hare1'] and row['to_stag1'] > row['to_hare2']:
    return 'stag_furthermost'
  else:
    return 'stag_between'

df_distance_action['position_type'] = df_distance_action.apply(get_position_type, axis=1)
df_distance_action['is_coop'] = (df_distance_action['action'] == 'stag').astype(int)
grouped = df_distance_action.groupby(['position_type', 'round_id', 'chat_visible', 'others_visible']).agg(
    cooperation_rate=('is_coop', 'mean'),
    cooperate_se=('is_coop', lambda x: np.std(x) / np.sqrt(len(x)))
).reset_index()



fig, axes = plt.subplots(2, 2, figsize=(14, 12), sharey=True)
conditions = [(True, True), (True, False), (False, True), (False, False)]
titles = [
  "Chat Visible, Others Visible",
  "Chat Visible, Others Not Visible",
  "Chat Not Visible, Others Visible",
  "Chat Not Visible, Others Not Visible"
]
for ax, (chat_visible, others_visible), title in zip(axes.flatten(), conditions, titles):
  data = grouped[(grouped['chat_visible'] == chat_visible) & (grouped['others_visible'] == others_visible)]
  sns.barplot(data=data, x='position_type', y='cooperation_rate', ax=ax, ci=None, palette='muted')

  # # Adding error bars manually
  # for idx, row in data.iterrows():
  #   ax.errorbar(
  #     x=idx, y=row['cooperation_rate'], yerr=row['cooperate_se'], fmt='none', c='black'
  #   )

  ax.set_title(title)
  ax.set_xlabel('Position Type')
  ax.set_ylabel('Cooperation Rate')

plt.tight_layout()
# %%
