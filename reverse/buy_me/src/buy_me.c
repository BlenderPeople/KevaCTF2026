#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void store();

void cipher();

void print();

int choise;
char ascii[200];
int money = 100;
int sloyka_s_tvorogom_i_lemonom = 9999;
int sloyka_s_abrikosom = 35;
int sloyka_s_chernikoy = 40;
int sloyka_s_sosiskoy = 50;
int sloyka_s_vetchinoy_i_sirom = 45;

int main()
{
    printf("Сделай выбор:\n");
    printf("1. Сходить в ярче\n2. Голодать\n");
    scanf("%d", &choise);
    switch (choise)
    {
        case 1:
        store();
        break;
        case 2:
        exit(0);
    }
    return 0;
}

void cipher()
{
    //сдвиг 10
    char text[] = "100 39 89 91 85 111 38 107 85 94 42 108 91 85 42 85 98 42 89 38 99 97 42 85 100 38 109 85 93 38 85 106 38 85 106 94 91 85 107 98 97 85 42 100 90 85 102 38 98 42 97 38 99 39 105 85 38 100 85 106 94 91 85 92 39 104 105 106 85 92 98 38 38 104";
    char buf[4];
    int t = 0;
    int z = 0;
    for (int i = 0; text[i] != '\0'; i++)
    {
        if (text[i] == 32)
        {
            buf[t] = '\0';
            ascii[z++] = (char)(atoi(buf)+10);
            t = 0;
        }
        else
        {
            buf[t] = text[i];
            t++;
        }
        
    }
    buf[t] = '\0';
    ascii[z++] = (char)(atoi(buf)+10);
    ascii[z] = '\0';
}

void print()
{
    printf("Успешная покупка\n");
}

void store()
{
    char flag[200];
    printf("У тебя есть всего: %d\nВыбор очевиден, ведь так?\n", money);
    printf("1. Слойка с творогом и лемоном: %d\n", sloyka_s_tvorogom_i_lemonom);
    printf("2. Слойка с абрикосом: %d\n", sloyka_s_abrikosom);
    printf("3. Слойка с черникой: %d\n", sloyka_s_chernikoy);
    printf("4. Слойка с сосиской: %d\n", sloyka_s_sosiskoy);
    printf("5. Слойка с ветчиной и сыром: %d\n", sloyka_s_vetchinoy_i_sirom);
    scanf("%d", &choise);
    switch (choise)
    {
        case 1:
        if (sloyka_s_tvorogom_i_lemonom > money){printf("Денег нет, но ты держись\n");}
        else 
        {
            cipher();
            sprintf(flag, "kevactf{%s}", ascii);
            printf("Как хорошо ты полакомился...%s\n", flag);
        }
        break;
        case 2:
        print();
        break;
        case 3:
        print();
        break;
        case 4:
        print();
        break;
        case 5:
        print();
        break;
    }
}