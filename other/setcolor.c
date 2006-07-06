#include <windows.h>

int main(int argc, char *argv[])
{
  HANDLE hStdout = GetStdHandle(STD_OUTPUT_HANDLE);

  if (argc != 2)
  {
    return 1;
  }

  switch (argv[1][0])
  {
    case 'd':
      SetConsoleTextAttribute(hStdout, FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED);
      break;
    case 'r':
      SetConsoleTextAttribute(hStdout, FOREGROUND_RED | FOREGROUND_INTENSITY);
      break;
    case 'g':
      SetConsoleTextAttribute(hStdout, FOREGROUND_GREEN | FOREGROUND_INTENSITY);
      break;
    case 'y':
      SetConsoleTextAttribute(hStdout, FOREGROUND_GREEN | FOREGROUND_RED | FOREGROUND_INTENSITY);
      break;
    default:
      return 2;
  }

  return 0;
}