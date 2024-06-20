
library(dplyr)
library(ggplot2)

data = read.csv('start_distance.csv')

# categorize types
data_position = data %>%
  mutate(position_type=ifelse(to_stag1<to_hare1 & to_stag1<to_hare2, 'close',
                              ifelse(to_stag1>to_hare1 & to_stag1>to_hare2, 'far', 'between'))) %>%
  group_by(game_id, round_id, chat_visible, others_visible, action) %>%
  summarise(position_type=case_when(
    all(position_type == "close") ~ "both_close",
    all(position_type == "far") ~ "both_far",
    TRUE ~ "in_between"
  )) %>%
  ungroup() %>%
  mutate(is_stag = as.numeric(action=='stag'))

# compute cooperation rate
data_grouped = data_position %>%
  group_by(chat_visible, others_visible, position_type) %>%
  summarise(coop_mean=mean(is_stag), se=sd(is_stag)/sqrt(n())) %>%
  filter(nchar(chat_visible)>0)

# plot
ggplot(data_grouped, aes(x = position_type, y = coop_mean, fill = position_type)) +
  geom_bar(stat = "identity", position = position_dodge(), width = 0.7) +
  geom_errorbar(aes(ymin = coop_mean - se, ymax = coop_mean + se), 
                width = 0.2, position = position_dodge(0.7)) +
  labs(title = "Cooperation Rate by Conditions",
       x = "Position Type",
       y = "Cooperation Rate (Mean)") +
  theme_minimal() +
  facet_grid(others_visible~chat_visible, labeller = label_both) +
  theme(legend.position = 'bottom')
