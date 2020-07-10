#############################
 TABD - Projeto de Avaliação
#############################


---- Autores

    -> Bruno Casteleiro (201505347)
    -> José Rocha       (201503229)


---- Requerimentos

    Para compilação e execução do nosso programa é necessário
    a instalação do 'postgresql', 'postgis', 'Python 3.8.3' e
    os seguintes módulos:

      -> matplotlib
      -> psycopg2
      -> numpy
      -> postgis
      -> argparse
      -> pytz

    Dentro de um ambiente linux será suficiente executar o
    seguinte comando para a instalação de todos os módulos
    Python listados em cima:

      $ ./install_requirements.sh

    Não garantimos a execução em versões inferiores do Python,
    mas em princípio não haverá problemas desde que a versão
    instalada seja >= 3.8.0.

    Finalmente, poderá ou não ser necessário instalar o 'ffmpeg'
    no sistema caso a gravação de animações seja necessária.


---- Configuração

    Dentro do postgresql deverá existir uma base de dados
    com os dados taxi_stands e cont_aad_caop2018. Esta base
    de dados deve estar configurada com a extensão do postgis
    e com os indíces e projeções apropriadas (como visto nas
    aulas).

    O utilizador, password e nome da base de dados devem ser
    fornecidos no ficheiro 'src/config.py', nos campos
    respetivos dentro do objeto DATABASE.


---- Execução

    Dentro do diretório 'src/' será suficiente executar o programa
    'main.py' para correr o programa com valores default:

      $ python main.py

    O nosso programa é altamente parametrizável, pelo que aconselhamos
    uma primeira execução com o argumento '--help' para obter toda a
    informação sobre estes parâmetros:

      $ python main.py --help

    Para execuções mais exigentes aconselhamos o aumento do delay entre
    frames da animação, através do parâmetro 'delay', ou o uso da flag
    'offline' que irá mostrar a animação apenas após pré-calcular
    informação relevante aos frames da mesma.

    Exemplos de execução:

      -> defaults
         (24h, 500ms delay, 10s step, 2 taxis infetados)

         $ python main.py

      -> 12h-15:30h + defaults

        $ python main.py --start 12 0 0 --end 15 30 0

      -> 200ms delay, 60s step + defaults

        $ python main.py --delay 200ms --step 60

      -> offline + defaults

        $ python main.py --offline

      -> 6 taxis infetados, record + defaults

        $ python main.py --infected 3 --record


---- Offset caching

    Para os mesmos argumentos 'start', 'end' e 'step' o nosso
    programa guarda informação relativa aos offsets e primeiros
    10 taxis a aparecer no Porto e Lisboa em ficheiros '.csv'
    dentro de 'src/data/'. Desta forma evita-se a computação
    destes valores que, mediante os parâmetros, pode demorar
    algum tempo.

    Para facilitar o uso do programa fornecemos desde já os
    ficheiros necessários para as seguintes configurações:

      -> 12h-15h + defaults
         $ python main.py --start 12 0 0 --end 15 0 0

      -> 60s step + defaults
         $ python --step 60

    Para utilizar estes ficheiros é apenas necessário
    descompactar o ficheiro cached.zip dentro do diretório
    'src/data/':

       $ unzip cached.zip
