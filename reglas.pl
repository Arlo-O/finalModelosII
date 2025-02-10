:- dynamic receta/3.
:- dynamic ingrediente/1.

% Permitir agregar ingredientes dinámicamente
ingrediente(_).
% Base de conocimientos sobre recetas
receta(ensalada, [lechuga, tomate, pepino, zanahoria], 10).
receta(hamburguesa, [pan, carne, lechuga, tomate, queso], 25).
receta(pizza, [harina, queso, salsa_tomate, pepperoni], 30).
receta(sopa, [agua, zanahoria, cebolla, papa], 20).
receta(batido_verde, [espinaca, manzana, platano, agua], 5).

% Clasificación de ingredientes como vegetales
vegetal(lechuga).
vegetal(tomate).
vegetal(pepino).
vegetal(zanahoria).
vegetal(espinaca).
vegetal(cebolla).
vegetal(papa).

% Clasificación de ingredientes comunes

comun(lechuga).
comun(tomate).
comun(pepino).
comun(zanahoria).
comun(harina).
comun(queso).
comun(salsa_tomate).
comun(agua).
comun(platano).
comun(manzana).
comun(espinaca).

% Regla para determinar si una receta es saludable (mínimo 2 vegetales)
saludable(Receta) :-
    receta(Receta, Ingredientes, _),
    findall(I, (member(I, Ingredientes), vegetal(I)), ListaVegetales),
    length(ListaVegetales, Cantidad),
    Cantidad > 2.

% Regla para determinar si una receta es sencilla (menos de 20 min y todos sus ingredientes son comunes)
sencilla(Receta) :-
    receta(Receta, Ingredientes, Tiempo),
    Tiempo =< 20,
    forall(member(I, Ingredientes), comun(I)).

% Regla para determinar si una receta es elaborada (más de 20 min o ingredientes no comunes)
elaborada(Receta) :-
    receta(Receta, _, Tiempo),
    Tiempo > 20.

elaborada(Receta) :-
    receta(Receta, Ingredientes, _),
    member(I, Ingredientes),
    \+ comun(I).

% Regla para buscar recetas que contengan un ingrediente específico
recetas_con_ingrediente(Ingrediente, Receta) :-
    receta(Receta, Ingredientes, _),
    member(Ingrediente, Ingredientes).
