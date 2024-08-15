
library(dplyr)
library(tidyr)
library(lubridate)
library(ggplot2)

pos = read.csv('start_distance.csv')

action = read.csv('all_cleaned.csv')
action$time_stamp <- ymd_hms(action$time_stamp)

first_action = action %>%
  filter(action=='item') %>%
  select(game_id, round_id, player_id, value, time_stamp) %>%
  group_by(game_id, round_id, player_id) %>%
  slice_min(time_stamp) %>%
  select(-time_stamp) %>%
  mutate(player_id=paste0('player',player_id))


df_dist = pos %>%
  #filter(round_id==5) %>%
  mutate(to_hare = ifelse(to_hare1 < to_hare2, to_hare1, to_hare2)) %>%
  mutate(distance = (to_stag1-to_hare)/28) %>%
  select(round_id, game_id, player_id, distance)

df_action = df_dist %>%
  left_join(first_action, by=c('game_id', 'round_id', 'player_id')) %>%
  mutate(action=ifelse(is.na(value), 'stag',  value)) %>%
  select(game_id, round_id, player_id, action)

df_info = action %>%
  select(game_id, round_id, others_visible, chat_visible) %>%
  unique()

df_dist_long <- df_dist %>%
  pivot_wider(names_from = player_id, values_from = distance)


df_extended = df_dist_long %>%
  left_join(df_info, by=c('round_id', 'game_id')) %>%
  full_join(df_action, by=c('round_id', 'game_id')) %>%
  mutate(coop=as.numeric(action=='stag'))

# make scatter plot
ggplot(df_extended, aes(x = player1, y = player2)) +
  geom_point(data = subset(df_extended, coop == 0), aes(color = factor(coop), shape = factor(coop)), size = 3, position = position_jitter(width = 0.1, height = 0.1)) +
  geom_point(data = subset(df_extended, coop == 1), aes(color = factor(coop), shape = factor(coop)), size = 3, position = position_jitter(width = 0.1, height = 0.1)) +
  # geom_point(aes(color = factor(coop), shape = factor(coop)), size = 3, position = position_jitter(width = 0.1, height = 0.1)) +
  geom_hline(yintercept=0) +
  geom_vline(xintercept=0) +
  scale_color_manual(values = c('0' = 'gray', '1' = 'brown'), labels = c('Hare', 'Stag')) +
  scale_shape_manual(values = c('0' = 17, '1' = 16), labels = c('Hare', 'Stag')) +
  labs(x = 'Player 1 distance', y = 'Player 2 distance', color = 'Action', shape = 'Action') +
  theme_bw() +
  facet_grid(others_visible~chat_visible, labeller = label_both) +
  theme(text = element_text(size = 20))

