# %%
import pandas as pd
import json
import re
import os

# %%
# test with one csv
def parse_data(file_name, game_id):
  test_data = pd.read_csv(file_name)

  # only look at events
  event_data = test_data[test_data['type'] == 'event'][['creation_time', 'details']]

  # filter key info
  condition = (event_data['details'].str.startswith('{"type": "new_round"') |
               event_data['details'].str.startswith('{"item"') |
               event_data['details'].str.startswith('{"type": "connect"') |
               event_data['details'].str.startswith('{"type": "chat"'))
  filtered_data = event_data[condition]
  filtered_sorted = filtered_data.sort_values(by='creation_time').reset_index(drop=True)
  # filtered_data.to_csv('test_filtered.csv', index=False)

  # clean up item selections
  transformed_data = []
  current_round = 1

  for index, row in filtered_sorted.iterrows():
      creation_time = row['creation_time']
      details = json.loads(row['details'])

      # Check if the event is a new round and update the current round
      if details.get('type') == 'new_round':
          current_round = details.get('round')+1

      # If the event is an item interaction, extract the relevant information
      elif 'item' in details:
          player_id = details.get('player_id')
          item_id = details['item'].get('item_id')
          # Append the transformed data to the list
          transformed_data.append({
              'round_id': current_round,
              'time_stamp': creation_time,
              'player_id': player_id,
              'action': 'item',
              'value': item_id
          })

      # Append chat history
      elif details.get('type') == 'chat':
        player_id = details.get('player_id')
        chat_content = details.get('contents')
        transformed_data.append({
            'round_id': current_round,
            'time_stamp': creation_time,
            'player_id': player_id,
            'action': 'chat',
            'value': chat_content
        })

  # Create a new DataFrame from the transformed data
  transformed_df = pd.DataFrame(transformed_data)

  # Append extra data
  info_rows = test_data[test_data['details'].str.startswith('{"rows": 15, "round": 0,')]
  first_info_row = info_rows.iloc[0]
  details = first_info_row['details']
  match = re.search(r'"chat_visible": (true|false), "others_visible": (true|false)', details)

  transformed_df['chat_visible'] =  match.group(1)
  transformed_df['others_visible'] =  match.group(2)
  transformed_df['game_id'] = game_id

  ret_df = transformed_df[['game_id','round_id','player_id','action', 'value', 'chat_visible','others_visible','time_stamp']]

  return ret_df

parse_data('../demos/Experiment_Data/DataTrial-experiment-2024-04-13_15-01-28-14 (1).csv', 'x')

# %% debug
# file_name = '../demos/Experiment_Data/DataTrial-experiment-2024-04-13_15-06-05-4 (1).csv'

# %%
# load all data
ret_df = None
directory = '../demos/Experiment_Data/'
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

for i, file_name in enumerate(sorted(csv_files), start=1):
    game_id = f"{i:03}"  # Format game_id as 3-digit string, e.g., 001, 002, ...
    file_path = os.path.join(directory, file_name)
    cleaned = parse_data(file_path, game_id)
    ret_df = pd.concat([ret_df, cleaned], ignore_index=True)

ret_df.to_csv('all_cleaned.csv')

# %% Get all game round time
time_df = None
directory = '../demos/Experiment_Data/'
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

for i, file_name in enumerate(sorted(csv_files), start=1):
  game_id = f"{i:03}"  # Format game_id as 3-digit string, e.g., 001, 002, ...
  file_path = os.path.join(directory, file_name)
  test_data = pd.read_csv(file_path)
  event_data = test_data[test_data['type'] == 'event'][['creation_time', 'details']]
  condition = event_data['details'].str.startswith('{"type": "connect", "player_id": "2"') | event_data['details'].str.startswith('{"type": "new_round"')
  filtered_data = event_data[condition]
  filtered_sorted = filtered_data.sort_values(by='creation_time').reset_index(drop=True)
  filtered_sorted = filtered_sorted.head(5)
  filtered_sorted['round'] = [1,2,3,4,5]
  filtered_sorted['game_id'] = game_id
  filtered_data = filtered_sorted[['game_id', 'round', 'creation_time']]
  time_df = pd.concat([time_df, filtered_data], ignore_index=True)

time_df.to_csv('all_time.csv')

# %%
dat_df = pd.read_csv('all_cleaned.csv', index_col=0).reset_index(drop=True)
time_df = pd.read_csv('all_time.csv', index_col=0).reset_index(drop=True)

time_df = time_df.rename(columns={'round': 'round_id'})
merged_df = pd.merge(dat_df, time_df, on=['game_id', 'round_id'])
merged_df = merged_df.rename(columns={'creation_time': 'round_start'})

merged_df['round_start'] = pd.to_datetime(merged_df['round_start'])
merged_df['time_stamp'] = pd.to_datetime(merged_df['time_stamp'])
merged_df['round_elapse'] = ((merged_df['time_stamp'] - merged_df['round_start']).dt.total_seconds()).round(2)

ret_df = merged_df[['game_id','round_id','player_id','action','value',
                    'chat_visible','others_visible','time_stamp','round_start','round_elapse']]
ret_df.to_csv('all_data.csv')
