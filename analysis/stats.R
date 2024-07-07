
library(dplyr)
library(ggplot2)

data = read.csv('all_data.csv')

coop_data = data %>%
  filter(action=='item') %>%
  select(game_id, round_id, player_id, value, chat_visible, others_visible) %>%
  mutate(is_coop = value=='stag') %>%
  group_by(game_id, round_id, chat_visible, others_visible) %>%
  summarise(is_coop = sum(is_coop)/n()==1) %>%
  ungroup()
