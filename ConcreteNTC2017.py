# Factores de resistencia (3.7)
frF = 0.9  # Flexión (3.5.e)
frV = 0.75  # Cortante y torsión
frFC = 0.75  # Flexo compresión
frFCnotCon = 0.65  # Flexo compresión no confinado
frAp = 0.65  # Aplastamiento
# Beta
def beta(fc):
    if fc <= 280:
        return 0.85
    else:
        return max(1.05 - fc / 1400, 0.65)


def FlexComForces(b, h, d, c, fc, fy, asMatrix):
    beta1 = beta(fc)
    Pc = 0.85 * beta1 * fc * b * (d - c)
    brc = (h - beta1 * (d - c)) / 2
    Mc = Pc * brc
    pu = 0
    mu = 0

    for i in range(len(asMatrix)):
        di = asMatrix[i][1]
        bri = asMatrix[i][2]
        asi = asMatrix[i][0]
        eps1 = (di - c) / (d - c) * 0.003
        if eps1 >= 0:
            fyi = min(fy, eps1 * 2100000)
        else:
            fyi = max(-fy, eps1 * 2100000)

        fti = asi * fyi
        mi = bri * fti
        pu = pu + fti
        mu = mu + mi

    pu = pu + Pc
    mu = mu + Mc

    return [mu * frFC, pu * frFC]

