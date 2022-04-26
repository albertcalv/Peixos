#
#    
#
#
#    Antes de ejecutar rm the following files from the directory
#    Q25N40_A_data.csv
#    Q25N40_A_global.csv
#    Q25N40_A_individual.csv
#
#
#
#
# Cambiar working directory a carpeta con datos
setwd("./")
#setwd("/home/ivan/documents/loveyourdata/peixos/LYD-Peixos/playground/")
n.vecinos <- 6

xmax <- 1072 # Ancho del acuario en pixeles
ymax <- 1004 # Alto del acuario en pixeles

##########################################
#install.packages("sp")
#install.packages("geometry")
#install.packages("circular")
#install.packages("dplyr")
#install.packages("tictoc")

library("grDevices")
library("sp")
library("geometry")
library("circular")
library("dplyr")
library("tictoc")


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
lista <- list.files(pattern = "*.csv")
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
  tic("start")
  for (t in 1:max(data$Time)) {
    t2 <- data[data$Time == t,]
    
    if(t > 1) {
    t1 <- data[data$Time == t-1,]
    }
   
    for (i in 1:max(data$Subject)) {
      if(t == 1) {
      out_list[[row]] <- c(t, i, t2$X[i], t2$Y[i], NA, NA, NA, NA, NA, NA)
      } else {
        

      # convierte en vector el renglón de "data" dataframe del tiempo actual 
      #t2 <- unlist(data[data$Subject == i & data$Time == t,])
      #t1 <- unlist(data[data$Subject == i & data$Time == t-1,])

      
      
        # Utiliza función declarada al inicio 
      output <-  c(t, i,t2$X[i], t2$Y[i], calc.vector.subj(i,t, t1$X[i], t2$X[i], t1$Y[i], t2$Y[i]))
    
      out_list[[row]] <- output
      }
      row <- row + 1 
      
      
    }
    print(paste("Tiempo =",t, sep = " "))

  
  }
  toc()
  
  data <- as.data.frame(do.call(rbind, out_list))
  
  colnames(data) <- c("Time", "Subject", "X", "Y", "Angle", "compX","compY","Mod","compXu","compYu")

  
  ### ------- 2. Distancia al Borde, NND, Interdistancias y Polarizaci�n Local ---------------
  
  # Funci�n que calcula distancia entre dos puntos
  distance <- function (x1, y1, x2, y2) {
    c <- sqrt((x2 - x1)^2 + (y2 - y1)^2)
    return(c)
  }
  
  distance.hull <- function(x1,y1,x2,y2,xp,yp) {
    if (x1 == x2) {
      dist <- abs(xp - x1)
      xc <- x1
      yc <- yp
    } else {
      if (y1 == y2) {
        dist  <- abs(y1 - yp)
        xc <- xp
        yc <- y1
        
      } else {
        A <- (y2-y1) / (x2-x1)
        B <- y1-(A*x1)
        dist <- (abs((A*xp)-yp + B)) / sqrt(A^2 + 1)
        A2 <- -(1/A)
        B2 <- yp - (A2*xp)
        xc <- ((B2-B)*A)/(A^2+1)
        yc <- (A*xc)+B
      }
    }
    
    if ((xc < x1) & (xc < x2)) { dist <- NA }
    if ((xc > x1) & (xc > x2)) { dist <- NA }
    if ((yc < y1) & (yc < y2)) { dist <- NA }
    if ((yc > y1) & (yc > y2)) { dist <- NA }
    return(list(dist=dist, xc=xc, yc=yc))
  }
  
  
  # Crea dataframe con distancia al borde, NND, interdistancia media y polarizaci�n local de cada invididuo en cada unitad de tiempo
  dist.m <- matrix (NA, ncol=max(data$Subject), nrow=max(data$Subject))
  individual.df <- data.frame(matrix(NA, ncol=6, dimnames=list(NULL, c("Time",
                                                                        "Subject",
                                                                        "Dist.border",
                                                                        "NND", 
                                                                        "NND_X",
                                                                        "Velocity"))))
  
  
  
  
  k <- 1
  individual.list <- list()
  tic("START")
  for (t in 1:max(data$Time)){

    print(paste("Time = ", t))
    step <- data[data$Time == t, c("X", "Y", "Mod")]
    for (i in 1:max(data$Subject)){
      for(j in 1:max(data$Subject)){
        if (i < j){ dist.m[i,j] = distance(step$X[i], step$Y[i], step$X[j], step$Y[j])}
      }
      dist.m[lower.tri(dist.m)] <- t(dist.m)[lower.tri(dist.m)]
      
      #Distancia al borde para forma cuadrada
      if (forma == "Q") {
        d.border <- min(step$X[i], step$Y[i], xmax-step$X[i], ymax-step$Y[i])
      } else {
        # Distancia al borde para forma redonda
        # Cargar forma hull y calcular distancia al borde
        forma.points <- read.delim(paste0("hull_", save.name,".xls"))
        forma.points <- forma.points[, c("X", "Y")]
        forma.points[,"Y"] <- ymax - forma.points[,"Y"]
        hull.points <- forma.points[c(chull(x=forma.points[,1], y=forma.points[,2]), chull(x=forma.points[,1], y=forma.points[,2])[1]),]
        s <- 1 # sides of the convex hull
        dist.counter <- c()
        xp <-step$X[j]
        yp <- step$Y[j]
        if (all(hull.points$X != xp & hull.points$Y != yp)) {
          while (s <= (dim(hull.points)[1]-1)) {
            x1 <- hull.points$X[s]
            y1 <- hull.points$Y[s]
            x2 <- hull.points$X[s+1]
            y2 <- hull.points$Y[s+1]
            dist.counter[s] <- distance.hull(x1,y1,x2,y2,xp,yp)$dist
            s
            s <- s+1
          }
        } else {
          dist.counter[s] <- 0
        }
        d.border <- min(dist.counter, na.rm = T)
      }
      
      # Tiempo, individuo, distancia al borde, distancia mínima a vecino, distancia media de NN. 
      vecinos_dist <- sort(dist.m[i,])[1:n.vecinos] # ordenar sujetos por distancia (orden creciente)
      individual.temp <- c(t,i, d.border, min(dist.m[i,], na.rm = T), mean(vecinos_dist, na.rm = T), step$Mod[i])
      
      #individual.df[k,1:5] <- c(t,i, d.border, min(dist.m[i,], na.rm = T), mean(vecinos_dist, na.rm = T))
      
      #individual.df[k, 6] <- step$Mod[i]
      
      individual.list[[k]] <- individual.temp
      
      k <- k + 1
    }
  

  }
  individual.df <- as.data.frame(do.call(rbind, individual.list))
  toc()
  
  
  colnames(individual.df) <- c("Time",
                               "Subject",
                               "Dist.border",
                               "NND", 
                               "NND_X",
                               "Velocity")
   
  

  global.df <- as.data.frame(list("Time" = 1:max(individual.df$Time),
                                  "Mean.NND" = tapply(individual.df$NND, individual.df$Time, mean),
                                  "Mean.NND_X" = tapply(individual.df$NND_X, individual.df$Time, mean),
                                  "Mean.Velocity" = tapply(individual.df$Velocity, individual.df$Time, mean, na.action = na.omit), 
                                  "MeanDistBorder" = tapply(individual.df$Dist.border, individual.df$Time, mean, na.action = na.omit)))
                                  



  ### ------- 3. Polarización Global ---------------
  
  # Calcula polarizacion global en cada unidad de tiempo según el método de Couzin et al. (2002)
  for (t in 2:(max(data$Time))) {
    global.df[t,"Polarity"] <- 1 - var.circular(circular(data$Angle[data$Time==t], type="angles", units="degrees"), na.rm=T)

  }
  
  
  
  # Guarda los archivos de cada filmación
  write.table(data, file=paste(save.name, replica, "data.csv", sep="_"), sep=";", dec=".", row.names = F)
  write.table(individual.df, file=paste(save.name, replica, "individual.csv", sep = "_"), sep = ";", dec= ".", row.names = F)
  write.table(global.df, file=paste(save.name, replica, "global.csv", sep="_"), sep=";", dec=".", row.names = F)
  #write.table(individual.df, file=paste(save.name, replica, "individual.csv", sep="_"), sep=";", dec=".", row.names = F)

  
}






