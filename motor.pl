:- consult('reglas.pl').  % Cargar la base de conocimientos 

% Función para obtener recetas saludables
obtener_recetas_saludables(Recetas) :-
    findall(Receta, saludable(Receta), Recetas).

% Función para obtener recetas con un ingrediente específico
buscar_recetas_por_ingrediente(Ingrediente, Recetas) :-
    findall(Receta, recetas_con_ingrediente(Ingrediente, Receta), Recetas).

% Función para obtener recetas según su nivel de elaboración (sencilla o elaborada)
obtener_recetas_por_tipo(sencilla, Recetas) :-
    findall(Receta, sencilla(Receta), Recetas).

obtener_recetas_por_tipo(elaborada, Recetas) :-
    findall(Receta, elaborada(Receta), Recetas).
