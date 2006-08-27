#include <windows.h>

// compile with:
//   cl setcolor.c user32.lib kernel32.lib /link /nodefaultlib /entry:main /opt:nowin98

int main()
{
  HANDLE hStdout = GetStdHandle(STD_OUTPUT_HANDLE);

  const char *szCmdLine = GetCommandLine();
  char cCmd = CharPrev(szCmdLine, szCmdLine + lstrlen(szCmdLine))[0];

  switch (cCmd)
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
      return 1;
  }

  return 0;
}
