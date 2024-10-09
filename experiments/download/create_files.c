#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

void intToStr(int N, char *str) {
    int i = 0;
    int sign = N;

    if (N < 0)
        N = -N;

    while (N > 0) {
        str[i++] = N % 10 + '0';
      	N /= 10;
    } 

    if (sign < 0) {
        str[i++] = '-';
    }
    str[i] = '\0';

    for (int j = 0, k = i - 1; j < k; j++, k--) {
        char temp = str[j];
        str[j] = str[k];
        str[k] = temp;
    }
}

int main() {	
    char file_name[50];
    char str_int[12];
    unsigned char hex_digit;

    for (int pow_n = 0; pow_n < 8; pow_n++) {
	hex_digit = 0;
	strcpy(file_name, "block_");
	intToStr(pow(2, pow_n), str_int);
        strcat(file_name, str_int);
	strcat(file_name, "B");	

    	FILE *file = fopen(file_name, "wb");

    	// Write a Mega of hexadecimal
	for (int i = 0; i < 1048576; i++) {
 	    fputc(hex_digit, file);

	    hex_digit++;
	    if (hex_digit == pow(2, pow_n)) {
	    	hex_digit = 0;
	    }
    	}

    	// Close the file
    	fclose(file);
    }

    return 0;
}
