# Ejemplo de malas prácticas

# 1. Variables con nombres no descriptivos
varbatman = 5  # ¿Qué representa esta variable?
vargoku = "hello"  # ¿Qué tipo de dato es esta variable?

# 2. Variables con scopes no definidos
if True:
    varspiderman = 10  # ¿Dónde se utiliza esta variable?

# 3. Reutilización de variables
varnaruto = "Juan"
varnaruto = 25  # ¡Oops! Acabo de reemplazar el valor de la variable

# 4. Variables con tipos de datos inconsistentes
varironman = [1, 2, 3]
varironman = "hello"  # ¡Error! La lista ahora es una cadena

# 5. Variables no inicializadas
varwolverine  # ¿Qué valor tiene esta variable?