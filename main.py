import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import io

#--------------------------------------------------Cambios Visuales con CSS-------------------------------------------------
st.markdown("""
<style>
/* Afecta solo la barra lateral. */
[data-testid="stSidebar"] {
    background-color: #78BCC4;
}
/* Cambia el color de fondo de toda la aplicación */
.stApp {
    background-color: #ECE4D4;
}
</style>
""", unsafe_allow_html=True)

#def TBlue(Text):
#st.markdown(":blue-background[Text with a blue background]") #Opcion pa crear texto con fondos de colores.

#--------------------------------------------------Funciones Importantisimas-------------------------------------------------
#PRUEBA DE NORMALIDAD SHAPIRO-WILK
def shapiro_local(Datos0): #Esto te lo hace por columnas
    #Datos1 = np.array(Datos0)#Convertir Datos0 en un array para que se pueda meter en Shapiro.
    Datos1 = pd.to_numeric(Datos0, errors="coerce").dropna() #Elimina las filas con datos vacios, esto es un manejo de los Null.
    if len(Datos1)<3:
        return None #Basicamente, si son muy poquitos datos nada se puede hacer y te tira este comentario.
    else:
        w, p = stats.shapiro(Datos1)
        return p
    
def F_NORMALIDAD(df1): #Para hacer la normalidad aqui se asume que cumple todas las condiciones, excepto la de cantidad
    df3 = df1.melt(var_name="Grupo", value_name="Valor")
    df3["Valor"] = pd.to_numeric(df3["Valor"],errors="coerce") #Convierte todo en formato Variable Valor, y se asegura que los valores si sean numeros. El coerce quita los errores.
    
    GRUPOS = df3["Grupo"].unique()
    SIZE = True #VARIABLE BANDERA
    VARNORMALIDAD = [] #Aca se almacena el resultado del test para cada variable, cada es p o un None

    for Grupo in GRUPOS:
        Lista_Valores = df3[df3["Grupo"]==Grupo]["Valor"] #Hace una lista de listas en donde en cada lista estan todos los valores asociados a una variable en especifica. Hace esto para una variable en especifico.
        VARNORMALIDAD.append(shapiro_local(Lista_Valores)) #Aplica normalidad para esa variable en especifica "Grupo"
        if shapiro_local(Lista_Valores) is None:
            SIZE=False
    
    if SIZE:
        return VARNORMALIDAD #Esto es una lista de los p's
    else:
        return None #Si algun grupo no es valido, todos no son validos.


def guardar_png(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=200, bbox_inches="tight")
    return buffer.getvalue()
        
#----------------------------------------------------Inicia EL CODIGO-----------------------------------------------------------------
GRAPHS = ["Ninguna", "Diagrama de Barras", "Diagrama de Bigotes", "Diagrama de Dispersion"]

with st.sidebar:
    st.title("Opciones Adicionales")
    Graph = st.selectbox("Graficas", GRAPHS)
    
st.title("Calculadora Estadistica") #Titulo con fondo azul.
st.write("Para ingresar nuevos datos por favor refresque la pagina.")
st.markdown("---")
st.subheader("Responda las siguientes preguntas.") #Reemplzar formato Si/No con botones.

#Añadir opcion de persistencia mas adelante mediante log in

#---------------------------------------------------Variables Banderas---------------------------------------------------------------
PEARSON = False 
UMANN = False
ANOVA = False
#WALLIS = False
TSTUDENT = False
CHI2 = False
NORMALIDAD = False
MULTINORMALIDAD = False

#--------------------------------------------------Preguntas de los Datos-------------------------------------------------------
PREG1= st.selectbox("¿Acaso tus variables independientes y dependientes son cualitativas?",["", "Si", "No"])
if PREG1=="":
    st.stop()
elif PREG1 == "Si":
    CHI2=True
else:
    PREG2= st.selectbox("¿Cuantas variables independientes tienes?", ["", "1", "2", "Mas de dos"])  #Aplicar Normalidad con base a esto
    if PREG2=="":
        st.stop()
    elif PREG2 == "1":
        st.write("**:red[ERROR. Se necesitan al menos dos variables para realizar la prueba de hipotesis.]**")
        st.stop()
    elif PREG2 == "Mas de dos":
        MULTINORMALIDAD=True #Añadir aqui el Kruster-Wallis mas tarde si toca. 
    else:
        PREG3=st.selectbox("¿Deseas hacer una comparacion o una correlacion con los datos?", ["", "Comparacion", "Correlacion"])
        if PREG3=="":
            st.stop()
        elif PREG3=="Correlacion":
            PEARSON=True
        else:
            NORMALIDAD=True
    
#-------------------------------------------Recomendacion Pruebas de Hipotesis----------------------------------------------------------
#Aqui se recomienda que tipo de prueba de hipotesis se debe hacer.
if CHI2:
    Response = "**:red[Chi Cuadrado]** porque todas las variables son cualitativas"
    st.write(f"Con base a lo respondido, se recomienda hacer una prueba de hipotesis de {Response}.")
elif PEARSON:
    st.write("Con base a lo respondido, se recomienda calcular el **:red[coeficiente de Pearson]** para ver si hay una correlacion linear entre los datos.")
elif MULTINORMALIDAD==True:
    st.write("Con base a lo respondido, es necesario hacer una **:red[prueba de normalidad de Shapiro-Wilk]** para determinar el tipo de prueba de hipotesis. Suba los datos para realizar la prueba de normalidad.")
elif NORMALIDAD==True:
    st.write("Con base a lo respondido, es necesario hacer una **:red[prueba de normalidad de Shapiro-Wilk]** para determinar el tipo de prueba de hipotesis. Suba los datos para realizar la prueba de normalidad.")

st.markdown("**Por favor suba los datos para poder continuar con el proceso. Si son datos mixtos (Cualitativos/Cuantitativos) coloque las variables al inicio de cada columna y debajo coloque los valores asociados. Si son datos cualitativos, coloque cada variable a la izquierda de cada fila con un valor que se les asocia a la derecha para cada valor que haya.**")
#Añadir imagen para que sea mas facil comprender el formato de las tablas. Esta imagen luego deberia desaparece despues de que se haya subido el archivo.

#---------------------------------------------------Subir Tabla y Manipulacion de los Datos-------------------------------------
#Ejemplo de como se debe ver la tabla
st.image(["Tabla_Chi2.png","Tabla_Comparacion.png"], width=300)
st.image("Tabla_Comparacion.png", width=300)

#Esto hace que se pueda subir la tabla
RawData= st.file_uploader("Sube una tabla en formato .CSV de maximo 20 MB.",type=["csv"], max_upload_size=20) #Limita el tamaño maximo de archivo a 20MB

#Esto hace que no salga un error cuando aun no han subido el archivo.
if RawData is None:
    st.stop()
else:
    df0 = pd.read_csv(RawData) #Lectura de la tabla como una matriz en pandas.

#Muestra la tabla como un menu despegable.
with st.expander("Vista Previa"):
    st.dataframe(df0, use_container_width=True)

#-------------------------------------------PRUEBA DE NORMALIDAD----------------------------------------------------------
if NORMALIDAD:
    NORMAL=F_NORMALIDAD(df0) #Se crea normal para no tener que llamar la misma funcion varias veces
    df10 = df0.melt(var_name="Grupo", value_name="Valor")
    VARIABLES=df10["Grupo"].unique()
    if NORMAL is not None and len(VARIABLES)==2:
        st.write("El resultado de la prueba de normalidad para",
                VARIABLES[0], "es de P:", NORMAL[0], ". Mientras que para", VARIABLES[1], "es de P:", NORMAL[1], ".") #Se coge de la lista el p.
        if NORMAL[0]>0.05 and NORMAL[1]>0.05:
            st.write("Ya que ambos p-valores tienen una significancia mayor que 0.05 esto signfica los datos siguen una distribucion normal por lo que es recomendabla hacer una prueba de hipotesis T de Student.")
            TSTUDENT=True
        else:
            st.write("Ya que al menos uno de los p-valores tiene una significancia menor que 0.05 esto signfica los datos NO siguen una distribucion normal por lo que es recomendabla hacer una prueba de hipotesis de U-Mann-Whitney.")
            UMANN=True
    elif len(VARIABLES)!=2:
        st.write("**:red[ERROR. No hay exactamente dos variables independientes.]**")
        st.stop()
    else:
        st.write("**:red[ERROR. Hay muy pocos datos en alguno de las variables para que el analisis sea estadisticamente significativo. Trata de reunir mas datos en esa variable.]**")
        st.stop()
elif MULTINORMALIDAD: #Cambiar luego para cuando se pueda hacer ANOVA y Kruger-Willis
    NORMAL=F_NORMALIDAD(df0) #Se crea normal para no tener que llamar la misma funcion varias veces
    df10 = df0.melt(var_name="Grupo", value_name="Valor")
    VARIABLES=df10["Grupo"].unique()
    if NORMAL is not None and len(VARIABLES)>2:
        st.write("El resultado de la prueba de normalidad es:")
        RESULT = True
        for i in range(len(NORMAL)):
            st.write(VARIABLES[i], "es de P:", NORMAL[i])
            if NORMAL[i]<0.05:
                RESULT = False #Otra variable bandera que verifica que todo sub lista tenga un p-valor mayor que 0.05
        if RESULT:
            st.write("Ya que hay mas de dos variables independientes y todos los p-valores tienen una significancia mayor que 0.05 esto signfica los datos siguen una distribucion normal por lo que es recomendabla hacer una prueba de hipotesis ANOVA.")
            ANOVA=True
        else:
            st.write("Ya que hay mas de dos variables independientes y al menos uno de los p-valores tiene una significancia menor que 0.05 esto signfica los datos NO siguen una distribucion normal por lo que es recomendabla hacer una prueba de Kruskal-Wallis. Lamentable, la calculadora no cuenta con esta funcionalidad en el momento.")
            #WALLIS=True
    elif len(VARIABLES)<3:
        st.write("**:red[ERROR. Se necesitan al menos tres variables independientes.]**")
        st.stop()
    else:
        st.write("**:red[ERROR. Hay muy pocos datos en alguno de las variables para que el analisis sea estadisticamente significativo. Trata de reunir mas datos en esa variable.]**")
        st.stop()

#st.subheader("¿Que desea hacer a continuacion?")
#------------------------------------------------------Pruebas de Hipotesis-------------------------------------------------------
if ANOVA:
    Prueba = "ANOVA"
    LINK = "https://www.questionpro.com/blog/es/anova/"
elif UMANN:
    Prueba = "U de Mann-Whitney"
    LINK = "https://www.questionpro.com/blog/es/prueba-u-de-mann-whitney/"
elif TSTUDENT:
    Prueba = "T de Student"
    LINK = "https://www.questionpro.com/blog/es/prueba-t-de-student/"
elif CHI2:
    Prueba = "Chi Cuadrado"
    LINK = "https://www.questionpro.com/blog/es/prueba-de-chi-cuadrado-de-pearson/"
elif PEARSON:
    Prueba = "Coeficiente de Pearson"
    LINK = "https://numiqo.es/tutorial/pearson-correlation"

st.link_button(f"¿Que es {Prueba}?", LINK) #Boton que lleva a un sitio que explica como funciona la Prueba de Hipotesis.

if not PEARSON:
    TEXT1="hipotesis"
else:
    TEXT1="correlacion"

TESTING = st.selectbox(f"¿Deseas realizar la prueba de {TEXT1}?", ["","Si","No"]) #Opcion para empezar la prueba de hipotesis
START = False

if TESTING!="Si":
    st.stop()

if ANOVA:
    if len(df0.columns)!=3: #NOTA: Si se hace el Anova generalizado se cambia esto a que saque error si es menor que 3
        st.write("**:red[ERROR. Para realizar ANOVA necesitas tres variables.]**")
        st.stop()
    
    st.subheader("Prueba de Hipotesis ANOVA")
    df = df0.melt(var_name="Grupo", value_name="Valor") #Rota la matriz para que este en formato variable-valor, o sea el formato anterior a parejas, con la columna Grupo teniendo la variable, y la columna Valor tneiendo los valores.
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce") #Mira la columna de los valores y los convierte en numeros si son strings. El coerce es pa evitar errores.

    GRUPOS = df["Grupo"].unique() #Saca cada variable independiente de la tabla.
    LISTA=[]
    for Grupo in GRUPOS:
        LISTA.append(df[df["Grupo"]==Grupo]["Valor"]) #Saca todos los valores asociados a una variables, los vuelve una lsita, y luego los mete a la LISTA y hace eso para cada vairable.
    f, P_ANOVA = stats.f_oneway(*LISTA) #Realiza ANOVA a los datos. El "*" es para que en vez de que LISTA sea una lista de lista, solo le da varias listas a ANOVA que es el parementro que necesita.
    
    st.write("El p-valor de ANOVA es P =", P_ANOVA,".")
    if P_ANOVA<0.05:
        st.write("Al ser P < 0.05, se rechaza la hipotesis nula. Hay una diferencia significativa entre las medias de dos variables.")
    else:
        st.write("Al ser P > 0.05, NO se rechaza la hipotesis nula. NO hay una diferencia significativa entre las medias de las variables.")
elif CHI2: #Hacer que tire error si hay menos de 5 datos
    st.subheader("Prueba de Hipotesis Chi Cuadrado")

    if len(df0.columns)!=2:
        st.write("**:red[ERROR. Se necesitan exactactamente dos columnas cualitativas.]**")
        st.stop()
    
    COL1= df0.columns[0] #Nombra a cada una de las columnas, la columna de Variables y la columna de respuestas.
    COL2 = df0.columns[1]

    Tabla = pd.crosstab(df0[COL1], df0[COL2])
    st.write("Tabla de Contingencia:")
    st.dataframe(Tabla)

    chi, P_CHI, dof, expected = stats.chi2_contingency(Tabla)
    st.write("El p-valor de Chi Cuadrado es P =", P_CHI,".")
    
    if P_CHI<0.05:
        st.write("Al ser P < 0.05, se rechaza la hipotesis nula. Las dos variables estan significativamente relacionadas.")
    else:
        st.write("Al ser P > 0.05, NO se rechaza la hipotesis nula. Las dos variables NO estan significativamente relacionadas.")
elif UMANN:
    st.subheader("Prueba de Hipotesis U de Mann-Whitney")
    df = df0.melt(var_name="Grupo", value_name="Valor")
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce") #Se cambia el formato de la matrix

    GRUPOS = df["Grupo"].unique()
    G1 = df[df["Grupo"]==GRUPOS[0]]["Valor"].dropna() #Variable independiente 1
    G2 = df[df["Grupo"]==GRUPOS[1]]["Valor"].dropna() #""

    u, P_UMANN = stats.mannwhitneyu(G1, G2) #Aplicacion de la prueba

    st.write("El p-valor de U de Mann-Whitney es de P =", P_UMANN)

    if P_UMANN<0.05:
        st.write("Al ser P < 0.05, se rechaza la hipotesis nula. Las distribuciones son significativamente diferentes.")
    else:
        st.write("Al ser P > 0.05, NO se rechaza la hipotesis nula. Las distribuciones NO son significativamente diferentes.")
elif TSTUDENT:
    df = df0.melt(var_name="Grupo", value_name="Valor")
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

    GRUPOS = df["Grupo"].unique()
    G1 = df[df["Grupo"]==GRUPOS[0]]["Valor"].dropna()
    G2 = df[df["Grupo"]==GRUPOS[1]]["Valor"].dropna()

    t, P_TSTUDENT = stats.ttest_ind(G1, G2)

    st.write("El p-valor de T de Student es de P =", P_TSTUDENT)

    if P_TSTUDENT<0.05:
        st.write("Al ser P < 0.05, se rechaza la hipotesis nula. Las medias son significativamente diferentes.")
    else:
        st.write("Al ser P > 0.05, NO se rechaza la hipotesis nula. Las medias NO son significativamente diferentes.")


#--------------------------------------------¡¡¡¡SECCION PARA LAS GRAFICAS!!!!-------------------------------------------------------------
#Tipos de graficas permitidos para cada tipo de datos.
GRAPHCHI2 = ["Ninguna", "Diagrama de Barras"]
GRAPHCOMPARACION = ["Ninguna","Diagrama de Bigotes"]
GRAPHCORRELACION = ["Ninguna","Diagrama de Bigotes", "Diagrama de Dispersion"]
GRAPHANOVA = ["Ninguna","Diagrama de Bigotes"]

if CHI2:
    GRAPHS= GRAPHCHI2
elif NORMALIDAD and not ANOVA:
    GRAPHS= GRAPHCOMPARACION
elif ANOVA:
    GRAPHS=GRAPHANOVA
elif PEARSON:
    GRAPHS=GRAPHCORRELACION
#Hacer que saca un error si se selecciona una grafica que no esta ahi

if Graph=="Ninguna":
    st.stop()
elif Graph=="Diagrama de Bigotes" and not CHI2:
    fig, ax = plt.subplots()
    df.boxplot(column="Valor", by="Grupo", ax= ax)
    plt.suptitle("") #Añadir opcion para que el usuario le ponga nombre al grafico.
    st.pyplot(fig, use_container_width=True)

    st.download_button(
    "Descargar PNG",
    guardar_png(fig),
    file_name= str("Diagrama_de_Bigotes") + ".png",
    mime="image/png"
    )
    #Cambiar Valor y Grupo que eso hace que los ejes tengan nombres raros.
elif Graph=="Diagrama de Barras" and CHI2: #NOTA, Actuamente falla y toca cambiarlo
    fig, ax = plt.subplots()
    Tabla.plot(kind="bar",ax=ax)
    st.pyplot(fig)
    
    st.download_button(
    "Descargar PNG",
    guardar_png(fig),
    file_name= str("Diagrama_de_Barras") + ".png",
    mime="image/png"
    )
elif Graph == "Diagrama de Dispersion" and (NORMALIDAD or PEARSON):
    if len(df0.columns) < 2:
        st.write("Se necesitan al menos dos columnas.")
        st.stop()

    COL1 = df0.columns[0]
    COL2 = df0.columns[1]

    x = pd.to_numeric(df0[COL1], errors="coerce")
    y = pd.to_numeric(df0[COL2], errors="coerce")

    fig, ax = plt.subplots()
    ax.scatter(x, y)

    ax.set_title("Diagrama de Dispersion")
    ax.set_xlabel(COL1)
    ax.set_ylabel(COL2)

    st.pyplot(fig)

    st.download_button(
    "Descargar PNG",
    guardar_png(fig),
    file_name="Diagrama_de_Dispersion.png",
    mime="image/png"
    )
else:
    st.write("**:red[ERROR. La opcion de grafico no es valida o no se puede graficar aun.]**")















