require(ggplot2)
require(GGally)
require(reshape2)
require(lme4)
require(compiler)
require(parallel)
require(boot)
require(lattice)

hunt <- read.csv("C:/Users/lslin/OneDrive/Desktop/Senior Thesis/Analysis/trials.csv")

m <- glmer(stag ~  trial * (visible + chat) + (1 | dyad), 
           data = hunt, 
           family = binomial)

# print the mod results without correlations among fixed effects
print(m, corr = FALSE)
summary(m)