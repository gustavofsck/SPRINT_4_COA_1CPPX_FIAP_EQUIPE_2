from machine import Pin, ADC, I2C
from time import sleep, ticks_ms, ticks_diff
from pico_i2c_lcd import I2cLcd

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

led_vermelho = Pin(4, Pin.OUT)
led_amarelo = Pin(3, Pin.OUT)
led_verde = Pin(2, Pin.OUT)

botao_decimal = Pin(7, Pin.IN, Pin.PULL_UP)
botao_binario = Pin(8, Pin.IN, Pin.PULL_UP)
botao_hexadecimal = Pin(9, Pin.IN, Pin.PULL_UP)

botoes_base = [
    (botao_decimal, "dec"),
    (botao_binario, "bin"),
    (botao_hexadecimal, "hex")
]
estados_botoes = [1, 1, 1]

presenca = [
    Pin(10, Pin.IN, Pin.PULL_UP),
    Pin(11, Pin.IN, Pin.PULL_UP),
    Pin(12, Pin.IN, Pin.PULL_UP)
]

pot_disponibilidade = ADC(28)

veiculos = [
    {
        "id": "EV1",
        "bateria": 25,
        "solicitada": 60,
        "recebida": 0,
        "estado": "AUSENTE"
    },
    {
        "id": "EV2",
        "bateria": 70,
        "solicitada": 40,
        "recebida": 0,
        "estado": "AUSENTE"
    },
    {
        "id": "EV3",
        "bateria": 45,
        "solicitada": 50,
        "recebida": 0,
        "estado": "AUSENTE"
    }
]


def mostrar_lcd(linha1, linha2):
    linha1 = str(linha1)[:16]
    linha2 = str(linha2)[:16]

    linha1 = linha1 + (" " * (16 - len(linha1)))
    linha2 = linha2 + (" " * (16 - len(linha2)))

    lcd.move_to(0, 0)
    lcd.putstr(linha1)
    lcd.move_to(0, 1)
    lcd.putstr(linha2)

def acender_led(led):
    led_verde.value(0)
    led_amarelo.value(0)
    led_vermelho.value(0)
    led.value(1)


def ler_energia():
    return (pot_disponibilidade.read_u16() * 180) // 65535


def formatar_inteiro(valor, base):
    valor = int(valor)

    if base == "hex":
        return "{:X}".format(valor)

    if base == "bin":
        return "{:b}".format(valor)

    return str(valor)


def atualizar_presenca():
    for i in range(len(veiculos)):
        if presenca[i].value() == 0:
            if veiculos[i]["estado"] == "AUSENTE":
                veiculos[i]["estado"] = "BLOQUEADA"
        else:
            veiculos[i]["estado"] = "AUSENTE"
            veiculos[i]["recebida"] = 0


def distribuir_energia(energia_disponivel):
    presentes = [
        veiculo for veiculo in veiculos
        if veiculo["estado"] != "AUSENTE"
    ]

    if not presentes:
        return "SEM VEICULOS"

    for veiculo in presentes:
        veiculo["recebida"] = 0

        if veiculo["bateria"] >= 100:
            veiculo["bateria"] = 100
            veiculo["estado"] = "COMPLETA"
        else:
            veiculo["estado"] = "BLOQUEADA"

    demanda_total = sum(
        veiculo["solicitada"]
        for veiculo in presentes
        if veiculo["estado"] != "COMPLETA"
    )

    if demanda_total == 0:
        return "CARGA COMPLETA"

    if demanda_total <= energia_disponivel:
        for veiculo in presentes:
            if veiculo["estado"] != "COMPLETA":
                veiculo["recebida"] = veiculo["solicitada"]
                veiculo["estado"] = "ATIVA"

        return "RECARGA ATIVA"

    energia_restante = energia_disponivel

    for veiculo in sorted(presentes, key=lambda item: item["bateria"]):
        if veiculo["estado"] == "COMPLETA":
            continue

        if energia_restante <= 0:
            break

        veiculo["recebida"] = min(
            energia_restante,
            veiculo["solicitada"]
        )

        if veiculo["recebida"] == veiculo["solicitada"]:
            veiculo["estado"] = "ATIVA"
        else:
            veiculo["estado"] = "REDUZIDA"

        energia_restante -= veiculo["recebida"]

    carregando = sum(
        1 for veiculo in presentes
        if veiculo["recebida"] > 0
    )

    if carregando <= 1:
        return "RECARGA LIMITADA"

    return "REC. CONTROLADA"


def carregar_baterias():
    for veiculo in veiculos:
        if (
            veiculo["estado"] in ("ATIVA", "REDUZIDA")
            and veiculo["recebida"] > 0
        ):
            veiculo["bateria"] = min(100, veiculo["bateria"] + 1)

            if veiculo["bateria"] >= 100:
                veiculo["bateria"] = 100
                veiculo["recebida"] = 0
                veiculo["estado"] = "COMPLETA"


def atualizar_leds(status):
    if status in ("RECARGA ATIVA", "CARGA COMPLETA"):
        acender_led(led_verde)
    elif status == "REC. CONTROLADA":
        acender_led(led_amarelo)
    else:
        acender_led(led_vermelho)


def selecionar_base(base):
    for i, (botao, nova_base) in enumerate(botoes_base):
        estado_atual = botao.value()

        if estado_atual == 0 and estados_botoes[i] == 1:
            base = nova_base

        estados_botoes[i] = estado_atual

    return base


def mostrar_energia(energia, base, status):
    valor = formatar_inteiro(energia, base)
    mostrar_lcd(status, "ENERGIA: {}W".format(valor))


def mostrar_veiculo(indice, base):
    veiculo = veiculos[indice]

    estados = {
        "ATIVA": "ATV",
        "REDUZIDA": "RED",
        "BLOQUEADA": "BLQ",
        "COMPLETA": "OK"
    }

    bateria = formatar_inteiro(veiculo["bateria"], base)
    recebida = formatar_inteiro(veiculo["recebida"], base)
    estado = estados.get(veiculo["estado"], veiculo["estado"])

    linha1 = "{} B:{}%".format(veiculo["id"], bateria)
    linha2 = "{} {}W".format(estado, recebida)

    mostrar_lcd(linha1, linha2)


def obter_presentes():
    return [
        i for i, veiculo in enumerate(veiculos)
        if veiculo["estado"] != "AUSENTE"
    ]


def main():
    base = "dec"
    indice = 0
    tela_energia = True
    ultimo_lcd = ticks_ms()
    ultimo_carregamento = ticks_ms()

    mostrar_lcd("ESTACAO DE", "RECARGA")
    sleep(2)

    while True:
        base = selecionar_base(base)

        energia = ler_energia()
        atualizar_presenca()

        status = distribuir_energia(energia)
        atualizar_leds(status)

        agora = ticks_ms()

        if ticks_diff(agora, ultimo_carregamento) >= 1000:
            carregar_baterias()
            ultimo_carregamento = agora

        if ticks_diff(agora, ultimo_lcd) >= 2500:
            if tela_energia:
                mostrar_energia(energia, base, status)
            else:
                presentes = obter_presentes()

                if presentes:
                    indice %= len(presentes)
                    mostrar_veiculo(presentes[indice], base)
                    indice = (indice + 1) % len(presentes)
                else:
                    mostrar_lcd("SEM VEICULOS", "DISPONIVEIS")

            tela_energia = not tela_energia
            ultimo_lcd = agora

        sleep(0.1)


main()
