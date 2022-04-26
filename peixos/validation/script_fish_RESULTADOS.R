library(ggplot2)
library(dplyr)
library(tidyr)
library(gridExtra)
library(ggpubr)
library(colorspace)
library(viridis)
library(RColorBrewer)
library(cowplot)
library(jcolors)
library(bspec)

#----------------    DATOS    ------------------------------

setwd("/home/ivan/documents/loveyourdata/peixos/LYD-Peixos/playground")


#       Individual dataframes
lista_ind <- list.files(pattern = "*A_individual.csv*")
data_ind <- lapply(lista_ind, read.csv, header = TRUE, sep = ";")


#       Global dataframes
lista_global <- list.files(pattern = "*A_global.csv*")

data_global <- lapply(lista_global, read.csv, header = TRUE, sep = ";")

print(lista_ind)


for(i in 1:length(lista_ind)) {

  #       2. Individual dataframes processing

  save.name_ind <- sub(".csv", "", lista_ind[[i]])

  save.name_ind <- sub("_individual", "" , save.name_ind)

  data_ind[[i]]$replica <- substr(save.name_ind, nchar(save.name_ind), nchar(save.name_ind))

  save.name_ind <- sub(paste0("_", unique(data_ind[[i]]$replica)), "", save.name_ind)

  data_ind[[i]]$forma <- substr(save.name_ind, 1, 1)


  if (any(substr(save.name_ind, 3, 3) == LETTERS)) {
    data_ind[[i]]$altura <- substr(save.name_ind, 2, 2)
    data_ind[[i]]$numero <- substr(save.name_ind, 4, 5)
  } else {
    data_ind[[i]]$altura <- substr(save.name_ind, 2, 3)
    data_ind[[i]]$numero <- substr(save.name_ind, 5, 6)
  }
  data_ind[[i]]$especie <- substr(save.name_ind, nchar(save.name_ind)-2, nchar(save.name_ind)-2)


    #       3. Global dataframes names processing

  save.name_global <- sub(".csv", "", lista_global[[i]])

  save.name_global <- sub("_global", "" , save.name_global)

  data_global[[i]]$replica <- substr(save.name_global, nchar(save.name_global), nchar(save.name_global))

  save.name_global <- sub(paste0("_", unique(data_ind[[i]]$replica)), "", save.name_global)

  data_global[[i]]$forma <- substr(save.name_global, 1, 1)


  if (any(substr(save.name_global, 3, 3) == LETTERS)) {
    data_global[[i]]$altura <- substr(save.name_global, 2, 2)
    data_global[[i]]$numero <- substr(save.name_global, 4, 5)
  } else {
    data_global[[i]]$altura <- substr(save.name_global, 2, 3)
    data_global[[i]]$numero <- substr(save.name_global, 5, 6)
  }

  data_global[[i]]$especie <- substr(save.name_global, nchar(save.name_global)-2, nchar(save.name_global)-2)

}



all_data_ind <- as.data.frame(do.call("rbind", data_ind))

all_data_global <- as.data.frame(do.call("rbind", data_global))

all_data_global <- all_data_global %>%
  mutate(condition = paste(forma, altura, especie, numero, sep = "")) %>%
  drop_na() 




















#   1.2. phi/v0 vs tiempo para replica Q56N40C

replica_data <- all_data_global %>% filter(Time > 1000, Time < 2000)

v0_time <- replica_data %>%
  ggplot(aes(x = Time, y = Mean.Velocity)) + geom_line(alpha = 0.7, color = "blue") +
  theme_classic() +
  labs(subtitle = "Multitracker results", y = expression("v"[0])) +
  theme(
    panel.background = element_rect(fill = "transparent") # bg of the panel
    , plot.background = element_rect(fill = "transparent", color = NA) # bg of the plot
    , panel.grid.major = element_blank() # get rid of major grid
    , panel.grid.minor = element_blank() # get rid of minor grid
    , legend.background = element_rect(fill = "transparent") # get rid of legend bg
    , legend.box.background = element_rect(fill = "transparent")
    , axis.text=element_text(size=12)
    , axis.title.x=element_blank()
    , axis.title=element_text(size=14,face="bold")
    , legend.text=element_text(size=10)
    , legend.title=element_text(size=12)
    , strip.background =element_rect(fill="transparent")
  )

phi_time <- replica_data %>% 
  ggplot(aes(x = Time, y = Polarity)) + geom_line(alpha = 0.7, color = "red") +
  theme_classic() +
  labs(x = "Time", y = expression(phi))  +
  theme(
    panel.background = element_rect(fill = "transparent") # bg of the panel
    , plot.background = element_rect(fill = "transparent", color = NA) # bg of the plot
    , panel.grid.major = element_blank() # get rid of major grid
    , panel.grid.minor = element_blank() # get rid of minor grid
    , legend.background = element_rect(fill = "transparent") # get rid of legend bg
    , legend.box.background = element_rect(fill = "transparent")
    , axis.text=element_text(size=12)
    #, axis.title.x=element_blank()
    , axis.title=element_text(size=14,face="bold")
    , legend.text=element_text(size=10)
    , legend.title=element_text(size=12)
    , strip.background =element_rect(fill="transparent")
  )


v0_phi_time_plot <- ggarrange(v0_time, phi_time, nrow = 2, align = "hv")


ggsave("phi_v0_time_2000frames_multitracker.png", width = 25, height = 15, units = "cm")




#               5. An??lisis de fourier para cada condici??n

#   5.1. An??lisis de fourier per se
# Ordenar por tiempo
all_data_global <- all_data_global[order(all_data_global$Time),]


global_norm <- all_data_global %>%
  mutate(condition = paste(forma, altura, especie, numero, sep = "")) %>%
  drop_na() %>%
  group_by(condition, replica) %>%
  mutate(time_allrep = row_number(), mean.v0.norm = scale(Mean.Velocity), mean.phi.norm = scale(Polarity))

# Crear una variable condición_replica para ordenar los datos
global_norm <- global_norm %>% mutate(condition_r = paste(condition, replica, sep = ""))
#Ordenar por condicion_replica
global_norm <- global_norm[order(global_norm$condition_r),]


global_norm <- global_norm %>% group_by(condition) %>% mutate(Time_dos = row_number())



plot_list <-list()

fourier_all <- data.frame(freq = numeric(0),
                          spec = numeric(0),
                          period = numeric(0),
                          condition = character(0)
                        )

j <- 1
sample_int <- 1  # En peces y vicsek, siempre 1.

for(i in unique(global_norm$condition)){

  sample <- filter(global_norm, condition == i)

  # FOURIER ANALYSIS FOR PHI

  fourier_phi <- welchPSD(ts(sample$mean.phi.norm), seglength = 200,r = 0.0001)
  fourier_phi <- data.frame(freq = fourier_phi$frequency, spec = fourier_phi$power)
  fourier_phi$period <- 1/fourier_phi$freq
  fourier_phi$condition <- i
  fourier_phi$parameter <- as.factor("phi")
  fourier_phi$freq <- fourier_phi$freq/sample_int
  fourier_phi$spec <- fourier_phi$spec * 2

  # FOURIER ANALYSIS FOR V0
  
  fourier_v0 <- welchPSD(ts(sample$mean.v0.norm), seglength = 200, r = 0.0001)
  fourier_v0 <- data.frame(freq = fourier_v0$frequency, spec = fourier_v0$power)
  fourier_v0$period <- 1/fourier_v0$freq
  fourier_v0$condition <- i
  fourier_v0$parameter <- as.factor("v0")
  fourier_v0$freq <- fourier_v0$freq/sample_int
  fourier_v0$spec <- fourier_v0$spec * 2

  # UNITE BOTH FOURIERS
  fourier <- bind_rows(fourier_phi, fourier_v0)
  fourier <- filter(fourier, freq > 0.001)


  fourier_all <- bind_rows(fourier_all, fourier)
  j <- j+1

}

fourier_condition <- filter(fourier_all, condition == "Q25N40")

#    Periodogram of one condition

one_condition_plot <- fourier_all %>%  filter(freq <= 0.08) %>%
  ggplot(aes(x = freq, y = log(spec), color = parameter)) +
    geom_line(size = 0.5, alpha = 0.7) +
    #geom_point(aes(shape = parameter), size = 0.8, alpha = 0.8) +
    scale_x_continuous(breaks = seq(0,0.08, 0.005)) +
    labs(y="spec", shape = "Parameter", x = expression("f")) +
    theme_classic() +
    scale_color_manual(values = c("blue", "red")) +
    geom_vline(xintercept = fourier_all$freq[which.max(fourier_all$spec)], color = "black") 

ggsave("Spectral_Phi_v0_normalized_overlapped_FishConditionQ5N40_span=8.png", one_condition_plot, width = 30, height = 20, units = "cm", bg = "transparent")


######################################################################




# ---------------------------------- 2. v0 Histogram ----------------------- 





v0_comparison <- ggplot(all_data_global) +
  geom_histogram(aes(x = Mean.Velocity, y = ..ncount..), fill = "transparent", color = "blue")  

ggsave("v0_histogram_postprocessed_multitracker.png", v0_comparison, width = 20, height = 17, units = "cm")





