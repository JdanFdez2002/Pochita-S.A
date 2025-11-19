# 1.`usuarios`
### **Función principal**
Gestionar todo lo relacionado con **autenticación, roles y permisos**.

### **Por qué debe ser una app individual**
- Las historias de usuario están basadas en roles: *Recepcionista* y *Veterinario*.
- El sistema necesita saber **quién está entrando** para mostrar o restringir funcionalidades.
- La autenticación no debe mezclarse con lógica de la agenda, fichas o disponibilidad.

### **Qué hace esta app**
- Login / Logout  
- Sistema de roles (recepcionista, veterinario)  
- Autorización y permisos  
- Redirecciones según rol  
- Formularios y vistas de autenticación  
---

# 2. `pacientes`
### **Función principal**
Gestionar **las mascotas** y sus **fichas clínicas**.

### **Por qué debe ser una app individual**
- Los pacientes son una entidad totalmente independiente.
- La agenda utiliza pacientes, pero no debe definirlos.
- Los veterinarios atienden pacientes, pero no deben manejar su estructura interna.

### **Qué hace esta app**
- Modelo `Paciente`  
- Ficha clínica y antecedentes  
- Formularios para registrar/editar mascotas  
- Búsqueda y listado de pacientes  

### **Historias de Uso relacionadas**
- **HU003:** Crear ficha del paciente  
- **HU009:** Registrar antecedentes  
- **HU010:** Consultar datos del paciente  

---
# 3. `veterinarios`
### **Función principal**
Gestionar los **veterinarios** y su **disponibilidad de atención**.

### **Por qué debe ser una app individual**
- La disponibilidad es un módulo complejo que implica reglas propias.
- La agenda depende de la disponibilidad, pero no debe manejarla internamente.
- Los veterinarios tienen funciones distintas a los pacientes y a las citas.

### **Qué hace esta app**
- Modelo `Veterinario`  
- Modelo `Disponibilidad`  
- Agregar/quitar bloques de horario  
- Cambiar estado de disponibilidad  
- Mostrar disponibilidad para la recepcionista  

### **Historias de Uso relacionadas**
- **HU001:** Ver disponibilidad  
- **HU007:** Cambiar disponibilidad  
- **HU008:** Ingresar disponibilidad  
- **HU012:** Cambiar disponibilidad del veterinario  

---

# 4. `agenda`
### **Función principal**
Gestionar todo lo relacionado con **horas de atención**, calendarios y **reprogramaciones**.

### **Por qué debe ser una app individual**
- Es el corazón funcional del proyecto.
- Su lógica es compleja y no debe mezclarse con pacientes o veterinarios.
- Las historias evaluadas (HU002 y HU006) están directamente aquí.

### **Qué hace esta app**
- Modelo `Cita`  
- Modelo `EstadoCita`  
- Validación de disponibilidad antes de agendar  
- Cancelación de citas  
- Reprogramación cuando el veterinario cancela  
- Mostrar disponibilidad por vet en el calendario  

### **Historias de Uso relacionadas**
- **HU002:** Agendar hora  
- **HU004:** Cancelar hora  
- **HU006:** Replanificar horas  
- **HU005 / HU011:** (si se implementan más adelante)  

---

# Resumen de la arquitectura

| App | Responsabilidad | Por qué es independiente | Historias de Uso |
|-----|-----------------|--------------------------|------------------|
| **usuarios** | Roles, login, permisos | Autenticación es transversal | Todas |
| **pacientes** | Mascotas y fichas | Independiente de agenda/vet | HU003, HU009, HU010 |
| **veterinarios** | Datos y disponibilidad | Agenda usa disponibilidad, pero no la define | HU001, HU007, HU008, HU012 |
| **agenda** | Citas, horarios, reprogramación | Núcleo del proyecto | HU002, HU004, HU006 |

---