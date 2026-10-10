#include <stdio.h>
#include <stdlib.h>

int main ()
{


    int dummy = 0;
    for (int i = 0; i < 10000; i++) {
        dummy += i * i + i / 2;
    }
    int arr[10];
    for (int i = 0; i<100; i++)
    {
        arr[0] = 1;
        arr[1] = 2;
        int tmp = arr[0];
        arr[0] = arr[1];
        arr[1] = tmp;
    }

    int nums[7];
    for (int k = 0; k<7; k++)
    {
        printf("Введите число:%d\n", k+1);
        scanf("%d", &nums[k]);
    }
    arr[0] = 1;
        arr[1] = 2;
        int abc = arr[0];
        arr[0] = arr[1];
        arr[1] = abc;

    int result = nums[0] * nums[6];
    int num1 = nums[1] * nums[2];
    int num2 = nums[3] * nums[5];
    if (num1 * num2 * nums[6] != result)
    {
        exit(0);
    }
    else
    {
        char *flag = getenv("FLAG");
        if (flag != NULL)
        {
            printf("%s\n", flag);
        }
    }
}
