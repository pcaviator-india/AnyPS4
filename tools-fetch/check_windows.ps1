Add-Type @'
  using System;
  using System.Runtime.InteropServices;
  using System.Collections.Generic;
  using System.Text;

  public class WinEnum {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    public static List<string> GetWindowsForPid(uint targetPid) {
      var list = new List<string>();
      EnumWindows((hWnd, lParam) => {
        uint pid;
        GetWindowThreadProcessId(hWnd, out pid);
        if (pid == targetPid) {
          StringBuilder sb = new StringBuilder(256);
          GetWindowText(hWnd, sb, 256);
          bool vis = IsWindowVisible(hWnd);
          list.Add(string.Format("HWND: 0x{0:X}, Title: '{1}', Visible: {2}", hWnd.ToInt64(), sb.ToString(), vis));
        }
        return true;
      }, IntPtr.Zero);
      return list;
    }
  }
'@
[WinEnum]::GetWindowsForPid(43056)
