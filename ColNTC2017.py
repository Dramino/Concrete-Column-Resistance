import ConcreteNTC2017 as NTC
import matplotlib.pyplot as plt
import math, subprocess, os, csv

# Datos inciales
# Dimensiones
b = 20  # [cm]
h = 20  # [cm]
r = 3  # [cm]
d = h - r  # [cm]
ac = b * h

# Materiales
fc = 250  # [kg/cm]
fy = 4200  # [kg/cm2]
Es = 2100000  # [kg/cm2]
beta = NTC.beta(fc)

# Acero
VarAs = 4  # Varilla del numero VarAs
AsCol = 3  # Numero de Varillas horizontales
AsRow = 3  # Numero de varillas verticales

AsSingle = (VarAs ** 2) * 0.07917304361
asTotal = (2 * AsCol + 2 * (AsRow - 2)) * AsSingle

# Creacion de la matriz de acero
asMatrix = []
deltaD = (h - 2 * r) / (AsRow - 1)
for i in range(AsRow):
    if i == 0 or i == (AsRow - 1):
        asi = AsSingle * AsCol
    else:
        asi = AsSingle * 2

    di = h - 2 * r - deltaD * i
    bri = di + r - h / 2

    asMatrixi = [asi, di, bri]
    asMatrix.append(asMatrixi)
# Facotres de resistencia
FR = NTC.frFC

# Compresión pura
Pu = FR * (ac * 0.85 * fc + asTotal * fy)

# Tensión pura
Tu = FR * (-asTotal * fy)

forcesCol = []
forcesCol.append([0, Pu])
# Zonas intermedias
deltaC = (h - 2 * r) / (8)

for i in range(8):
    c = max(r, deltaC * (i + 1))
    forces = NTC.FlexComForces(b, h, d, c, fc, fy, asMatrix)
    forcesCol.append(forces)

forcesCol.append([0, Tu])
xAxes = []
yAxes = []

for i in range(len(forcesCol)):
    xAxes.append(forcesCol[i][0] / 100000)
    yAxes.append(forcesCol[i][1] / 1000)

plt.plot(xAxes, yAxes)


# Importar valores actuantes
xAct = []
yAct = []

csv_path = "Data.csv"
with open(csv_path, "r") as f_obj:
    reader = csv.reader(f_obj, delimiter="\t")
    next(reader)
    for row in reader:
        piAct = float(row[4]) * -1
        miAct = abs(float(row[9]))
        xAct.append(miAct)
        yAct.append(piAct)
plt.plot(xAct, yAct, "ro")

plt.grid(True)
plt.xlabel("M[t-m]")
plt.ylabel("P[t]")
plt.savefig("ConcreteCol.png")


# Escritura en latex
# Datos para el texto
eps1 = []
asi = []
di = []
bri = []
fti = []
mi = []
pui = []
mui = []
fyi = []
pu = 0
mu = 0

for i in range(AsRow):
    asi.append(asMatrix[i][0])
    di.append(asMatrix[i][1])
    bri.append(asMatrix[i][2])
    eps1.append((di[i] - r) / (d - r) * 0.003)
    if eps1[i] >= 0:
        fyi.append(min(fy, eps1[i] * 2100000))
    else:
        fyi.append(max(-fy, eps1[i] * 2100000))

    fti.append(asi[i] * fyi[i])
    mi.append(bri[i] * fti[i])
    pu = pu + fti[i]
    mu = mu + mi[i]

Pc = 0.85 * beta * fc * b * (d - r)
brc = (h - beta * (d - r)) / 2
Mc = Pc * brc
pr = pu + Pc
mu = mu + Mc


texStart1 = r"""\documentclass{article}
\usepackage[latin1]{inputenc}
\usepackage[spanish,es-tabla]{babel}
\usepackage{amsmath}
\usepackage{helvet}
\usepackage{caption}
\usepackage{graphicx}
\captionsetup{labelsep=period}
\captionsetup[table]{skip=1pt}
\spanishdecimal{.}
\begin{document}

\section{Revisión de columna de concreto}
Revisión de columna de concreto a flexo compresión

%% Datos iniciales
\subsection{Datos de los elementos}

Los datos de  la columna se muestran en la tabla \ref{t:datos}

\begin{table}[htbp]
\caption{Datos de la columna}
\label{t:datos}
\centering
\begin{tabular}{|llll|}
\hline
Dato & Valor & Unidades & Comentarios \\ \hline
"""
textDatah = "h     & %.2f    & cm         & Alto de la columna       \\\\ \n" % h
textDatab = "b     & %.2f    & cm         & Ancho de la columna       \\\\ \n" % b
textDatar = "r     & %.2f     & cm         & Recubrimiento              \\\\ \n" % r
textDatafc = "f'c   & %.0f   & $kg/cm^2$  & Resistencia del concreto    \\\\ \n" % fc
textDatafy = (
    "fy    & %.0f  & $kg/cm^2$  & Resistencia del acero      \\\\ \\hline \n" % fy
)
textDataEnd = r"""\end{tabular}
\end{table}
"""

textData = textDatab + textDatab + textDatar + textDatafc + textDatafy + textDataEnd

textCompIntro = r"""
\subsection{Compresión pura}

La resistencia a compresión pura se obtiene con:

\begin{equation}\label{eq:pu}
P_u=F_r(A_g f''_c + A_s f_y )
\end{equation}

donde $P_u$ es la capacidad resistente del concreto, $F_r=0.75$, $A_g$ es el área del concreto, $A_s$ es el área del acero.
"""
textComp1 = (
    "El área del concreto se obtiene con $A_g=BH$; el área de una varilla del \\#%.0f es %.2f cm por lo que:\n \n"
    % (VarAs, AsSingle)
)
textComp2 = "\\begin{align*}\n"
textComp3 = "A_g=& (%.2f)(%.2f) \\\\ \n" % (b, h)
textComp4 = "A_g=& %.2f cm^2 \\\\ \n" % ac
textComp5 = "A_s=& %.2f(%.0f) \\\\ \n" % (AsSingle, (2 * AsCol + 2 * (AsRow - 2)))
textComp6 = "A_s=& %.2f cm^2 \\\\ \n" % asTotal
textComp7 = r"""\end{align*}

Por lo que el la resistencia a compresión pura es:

\begin{align*}"""
textComp8 = "P_u=&0.75[(%.2f)(0.85)(%.0f) + (%.2f)(%.0f)]\\\\ \n" % (
    ac,
    fc,
    asTotal,
    fy,
)
textComp9 = "P_u=&%.2f kg \n" % (Pu)
textComp10 = "\\end{align*} \n"

textComp = (
    textCompIntro
    + textComp1
    + textComp2
    + textComp3
    + textComp4
    + textComp5
    + textComp6
    + textComp7
    + textComp8
    + textComp9
    + textComp10
)

textFlexIntro = r"""
\subsection{Flexo-Compresión}
Para el diseño a flexo-compresión se propone un eje neutro $c$ a diferentes distancias para obtener su capacidad a flexión y compresión.

Para obtener la deformación de cada barra de acero se considera que la deformación actúa como se muestra en la Figura %\ref{fig:def}

Para obtener las deformaciones en cada punto se considera que la deformación se obtiene con:

\begin{equation}\label{eq:def}
\epsilon_i=\left(\frac{d_i-c}{d-c}\right)0.003
\end{equation}

donde $\epsilon_i$ es la deformación de la barra de acero a una altura $i$ deseada, $d_i$ es la distancia de la barra de acero $i$ a la barra más profunda, $d$ es el peralte efectivo, y $c$ es la distancia al eje neutro desde la barra más profunda.

En la Tabla \ref{t:di} se muestran las distancias $d_i$ de cada barra con sus respectivas áreas.

\begin{table}[htbp]
\caption{Distancias de cada barra respecto a la barra mas profunda}
\label{t:di}
\centering
\begin{tabular}{|lll|}
\hline
Barra & $d_i$(cm) & $A_s$($cm^2$) \\ \hline
"""
textFlex1 = ""
for i in range(AsRow):
    textFlex1m = "%.0f     & %.2f    & %.2f                 \\\\ \n " % (
        i + 1,
        di[i],
        asi[i],
    )
    textFlex1 = textFlex1 + textFlex1m
textFlex2 = r"""\hline
\end{tabular}
\end{table}

"""

textFlex3 = (
    "Considerando un eje neutro igual a $c=%.2f$ y aplicando la ecuación \\ref{eq:def} se tiene que para la barra 1 la deformación es: \n \n "
    % (r)
)
textFlex4 = "\\begin{align*}\n"
textFlex5 = "\\epsilon_1&=\\left(\\frac{%.2f-%.2f}{%.2f-%.2f}\\right)0.003\\\\ \n" % (
    asMatrix[0][1],
    r,
    d,
    r,
)
textFlex6 = "\\epsilon_1&=%.4f\n" % (eps1[0])
textFlex7 = r"""\end{align*}

Aplicando las ecuaciones para las demás barras se tiene

\begin{align*}
"""
textFlex8 = ""
for i in range(AsRow - 1):
    textFlex8m = (
        "\\epsilon_%.0f&=\\left(\\frac{%.2f-%.2f}{%.2f-%.2f}\\right)0.003\\\\ \n"
        % (i + 2, di[i + 1], r, d, r)
    )
    textFlex8m = "\\epsilon_%.0f&=%.4f\\\\ \n" % (i + 2, eps1[i + 1])
    textFlex8 = textFlex8 + textFlex8m

textFlex9 = r"""\end{align*}

El esfuerzo máximo que alcanza el acero es $\epsilon_s =0.002$ por lo que se considera la siguiente desigualdad

\begin{equation}\label{eq:fs}
F_s=\epsilon E_y \le 0.002 E_y
\end{equation}

Cosndierando que $E_y=2 100 000 kg/cm^2$ se tiene entonces que los esfuerzos de cada barra son:

\begin{align*}
"""
textFlex10 = ""
for i in range(AsRow):
    textFlex10m = "Fs_%.0f&=(%.4f)(2100000)&=&%.2fkg/cm^2 \\\\ \n" % (
        i + 1,
        eps1[i],
        fyi[i],
    )
    textFlex10 = textFlex10 + textFlex10m
textFlex11 = r"""\end{align*}

Para obtener la fuerza se multiplica el esfuerso $F_s$ por el área por lo que las fuerzas se muestran en la Tabla \ref{t:fuerzas}

Para obtener la fuerza a compresión del concreto se aplica la ecuación \ref{eq:conC}

\begin{equation}\label{eq:conC}
F_c=(0.85)(f'c)(B)0.85(d-c)
\end{equation}

Por lo que la fuerza compresión del concreto es

\begin{align*}
"""
textFlex12 = "F_c&=(0.85)(%.0f)(%.2f)0.85(%.2f-%.2f)\\\\ \n" % (fc, b, d, r)
textFlex13 = "F_c&=%.2f kg\n" % (0.85 * fc * b * 0.85 * (d - r))
textFlex14 = r"""\end{align*}

En la tabla \ref{t:fuerzas} se muestran las fuerzas del acero y concreto

\begin{table}[htbp]
\caption{Fuerzas de cada barra}
\label{t:fuerzas}
\centering
\begin{tabular}{|lllll|}
\hline
Barra  & $\epsilon$ & $F_s$($kg/cm^2$) & $A_s$($cm^2$)&$F_i$($kg$)\\ \hline
"""
textFlex15 = ""
for i in range(AsRow):
    textFlex15m = "%.0f     & %.4f    & %.2f & %.2f & %.2f                \\\\\n" % (
        i + 1,
        eps1[i],
        fyi[i],
        asi[i],
        fti[i],
    )
    textFlex15 = textFlex15 + textFlex15m
textFlex16 = "Concreto     & 0.003    &%.0f&&%.2f                \\\\ \\hline \n" % (
    fc,
    Pc,
)
textFlex17 = "&&&$P_r$=&%.2f\\\\ \\hline \n" % (pr)
textFlex18 = r"""
\end{tabular}
\end{table}

Para obtener los momentos se requiere multiplicar las fuerzas de la Tabla \ref{t:fuerzas} por su brazo de palanca al centro de la columna. 

El brazo de palanca para el bloque de concreto se obtiene:

\begin{equation}\label{eq:brazo}
b_r=\left[B-0.85(d-c)\right]/2
\end{equation}

por lo que el brazo de palanca es

\begin{align*}
"""
textFlex19 = "b_r&=\\left[%.2f-0.85(%.2f-%.2f)\\right]/2 \\\\ \n" % (b, d, r)
textFlex20 = "b_r&=%.2f cm \n" % (brc)
textFlex21 = r"""\end{align*}

En la tabla \ref{t:momentos} se muestran los momentos del acero y concreto

\begin{table}[htbp]
\caption{Momentos}
\label{t:momentos}
\centering
\begin{tabular}{|llll|}
\hline
Barra  & Fuerza (kg) & Brazo (cm) & Momento (kg-cm) \\ \hline
"""
textFlex22 = ""
for i in range(AsRow):
    textFlex22m = "%.0f      & %.2f      & %.2f    & %.2f      \\\\ \n" % (
        i + 1,
        fti[i],
        bri[i],
        mi[i],
    )
    textFlex22 = textFlex22 + textFlex22m

textFlex23 = "Concreto      & %.2f      & %.2f    & %.2f      \\\\ \\hline \n" % (
    Pc,
    brc,
    Mc,
)
textFlex24 = "  &    &  Suma& %.2f T-m      \\\\ \\hline" % (mu)
textFlex25 = r"""
\end{tabular}
\end{table}

"""
textFlex = (
    textFlexIntro
    + textFlex1
    + textFlex2
    + textFlex3
    + textFlex4
    + textFlex5
    + textFlex6
    + textFlex7
    + textFlex8
    + textFlex9
    + textFlex10
    + textFlex11
    + textFlex12
    + textFlex13
    + textFlex14
    + textFlex15
    + textFlex16
    + textFlex17
    + textFlex18
    + textFlex19
    + textFlex20
    + textFlex21
    + textFlex22
    + textFlex23
    + textFlex24
    + textFlex25
)

textEnd = r"""
En la Figura \ref{fig:ConcreteCol} se muestra el diagrama de interacción de la columna

\begin{figure}[htbp]
	\centering
		\includegraphics[width=0.80\textwidth]{D:/Investigacion/Latex/Latex/Ingenieria/Concreto/Columna/ColumnaConcreto/Python/ConcreteCol.png}
	\caption{Diagrama de Interacción de Columna}
	\label{fig:ConcreteCol}
\end{figure}

\end{document}
"""

text = texStart1 + textData + textComp + textFlex + textEnd

with open("ColNtec2017.tex", "w") as f:
    f.write(text)

