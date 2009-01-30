// Testoob, Python Testing Out Of (The) Box
// Copyright (C) 2005-2006 The Testoob Team
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <windows.h>

// compile with:
//   cl setcolor.c user32.lib kernel32.lib /link /nodefaultlib /entry:main /opt:nowin98

int main(int argc, char **argv)
{
  HANDLE hStdout = GetStdHandle(STD_OUTPUT_HANDLE);
  HANDLE hStderr = GetStdHandle(STD_ERROR_HANDLE);
  if (argc < 2)
  {
    return 1; 
  }

  if (strcmp(argv[1],"get")==0)
  {
    CONSOLE_SCREEN_BUFFER_INFO screenBufferInfo;
    int r;
    
    r=GetConsoleScreenBufferInfo(hStderr, &screenBufferInfo);
    if (r==0) return 1;
    printf("%d\n",(unsigned int) (screenBufferInfo.wAttributes));
  }
  else if (strcmp(argv[1],"set")==0)
  {
    WORD color=0x0f;
    sscanf(argv[2],"%hd",&color);
    SetConsoleTextAttribute(hStdout, color);
  }    
  else
  {
    return 1;
  }

  return 0;
}
