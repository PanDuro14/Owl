CREATE DATABASE IF NOT EXISTS owldb_v1;
USE owldb_v1;

-- Tabla Usuarios 1
CREATE TABLE Usuarios (
  id_usuario INT PRIMARY KEY auto_increment,
  nom_usuario VARCHAR(45),
  nombre VARCHAR(45), 
  ap_paterno VARCHAR(45),
  ap_materno VARCHAR(45),
  correo VARCHAR(45),
  passw VARCHAR(45)
);

-- Tabla Paciente 2
CREATE TABLE Paciente (
  id_paciente INT PRIMARY KEY auto_increment,
  registro_online VARCHAR(2), 
  id_usuario INT,
  nombre_cliente VARCHAR(45),
  ap_pa VARCHAR(45),
  ap_ma VARCHAR(45),
  fecha_nacimiento DATE, -- Calcular si es mayor de edad xd
  genero VARCHAR(3),
  estado_civil VARCHAR(3),
  antecedentes_medicos VARCHAR(255),
  medicamentos_actuales VARCHAR(255),
  FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

-- Tabla Profesional_encargado 3
CREATE TABLE Profesional_encargado (
  id_pro INT PRIMARY KEY,
  nom VARCHAR(45),
  ap VARCHAR(45),
  especialidad VARCHAR(45),
  num_licencia VARCHAR(6),
  num_telefono INT(9),
  correo_elec VARCHAR(45),
  horario VARCHAR(3)
);

-- Tabla Horario 4
CREATE TABLE Horario (
  id_horario VARCHAR(3) PRIMARY KEY,
  desc_horario VARCHAR(255)
);

-- Tabla Citas 5
CREATE TABLE Citas (
  id_cita INT PRIMARY KEY auto_increment,
  descripcion VARCHAR(255),
  fecha DATE,
  lugar VARCHAR(255),
  id_usuario INT,
  id_paciente INT,
  nom_paciente VARCHAR(45),
  id_profesional INT,
  id_horario VARCHAR(3),
  sede VARCHAR(45),
  FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
  FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente),
  FOREIGN KEY (id_profesional) REFERENCES Profesional_encargado(id_pro),
  FOREIGN KEY (id_horario) REFERENCES Horario(id_horario)
);

-- Tabla Historial_citas 6
CREATE TABLE Historial_citas (
  id_cita INT,
  fecha DATE,
  progreso_paciente INT(10),
  FOREIGN KEY (id_cita) REFERENCES Citas(id_cita)
);
-- Contacto Emergencia 7
CREATE TABLE Contacto_emergencia(
   nombre_contacto VARCHAR(45),
   relacion_paciente VARCHAR(45),
   num_tel int(10)
); 

