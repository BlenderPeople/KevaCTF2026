#include <stdio.h>
#include <string.h>
#include <stdlib.h>

char result[2048];

void transform(char *input);

int main(int argc, char *argv[])
{
    if (argc < 2) 
    {
        printf("Передайте строку как аргумент\n");
        return 1;
    }
    transform(argv[1]);
    return 0;
}

int binary_string_to_bytes(const char *bin_str, unsigned char *out, int max_out)
{
    char copy[2048];
    strcpy(copy, bin_str);
    int count = 0;
    char *token = strtok(copy, " ");
    while (token != NULL && count < max_out) 
    {
        // Проверяем, что строка состоит ровно из 8 символов '0'/'1'
        unsigned char byte = 0;
        for (int i = 0; i < 8; i++) 
        {
            if (token[i] != '0' && token[i] != '1') return -1;
            byte = (byte << 1) | (token[i] - '0');
        }
        out[count++] = byte;
        token = strtok(NULL, " ");
    }
    return count;
}

void transform(char *input)
{
    char change[2048] = {0};
    int bin_idx = 0;
    for (int i = 0; input[i] != '\0'; i++) 
    {
        unsigned char ch = (unsigned char)input[i];
        for (int bit = 7; bit >= 0; bit--) 
        {
            int val = ch & (1 << bit);
            change[bin_idx++] = val ? '0' : '1'; 
        }
        if (input[i+1] != '\0') 
        {
            change[bin_idx++] = ' ';
        }
    }
    change[bin_idx] = '\0';

    unsigned char expected[] = 
    {
        0x94, 0x9A, 0x89, 0x9E, 0x9C, 0x8B, 0x99,
        0x84, 0x98, 0xCF, 0xCF, 0x9B, 0xA0, 0x98, 0xCF,
        0xCF, 0x9B, 0xA0, 0x98, 0xCF, 0xCF, 0x9B, 0x82
    };
    int expected_len = sizeof(expected);

    //Преобразуем change в массив байтов
    unsigned char received[128];
    int received_len = binary_string_to_bytes(change, received, sizeof(received));

    if (received_len == expected_len && memcmp(received, expected, expected_len) == 0) 
    {
        printf("Успех\n");
    }
    else 
    {
        //Применяем циклический сдвиг влево на 1 к каждому байту и собираем строку
        char output[2048] = {0};
        int out_idx = 0;
        for (int i = 0; i < received_len; i++) 
        {
            unsigned char shifted = (received[i] << 1) | (received[i] >> 7);
            output[out_idx++] = (char)shifted;
        }
        output[out_idx] = '\0';
        strcpy(result, output);
        printf("%s\n", result);
    }
}

// #include <stdio.h>
// #include <string.h> 
// #include <stdlib.h> 

// char middle[2048];
// char result[2048];
// char buf[128];
// void transform(char *input);


// int main(int argc, char *argv[])
// {
//     if (argc < 2) {
//         printf("Передайте строку как аргумент\n");
//         return 1;
//     }
//     transform(argv[1]);
//     return 0;
// }

// void transform(char *input)
// {
//     int bin_idx = 0;
//     char binary[2048];
//     char change[2048];
//     for (int i = 0; input[i] != '\0'; i++)
//     {
//         unsigned char ch = (unsigned char)input[i];
//         for (int bit = 7; bit >= 0; bit--)
//         {
//             binary[bin_idx] = (ch & (1 << bit) ? '1' : '0');
//             change[bin_idx] = (binary[bin_idx] == '0') ? '1': '0';
//             bin_idx++;
//         }
//        if (input[i+1] != '\0') 
//         {
//             binary[bin_idx] = ' ';
//             change[bin_idx] = ' ';
//             bin_idx++;
//         }
//     }
//     binary[bin_idx] = '\0';
//     change[bin_idx] = '\0';

//     char a[2048] = "10010100 10011010 10001001 10011110 10011100 10001011 10011001";
//     char b[512] = "10000100 10011000 11001111 11001111 10011011 10100000 10011000 11001111";
//     char c[512] = "11001111 10011011 10100000 10011000 11001111 11001111 10011011 10000010";
//     strcpy(middle, a);
//     strcat(middle, " ");
//     strcat(middle, b);
//     strcat(middle, " ");
//     strcat(middle, c);

//     if (strcmp(middle, change) == 0)
//     {
//         printf("Успех\n");
//     }
//     else
//     {
//         char *token = strtok(change, " ");
//         char output[2048] = {0};
//         int out_idx = 0;
//         while (token != NULL) {

//             unsigned char byte = 0;
//             for (int i = 0; i < 8; i++) {
//                 byte = (byte << 1) | (token[i] - '0');
//             }

//             byte = (byte << 1) | (byte >> 7);
    
//             output[out_idx++] = (char)byte;
//             token = strtok(NULL, " ");
//         }
//         output[out_idx] = '\0';
//         strcpy(result, output);
//         printf("%s\n", result);
//         exit(0);
//     }

// }
//kevactf{g00d_g00d_g00d}
//107 101 118 97 99 116 102 123 103 48 48 100 95 103 48 48 100 95 103 48 48 100 125
//128 64 32 16 8 4 2 1
//01101011 01100101 01110110 01100001 01100011 01110100 01100110 kevactf 
//01111011 {
//01100111 00110000 00110000 01100100 01011111 01100111 00110000 00110000 01100100 01011111 01100111 00110000 00110000 01100100 g00d_g00d_g00d
//01111101 }

//инверсия
//10010100 10011010 10001001 10011110 10011100 10001011 10011001
//10000100 10011000 11001111 11001111 10011011 10100000 10011000 11001111
//11001111 10011011 10100000 10011000 11001111 11001111 10011011 10000010