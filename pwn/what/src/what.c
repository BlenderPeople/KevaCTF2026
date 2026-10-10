#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

void enter();
void hint();

int main()
{
    int choice;
    do
    {
        printf("Привет, сделай свой выбор:\n");
        printf("1. Ввести формат\n");
        printf("2. Подсказка\n");
        printf("3. Выйти\n");
        scanf("%d", &choice);
        getchar();
        
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
    char buf[64];
    char *flag = "kevactf{f0rm4t_str1ng_1s_fun}\n";
    printf("Введите верный формат: \n");
    fgets(buf, sizeof(buf), stdin);
    size_t len = strlen(buf);
    if (len > 0 && buf[len-1] == '\n')
        buf[len-1] = '\0';
    
    if (strcmp(buf, "abra_cadabra") == 0)
    {
        printf("%s\n",&flag);
        exit(0);
    }
    else
    {
        printf(buf);
        exit(0);
    }
}

void hint()
{
    printf("Пробуй ещё\n");
}