#
# Usage:
# 1. Install the following R libraries : "grDevices" "sp" "geometry" "circular"
# 2. Set the appropiate path of the working directory
# 3. Execute the script in a terminal: 
#    $ RScript file_name.R
#
# 4. The script creates two files containing the variables

# Cambiar working directory a carpeta con datos
setwd("~/MEGA/TRACKING_EVAL")


xmax <- 1072 # Ancho del acuario en pixeles
ymax <- 1004 # Alto del acuario en pixeles

##########################################

library("grDevices")
library("sp")
library("geometry")
library("circular")


# ---------- FUNCIONES ---------
# Función que calcula ángulo, las componentes X e Y, el módulo y las componentes X e Y unitarias
calc.vector.subj <- function (subj,t,x1, x2, y1, y2) {
  x = x2-x1
  y = y2-y1
  angle <- atan2((y),(x)) * (180/pi)
  mod <- sqrt((x)^2 + (y)^2)
  c <- c(angle, x, y, mod, x/mod, y/mod) # Devuelve ángulo, componentes del vector, m�dulo y componentes vector unitario
  c[which(is.nan(c))]<- 0
  return(c)
}



# ---------------1. Enlista los archivos que hay en el working directory ----------
lista <- list.files(pattern = "*tracking_Q25N40_A.csv*")
options(scipen = 999)

for (tr in 1:length(lista)){
  #---------------2.  Guardar el nombre de la réplica para los archivos de salida -------------
  save.name <- sub(".csv", "", lista[tr])
  save.name <- sub("tracking_", "" , save.name)
  replica <- substr(save.name, nchar(save.name), nchar(save.name))
  save.name <- sub(paste0("_", replica), "", save.name)
  
  forma <- substr(save.name, 1, 1)
  if (any(substr(save.name, 3, 3) == LETTERS)) {
    altura <- substr(save.name, 2, 2)
  } else {
    altura <- substr(save.name, 2, 3)
  }
  especie <- substr(save.name, nchar(save.name)-2, nchar(save.name)-2)
  
#                           *---* 
  
  
  # ---------------3. Leer archivo de lista y asignarlo a dataframe -------------------
  data <- read.csv(lista[tr], sep = ",")


  colnames(data) <- c("Time", "Subject", "X", "Y")

  
  #  Sujeto y Tiempo empiezan en 1 (no en 0)
  data$Subject <- data$Subject + 1
  data$Time <- data$Time + 1
  
  #   Cambia el origen de las coordenadas Y a la esquina inferior izquierda (en lugar de la esquina superior izquierda)
  data[,"Y"] <- ymax - data[,"Y"]

  
  #   Extrae ángulos y componentes de los vectores invididuales en cada unitad de tiempo (para t == 1, poner NA)
  out_list <- list()
  row <- 1 
  
  for (t in 1:max(data$Time)) {
    for (i in 1:max(data$Subject)) {
      # convierte en vector el renglón de "data" dataframe del tiempo actual 
      t2 <- unlist(data[data$Subject == i & data$Time == t,])
      
      if(t == 1) {
        output <- c(t, i, t2[3], t2[4], NA, NA, NA, NA, NA, NA)
      }
      else {
        
        t1 <- unlist(data[data$Subject == i & data$Time == t-1,])
      
        # Utiliza función declarada al inicio 
        output <-  c(t, i,t2[3], t2[4], calc.vector.subj(i,t,t1[3], t2[3], t1[4], t2[4]))
      }
      out_list[[row]] <- output
      row <- row + 1 
      
      
    }
    print(paste("Tiempo =",t, sep = " "))
  }
  
  data <- as.data.frame(do.call(rbind, out_list))
  
  colnames(data) <- c("Time", "Subject", "X", "Y", "Angle", "compX","compY","Mod","compXu","compYu")


  # Función que calcula distancia entre dos puntos
  distance <- function (x1, y1, x2, y2) {
    c <- sqrt((x2 - x1)^2 + (y2 - y1)^2)
    return(c)
  }
  
  
  global.df <- as.data.frame(list("Time" = 1:max(data$Time),
                                   "Mean.Velocity" = tapply(data$Mod,data$Time, mean)))

  
  ### ------- 3. Polarización Global ---------------
  
  # Calcula polarizacion global en cada unidad de tiempo según el método de Couzin et al. (2002)
  for (t in 2:(max(data$Time))) {
    global.df[t,"Polarity"] <- 1 - var.circular(circular(data$Angle[data$Time==t], type="angles", units="degrees"), na.rm=T)

  }
  
  
  
  # Guarda los archivos de cada filmación
  write.table(data, file=paste(save.name, replica, "data.csv", sep="_"), sep=";", dec=".", row.names = F)
  write.table(global.df, file=paste(save.name, replica, "global.csv", sep="_"), sep=";", dec=".", row.names = F)
  #write.table(individual.df, file=paste(save.name, replica, "individual.csv", sep="_"), sep=";", dec=".", row.names = F)

  
}






