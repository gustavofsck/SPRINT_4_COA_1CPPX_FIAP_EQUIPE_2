# SPRINT_4_COA_1CPPX_FIAP_EQUIPE_2

# Integrantes:

* Bruno Riquelme Coutinho Pereira - 569619
* Eduardo Bigoli Portela - 569897
* Gabriel Martins Cordeiro Rodrigues - 570497
* Gustavo Fondato de Souza - 573651
* Gustavo Martins Da Silva - 570584
* Lucas Lino Marques da Silva - 572863

# Link do projeto no Wokwi:

# https://wokwi.com/projects/476798525301330945

# Descrição:

O projeto acadêmico de Arquitetura e Organização de Computadores consiste na simulação, no Wokwi, de uma estação inteligente de recarga de veículos elétricos, controlada por um Raspberry Pi Pico e programada em Python.

O algoritmo identifica os veículos presentes e calcula a demanda total de energia. Se houver energia disponível para todos, cada veículo recebe a potência solicitada. Caso contrário, o sistema prioriza os veículos com menor nível de bateria, distribuindo a energia restante: alguns recebem a potência solicitada, outros recebem potência reduzida e os demais ficam bloqueados quando não há energia suficiente. O visor LCD apresenta as informações da recarga, enquanto os LEDs indicam o estado geral do sistema.

# Componentes utilizados:

* 1 Raspberry Pi Pico
* 1 tela LCD 16×2 com interface I²C
* 3 LEDs (vermelho, amarelo e verde)
* 1 potenciômetro
* 3 chaves deslizantes
* 3 botões e três resistores de 1,2 kΩ.
