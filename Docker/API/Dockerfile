# Étape 1 : Construction de l'application avec Maven
FROM maven:3.9.5-eclipse-temurin-21 AS build


WORKDIR /app

# Copie des fichiers du projet dans le conteneur
COPY ../API/dataforest /app

# Compilation et construction du JAR
RUN mvn clean package -DskipTests

# Étape 2 : Exécution de l'application avec une image plus légère
FROM eclipse-temurin:21-jdk

WORKDIR /app

# Copie du JAR généré depuis l'étape de build
COPY --from=build /app/target/*.jar app.jar

# Exposition du port 8080
EXPOSE 8080

# Commande pour exécuter l'application
#ENTRYPOINT ["java", "-jar", "app.jar"]

