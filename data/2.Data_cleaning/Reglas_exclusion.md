# Reglas exclusion de datos y fusion 
* Al hacer busqueda de palabras asegurate de usar sinonimos y versiones con y sin tilde.
* Todos los numeros deben ser natuales, no debe haber floats.

Queremos las siguientes columnas: N_informe, fecha, edad, sexo, RCP_TRANSTELEFONICA (0 o 1);RCP_TESTIGOS(0, lego, policia bombero, sanitario);Tiempo llegada (Suma de C0_C1;C1_C2;C2_C3);DESA_EXTERNO(0 o 1),RITMO INICIAL(0 o 1, descrito mas adelante), Tiempo RCP(C3_C4, si esta vacio entonces se deja vacio), ROSC (es decir, si se le saca de la parada, como 0 o 1), Supervivencia_7dias(), CPC 

* Quitamos paradas traumaticas, solo medicas: Se identifica por palabras en la casilla CONSULTA como ahogamiento, herida, precipitado, arma, trauma, accidente, colision, etc...
* Quitamos todas las filas que no tengan RCP transtelefonica rellena.
* El resto de datos como edad, sexo, etc. SI esta vacio se deja vacio
* Fusionamos los datos de SVA a SVB, coinciden en fecha y hora, NO en numero infome. Si uno de los 2 tiene RCP transtelefonica como verdadero, entonces prima esa. El resto de datos prima el de SVA, si esta vacio entonces si se usa, si esta, el de SVB.
* Si las de SVB no se puede emparejar entonces se elimina
* El ritmo incial se transforma a 1 si es desfibrilable(FV, TV, TV sin pulso, fibriliacion ventricular, taquicardia ventricular, fibrilación...), o 0 si no.
* Identificamos RCP_testigos mediante palabras clave en casillas (CONSULTA,ANTECEDENTES)
    * Recuerda, lego es aquel que no esta entrenado en rcp, ni es policia ni bombero ni sanitario
    * Si hay rcp transtelefonica como verdadero, encontes el tipo es lego
    * bombero como palabras clave incluye beta, 080, bomberos,...
    * policia incluye como palabaras clave 092, 091, 062, agente, municipal, nacional...
    * sanitario incluye TES, SVB, basica, UPR, basico, sanitario, personal hospital, socorrista...
    * Si no se identifica el tipo pero hay rcp testigos entonces es lego

* Si hay hospital entonces el rosc es 1. Si el rosc es 0 entonces el tiempo de rcp se estima leyendo la casilla tecnicas (patrones como "tras X min de RCP"). Si en esta casilla aparece la hora de fallecimiento, y hay rcp testigos se calcula cogiendo la hora de inicio en FECHA siendo la inicial, y la escrita de fallecimiento la final. Eso sera el tiempo total. Si no hay rcp testigos, entonces se le resta el tiempo llegada.


* Lee las casillas 6 y determina si ha fallecido mediante palabras clave. Si es asi supervivencia es 0 y cpc es 5
* Mediante la lectura 7 Dias se determina su supervivencia a los 7 dias y CPC. Si esta vacio entonces no hay supervivencia y es 0. Si es 0 entonces cpc es 5. Si hay escrito determina si ha fallecido mediante palabras clave como exitus, fallecimiento, fallecido... Si no determinas ninguna, pero hay escrito, la supervivencia es 1 pero el cpc vacio.
* Identifica el CPC normalmente escrito como "CPC de X" siendo X el numero entre 1 y 5. Si supervivencia es 1 entonces cpc es entre 1 y 4.


## Informe comprobacion a mano

Añade un report en md que sirva para comprobar de una manera mas facil las anomalias que se produzcan en la limpieza de los datos. Incluye, citando en N informe los siguientes:
* Aquellos que tengan supervivencia pero no haya cpc
* Aquellos que tengan datos vacios en al menos 4 casillas