from pyswip import Prolog

prolog = Prolog()

# Cargar las reglas de Prolog
prolog.consult("motor.pl")

def filtrar_recetas_por_tipo(recetas_db, tipo):
    prolog_reglas = Prolog()
    prolog_reglas.consult("reglas.pl")
    recetas_filtradas = []
    
    for receta in recetas_db:
        nombre = receta.nombre  # Acceder como atributo
        ingredientes = receta.ingredientes  # Lista de ingredientes
        tiempo_preparacion = receta.tiempo_preparacion  # Tiempo de preparación
        
        # Consulta Prolog para ver si ya existe la receta en las reglas
        query = f"receta('{nombre}', _, _)"  # Comprobamos si la receta está definida en Prolog
        result = list(prolog_reglas.query(query))
        
        # Si la receta no está definida, la agregamos dinámicamente
        if not result:
            # Convertir ingredientes a un formato adecuado para Prolog, por ejemplo, una lista
            ingredientes_prolog = ', '.join([f"'{ingrediente}'" for ingrediente in ingredientes])
            
            # Agregar la receta a las reglas de Prolog, incluyendo ingredientes y tiempo de preparación
            prolog_reglas.assertz(f"receta('{nombre}', [{ingredientes_prolog}], {tiempo_preparacion})")
        
        # Ahora procedemos con la consulta dinámica de Prolog para determinar si es del tipo saludable, sencilla, etc.
        query = f"{tipo}('{nombre}')"  # Llamada a Prolog con el tipo (saludable, sencilla, etc.)
        result = list(prolog_reglas.query(query))
        
        # Si la receta cumple con la regla (saludable, sencilla, etc.), la agregamos a la lista filtrada
        if result:
            recetas_filtradas.append(str(nombre))  # Asegurar que es un string
    
    return recetas_filtradas

def cargar_recetas_iniciales():
    prologInicial = Prolog()

    # Cargar las reglas de Prolog
    prologInicial.consult("reglas.pl")
    recetas_query = prolog.query("receta(Nombre, Ingredientes, Tiempo)")
    recetas = []
    for receta in recetas_query:
        recetas.append({
            "nombre": receta["Nombre"],
            "ingredientes": receta["Ingredientes"],
            "tiempo": receta["Tiempo"]
        })
    return recetas

def filtrar_recetas_por_ingrediente(recetas_db, ingrediente):
    prolog = Prolog()
    
    # Cargar reglas base de Prolog
    prolog.consult("reglas.pl")  

    # Verificar si el ingrediente ya está en Prolog
    query = f"ingrediente('{ingrediente}')"
    result = list(prolog.query(query))

    if not result:
        prolog.assertz(f"ingrediente('{ingrediente}')")  

    # Agregar recetas a Prolog asegurando que los ingredientes se pasen como nombres
    for receta in recetas_db:
        ingredientes_str = "[" + ", ".join(f"'{ing.nombre}'" for ing in receta.ingredientes) + "]"
        prolog.assertz(f"receta('{receta.nombre}', {ingredientes_str}, {receta.tiempo_preparacion})")

    recetas_filtradas = []
    query_recetas = f"recetas_con_ingrediente('{ingrediente}', Receta)"
    
    for solucion in prolog.query(query_recetas):
        recetas_filtradas.append(solucion["Receta"])
    
    if not recetas_filtradas:
        recetas_filtradas = [receta.nombre for receta in recetas_db if any(ing.nombre == ingrediente for ing in receta.ingredientes)]

    return recetas_filtradas


# # def obtener_recetas_por_tipo(tipo):
# #     query = f"obtener_recetas_por_tipo({tipo},Receta)"
# #     result = list(prolog.query(query))
# #     print(result)
# #     return [str(res["Receta"]) for res in result]

# def filtrar_recetas_prolog(recetas_db, tipo):
#     prolog_reglas = Prolog()
#     prolog_reglas.consult("reglas.pl")
#     recetas_filtradas = []
#     print("Recetas en la base de datos:")
#     for receta in recetas_db:
#         print(receta.nombre) 
#     for receta in recetas_db:
#         nombre = receta.nombre  # Acceder como atributo
#         query = f"{tipo}('{nombre}')"  # Llamada a Prolog con el nombre de la receta
#         result = list(prolog_reglas.query(query))
#         if result:
#             recetas_filtradas.append(str(nombre))  # Asegurar que es un string
#     print(recetas_filtradas)
#     return recetas_filtradas  # Devuelve list[str] correctamente

# def filtrar_recetas_por_filtro(recetas_db, filtro):
#     prolog_reglas = Prolog()
#     prolog_reglas.consult("reglas.pl")
#     recetas_filtradas = []

#     for receta in recetas_db:
#         nombre = receta.nombre  
#         query = f"recetas_con_ingrediente('{filtro}', '{nombre}')"  
#         result = list(prolog_reglas.query(query))
#         if result:
#             recetas_filtradas.append(str(nombre)) 
#     return recetas_filtradas    