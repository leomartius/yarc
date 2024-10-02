from __future__ import annotations

banner = """\
............................................................
:'##:::'##::::::'###:::::::::'########::::::::'######:::::::
:. ##:'##::::::'## ##:::::::: ##.... ##::::::'##... ##::::::
::. ####::::::'##:. ##::::::: ##:::: ##:::::: ##:::..:::::::
:::. ##::::::'##:::. ##:::::: ########::::::: ##::::::::::::
:::: ##:::::: #########:::::: ##.. ##:::::::: ##::::::::::::
:::: ##:'###: ##.... ##:'###: ##::. ##::'###: ##::: ##:'###:
:::: ##: ###: ##:::: ##: ###: ##:::. ##: ###:. ######:: ###:
::::..::...::..:::::..::...::..:::::..::...:::......:::...::
""".splitlines()

help_text = r"""

  y k u      7 8 9
   \|/        \|/
  h- -l  or  4- -6   move or melee
   /|\        /|\
  b j n      1 2 3

    .    or    5     rest for a turn


    ?    show help screen
    /    show symbol key
    m    message log
    i    inventory
    d    drop object
    q    quaff potion
    r    read scroll
    w    wield a weapon
    W    wear armor
    T    take armor off
    >    go down a staircase
    v    print version number
""".splitlines()[1:]

symbol_key = """\
    .    room floor                         *    gold
  -   |  wall of a room                     :    food
    +    door                               !    potion
    #    passage                            ?    scroll
    %    a staircase                        )    weapon
    ^    trap                               ]    armor
    ,    the Amulet of Yendor               =    ring
    @    you                                /    wand or staff

    A    giant ant                          N    nymph
    B    bat                                O    orc
    C    centaur                            P    purple worm
    D    dragon                             Q    quasit
    E    floating eye                       R    rust monster
    F    violet fungi                       S    snake
    G    gnome                              T    troll
    H    hobgoblin                          U    umber hulk
    I    invisible stalker                  V    vampire
    J    jackal                             W    wraith
    K    kobold                             X    xorn
    L    leprechaun                         Y    yeti
    M    mimic                              Z    zombie
""".splitlines()

tombstone = r"""
                       __________
                      /          \
                     /    REST    \
                    /      IN      \
                   /     PEACE      \
                  /                  \
                  |      Rodney      |
                  |      999 Au      |
                  |   killed by an   |
                  |       ogre       |
                  |       1980       |
                 *|     *  *  *      | *
         ________)/\\_//(\/(/\)/\//\/|_)_______
""".splitlines()[1:]
