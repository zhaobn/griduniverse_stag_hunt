require(ggplot2)

# Assuming hunt is your data frame
hunt <- read.csv("C:/Users/lslin/OneDrive/Desktop/Senior Thesis/Analysis/plot_data.csv")

# Convert 'visible' to factor if it's not already
hunt$visible <- factor(hunt$visible)

# Create four separate data frames based on the combinations of 'chat' and 'visible'
hunt_chat0_visible0 <- subset(hunt, chat == 0 & visible == 0)
hunt_chat0_visible1 <- subset(hunt, chat == 0 & visible == 1)
hunt_chat1_visible0 <- subset(hunt, chat == 1 & visible == 0)
hunt_chat1_visible1 <- subset(hunt, chat == 1 & visible == 1)

# Define the order of the plots
plot_order <- c("No Communication", "Players Visible", "Chat On", "Players Visible and Chat On")

hunt_chat0_visible0$x_order <- factor("No Communication", levels = plot_order)
hunt_chat0_visible1$x_order <- factor("Players Visible", levels = plot_order)
hunt_chat1_visible0$x_order <- factor("Chat On", levels = plot_order)
hunt_chat1_visible1$x_order <- factor("Players Visible and Chat On", levels = plot_order)

# Combine all data frames
combined_data <- rbind(hunt_chat0_visible0, hunt_chat0_visible1, hunt_chat1_visible0, hunt_chat1_visible1)

# Create a vector of colors for each combination of chat and visible
my_colors <- c("blue", "red", "green", "orange")

# Create violin plots
p <- ggplot(combined_data, aes(x = x_order, y = stag, fill = interaction(chat, visible))) +
  geom_violin() +
  scale_fill_manual(values = my_colors) +  # Specify colors
  labs(x = "Visibility and Chat", y = "Number of Stags Collected") +
  theme_minimal() +
  guides(fill = FALSE)  # Remove the legend for fill

p
