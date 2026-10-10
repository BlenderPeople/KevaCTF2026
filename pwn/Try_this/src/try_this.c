#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

void enter();

void win();

void hint();

int main ()
{
    int choice;

    do
    {
        printf("Привет, сделай свой выбор:\n");
        printf("1. Войти\n");
        printf("2. Подсказка\n");
        printf("3. Выйти\n");
        scanf("%d", &choice);
        
        switch (choice)
        {
            case 1:
                enter();
                break;
            case 2:
                hint();
                break;
            case 3:
                exit(0);
            default:
                printf("Неверный выбор\n");
                break;
        }
    } while (choice != 3);
    return 0;
}

void enter()
{
    bool flag = 0;
    char buf[64];
    printf("Введите пароль: \n");
    scanf("%s", buf);
    if (strcmp(buf, "pass_pass_pass_pass_pass_pass_pass") == 0)
    {
        flag = 1;
    }
    else
    {
        printf("Неверный пароль\n");
    }
    if (flag)
    {
        win();
    }
}

void win()
{
    char *flag = getenv("FLAG");
    if (flag != NULL)
    {
        printf("%s\n", flag);
    }
    else 
    {
        printf("FLAG not found\n");
    }
    exit(0);
}

void hint()
{
    printf("Попробуй спросить соседа справа, может он знает пароль\n");
}